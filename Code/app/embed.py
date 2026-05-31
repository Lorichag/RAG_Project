import re
from dataclasses import dataclass
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import settings


@dataclass
class ChunkMetadata:
    text: str
    chunk_index: int
    char_start: int


class EmbeddingService:
    def __init__(self):
        self.model_name = settings.embedding_model
        self.model = SentenceTransformer(self.model_name)

    def embed_text(self, text: str) -> List[float]:
        embeddings = self.model.encode([text], convert_to_numpy=False)
        vector = embeddings[0]
        if hasattr(vector, 'tolist'):
            return vector.tolist()
        return vector

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_numpy=False)
        if hasattr(embeddings, 'tolist'):
            return embeddings.tolist()
        return [item.tolist() if hasattr(item, 'tolist') else item for item in embeddings]

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 512,
        overlap: int = 64,
    ) -> List[ChunkMetadata]:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
        if not sentences:
            return []

        chunks: List[ChunkMetadata] = []
        current = ""
        current_start = 0
        index = 0
        position = 0

        for sentence in sentences:
            sentence_start = text.find(sentence, position)
            position = sentence_start + len(sentence)
            candidate = f"{current} {sentence}".strip() if current else sentence

            if len(candidate) <= chunk_size:
                if not current:
                    current_start = sentence_start
                current = candidate
            else:
                if current:
                    chunks.append(ChunkMetadata(text=current, chunk_index=index, char_start=current_start))
                    index += 1
                    overlap_text = current[-overlap:] if len(current) > overlap else current
                    current = overlap_text.strip()
                    current_start = max(0, current_start + len(current) - len(overlap_text))
                if len(sentence) > chunk_size:
                    for i in range(0, len(sentence), chunk_size - overlap):
                        segment = sentence[i : i + chunk_size]
                        chunks.append(ChunkMetadata(text=segment, chunk_index=index, char_start=sentence_start + i))
                        index += 1
                    current = ""
                else:
                    current = sentence
                    current_start = sentence_start

        if current:
            chunks.append(ChunkMetadata(text=current, chunk_index=index, char_start=current_start))

        return chunks
