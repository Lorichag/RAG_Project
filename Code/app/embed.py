from typing import List
from sentence_transformers import SentenceTransformer
from app.config import settings


class EmbeddingService:
    def __init__(self):
        self.model_name = settings.embedding_model
        self.model = SentenceTransformer(self.model_name)

    def chunk_text(self, text: str) -> List[str]:
        tokens = text.split()
        chunks: List[str] = []
        current: List[str] = []
        for token in tokens:
            current.append(token)
            if len(current) >= settings.chunk_size:
                chunks.append(" ".join(current))
                current = current[-settings.chunk_overlap :]
        if current:
            chunks.append(" ".join(current))
        return chunks

    def embed(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, convert_to_numpy=False).tolist()
