from pydantic import BaseModel
from typing import List, Optional


class HealthResponse(BaseModel):
    status: str
    environment: str


class IngestRequest(BaseModel):
    document_name: str
    content: str


class IngestResponse(BaseModel):
    document_id: str
    chunk_count: int


class QueryRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryResult(BaseModel):
    text: str
    score: float
    source: Optional[str]


class QueryResponse(BaseModel):
    query: str
    results: List[QueryResult]
    answer: Optional[str]
