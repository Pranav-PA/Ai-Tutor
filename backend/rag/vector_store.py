"""RAG (Retrieval-Augmented Generation) system using ChromaDB."""
import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from backend.config import CHROMA_PERSIST_DIR
from backend.services.ai_provider import get_embeddings


class VectorStore:
    """ChromaDB-based vector store for document embeddings."""

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=CHROMA_PERSIST_DIR,
            settings=Settings(anonymized_telemetry=False)
        )

    def get_or_create_collection(self, course_id: int) -> chromadb.Collection:
        """Get or create a collection for a course."""
        collection_name = f"course_{course_id}"
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, course_id: int, chunks: List[Dict[str, Any]], document_id: int):
        """Add document chunks to the vector store."""
        collection = self.get_or_create_collection(course_id)

        texts = [chunk["text"] for chunk in chunks]
        ids = [f"doc_{document_id}_chunk_{chunk['id']}" for chunk in chunks]
        metadatas = [
            {
                "document_id": document_id,
                "chunk_id": chunk["id"],
                "start": chunk["start"],
                "end": chunk["end"],
                **{k: str(v) for k, v in chunk.get("metadata", {}).items()}
            }
            for chunk in chunks
        ]

        # Generate embeddings
        embeddings = get_embeddings(texts)

        if embeddings:
            collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
        else:
            # Fallback: let ChromaDB handle embeddings with default model
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )

        return len(texts)

    def search(self, course_id: int, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents using semantic similarity."""
        collection = self.get_or_create_collection(course_id)

        if collection.count() == 0:
            return []

        # Generate query embedding
        query_embedding = get_embeddings([query])

        if query_embedding:
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=min(n_results, collection.count())
            )
        else:
            results = collection.query(
                query_texts=[query],
                n_results=min(n_results, collection.count())
            )

        # Format results
        documents = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                })

        return documents

    def delete_document(self, course_id: int, document_id: int):
        """Delete all chunks for a specific document."""
        collection = self.get_or_create_collection(course_id)
        # Get all IDs that start with this document prefix
        try:
            results = collection.get(
                where={"document_id": document_id}
            )
            if results['ids']:
                collection.delete(ids=results['ids'])
        except Exception:
            pass

    def delete_collection(self, course_id: int):
        """Delete entire collection for a course."""
        collection_name = f"course_{course_id}"
        try:
            self.client.delete_collection(collection_name)
        except Exception:
            pass

    def get_collection_stats(self, course_id: int) -> Dict[str, Any]:
        """Get statistics about a collection."""
        collection = self.get_or_create_collection(course_id)
        return {
            "total_chunks": collection.count(),
            "collection_name": f"course_{course_id}"
        }


# Singleton instance
vector_store = VectorStore()
