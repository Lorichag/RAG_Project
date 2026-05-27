from contextlib import asynccontextmanager
from typing import List
import time
import requests
from psycopg import OperationalError, connect
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import SessionLocal
from app.db_models import Document, DocumentChunk, IngestRun
from app.ingest import IngestPipeline
from app.retrieve import RetrievalService
from app.generate import GenerationService
from app.vector_store import VectorStore
from app.models import (
    BatchIngestResponse,
    DocumentRun,
    HealthResponse,
    IngestObjectRequest,
    IngestRequest,
    IngestResult,
    QueryRequest,
    QueryResponse,
    QueryResult,
)


def wait_for_postgres() -> None:
    max_retries = 30
    for attempt in range(1, max_retries + 1):
        try:
            with connect(settings.psycopg_dsn, autocommit=True) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            return
        except OperationalError:
            time.sleep(2)
    raise RuntimeError("Impossible de se connecter à PostgreSQL dans le délai imparti")


def wait_for_minio() -> None:
    minio_health_url = f"http://{settings.minio_endpoint}/minio/health/live"
    max_retries = 30
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(minio_health_url, timeout=3)
            if resp.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(2)
    raise RuntimeError("Impossible de se connecter à MinIO dans le délai imparti")


def wait_for_chroma() -> None:
    chroma_url = f"http://{settings.chroma_host}:{settings.chroma_port}/openapi.json"
    max_retries = 30
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(chroma_url, timeout=3)
            if resp.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(2)
    raise RuntimeError("Impossible de se connecter à ChromaDB dans le délai imparti")


@asynccontextmanager
async def lifespan(app: FastAPI):
    wait_for_postgres()
    wait_for_minio()
    wait_for_chroma()

    app.state.ingest_pipeline = IngestPipeline()
    app.state.retrieval_service = RetrievalService()
    app.state.generation_service = GenerationService()
    yield


app = FastAPI(title="RAG Knowledge Platform", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.environment)


@app.post("/ingest", response_model=IngestResult)
def ingest_document(request: IngestRequest) -> IngestResult:
    pipeline: IngestPipeline = app.state.ingest_pipeline
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Pipeline non initialisé")
    return pipeline.ingest_document(request.document_name, request.content)


@app.post("/ingest/raw", response_model=IngestResult)
def ingest_raw_document(request: IngestObjectRequest) -> IngestResult:
    pipeline: IngestPipeline = app.state.ingest_pipeline
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Pipeline non initialisé")
    return pipeline.run_document(request.object_name)


@app.post("/ingest/all", response_model=BatchIngestResponse)
def ingest_all_documents() -> BatchIngestResponse:
    pipeline: IngestPipeline = app.state.ingest_pipeline
    if pipeline is None:
        raise HTTPException(status_code=500, detail="Pipeline non initialisé")
    pending = pipeline.list_pending_documents()
    ingested: List[IngestResult] = []
    for object_name in pending:
        try:
            ingested.append(pipeline.run_document(object_name))
        except Exception:
            continue
    return BatchIngestResponse(ingested=ingested)


@app.get("/documents", response_model=List[DocumentRun])
def list_document_runs() -> List[DocumentRun]:
    with SessionLocal() as session:
        runs = session.query(IngestRun).order_by(IngestRun.created_at.desc()).all()
        return [
            DocumentRun(
                id=run.id,
                object_name=run.object_name,
                status=run.status,
                chunk_count=run.chunk_count,
                created_at=run.created_at,
                completed_at=run.completed_at,
                error_message=run.error_message,
                document_id=run.document_id,
            )
            for run in runs
        ]


@app.get("/documents/{run_id}", response_model=DocumentRun)
def get_document_run(run_id: str) -> DocumentRun:
    with SessionLocal() as session:
        run = session.get(IngestRun, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run non trouvée")
        return DocumentRun(
            id=run.id,
            object_name=run.object_name,
            status=run.status,
            chunk_count=run.chunk_count,
            created_at=run.created_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
            document_id=run.document_id,
        )


@app.delete("/documents/{run_id}")
def delete_document_run(run_id: str) -> dict:
    with SessionLocal() as session:
        run = session.get(IngestRun, run_id)
        if not run:
            raise HTTPException(status_code=404, detail="Run non trouvée")

        chunks = session.query(DocumentChunk).filter(DocumentChunk.run_id == run_id).all()
        chunk_ids = [chunk.id for chunk in chunks]
        vector_store = VectorStore()
        vector_store.delete_documents(chunk_ids)

        session.query(DocumentChunk).filter(DocumentChunk.run_id == run_id).delete(synchronize_session=False)
        if run.document_id:
            session.query(Document).filter(Document.id == run.document_id).delete(synchronize_session=False)
        session.delete(run)
        session.commit()

    return {"deleted": run_id}


@app.post("/query", response_model=QueryResponse)
def query_document(request: QueryRequest) -> QueryResponse:
    retrieval_service: RetrievalService = app.state.retrieval_service
    generation_service: GenerationService = app.state.generation_service
    if retrieval_service is None or generation_service is None:
        raise HTTPException(status_code=500, detail="Services non initialisés")

    results = retrieval_service.search(request.query, top_k=request.top_k)
    if not results:
        raise HTTPException(status_code=404, detail="Aucun document pertinent trouvé")

    context = retrieval_service.format_context(results)
    sources = [item.get("source") or "unknown" for item in results]
    generation = generation_service.answer(request.query, context, sources)

    return QueryResponse(
        query=request.query,
        results=[
            QueryResult(
                text=item["text"],
                score=item["score"],
                source=item.get("source"),
                metadata=item.get("metadata"),
            )
            for item in results
        ],
        answer=generation.get("answer"),
    )
