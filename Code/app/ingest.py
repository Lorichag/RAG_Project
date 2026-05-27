import io
import time
import uuid
from datetime import datetime
from typing import List
from pypdf import PdfReader
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings
from app.database import SessionLocal, init_db
from app.db_models import Document, DocumentChunk, IngestRun
from app.embed import ChunkMetadata, EmbeddingService
from app.minio_store import MinIOStore
from app.vector_store import VectorStore
from app.models import IngestResult


class IngestPipeline:
    def __init__(self):
        self.store = MinIOStore()
        self.embedder = EmbeddingService()
        self.vector_store = VectorStore()
        init_db()

    def _extract_text(self, object_name: str, raw_bytes: bytes) -> str:
        lower_name = object_name.lower()
        if lower_name.endswith(".pdf"):
            reader = PdfReader(io.BytesIO(raw_bytes))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(pages).strip()

        try:
            return raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return raw_bytes.decode("latin-1", errors="ignore")

    def _create_run(self, object_name: str) -> IngestRun:
        with SessionLocal() as session:
            run = IngestRun(object_name=object_name, status="processing")
            session.add(run)
            session.commit()
            session.refresh(run)
            return run

    def _complete_run(self, run: IngestRun, document_id: str, chunk_count: int) -> None:
        with SessionLocal() as session:
            session.merge(
                IngestRun(
                    id=run.id,
                    object_name=run.object_name,
                    status="completed",
                    chunk_count=chunk_count,
                    document_id=document_id,
                    created_at=run.created_at,
                    completed_at=datetime.utcnow(),
                )
            )
            session.commit()

    def _fail_run(self, run: IngestRun, error_message: str) -> None:
        with SessionLocal() as session:
            run.status = "failed"
            run.error_message = error_message
            run.completed_at = datetime.utcnow()
            session.merge(run)
            session.commit()

    def ingest_document(self, document_name: str, content: str) -> IngestResult:
        self.store.ensure_bucket()
        raw_object_name = f"{document_name}"
        self.store.client.put_object(
            Bucket=self.store.bucket,
            Key=f"{self.store.RAW_PREFIX}{raw_object_name}",
            Body=content.encode("utf-8"),
        )
        return self.run_document(raw_object_name)

    def run_document(self, object_name: str) -> IngestResult:
        object_key = object_name
        if not object_key.startswith(self.store.RAW_PREFIX) and not object_key.startswith(self.store.PROCESSED_PREFIX):
            object_key = f"{self.store.RAW_PREFIX}{object_key}"
        run = self._create_run(object_key)
        start_time = time.monotonic()

        try:
            raw_bytes = self.store.download_document(object_key)
            text = self._extract_text(object_key, raw_bytes)
            if not text.strip():
                raise ValueError("Le document est vide ou n'a pas pu être analysé.")

            chunks = self.embedder.chunk_text(text, settings.chunk_size, settings.chunk_overlap)
            if not chunks:
                raise ValueError("Aucun chunk généré pour ce document.")

            embeddings = self.embedder.embed_batch([chunk.text for chunk in chunks])
            ids = [str(uuid.uuid4()) for _ in chunks]
            metadatas = [
                {
                    "source": object_key,
                    "chunk_index": chunk.chunk_index,
                    "char_start": chunk.char_start,
                }
                for chunk in chunks
            ]

            self.vector_store.add_documents(ids=ids, documents=[chunk.text for chunk in chunks], metadatas=metadatas)

            document_id = str(uuid.uuid4())
            with SessionLocal() as session:
                document = Document(id=document_id, name=object_key)
                session.add(document)
                session.flush()

                for chunk_id, chunk_metadata in zip(ids, chunks):
                    chunk = DocumentChunk(
                        id=chunk_id,
                        document_id=document_id,
                        run_id=run.id,
                        chunk_index=chunk_metadata.chunk_index,
                        char_start=chunk_metadata.char_start,
                        chroma_id=chunk_id,
                        object_name=object_key,
                        chunk_text=chunk_metadata.text,
                        chunk_metadata={
                            "object_name": object_key,
                            "chunk_index": chunk_metadata.chunk_index,
                            "char_start": chunk_metadata.char_start,
                        },
                    )
                    session.add(chunk)
                session.commit()

            self.store.mark_processed(object_key)
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            self._complete_run(run, document_id=document_id, chunk_count=len(chunks))
            return IngestResult(
                document_id=document_id,
                object_name=object_key,
                chunk_count=len(chunks),
                elapsed_ms=elapsed_ms,
                status="completed",
            )
        except Exception as exc:
            self._fail_run(run, str(exc))
            raise

    def list_pending_documents(self) -> List[str]:
        return self.store.list_raw_documents()
