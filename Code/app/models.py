from datetime import datetime
from pydantic import BaseModel
from typing import Dict, List, Optional


class HealthResponse(BaseModel):
    status: str
    environment: str


class IngestRequest(BaseModel):
    document_name: str
    content: str


class IngestObjectRequest(BaseModel):
    object_name: str


class IngestResult(BaseModel):
    document_id: str
    object_name: str
    chunk_count: int
    elapsed_ms: int
    status: str


class BatchIngestResponse(BaseModel):
    ingested: List[IngestResult]


class DocumentRun(BaseModel):
    id: str
    object_name: str
    status: str
    chunk_count: Optional[int]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    document_id: Optional[str]


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryResult(BaseModel):
    text: str
    score: float
    source: Optional[str]
    metadata: Optional[Dict[str, str]] = None


class QueryResponse(BaseModel):
    query: str
    results: List[QueryResult]
    answer: Optional[str]


class GenerationResult(BaseModel):
    answer: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    sources: Optional[List[str]] = None
