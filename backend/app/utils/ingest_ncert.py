"""
Script to ingest NCERT content into the vector database

This script processes NCERT textbook content and stores it in ChromaDB
for RAG-based retrieval.

Usage:
    python -m app.utils.ingest_ncert
"""

import os
import json
from typing import List, Dict, Any
import logging
from pathlib import Path

from app.services.rag_service import rag_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks

    Args:
        text: Text to split
        chunk_size: Size of each chunk
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at sentence boundary
        if end < len(text):
            # Look for period followed by space
            last_period = text.rfind('. ', start, end)
            if last_period > start:
                end = last_period + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def ingest_sample_content():
    """
    Ingest sample NCERT content for demonstration

    In production, this would read from actual NCERT PDFs or text files
    """
    logger.info("Starting sample content ingestion...")

    # Sample content for Grade 5 Mathematics - Fractions
    sample_content = [
        {
            "text": """Fractions represent parts of a whole. When we divide something into equal parts,
            each part is called a fraction. For example, if we divide a pizza into 4 equal parts and
            take 1 part, we have 1/4 (one-fourth) of the pizza. The number above the line is called
            the numerator, and the number below the line is called the denominator. The denominator
            tells us into how many equal parts the whole is divided, and the numerator tells us how
            many of those parts we are considering.""",
            "metadata": {
                "grade": 5,
                "subject": "Mathematics",
                "chapter": "Fractions",
                "topic": "Introduction to Fractions",
                "page": 45
            }
        },
        {
            "text": """Types of Fractions: 1) Proper Fractions - where numerator is less than denominator
            (like 3/4, 2/5). 2) Improper Fractions - where numerator is greater than or equal to
            denominator (like 5/3, 7/4). 3) Mixed Numbers - combination of whole number and proper
            fraction (like 2 1/2, 3 3/4). We can convert improper fractions to mixed numbers by
            dividing the numerator by the denominator.""",
            "metadata": {
                "grade": 5,
                "subject": "Mathematics",
                "chapter": "Fractions",
                "topic": "Types of Fractions",
                "page": 46
            }
        },
        {
            "text": """Equivalent Fractions are fractions that represent the same value even though they
            look different. For example, 1/2 = 2/4 = 3/6 = 4/8. We can find equivalent fractions by
            multiplying or dividing both numerator and denominator by the same number. To compare
            fractions, we can convert them to equivalent fractions with the same denominator, called
            the common denominator.""",
            "metadata": {
                "grade": 5,
                "subject": "Mathematics",
                "chapter": "Fractions",
                "topic": "Equivalent Fractions",
                "page": 48
            }
        },
    ]

    # Sample content for Grade 6 Science - Photosynthesis
    sample_content.extend([
        {
            "text": """Photosynthesis is the process by which green plants make their own food. Plants
            have a green pigment called chlorophyll in their leaves, which captures sunlight. Plants
            use this sunlight energy to convert carbon dioxide (from air) and water (from soil) into
            glucose (a type of sugar) and oxygen. The oxygen is released into the air, which we breathe.
            The equation for photosynthesis is: Carbon dioxide + Water + Sunlight → Glucose + Oxygen.""",
            "metadata": {
                "grade": 6,
                "subject": "Science",
                "chapter": "Nutrition in Plants",
                "topic": "Photosynthesis",
                "page": 12
            }
        },
        {
            "text": """Chlorophyll is the green pigment present in leaves that makes photosynthesis possible.
            It is found in special structures called chloroplasts. Chlorophyll absorbs light energy,
            especially red and blue light, and reflects green light, which is why leaves appear green.
            Without chlorophyll, plants cannot make food and will die. This is why plants need sunlight
            to survive - it provides the energy for photosynthesis.""",
            "metadata": {
                "grade": 6,
                "subject": "Science",
                "chapter": "Nutrition in Plants",
                "topic": "Role of Chlorophyll",
                "page": 13
            }
        },
    ])

    # Process and add content
    all_texts = []
    all_metadatas = []
    all_ids = []

    for i, item in enumerate(sample_content):
        # Chunk long texts
        chunks = chunk_text(item["text"], chunk_size=500, overlap=100)

        for j, chunk in enumerate(chunks):
            all_texts.append(chunk)
            all_metadatas.append(item["metadata"])
            all_ids.append(f"sample_{i}_{j}")

    # Add to vector database
    rag_service.add_documents(
        texts=all_texts,
        metadatas=all_metadatas,
        ids=all_ids
    )

    logger.info(f"Successfully ingested {len(all_texts)} chunks from {len(sample_content)} documents")

    # Show stats
    stats = rag_service.get_collection_stats()
    logger.info(f"Collection stats: {stats}")


def ingest_from_json_file(file_path: str):
    """
    Ingest content from a JSON file

    JSON format:
    [
        {
            "text": "content here",
            "metadata": {
                "grade": 5,
                "subject": "Mathematics",
                "chapter": "Fractions",
                "topic": "Introduction",
                "page": 45
            }
        },
        ...
    ]

    Args:
        file_path: Path to JSON file
    """
    logger.info(f"Ingesting from file: {file_path}")

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = json.load(f)

    all_texts = []
    all_metadatas = []
    all_ids = []

    for i, item in enumerate(content):
        # Chunk long texts
        chunks = chunk_text(item["text"], chunk_size=1000, overlap=200)

        for j, chunk in enumerate(chunks):
            all_texts.append(chunk)
            all_metadatas.append(item["metadata"])
            all_ids.append(f"doc_{i}_{j}")

    # Add to vector database
    rag_service.add_documents(
        texts=all_texts,
        metadatas=all_metadatas,
        ids=all_ids
    )

    logger.info(f"Successfully ingested {len(all_texts)} chunks from {len(content)} documents")


def test_search():
    """Test the RAG search functionality"""
    logger.info("\n=== Testing RAG Search ===\n")

    # Test query 1
    query1 = "What are fractions?"
    logger.info(f"Query: {query1}")
    results = rag_service.search(query1, n_results=2, grade=5)
    for i, result in enumerate(results, 1):
        logger.info(f"\nResult {i}:")
        logger.info(f"Content: {result['content'][:200]}...")
        logger.info(f"Metadata: {result['metadata']}")

    # Test query 2
    query2 = "How does photosynthesis work?"
    logger.info(f"\n\nQuery: {query2}")
    results = rag_service.search(query2, n_results=2, grade=6)
    for i, result in enumerate(results, 1):
        logger.info(f"\nResult {i}:")
        logger.info(f"Content: {result['content'][:200]}...")
        logger.info(f"Metadata: {result['metadata']}")

    # Test context retrieval
    logger.info("\n\n=== Testing Context Retrieval ===\n")
    context = rag_service.get_context_for_topic(
        topic="Fractions",
        grade=5,
        subject="Mathematics",
        max_chunks=3
    )
    logger.info(f"Context for 'Fractions':\n{context[:500]}...\n")


if __name__ == "__main__":
    import sys

    # Check if ChromaDB collection should be cleared
    if "--clear" in sys.argv:
        logger.warning("Clearing existing collection...")
        rag_service.clear_collection()

    # Ingest sample content
    ingest_sample_content()

    # Test search
    if "--test" in sys.argv:
        test_search()

    logger.info("\nIngestion complete!")
    logger.info("\nTo test search, run: python -m app.utils.ingest_ncert --test")
