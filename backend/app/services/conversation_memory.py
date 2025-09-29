"""
Conversation Memory Service
Handles conversation context, history, and memory for agentic interactions
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
import json
import uuid
import logging

from app.models.conversation import ConversationSession, ConversationMessage, ConversationContext
from app.schemas.conversation import (
    ConversationSessionCreate, ConversationMessageCreate, ConversationContextCreate,
    ConversationSessionResponse, ConversationMessageResponse, ConversationSummary
)

logger = logging.getLogger(__name__)


class ConversationMemoryService:
    """Service for managing conversation memory and context"""

    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: Optional[str] = None, initial_context: Dict[str, Any] = None) -> ConversationSessionResponse:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())

        # Create session
        session = ConversationSession(
            id=session_id,
            user_id=user_id,
            status="active",
            metadata=initial_context or {}
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        # Initialize context if provided
        if initial_context:
            self._store_context(session_id, "initial_context", initial_context)

        return ConversationSessionResponse(
            id=session.id,
            user_id=session.user_id,
            status=session.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
            message_count=0,
            metadata=session.session_metadata
        )

    def add_message(
        self,
        session_id: str,
        message: str,
        message_type: str = "user",
        metadata: Dict[str, Any] = None,
        tool_calls: List[Dict] = None,
        citations: List[str] = None
    ) -> ConversationMessageResponse:
        """Add a message to conversation history"""

        # Validate session_id is a valid UUID
        try:
            import uuid
            uuid.UUID(session_id)
        except (ValueError, AttributeError):
            # Skip adding message for invalid session_id
            return None

        # Verify session exists
        session = self.db.query(ConversationSession).filter(
            ConversationSession.id == session_id
        ).first()

        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Create message
        message_obj = ConversationMessage(
            session_id=session_id,
            message_type=message_type,
            content=message,
            metadata=metadata or {},
            tool_calls=tool_calls or [],
            citations=citations or []
        )

        self.db.add(message_obj)

        # Update session
        session.updated_at = datetime.utcnow()
        session.message_count = self.db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id
        ).count() + 1

        self.db.commit()
        self.db.refresh(message_obj)

        return ConversationMessageResponse(
            id=message_obj.id,
            session_id=message_obj.session_id,
            message_type=message_obj.message_type,
            content=message_obj.content,
            metadata=message_obj.message_metadata,
            tool_calls=message_obj.tool_calls,
            citations=message_obj.citations,
            created_at=message_obj.created_at
        )

    def get_session_history(
        self,
        session_id: str,
        limit: int = 50,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """Get complete session history with messages and context"""

        # Validate session_id is a valid UUID
        try:
            import uuid
            uuid.UUID(session_id)
        except (ValueError, AttributeError):
            # Return empty history for invalid session_id
            return {
                "session_id": session_id,
                "messages": [],
                "context": {},
                "summary": None
            }

        session = self.db.query(ConversationSession).filter(
            ConversationSession.id == session_id
        ).first()

        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Get messages
        messages = self.db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id
        ).order_by(ConversationMessage.created_at).limit(limit).all()

        message_responses = [
            ConversationMessageResponse(
                id=msg.id,
                session_id=msg.session_id,
                message_type=msg.message_type,
                content=msg.content,
                metadata=msg.message_metadata,
                tool_calls=msg.tool_calls,
                citations=msg.citations,
                created_at=msg.created_at
            )
            for msg in messages
        ]

        # Get context if requested
        context = {}
        if include_context:
            context = self.get_session_context(session_id)

        return {
            "session": ConversationSessionResponse(
                id=session.id,
                user_id=session.user_id,
                status=session.status,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=session.message_count,
                metadata=session.session_metadata
            ),
            "messages": message_responses,
            "context": context,
            "summary": self._generate_conversation_summary(messages)
        }

    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get accumulated context for a session"""

        # Validate session_id is a valid UUID
        try:
            import uuid
            uuid.UUID(session_id)
        except (ValueError, AttributeError):
            # Return empty context for invalid session_id
            return {}

        context_entries = self.db.query(ConversationContext).filter(
            ConversationContext.session_id == session_id
        ).order_by(desc(ConversationContext.created_at)).all()

        # Merge context with most recent taking precedence
        merged_context = {}
        for entry in reversed(context_entries):  # Oldest first
            if entry.context_data:
                merged_context.update(entry.context_data)

        return merged_context

    def update_context(
        self,
        session_id: str,
        context_type: str,
        context_data: Dict[str, Any],
        merge_with_existing: bool = True
    ) -> bool:
        """Update session context"""

        try:
            if merge_with_existing:
                # Get existing context and merge
                existing_context = self.get_session_context(session_id)
                existing_context.update(context_data)
                final_context = existing_context
            else:
                final_context = context_data

            # Store new context entry
            self._store_context(session_id, context_type, final_context)

            return True
        except Exception as e:
            logger.error(f"Failed to update context for session {session_id}: {e}")
            return False

    def extract_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """Extract user preferences from conversation history"""

        messages = self.db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id,
            ConversationMessage.message_type == "user"
        ).order_by(ConversationMessage.created_at).all()

        preferences = {
            "brands": [],
            "price_range": {},
            "use_cases": [],
            "features": [],
            "requirements": []
        }

        # Simple preference extraction (in production, would use NLP)
        for message in messages:
            content_lower = message.content.lower()

            # Brand preferences
            if "hp" in content_lower or "hewlett" in content_lower:
                if "hp" not in preferences["brands"]:
                    preferences["brands"].append("HP")

            if "lenovo" in content_lower or "thinkpad" in content_lower:
                if "lenovo" not in preferences["brands"]:
                    preferences["brands"].append("Lenovo")

            # Use case detection
            use_cases = ["business", "gaming", "programming", "student", "travel"]
            for use_case in use_cases:
                if use_case in content_lower and use_case not in preferences["use_cases"]:
                    preferences["use_cases"].append(use_case)

            # Feature preferences
            features = ["touchscreen", "fingerprint", "backlit keyboard", "lightweight", "long battery"]
            for feature in features:
                if feature.replace(" ", "") in content_lower.replace(" ", "") and feature not in preferences["features"]:
                    preferences["features"].append(feature)

            # Price range extraction
            import re
            price_matches = re.findall(r'\$?(\d{3,4})', content_lower)
            if price_matches:
                prices = [int(p) for p in price_matches]
                if prices:
                    preferences["price_range"] = {
                        "min": min(prices) if len(prices) > 1 else None,
                        "max": max(prices),
                        "budget": max(prices)
                    }

        return preferences

    def get_conversation_insights(self, session_id: str) -> Dict[str, Any]:
        """Get insights about the conversation for better recommendations"""

        session_history = self.get_session_history(session_id, include_context=True)
        preferences = self.extract_user_preferences(session_id)

        # Analyze conversation patterns
        user_messages = [msg for msg in session_history["messages"] if msg.message_type == "user"]
        assistant_messages = [msg for msg in session_history["messages"] if msg.message_type == "assistant"]

        insights = {
            "preferences": preferences,
            "conversation_length": len(session_history["messages"]),
            "user_engagement": len(user_messages),
            "tool_usage": self._analyze_tool_usage(session_history["messages"]),
            "topics_discussed": self._extract_topics(user_messages),
            "decision_stage": self._analyze_decision_stage(session_history["messages"]),
            "next_actions": self._suggest_next_actions(session_history, preferences)
        }

        return insights

    def cleanup_old_sessions(self, days_to_keep: int = 30) -> int:
        """Clean up old conversation sessions"""

        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        # Delete old sessions and cascade will handle messages and context
        deleted_count = self.db.query(ConversationSession).filter(
            ConversationSession.updated_at < cutoff_date,
            ConversationSession.status != "active"
        ).delete()

        self.db.commit()

        logger.info(f"Cleaned up {deleted_count} old conversation sessions")
        return deleted_count

    def close_session(self, session_id: str, reason: str = "completed") -> bool:
        """Close a conversation session"""

        session = self.db.query(ConversationSession).filter(
            ConversationSession.id == session_id
        ).first()

        if not session:
            return False

        session.status = "closed"
        session.session_metadata["close_reason"] = reason
        session.session_metadata["closed_at"] = datetime.utcnow().isoformat()

        self.db.commit()
        return True

    def get_user_conversation_history(
        self,
        user_id: str,
        limit: int = 10,
        include_active_only: bool = False
    ) -> List[ConversationSummary]:
        """Get conversation history for a user"""

        query = self.db.query(ConversationSession).filter(
            ConversationSession.user_id == user_id
        )

        if include_active_only:
            query = query.filter(ConversationSession.status == "active")

        sessions = query.order_by(desc(ConversationSession.updated_at)).limit(limit).all()

        summaries = []
        for session in sessions:
            # Get message count and last message
            last_message = self.db.query(ConversationMessage).filter(
                ConversationMessage.session_id == session.id
            ).order_by(desc(ConversationMessage.created_at)).first()

            summary = ConversationSummary(
                session_id=session.id,
                status=session.status,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=session.message_count or 0,
                last_message_preview=last_message.content[:100] + "..." if last_message and len(last_message.content) > 100 else last_message.content if last_message else "",
                topics=self._extract_session_topics(session.id)
            )
            summaries.append(summary)

        return summaries

    # Helper methods

    def _store_context(self, session_id: str, context_type: str, context_data: Dict[str, Any]):
        """Store context data for a session"""

        context_entry = ConversationContext(
            session_id=session_id,
            context_type=context_type,
            context_data=context_data
        )

        self.db.add(context_entry)
        self.db.commit()

    def _generate_conversation_summary(self, messages: List[ConversationMessage]) -> Dict[str, Any]:
        """Generate a summary of the conversation"""

        if not messages:
            return {"status": "no_messages"}

        user_messages = [msg for msg in messages if msg.message_type == "user"]
        assistant_messages = [msg for msg in messages if msg.message_type == "assistant"]

        summary = {
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "duration_minutes": (messages[-1].created_at - messages[0].created_at).total_seconds() / 60 if len(messages) > 1 else 0,
            "topics": self._extract_topics(user_messages),
            "tools_used": list({(tool.get("name") or "unknown") for msg in assistant_messages for tool in (msg.tool_calls or [])})
        }

        return summary

    def _analyze_tool_usage(self, messages: List[ConversationMessageResponse]) -> Dict[str, Any]:
        """Analyze tool usage patterns in conversation"""

        tool_usage = {}
        total_tool_calls = 0

        for message in messages:
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    tool_name = tool_call.get("name", "unknown")
                    tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
                    total_tool_calls += 1

        return {
            "total_calls": total_tool_calls,
            "tools_used": tool_usage,
            "most_used_tool": max(tool_usage.keys(), key=tool_usage.get) if tool_usage else None
        }

    def _extract_topics(self, messages: List[ConversationMessage]) -> List[str]:
        """Extract main topics from user messages"""

        # Simple keyword-based topic extraction
        topics = set()
        common_topics = [
            "price", "budget", "performance", "gaming", "business", "programming",
            "battery", "display", "memory", "storage", "processor", "graphics",
            "portability", "weight", "design", "build quality", "keyboard",
            "touchscreen", "fingerprint", "security", "warranty", "support"
        ]

        for message in messages:
            content_lower = message.content.lower()
            for topic in common_topics:
                if topic in content_lower:
                    topics.add(topic)

        return list(topics)

    def _analyze_decision_stage(self, messages: List[ConversationMessageResponse]) -> str:
        """Analyze what stage of decision making the user is in"""

        if len(messages) < 2:
            return "initial"

        user_messages = [msg.content.lower() for msg in messages if msg.message_type == "user"]
        recent_messages = user_messages[-3:] if len(user_messages) >= 3 else user_messages

        # Simple heuristics for decision stage
        exploration_words = ["what", "how", "tell me", "options", "available", "types"]
        comparison_words = ["compare", "vs", "versus", "difference", "better", "which"]
        decision_words = ["buy", "purchase", "price", "cost", "order", "want", "need"]

        exploration_score = sum(1 for msg in recent_messages for word in exploration_words if word in msg)
        comparison_score = sum(1 for msg in recent_messages for word in comparison_words if word in msg)
        decision_score = sum(1 for msg in recent_messages for word in decision_words if word in msg)

        if decision_score > comparison_score and decision_score > exploration_score:
            return "decision"
        elif comparison_score > exploration_score:
            return "comparison"
        else:
            return "exploration"

    def _suggest_next_actions(self, session_history: Dict, preferences: Dict) -> List[str]:
        """Suggest next actions based on conversation state"""

        actions = []
        stage = self._analyze_decision_stage(session_history["messages"])

        if stage == "exploration":
            actions.extend([
                "Ask about specific use cases",
                "Gather budget requirements",
                "Identify preferred brands"
            ])
        elif stage == "comparison":
            actions.extend([
                "Provide detailed comparisons",
                "Show pros and cons",
                "Highlight key differences"
            ])
        else:  # decision
            actions.extend([
                "Show pricing and availability",
                "Provide purchase links",
                "Offer warranty information"
            ])

        # Add specific actions based on preferences
        if not preferences.get("brands"):
            actions.append("Ask about brand preferences")

        if not preferences.get("price_range"):
            actions.append("Clarify budget constraints")

        return actions[:5]  # Return top 5 suggestions

    def _extract_session_topics(self, session_id: str) -> List[str]:
        """Extract topics for a specific session"""

        messages = self.db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id,
            ConversationMessage.message_type == "user"
        ).all()

        return self._extract_topics(messages)