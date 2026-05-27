import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class IngestRun(Base):
    __tablename__ = "ingest_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    object_name = Column(String(1024), nullable=False)
    status = Column(String(50), nullable=False)
    chunk_count = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    document_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False)
    run_id = Column(String(36), ForeignKey("ingest_runs.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    char_start = Column(Integer, nullable=False)
    chroma_id = Column(String(255), nullable=False)
    object_name = Column(String(500), nullable=True)
    chunk_text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    chunk_metadata = Column(JSON, nullable=True)

    document = relationship("Document", back_populates="chunks")
