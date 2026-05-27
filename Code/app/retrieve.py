from typing import Dict, List
from app.embed import EmbeddingService
from app.vector_store import VectorStore


class RetrievalService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.embedder = EmbeddingService()

    def search(self, query_text: str, top_k: int = 5) -> List[Dict[str, object]]:
        query_vector = self.embedder.embed_text(query_text)
        results = self.vector_store.query_embeddings(embedding=query_vector, top_k=top_k)
        formatted = []
        for item in results:
            score = max(0.0, 1.0 - float(item["score"]))
            formatted.append(
                {
                    "id": item["id"],
                    "text": item["text"],
                    "score": score,
                    "source": item.get("source"),
                    "metadata": item.get("metadata"),
                }
            )
        return formatted

    def format_context(self, chunks: List[Dict[str, object]]) -> str:
        return "\n\n".join(
            f"[{item.get('source', 'unknown')}]: {item['text']}" for item in chunks
        )

    def format_sources(self, chunks: List[Dict[str, object]]) -> List[Dict[str, object]]:
        return [
            {
                "source": item.get("source"),
                "score": item.get("score"),
                "metadata": item.get("metadata"),
            }
            for item in chunks
        ]
