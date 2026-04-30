"""Vector store service using FAISS for document embeddings."""
import os
import pickle
from typing import List, Optional, Tuple
from uuid import UUID

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

settings = get_settings()


class VectorStore:
    """FAISS-based vector store for document retrieval."""

    def __init__(self):
        self.model = SentenceTransformer(settings.embedding_model)
        self.index_path = settings.faiss_index_path
        self.embeddings: dict = {}  # {doc_id: {"embedding": np.array, "text": str, "metadata": dict}}
        self._index = None
        self._id_map: List[str] = []
        os.makedirs(self.index_path, exist_ok=True)

    def _get_index_file(self, course_id: str) -> str:
        return os.path.join(self.index_path, f"{course_id}.pkl")

    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for a text."""
        return self.model.encode(text, normalize_embeddings=True)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts."""
        return self.model.encode(texts, normalize_embeddings=True, batch_size=32)

    async def add_documents(
        self,
        course_id: str,
        texts: List[str],
        metadata: List[dict],
        doc_ids: Optional[List[str]] = None
    ):
        """Add documents to the vector store for a given course."""
        import faiss

        if doc_ids is None:
            doc_ids = [str(UUID(int=i)) for i in range(len(texts))]

        embeddings = self.embed_texts(texts)
        dimension = embeddings.shape[1]

        # Load existing index or create new
        index_file = self._get_index_file(course_id)
        if os.path.exists(index_file):
            with open(index_file, "rb") as f:
                data = pickle.load(f)
                index = data["index"]
                id_map = data["id_map"]
                text_map = data["text_map"]
                meta_map = data["meta_map"]
        else:
            index = faiss.IndexFlatIP(dimension)  # Inner product (cosine with normalized vectors)
            id_map = []
            text_map = []
            meta_map = []

        # Add to index
        index.add(embeddings.astype(np.float32))
        id_map.extend(doc_ids)
        text_map.extend(texts)
        meta_map.extend(metadata)

        # Save index
        with open(index_file, "wb") as f:
            pickle.dump({
                "index": index,
                "id_map": id_map,
                "text_map": text_map,
                "meta_map": meta_map
            }, f)

    async def search(
        self,
        course_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[str, float, dict]]:
        """Search for similar documents. Returns list of (text, score, metadata)."""
        import faiss

        index_file = self._get_index_file(course_id)
        if not os.path.exists(index_file):
            return []

        with open(index_file, "rb") as f:
            data = pickle.load(f)

        index = data["index"]
        text_map = data["text_map"]
        meta_map = data["meta_map"]

        query_embedding = self.embed_text(query).reshape(1, -1).astype(np.float32)
        scores, indices = index.search(query_embedding, min(top_k, index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(text_map) and idx >= 0:
                results.append((text_map[idx], float(score), meta_map[idx]))

        return results

    async def delete_course_index(self, course_id: str):
        """Delete the index for a course."""
        index_file = self._get_index_file(course_id)
        if os.path.exists(index_file):
            os.remove(index_file)


# Singleton instance
vector_store = VectorStore()
