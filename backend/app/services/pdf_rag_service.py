"""
PDF RAG Service for processing and retrieving relevant PDF chunks
"""

import os
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# PDF Processing imports
try:
    import fitz  # PyMuPDF
    PDF_PROCESSING_AVAILABLE = True
except ImportError:
    PDF_PROCESSING_AVAILABLE = False
    fitz = None

# Gemini embeddings
try:
    import google.generativeai as genai
    from app.core.config import settings
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    genai = None


class PDFRAGService:
    """Service for processing PDFs and retrieving relevant chunks"""

    def __init__(self, pdf_directory: str = "./pdfs"):
        self.pdf_directory = Path(pdf_directory)
        self.pdf_directory.mkdir(exist_ok=True)

        # In-memory storage for PDF chunks (in production, use vector database)
        self.pdf_chunks = []
        self.genai_client = None
        self.pinecone_service = None

        if EMBEDDINGS_AVAILABLE and settings.GEMINI_API_KEY:
            self._initialize_embeddings()

        # Initialize Pinecone if available
        self._initialize_pinecone()

        # Load existing PDFs
        self._load_pdfs()

    def _initialize_pinecone(self):
        """Initialize Pinecone service connection"""
        try:
            from app.services.pinecone_service import pinecone_service
            if pinecone_service.is_available():
                self.pinecone_service = pinecone_service
                logger.info("Pinecone service connected for PDF RAG")
            else:
                logger.warning("Pinecone service not available for PDF RAG")
        except Exception as e:
            logger.warning(f"Could not initialize Pinecone for PDF RAG: {e}")

    def _initialize_embeddings(self):
        """Initialize Gemini embeddings"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.genai_client = True  # Flag to indicate it's configured
            logger.info("Initialized Gemini embeddings for PDF RAG")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini embeddings for PDF RAG: {e}")
            self.genai_client = None

    def _load_pdfs(self):
        """Load and process all PDFs in the directory"""
        if not PDF_PROCESSING_AVAILABLE:
            logger.warning("PDF processing not available - PyMuPDF not installed")
            return

        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files to process")

        for pdf_file in pdf_files:
            try:
                self._process_pdf(pdf_file)
            except Exception as e:
                logger.error(f"Failed to process PDF {pdf_file}: {e}")

    def _process_pdf(self, pdf_path: Path):
        """Process a single PDF file into chunks"""
        if not PDF_PROCESSING_AVAILABLE:
            return

        try:
            doc = fitz.open(pdf_path)
            filename = pdf_path.name

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()

                if text.strip():  # Only process pages with text
                    # Split into chunks (simple approach - can be enhanced)
                    chunks = self._split_text_into_chunks(text, max_chunk_size=1000, overlap=100)

                    for i, chunk in enumerate(chunks):
                        if len(chunk.strip()) > 50:  # Only keep meaningful chunks
                            chunk_data = {
                                "content": chunk.strip(),
                                "source": filename,
                                "page": page_num + 1,
                                "chunk_id": f"{filename}_p{page_num + 1}_c{i + 1}",
                                "metadata": {
                                    "file_path": str(pdf_path),
                                    "file_size": pdf_path.stat().st_size,
                                    "chunk_length": len(chunk)
                                }
                            }

                            # Generate embedding if model available
                            if self.embeddings_model:
                                try:
                                    embedding = self.embeddings_model.encode([chunk])[0].tolist()
                                    chunk_data["embedding"] = embedding
                                except Exception as e:
                                    logger.warning(f"Failed to generate embedding for chunk: {e}")

                            self.pdf_chunks.append(chunk_data)

            doc.close()
            logger.info(f"Processed PDF {filename}: extracted {len([c for c in self.pdf_chunks if c['source'] == filename])} chunks")

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")

    def _split_text_into_chunks(self, text: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= max_chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + max_chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for punct in ['. ', '! ', '? ', '\n\n']:
                    last_punct = text.rfind(punct, start, end)
                    if last_punct > start:
                        end = last_punct + len(punct)
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks

    def search_relevant_chunks(self, query: str, limit: int = 5, use_pinecone: bool = True) -> List[Dict[str, Any]]:
        """Search for relevant PDF chunks based on query"""
        # First try Pinecone if available
        if use_pinecone and self.pinecone_service:
            try:
                import asyncio
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an async context
                    pdf_contexts = asyncio.create_task(
                        self.pinecone_service.search_pdf_context(query, limit)
                    )
                else:
                    # If we need to create a new event loop
                    pdf_contexts = loop.run_until_complete(
                        self.pinecone_service.search_pdf_context(query, limit)
                    )

                if pdf_contexts:
                    return pdf_contexts
            except Exception as e:
                logger.warning(f"Pinecone PDF search failed, falling back to local search: {e}")

        # Fallback to local search
        if not self.pdf_chunks:
            return []

        # If no embeddings available, use simple keyword matching
        if not self.embeddings_model:
            return self._keyword_search(query, limit)

        try:
            # Generate query embedding
            query_embedding = self.embeddings_model.encode([query])[0]

            # Calculate similarities
            scored_chunks = []
            for chunk in self.pdf_chunks:
                if "embedding" in chunk:
                    similarity = self._cosine_similarity(query_embedding, chunk["embedding"])
                    scored_chunks.append({
                        **chunk,
                        "relevance_score": similarity
                    })

            # Sort by relevance and return top results
            scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
            return scored_chunks[:limit]

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return self._keyword_search(query, limit)

    def _keyword_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback keyword-based search"""
        query_words = query.lower().split()
        scored_chunks = []

        for chunk in self.pdf_chunks:
            content_lower = chunk["content"].lower()
            score = sum(1 for word in query_words if word in content_lower)

            if score > 0:
                scored_chunks.append({
                    **chunk,
                    "relevance_score": score / len(query_words)
                })

        scored_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_chunks[:limit]

    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        import numpy as np

        vec1 = np.array(vec1)
        vec2 = np.array(vec2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0

        return dot_product / (norm1 * norm2)

    def get_chunk_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Format chunks into context string"""
        if not chunks:
            return ""

        context_parts = []
        for i, chunk in enumerate(chunks):
            context_parts.append(f"""
PDF Source {i+1}: {chunk['source']} (Page {chunk['page']})
Relevance Score: {chunk.get('relevance_score', 0):.3f}
Content: {chunk['content'][:500]}{'...' if len(chunk['content']) > 500 else ''}
""")

        return "\n---\n".join(context_parts)

    def get_stats(self) -> Dict[str, Any]:
        """Get PDF processing statistics"""
        if not self.pdf_chunks:
            return {"total_chunks": 0, "sources": [], "embeddings_available": bool(self.embeddings_model)}

        sources = list(set(chunk["source"] for chunk in self.pdf_chunks))
        chunks_with_embeddings = sum(1 for chunk in self.pdf_chunks if "embedding" in chunk)

        return {
            "total_chunks": len(self.pdf_chunks),
            "sources": sources,
            "chunks_with_embeddings": chunks_with_embeddings,
            "embeddings_available": bool(self.embeddings_model),
            "average_chunk_length": sum(len(chunk["content"]) for chunk in self.pdf_chunks) / len(self.pdf_chunks)
        }

    async def sync_pdfs_to_pinecone(self, hp_config_path: str = None) -> Dict[str, Any]:
        """Sync PDF chunks to Pinecone with metadata from HP configuration"""
        if not self.pinecone_service:
            return {"success": False, "error": "Pinecone service not available"}

        try:
            import json

            # Load HP configuration if provided
            pdf_metadata_map = {}
            if hp_config_path and Path(hp_config_path).exists():
                with open(hp_config_path, 'r') as f:
                    hp_config = json.load(f)

                # Extract PDF links from configuration
                for product in hp_config.get('products', []):
                    base_product = product.get('Base_Product', {})
                    pdf_links = base_product.get('PDF_Specification_Doc_Links', [])

                    for pdf_link in pdf_links:
                        pdf_url = pdf_link.get('url', '')
                        product_title = pdf_link.get('title', '')

                        # Map PDF filename to metadata
                        if pdf_url:
                            filename = pdf_url.split('/')[-1] if '/' in pdf_url else pdf_url.split('=')[-1] if '=' in pdf_url else ''
                            pdf_metadata_map[filename] = {
                                'pdf_url': pdf_url,
                                'product_name': product_title,
                                'brand': 'HP'
                            }

            # Sync all PDF chunks to Pinecone
            total_synced = 0
            for chunk in self.pdf_chunks:
                # Get metadata for this PDF if available
                source_file = chunk.get('source', '')
                metadata = pdf_metadata_map.get(source_file, {})

                # Upsert chunk to Pinecone
                success = await self.pinecone_service.upsert_pdf_chunks([chunk], metadata)
                if success:
                    total_synced += 1

            return {
                "success": True,
                "chunks_synced": total_synced,
                "total_chunks": len(self.pdf_chunks)
            }

        except Exception as e:
            logger.error(f"Failed to sync PDFs to Pinecone: {e}")
            return {"success": False, "error": str(e)}

    def add_pdf_file(self, file_path: str) -> Dict[str, Any]:
        """Add a new PDF file to the system"""
        pdf_path = Path(file_path)

        if not pdf_path.exists():
            return {"success": False, "error": "File not found"}

        if pdf_path.suffix.lower() != '.pdf':
            return {"success": False, "error": "File must be a PDF"}

        try:
            # Copy to PDF directory if not already there
            if pdf_path.parent != self.pdf_directory:
                import shutil
                destination = self.pdf_directory / pdf_path.name
                shutil.copy2(pdf_path, destination)
                pdf_path = destination

            # Process the PDF
            initial_chunk_count = len(self.pdf_chunks)
            self._process_pdf(pdf_path)
            new_chunk_count = len(self.pdf_chunks) - initial_chunk_count

            return {
                "success": True,
                "chunks_added": new_chunk_count,
                "filename": pdf_path.name
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

# Global PDF RAG service instance
pdf_rag_service = PDFRAGService()