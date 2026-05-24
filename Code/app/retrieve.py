from typing import List, Dict
from app.vector_store import VectorStore


class RetrievalService:
    def __init__(self):
        self.vector_store = VectorStore()

    def query(self, query_text: str, top_k: int = 5) -> List[Dict[str, object]]:
        return self.vector_store.query(query_text=query_text, top_k=top_k)
