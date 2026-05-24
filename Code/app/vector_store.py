from typing import Any, Dict, List
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from app.config import settings


class VectorStore:
    COLLECTION_NAME = "rag_documents"

    def __init__(self):
        self.host = settings.chroma_host
        self.port = settings.chroma_port
        self.embedding_function = SentenceTransformerEmbeddingFunction(model_name=settings.embedding_model)
        self.client = chromadb.Client(
            Settings(
                chroma_api_impl="chromadb.api.fastapi.FastAPI",
                chroma_server_host=self.host,
                chroma_server_http_port=self.port,
            )
        )
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            embedding_function=self.embedding_function,
        )

    def add_documents(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]) -> None:
        self.collection.add(ids=ids, documents=documents, metadatas=metadatas)

    def query(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        result = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            include=["documents", "distances", "metadatas"],
        )
        documents = result["documents"][0]
        distances = result["distances"][0]
        metadatas = result["metadatas"][0]
        return [
            {
                "text": documents[i],
                "score": float(distances[i]),
                "source": metadatas[i].get("source"),
            }
            for i in range(len(documents))
        ]
