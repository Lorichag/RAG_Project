from typing import Any, Dict, List
import chromadb
from chromadb.config import Settings
import structlog
from app.config import settings

logger = structlog.get_logger()


class VectorStore:
    COLLECTION_NAME = "rag_documents"

    def __init__(self):
        self.host = settings.chroma_host
        self.port = settings.chroma_port
        self.client = chromadb.Client(
            Settings(
                chroma_api_impl="chromadb.api.fastapi.FastAPI",
                chroma_server_host=self.host,
                chroma_server_http_port=self.port,
            )
        )
        self.collection = self.client.get_or_create_collection(name=self.COLLECTION_NAME)

    def add_documents(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]) -> None:
        logger.info("Adding documents to vector store", count=len(ids))
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def query_embeddings(self, embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["documents", "distances", "metadatas"],
        )
        documents = result["documents"][0]
        distances = result["distances"][0]
        metadatas = result["metadatas"][0]
        ids = result.get("ids", [[]])[0]
        return [
            {
                "id": ids[i] if i < len(ids) else None,
                "text": documents[i],
                "score": float(distances[i]),
                "source": metadatas[i].get("source"),
                "metadata": metadatas[i],
            }
            for i in range(len(documents))
        ]

    def delete_documents(self, ids: List[str]) -> None:
        if not ids:
            return
        logger.info("Deleting documents from vector store", count=len(ids))
        self.collection.delete(ids=ids)
