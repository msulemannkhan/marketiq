from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.config import settings
from app.services.llm_service import LaptopAssistant
from typing import Optional
from app.models.user import User
import uuid
import logging

router = APIRouter()

# Initialize logger
logger = logging.getLogger(__name__)

# Global assistant instance (in production, this might be handled differently)
_assistant_instance = None


def get_assistant(db: Session = Depends(get_db)) -> LaptopAssistant:
    """Get or create LaptopAssistant instance"""
    global _assistant_instance

    # Force recreation for debugging (remove this in production)
    _assistant_instance = None

    if _assistant_instance is None:
        try:
            logger.warning("Creating new LaptopAssistant instance...")
            api_key = settings.GEMINI_API_KEY or ""
            _assistant_instance = LaptopAssistant(api_key=api_key, db=db)
            logger.warning("LaptopAssistant instance created successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LaptopAssistant: {e}")
            raise HTTPException(
                status_code=503,
                detail="Failed to initialize AI assistant service"
            )

    return _assistant_instance


def get_optional_current_user(db: Session = Depends(get_db)):
    """Get current user if authenticated, None otherwise"""
    try:
        from fastapi import Request
        from app.core.auth import get_current_user
        # Try to get authenticated user
        return get_current_user(db)
    except:
        # If authentication fails, return None (allow anonymous access)
        return None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Chat with the laptop recommendation assistant"""

    try:
        # Conversation memory service
        from app.services.conversation_memory import ConversationMemoryService
        memory_service = ConversationMemoryService(db)

        # Get assistant instance
        assistant = get_assistant(db)

        # Determine session
        session_id = request.session_id
        if request.start_new or not session_id:
            # Create a new session
            session = memory_service.create_session(
                user_id=str(current_user.id) if current_user else None,
                initial_context=request.context or {}
            )
            session_id = str(session.id)

        # Prepare context
        # Merge stored session context with incoming context
        try:
            stored_context = memory_service.get_session_context(session_id)
        except Exception:
            stored_context = {}
        context = {**(stored_context or {}), **(request.context or {})}
        context["session_id"] = session_id

        # Attach last 20-30 history messages for grounding (user/assistant roles)
        try:
            from app.services.session_service import session_manager

            # Get conversation history from session service (20-30 messages)
            conversation_history = session_manager.get_conversation_history(session_id, limit=25)
            context["conversation_history"] = conversation_history

            # Also get from memory service for compatibility
            history = memory_service.get_session_history(session_id=session_id, limit=20, include_context=False)
            history_messages = []
            for m in history.get("messages", []):
                role = "user" if getattr(m, "message_type", "user") == "user" else "assistant"
                history_messages.append({
                    "role": role,
                    "content": getattr(m, "content", "")
                })
            context["history_messages"] = history_messages
        except Exception as e:
            logger.warning(f"Could not retrieve conversation history: {e}")
            context["history_messages"] = []
            context["conversation_history"] = []

        # Store user message in memory
        try:
            from datetime import datetime
            memory_service.add_message(
                session_id=session_id,
                message=request.message,
                message_type="user",
                metadata={"timestamp": datetime.utcnow().isoformat()}
            )
        except Exception:
            # Non-blocking if memory persistence fails
            pass

        # Search for relevant PDF context using Pinecone
        try:
            from app.services.pinecone_service import pinecone_service
            from app.services.pdf_rag_service import pdf_rag_service

            pdf_contexts = []

            # First try Pinecone vector search for PDF chunks
            if pinecone_service.is_available():
                pdf_contexts = await pinecone_service.search_pdf_context(request.message, limit=5)
                logger.info(f"Found {len(pdf_contexts)} relevant PDF chunks from Pinecone")

            # Fallback to local PDF RAG if Pinecone fails
            if not pdf_contexts:
                pdf_contexts = pdf_rag_service.search_relevant_chunks(request.message, limit=5, use_pinecone=False)
                logger.info(f"Found {len(pdf_contexts)} relevant PDF chunks from local RAG")

            # Add PDF context to the request context
            if pdf_contexts:
                context["pdf_contexts"] = pdf_contexts
                context["pdf_summary"] = pdf_rag_service.get_chunk_context(pdf_contexts)
        except Exception as e:
            logger.warning(f"Could not retrieve PDF context: {e}")
            context["pdf_contexts"] = []

        # Get response from assistant with enhanced context
        logger.error(f"DEBUG: About to call assistant.chat with message: {request.message}")
        logger.info(f"Context includes: {len(context.get('conversation_history', []))} conversation messages, "
                    f"{len(context.get('pdf_contexts', []))} PDF chunks")
        response_data = await assistant.chat(
            message=request.message,
            context=context
        )
        logger.error(f"DEBUG: assistant.chat returned response")

        # Persist assistant response
        try:
            memory_service.add_message(
                session_id=session_id,
                message=response_data["response"],
                message_type="assistant",
                metadata=response_data.get("metadata", {}),
                tool_calls=response_data.get("tool_calls", []),
                citations=response_data.get("citations", [])
            )
        except Exception:
            pass

        # Log interaction in background
        background_tasks.add_task(
            log_chat_interaction,
            session_id,
            request.message,
            response_data["response"]
        )

        return ChatResponse(
            response=response_data["response"],
            citations=response_data.get("citations", []),
            recommendations=response_data.get("recommendations"),
            session_id=session_id
        )

    except Exception as e:
        logger.error(f"Chat request failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat request. Please try again."
        )


@router.post("/chat/feedback")
async def provide_chat_feedback(
    session_id: str,
    message_index: int,
    feedback: str,  # "helpful", "not_helpful", "inaccurate"
    comment: str = None,
    db: Session = Depends(get_db)
):
    """Provide feedback on chat responses"""

    # In a full implementation, this would store feedback in a database
    # For now, we'll just log it
    logger.info(f"Chat feedback received - Session: {session_id}, "
                f"Message: {message_index}, Feedback: {feedback}, Comment: {comment}")

    return {
        "message": "Feedback received. Thank you for helping us improve!",
        "session_id": session_id
    }


@router.get("/chat/sessions/{session_id}")
async def get_chat_session(
    session_id: str,
    include_context: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get chat session history with full conversation memory"""
    from app.services.conversation_memory import ConversationMemoryService

    try:
        # Validate UUID format
        try:
            uuid.UUID(session_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session ID format. Must be a valid UUID.")

        memory_service = ConversationMemoryService(db)
        session_history = memory_service.get_session_history(
            session_id=session_id,
            include_context=include_context
        )
        return session_history
    except HTTPException:
        # Re-raise HTTP exceptions (like our 400 for invalid UUID)
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get session history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session history")


@router.delete("/chat/sessions/{session_id}")
async def clear_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Clear/delete a chat session"""

    # In a full implementation, this would clear session data from database/cache
    logger.info(f"Chat session cleared: {session_id}")

    return {
        "message": f"Session {session_id} cleared successfully"
    }


@router.get("/chat/health")
async def check_chat_health(db: Session = Depends(get_db)):
    """Check if chat service is healthy and ready"""

    try:
        # Test if we can create an assistant instance
        if settings.GEMINI_API_KEY:
            assistant = get_assistant(db)
            status = "healthy"
            details = "Chat service is operational"
        else:
            status = "degraded"
            details = "LLM API key not configured"

        return {
            "status": status,
            "details": details,
            "llm_configured": bool(settings.GEMINI_API_KEY),
            "vector_store_available": assistant.vector_store is not None if 'assistant' in locals() else False
        }

    except Exception as e:
        logger.error(f"Chat health check failed: {e}")
        return {
            "status": "unhealthy",
            "details": str(e),
            "llm_configured": bool(settings.GEMINI_API_KEY),
            "vector_store_available": False
        }


@router.post("/chat/agentic", response_model=dict)
async def agentic_chat(
    request: dict,  # Using dict temporarily instead of AgenticChatRequest
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Enhanced agentic chat with full conversation memory and tool chaining"""
    from app.services.conversation_memory import ConversationMemoryService
    from datetime import datetime

    try:
        # Validate input
        if not isinstance(request, dict):
            raise HTTPException(status_code=400, detail="Invalid request body. Expected JSON object.")
        message = request.get("message")
        if not message or not isinstance(message, str):
            raise HTTPException(status_code=422, detail="Field 'message' is required and must be a non-empty string.")
        context = request.get("context") or {}
        if context is not None and not isinstance(context, dict):
            raise HTTPException(status_code=422, detail="Field 'context' must be an object if provided.")

        memory_service = ConversationMemoryService(db)

        # Get or create session
        session_id = request.get("session_id")
        if not session_id:
            session = memory_service.create_session(
                user_id=request.get("user_id"),
                initial_context=context
            )
            session_id = str(session.id)

        # Store user message
        user_message = memory_service.add_message(
            session_id=session_id,
            message=message,
            message_type="user",
            metadata={"timestamp": datetime.utcnow().isoformat()}
        )

        # Get assistant instance
        assistant = get_assistant(db)

        # Get conversation context
        conversation_context = memory_service.get_session_context(session_id)
        full_context = {**conversation_context, **context}

        # Attach last 20-30 history messages for grounding
        try:
            from app.services.session_service import session_manager

            # Get extended conversation history (25-30 messages)
            conversation_history = session_manager.get_conversation_history(session_id, limit=30)
            full_context["conversation_history"] = conversation_history

            # Also get from memory service
            history = memory_service.get_session_history(session_id=session_id, limit=20, include_context=False)
            history_messages = []
            for m in history.get("messages", []):
                role = "user" if getattr(m, "message_type", "user") == "user" else "assistant"
                history_messages.append({
                    "role": role,
                    "content": getattr(m, "content", "")
                })
            full_context["history_messages"] = history_messages
        except Exception as e:
            logger.warning(f"Could not retrieve conversation history: {e}")
            full_context["history_messages"] = []
            full_context["conversation_history"] = []

        # Search for relevant PDF context
        try:
            from app.services.pinecone_service import pinecone_service
            from app.services.pdf_rag_service import pdf_rag_service

            pdf_contexts = []

            # Try Pinecone vector search for PDF chunks
            if pinecone_service.is_available():
                # Analyze query for better search
                query_analysis = pinecone_service.analyze_and_improve_query(message, full_context)

                # Search with enhanced query
                vector_results = await pinecone_service.enhanced_vector_search(
                    query_analysis,
                    limit=10,
                    include_pdfs=True
                )

                # Extract PDF-specific results
                pdf_contexts = [r for r in vector_results if r.get('result_type') == 'pdf_chunk']
                logger.info(f"Found {len(pdf_contexts)} PDF chunks and {len(vector_results) - len(pdf_contexts)} product results")

                full_context["vector_search_results"] = vector_results

            # Fallback to local PDF RAG
            if not pdf_contexts:
                pdf_contexts = pdf_rag_service.search_relevant_chunks(message, limit=5, use_pinecone=False)

            # Add PDF context
            if pdf_contexts:
                full_context["pdf_contexts"] = pdf_contexts
                full_context["pdf_summary"] = pdf_rag_service.get_chunk_context(pdf_contexts)

        except Exception as e:
            logger.warning(f"Could not retrieve PDF/vector context: {e}")

        # Get response from assistant with enhanced context
        logger.info(f"Agentic chat context: {len(full_context.get('conversation_history', []))} messages, "
                   f"{len(full_context.get('pdf_contexts', []))} PDF chunks, "
                   f"{len(full_context.get('vector_search_results', []))} vector results")

        response_data = await assistant.chat(
            message=message,
            context=full_context
        )

        # Store assistant response
        assistant_message = memory_service.add_message(
            session_id=session_id,
            message=response_data.get("response", ""),
            message_type="assistant",
            metadata=response_data.get("metadata", {}),
            tool_calls=response_data.get("tool_calls", []),
            citations=response_data.get("citations", [])
        )

        # Update conversation context with new insights
        insights = None
        if request.get("enable_memory", True):
            insights = memory_service.get_conversation_insights(session_id)
            memory_service.update_context(
                session_id=session_id,
                context_type="conversation_insights",
                context_data=insights
            )

        # Generate next suggested questions
        suggested_questions = await _generate_suggested_questions(message, response_data)

        return {
            "response": response_data.get("response", ""),
            "session_id": session_id,
            "tool_calls_made": response_data.get("tool_calls", []),
            "citations": response_data.get("citations", []),
            "recommendations": response_data.get("recommendations"),
            "conversation_insights": insights if request.get("enable_memory", True) else None,
            "next_suggested_questions": suggested_questions,
            "response_time_ms": response_data.get("response_time_ms"),
            "tokens_used": response_data.get("tokens_used")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agentic chat request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process agentic chat: {str(e)}")


async def _generate_suggested_questions(user_message: str, response_data: dict) -> list:
    """Generate suggested follow-up questions based on conversation context"""

    # Simple implementation - in production would use LLM
    suggestions = []

    message_lower = user_message.lower()

    if "recommend" in message_lower or "suggest" in message_lower:
        suggestions.extend([
            "Can you compare these options?",
            "What's the price range for these recommendations?",
            "Are there any current deals or discounts?"
        ])
    elif "compare" in message_lower:
        suggestions.extend([
            "Which one offers better value for money?",
            "What are the main differences?",
            "Which would you recommend for my needs?"
        ])
    elif "price" in message_lower or "budget" in message_lower:
        suggestions.extend([
            "Are there any financing options available?",
            "Can you find similar laptops in a different price range?",
            "What features justify the price difference?"
        ])
    else:
        suggestions.extend([
            "Can you recommend something based on this?",
            "What are my options in this category?",
            "How do these compare to other brands?"
        ])

    return suggestions[:3]  # Return top 3 suggestions


async def log_chat_interaction(session_id: str, user_message: str, assistant_response: str):
    """Log chat interaction for analytics and improvement"""

    # In a production environment, this would:
    # 1. Store in a dedicated chat_logs table
    # 2. Include metadata like timestamp, response time, etc.
    # 3. Possibly send to analytics service

    logger.info(f"Chat interaction logged - Session: {session_id}, "
                f"User message length: {len(user_message)}, "
                f"Response length: {len(assistant_response)}")


@router.post("/chat/generate-embeddings")
async def generate_embeddings(
    db: Session = Depends(get_db)
):
    """Generate embeddings for all products (admin endpoint)"""

    try:
        assistant = get_assistant(db)
        await assistant.generate_embeddings_for_products()

        return {
            "message": "Embeddings generated successfully",
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate embeddings: {str(e)}"
        )


@router.post("/chat/sync-pinecone")
async def sync_products_to_pinecone(
    db: Session = Depends(get_db)
):
    """Sync all products to Pinecone vector database (admin endpoint)"""

    try:
        assistant = get_assistant(db)
        result = await assistant.sync_products_to_pinecone()

        if result.get("success"):
            return {
                "message": result.get("message"),
                "products_synced": result.get("products_synced"),
                "status": "completed"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Unknown error occurred")
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pinecone sync failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync products to Pinecone: {str(e)}"
        )


@router.get("/chat/pinecone-status")
async def get_pinecone_status():
    """Get Pinecone vector database status"""

    try:
        from app.services.pinecone_service import pinecone_service

        if pinecone_service.is_available():
            stats = await pinecone_service.get_index_stats()
            return {
                "available": True,
                "status": "connected",
                "index_stats": stats
            }
        else:
            return {
                "available": False,
                "status": "not_configured",
                "message": "Pinecone API key not configured or service unavailable"
            }

    except Exception as e:
        logger.error(f"Failed to get Pinecone status: {e}")
        return {
            "available": False,
            "status": "error",
            "error": str(e)
        }


@router.post("/chat/test-vector-search")
async def test_vector_search(
    query: str = Query(..., description="Test query for vector search"),
    limit: int = Query(5, ge=1, le=20, description="Number of results to return")
):
    """Test vector search functionality"""

    try:
        from app.services.pinecone_service import pinecone_service

        if not pinecone_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Pinecone service not available"
            )

        # Analyze and improve query
        query_analysis = pinecone_service.analyze_and_improve_query(query)

        # Perform vector search
        vector_results = await pinecone_service.enhanced_vector_search(query_analysis, limit=limit)

        return {
            "query": query,
            "query_analysis": query_analysis,
            "vector_results": vector_results,
            "results_count": len(vector_results)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Vector search test failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Vector search test failed: {str(e)}"
        )


@router.get("/chat/session/{session_id}")
async def get_session_info(session_id: str):
    """Get session information and history"""
    try:
        from app.services.session_service import session_manager

        session_context = session_manager.get_session_context(session_id)
        session_stats = session_manager.get_session_stats(session_id)

        if not session_context:
            raise HTTPException(status_code=404, detail="Session not found")

        return {
            "session_id": session_id,
            "context": session_context,
            "stats": session_stats
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session info: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session info: {str(e)}"
        )


@router.get("/chat/pdf-status")
async def get_pdf_rag_status():
    """Get PDF RAG service status"""
    try:
        from app.services.pdf_rag_service import pdf_rag_service

        stats = pdf_rag_service.get_stats()
        return {
            "status": "available",
            "stats": stats
        }

    except Exception as e:
        logger.error(f"Failed to get PDF RAG status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.post("/chat/sync-pdfs-to-pinecone")
async def sync_pdfs_to_pinecone(
    hp_config_path: Optional[str] = Query(
        default="data/hp_detailed_product_configurations.json",
        description="Path to HP configuration file with PDF metadata"
    ),
    db: Session = Depends(get_db)
):
    """Sync PDF chunks to Pinecone with product metadata from HP configuration"""
    try:
        from app.services.pdf_rag_service import pdf_rag_service
        from app.services.pinecone_service import pinecone_service

        # Check if services are available
        if not pinecone_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Pinecone service not available. Please configure PINECONE_API_KEY."
            )

        # Perform sync
        result = await pdf_rag_service.sync_pdfs_to_pinecone(hp_config_path)

        if result.get("success"):
            return {
                "message": "PDF chunks successfully synced to Pinecone",
                "chunks_synced": result.get("chunks_synced", 0),
                "total_chunks": result.get("total_chunks", 0),
                "status": "completed"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to sync PDFs: {result.get('error', 'Unknown error')}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF sync to Pinecone failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sync PDFs to Pinecone: {str(e)}"
        )