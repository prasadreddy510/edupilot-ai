"""
RAG (Retrieval-Augmented Generation) service for NCERT content
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import logging
import os

from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for NCERT content retrieval"""

    def __init__(self):
        """Initialize RAG service with ChromaDB and embeddings"""

        # Initialize embedding model
        logger.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        logger.info("Embedding model loaded successfully")

        # Initialize ChromaDB
        persist_directory = settings.CHROMA_PERSIST_DIRECTORY
        os.makedirs(persist_directory, exist_ok=True)

        self.chroma_client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        self.collection_name = "ncert_content"
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "NCERT textbook content for grades 3-10"}
            )
            logger.info(f"Created new collection: {self.collection_name}")

    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts

        Args:
            texts: List of text strings

        Returns:
            List of embedding vectors
        """
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return embeddings.tolist()

    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add documents to the vector database

        Args:
            texts: List of text chunks
            metadatas: List of metadata dicts (grade, subject, chapter, page, etc.)
            ids: Optional list of document IDs
        """
        if not texts:
            logger.warning("No texts provided to add")
            return

        # Generate embeddings
        embeddings = self._generate_embeddings(texts)

        # Generate IDs if not provided
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in texts]

        # Add to collection
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(texts)} documents to collection")

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    def search(
        self,
        query: str,
        n_results: int = 5,
        grade: Optional[int] = None,
        subject: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant content

        Args:
            query: Search query
            n_results: Number of results to return
            grade: Optional grade filter
            subject: Optional subject filter

        Returns:
            List of search results with content and metadata
        """
        # Generate query embedding
        query_embedding = self._generate_embeddings([query])[0]

        # Build metadata filter
        where_filter = {}
        if grade is not None:
            where_filter["grade"] = grade
        if subject is not None:
            where_filter["subject"] = subject

        # Search
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter if where_filter else None
            )

            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else None,
                        'id': results['ids'][0][i] if results['ids'] else None
                    })

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching: {str(e)}")
            return []

    def get_context_for_topic(
        self,
        topic: str,
        grade: int,
        subject: Optional[str] = None,
        max_chunks: int = 5
    ) -> str:
        """
        Get relevant context for a topic

        Args:
            topic: Topic name
            grade: Student grade
            subject: Optional subject filter
            max_chunks: Maximum number of chunks to return

        Returns:
            Combined context string
        """
        # Search for relevant content
        results = self.search(
            query=topic,
            n_results=max_chunks,
            grade=grade,
            subject=subject
        )

        if not results:
            return ""

        # Combine context from results
        context_parts = []
        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            content = result.get('content', '')

            # Format with metadata
            source_info = []
            if metadata.get('chapter'):
                source_info.append(f"Chapter: {metadata['chapter']}")
            if metadata.get('page'):
                source_info.append(f"Page: {metadata['page']}")

            source_text = f"[{', '.join(source_info)}]" if source_info else ""

            context_parts.append(f"{i}. {source_text}\n{content}")

        return "\n\n".join(context_parts)

    def clear_collection(self) -> None:
        """Clear all documents from collection (use with caution!)"""
        try:
            self.chroma_client.delete_collection(name=self.collection_name)
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "NCERT textbook content for grades 3-10"}
            )
            logger.info("Collection cleared and recreated")
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection

        Returns:
            Dictionary with collection stats
        """
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection_name,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {
                "error": str(e)
            }


# Global instance
rag_service = RAGService()
