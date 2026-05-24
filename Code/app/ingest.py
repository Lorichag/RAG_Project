import uuid
from app.minio_store import MinIOStore
from app.embed import EmbeddingService
from app.vector_store import VectorStore
from app.database import SessionLocal, init_db
from app.db_models import Document, DocumentChunk


class IngestPipeline:
    def __init__(self):
        self.store = MinIOStore()
        self.embedder = EmbeddingService()
        self.vector_store = VectorStore()
        init_db()

    def ingest_document(self, document_name: str, content: str) -> dict:
        self.store.ensure_bucket()
        self.store.upload_text(document_name, content)

        chunks = self.embedder.chunk_text(content)
        metadatas = [
            {"source": document_name, "chunk_index": idx}
            for idx, _ in enumerate(chunks)
        ]
        ids = [str(uuid.uuid4()) for _ in chunks]

        self.vector_store.add_documents(ids=ids, documents=chunks, metadatas=metadatas)

        with SessionLocal() as session:
            document = Document(id=str(uuid.uuid4()), name=document_name)
            session.add(document)
            session.flush()

            for index, chunk_text in enumerate(chunks):
                chunk = DocumentChunk(
                    id=ids[index],
                    document_id=document.id,
                    chunk_index=index,
                    text=chunk_text,
                    source=document_name,
                    chunk_metadata=metadatas[index],
                )
                session.add(chunk)

            session.commit()

        return {
            "document_id": document.id,
            "document_name": document_name,
            "chunk_count": len(chunks),
        }
