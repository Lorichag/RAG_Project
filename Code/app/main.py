from fastapi import FastAPI, HTTPException
import time
import requests
from app.config import settings
from app.models import (
    HealthResponse,
    IngestRequest,
    IngestResponse,
    QueryRequest,
    QueryResponse,
    QueryResult,
)
from app.ingest import IngestPipeline
from app.retrieve import RetrievalService
from app.generate import GenerationService

app = FastAPI(title="RAG Knowledge Platform")

ingest_pipeline: IngestPipeline | None = None
retrieval_service: RetrievalService | None = None
generation_service: GenerationService | None = None


@app.on_event("startup")
def startup_event() -> None:
    global ingest_pipeline, retrieval_service, generation_service
    # Wait for ChromaDB to be ready (poll openapi.json)
    chroma_url = f"http://{settings.chroma_host}:{settings.chroma_port}/openapi.json"
    max_retries = 30
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(chroma_url, timeout=3)
            if resp.status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(2)

    ingest_pipeline = IngestPipeline()
    retrieval_service = RetrievalService()
    generation_service = GenerationService()


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.environment)


@app.post("/ingest", response_model=IngestResponse)
def ingest_document(request: IngestRequest) -> IngestResponse:
    if ingest_pipeline is None:
        raise HTTPException(status_code=500, detail="Pipeline non initialisé")

    result = ingest_pipeline.ingest_document(request.document_name, request.content)
    return IngestResponse(document_id=result["document_id"], chunk_count=result["chunk_count"])


@app.post("/query", response_model=QueryResponse)
def query_document(request: QueryRequest) -> QueryResponse:
    if retrieval_service is None or generation_service is None:
        raise HTTPException(status_code=500, detail="Services non initialisés")

    results = retrieval_service.query(request.query, top_k=request.top_k)
    if not results:
        raise HTTPException(status_code=404, detail="Aucun document pertinent trouvé")

    context = "\n\n".join(item["text"] for item in results)
    answer = generation_service.generate_answer(request.query, context)
    return QueryResponse(
        query=request.query,
        results=[QueryResult(text=item["text"], score=item["score"], source=item.get("source")) for item in results],
        answer=answer,
    )
