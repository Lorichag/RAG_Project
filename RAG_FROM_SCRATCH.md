# RAG Knowledge Platform: Build from Scratch

## Overview

After completing the 11-rag-knowledge-platform exercises, you now understand how a Retrieval-Augmented Generation (RAG) system works in practice. This guide challenges you to **build the entire system from scratch** in 2 weeks, implementing all components yourself.

You will:
- Design a local-first RAG architecture without using LangChain or commercial APIs
- Orchestrate a multi-service Docker environment with proper healthchecks and dependencies
- Build document ingestion pipelines with chunking, embedding, and vector search
- Create REST APIs with validation and error handling
- Use Apache Airflow for workflow orchestration
- Validate data quality with Great Expectations
- Deploy and query a knowledge base end-to-end

**Time estimate:** 10-14 days of focused development (4-6 hours/day)

**Prerequisite knowledge:**
- Completed exercises 1-4 in the 11-rag-knowledge-platform project
- Understanding of Docker, Python, FastAPI basics
- Basic SQL knowledge
- Familiarity with environment variables and configuration management

---

## Learning Outcomes

By the end of this project, you will be able to:

1. **Design RAG Systems**
   - Understand the difference between retrieval-only, generative-only, and RAG approaches
   - Design chunking strategies that preserve semantic meaning
   - Choose embedding models and vector similarity metrics appropriately
   - Explain trade-offs between different vector database options

2. **Build Production-Ready Services**
   - Structure Python applications with proper separation of concerns
   - Implement error handling and logging at system boundaries
   - Use type hints effectively for code clarity and maintainability
   - Design idempotent operations for reliability

3. **Orchestrate Distributed Systems**
   - Configure multi-service Docker environments with dependencies
   - Use Airflow DAGs for reliable batch processing
   - Pass data between tasks using XCom in Airflow
   - Implement health checks and graceful degradation

4. **Integrate Multiple Databases**
   - Use PostgreSQL for structured metadata
   - Use MinIO as an S3-compatible object store
   - Use ChromaDB for vector similarity search
   - Design schemas that support efficient queries

5. **Deploy and Monitor**
   - Write Makefiles that encapsulate complex commands
   - Create data validation suites with Great Expectations
   - Build interactive CLI tools for system interaction
   - Document systems comprehensively for team handoffs

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     STUDENT SYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐                                      │
│  │    Documents     │ ─────────────────┐                  │
│  │  (synthetic or   │                  │                  │
│  │   real PDFs)     │                  ▼                  │
│  └──────────────────┘              ┌────────────┐         │
│                                    │   MinIO    │         │
│                                    │  (S3-like) │         │
│                                    └──────┬─────┘         │
│                                           │                │
│                        ┌──────────────────┼──────────────┐ │
│                        │                  │              │ │
│                        ▼                  ▼              │ │
│                   ┌─────────┐      ┌──────────┐         │ │
│                   │ Airflow │──────│PostgreSQL│         │ │
│                   │   DAG   │      │(metadata)│         │ │
│                   └────┬────┘      └──────────┘         │ │
│                        │                                 │ │
│                        ▼                                 │ │
│          ┌─────────────────────────────┐                │ │
│          │  Ingestion Pipeline (Python)│                │ │
│          │  - Chunking (sentence-wise) │                │ │
│          │  - Embedding (all-MiniLM)   │                │ │
│          │  - Vector indexing          │                │ │
│          └──────────┬────────────────────┘               │ │
│                     │                                    │ │
│         ┌───────────┴────────────┐                      │ │
│         │                        │                      │ │
│         ▼                        ▼                      │ │
│    ┌──────────┐           ┌────────────┐              │ │
│    │ ChromaDB │           │PostgreSQL  │              │ │
│    │(vectors) │           │(chunks)    │              │ │
│    └──────────┘           └────────────┘              │ │
│         ▲                        ▲                      │ │
│         └────────────┬───────────┘                      │ │
│                      │                                  │ │
│         ┌────────────▼──────────┐                      │ │
│         │   FastAPI REST API    │                      │ │
│         │  /query endpoint      │                      │ │
│         │  /ingest endpoint     │                      │ │
│         └────┬─────────────────┘                       │ │
│              │                                          │ │
│              │ (calls locally)                          │ │
│         ┌────▼──────┐                                  │ │
│         │  Ollama   │ ◄── (runs on host machine)       │ │
│         │LLM server │      port 11434                  │ │
│         └───────────┘                                  │ │
│                                                         │ │
└─────────────────────────────────────────────────────────┘ │
```

---

## Week-by-Week Breakdown

### Week 1: Core Infrastructure

**Days 1-2: Project Setup & Docker Foundation**
- [ ] Create project directory structure
- [ ] Initialize Git repository
- [ ] Create docker-compose.yml with 8 services
- [ ] Configure environment files (.env.example, .env)
- [ ] Set up Makefile with basic targets

**Days 3-4: Database & Object Store Setup**
- [ ] PostgreSQL schema design (ingest_runs, document_chunks tables)
- [ ] MinIO bucket creation and prefix structure
- [ ] Connection utilities for both services
- [ ] Write health check endpoints

**Days 5-7: FastAPI Application Structure**
- [ ] Project layout: app/ directory with modules
- [ ] Configuration management (config.py)
- [ ] Logging setup with structlog
- [ ] FastAPI main application with lifespan manager
- [ ] Basic /health endpoint

### Week 2: Document Processing Pipeline

**Days 8-9: Document Ingestion Core**
- [ ] Implement MinIOStore class (upload, download, list)
- [ ] Build EmbeddingService (text chunking, embedding)
- [ ] Create IngestPipeline orchestrator
- [ ] Database schema population

**Days 10-11: Retrieval & Generation**
- [ ] RetrievalService: ChromaDB queries
- [ ] GenerationService: Ollama integration
- [ ] QueryResponse formatting with sources
- [ ] Error handling for all services

**Days 12-13: Airflow Orchestration**
- [ ] Create Airflow DAG structure
- [ ] Implement 4 PythonOperator tasks
- [ ] XCom communication between tasks
- [ ] Integrate with PostgreSQL and MinIO

**Days 14: Testing & Documentation**
- [ ] Create Makefile targets for common operations
- [ ] Write Great Expectations validation suite
- [ ] Document API endpoints
- [ ] Create exercise instructions

---

## Detailed Requirements

### 1. Project Structure

Create the following directory layout:

```
11-rag-knowledge-platform-from-scratch/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings and env vars
│   ├── models.py               # Pydantic request/response models
│   ├── minio_store.py          # MinIO client wrapper
│   ├── embed.py                # Embedding service
│   ├── ingest.py               # Ingestion orchestrator
│   ├── retrieve.py             # ChromaDB retrieval
│   ├── generate.py             # Ollama generation
│   ├── database.py             # PostgreSQL utilities
│   └── Dockerfile
├── dags/
│   └── rag_ingestion_dag.py    # Airflow DAG
├── scripts/
│   ├── __init__.py
│   ├── document_seeder.py      # Synthetic data generator
│   ├── validate_documents.py   # GE validation
│   └── query_cli.py            # Interactive query tool
├── expectations/
│   └── document_suite.json     # Great Expectations suite
├── ollama/
│   └── pull_model.sh           # Model downloader script
├── docker-compose.yml          # 8 services
├── .env.example                # Environment template
├── Makefile                    # Build/run targets
├── requirements.txt            # Script dependencies
├── app/requirements-app.txt    # App dependencies
├── README.md                   # Comprehensive guide
├── exercises.md                # Student exercises
└── FROM_SCRATCH.md             # This file
```

### 2. Docker Services

Implement a docker-compose.yml file with these 8 services:

| Service | Image | Purpose | Port | Type |
|---------|-------|---------|------|------|
| postgres | postgres:15-alpine | Metadata & chunks storage | 5432 (internal) | Persistent |
| minio | minio/minio:latest | S3-compatible object store | 9000 API, 9001 Console | Persistent |
| minio-init | minio/mc:latest | One-shot bucket setup | N/A | Job |
| chromadb | chromadb/chroma:0.5.3 | Vector database | 8000 | Persistent |
| airflow-init | apache/airflow:2.8.1 | Airflow DB initialization | N/A | Job |
| airflow-webserver | apache/airflow:2.8.1 | Airflow UI | 8080 | Service |
| airflow-scheduler | apache/airflow:2.8.1 | Airflow task executor | N/A | Service |
| rag-api | python:3.11-slim | FastAPI app | 8000 | Service |

**Requirements:**
- Use `condition: service_healthy` for dependencies
- Define healthcheck scripts for each persistent service
- Mount volumes for PostgreSQL, MinIO, and Airflow
- Use environment variables from .env file
- Ensure port non-conflicts (map to 5450, 9100-9101, 8100, 8200, 8180)

### 3. Configuration Management (app/config.py)

Create a Settings class that:
- Reads all configuration from environment variables
- Has sensible defaults where appropriate
- Raises errors for missing required variables
- Is used globally throughout the application

**Required settings:**
- MinIO endpoint, credentials, bucket name
- PostgreSQL connection string
- ChromaDB host and port
- Ollama host and model name
- Embedding model name (all-MiniLM-L6-v2)
- Chunk size and overlap parameters
- Top-K retrieval parameter
- Airflow executor and database URL

### 4. MinIO Integration (app/minio_store.py)

Create a MinIOStore class with these methods:

```python
class MinIOStore:
    def __init__(self, config: Settings)
    
    def upload_document(self, local_path: str, object_name: str) -> str
        # Upload file from disk to raw/ prefix
        # Return S3 URI
    
    def download_document(self, object_name: str) -> bytes
        # Fetch document content from MinIO
    
    def list_raw_documents(self) -> list[str]
        # List all objects in raw/ prefix
    
    def mark_processed(self, object_name: str) -> bool
        # Copy from raw/ to processed/ prefix
    
    def upload_metadata(self, object_name: str, metadata: dict) -> bool
        # Store JSON metadata to embeddings/ prefix
    
    def document_exists(self, object_name: str) -> bool
        # Check if object is in raw/
```

**Constraints:**
- Use boto3 client (not s3fs)
- Handle connection errors gracefully
- Log all operations with structlog
- Create buckets and prefixes if they don't exist

### 5. Document Processing (app/embed.py)

Create an EmbeddingService class:

```python
class EmbeddingService:
    def __init__(self, config: Settings)
    
    def embed_text(self, text: str) -> list[float]
        # Single text embedding (384-dimensional for MiniLM)
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]
        # Batch embeddings for efficiency
    
    def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 512,
        overlap: int = 64
    ) -> list[ChunkMetadata]
        # Smart chunking: split on sentence boundaries first
        # Fall back to character-based chunking
        # Return chunks with metadata (index, char_start)
```

**Constraints:**
- Use sentence-transformers library (all-MiniLM-L6-v2)
- Split on `.`, `!`, `?` before character counts
- Chunks should preserve overlap for context
- Return structured metadata with each chunk

### 6. Ingestion Pipeline (app/ingest.py)

Create an IngestPipeline class:

```python
class IngestPipeline:
    def __init__(self, config: Settings)
    
    def run_document(self, object_name: str) -> IngestResult
        # 8-step pipeline:
        # 1. Download from MinIO raw/
        # 2. Extract text (handle .pdf, .txt, .md)
        # 3. Create ingest_runs record (status: processing)
        # 4. Chunk text
        # 5. Embed chunks in batch
        # 6. Upsert to ChromaDB with metadata
        # 7. Insert chunks into PostgreSQL
        # 8. Mark as processed in MinIO
        # Return IngestResult with doc_id, chunk_count, elapsed_ms
```

**Constraints:**
- Handle PDF files using pypdf
- Create database schema with IF NOT EXISTS
- Use ChromaDB get_or_create_collection pattern
- Batch embed for efficiency
- Track execution time and chunk count
- Mark runs as failed on exception

### 7. Retrieval Service (app/retrieve.py)

Create a RetrievalService class:

```python
class RetrievalService:
    def __init__(self, config: Settings)
    
    def search(
        self, 
        query: str, 
        top_k: int = 5
    ) -> list[RetrievedChunk]
        # 1. Embed the query
        # 2. Search ChromaDB
        # 3. Convert distance to relevance_score (1.0 - distance)
        # Return RetrievedChunk objects
    
    def format_context(self, chunks: list[RetrievedChunk]) -> str
        # Format chunks into prompt-ready string
        # Include source attribution
    
    def format_sources(self, chunks: list[RetrievedChunk]) -> list[dict]
        # Convert chunks to source list with relevance scores
```

### 8. Generation Service (app/generate.py)

Create a GenerationService class:

```python
class GenerationService:
    def __init__(self, config: Settings)
    
    def answer(
        self,
        question: str,
        context: str,
        sources_cited: list[str]
    ) -> GenerationResult
        # 1. Test Ollama connectivity
        # 2. Call /api/generate endpoint
        # 3. Format result with prompt tokens, model name
        # Return GenerationResult
```

**Constraints:**
- Use Ollama /api/generate endpoint (not /api/chat)
- Include SYSTEM instructions in prompt
- Handle Ollama unavailability gracefully
- Return structured response with metadata

### 9. FastAPI Application (app/main.py)

Create a FastAPI application with:

**Endpoints:**
- `GET /health` - Check service connectivity
- `POST /ingest` - Ingest single document
- `POST /ingest/all` - Batch ingest all raw/ documents
- `POST /query` - Query knowledge base
- `GET /documents` - List ingestion runs
- `GET /documents/{id}` - Get run details
- `DELETE /documents/{id}` - Delete document

**Features:**
- Lifespan context manager for service initialization
- CORS middleware (allow all origins)
- Pydantic models for validation
- Proper error responses

### 10. Airflow DAG (dags/rag_ingestion_dag.py)

Create a DAG named `rag_ingestion_pipeline` with 4 tasks:

1. **list_pending_documents** - Find all raw/ documents not yet ingested
2. **validate_documents** - Run Great Expectations checks
3. **ingest_documents** - Ingest pending documents (pull from XCom)
4. **log_summary** - Report final counts

**Constraints:**
- Use PythonOperator (not BashOperator)
- Use XCom to pass data between tasks
- Set retries=2, retry_delay=1 minute
- Use Airflow Variables for configuration
- Create Airflow connections for PostgreSQL

### 11. Data Generation (scripts/document_seeder.py)

Create a script that generates 30 synthetic documents:

**Categories (10 each):**
1. **Incident Reports** - Fields: incident_id, severity, pipeline, root_cause, mttr_minutes
2. **Data Quality Reports** - Fields: pipeline, dataset, total_rows, failures, expectation_type
3. **Architecture Decision Records** - Markdown format with status and consequences

**Features:**
- Use argparse for CLI parameters
- Upload to MinIO raw/ prefix
- Generate realistic content
- Support --count parameter for scaling

### 12. Data Validation (scripts/validate_documents.py)

Create a Great Expectations validation script:

**Expectations:**
- Table exists and has 8 columns
- Columns: id, run_id, object_name, chunk_index, char_start, chunk_text, chroma_id, created_at
- chunk_text: not null, length 10-2000
- object_name: not null, matches regex `^(raw|processed)/`
- chunk_index: between 0-500
- All primary keys not null

**Features:**
- Use PandasDataset for validation
- Log pass/fail for each expectation
- Exit with code 1 if any fail
- Support verbose output flag

### 13. Interactive CLI (scripts/query_cli.py)

Create an interactive query tool:

**Features:**
- Rich library for formatting
- Prompt user for questions
- Call /query endpoint
- Format response with answer, sources, metadata
- Support quit/exit commands
- Display response time and model name

### 14. Great Expectations Suite (expectations/document_suite.json)

Define a JSON expectation suite with 10 expectations:

- expect_table_to_exist
- expect_table_column_count_to_equal
- expect_table_columns_to_match_set
- expect_column_values_to_not_be_null (chunk_text, object_name, chroma_id, run_id)
- expect_column_value_lengths_to_be_between (chunk_text: 10-2000)
- expect_column_values_to_match_regex (object_name)
- expect_column_values_to_be_between (chunk_index: 0-500)

### 15. Ollama Model Script (ollama/pull_model.sh)

Create a bash script that:
- Checks if ollama is installed
- Warns if ollama serve is not running
- Pulls llama3.2:3b model (~2.5GB)
- Provides next steps

### 16. Makefile Targets

Implement these 12 targets:

```makefile
help                # Show all targets
up                  # Start all services
down                # Stop all services
restart             # Restart services
logs                # Tail logs (SERVICE=name)
shell               # Bash into rag-api container
setup               # Create schema and collections
seed                # Generate and upload synthetic documents
ingest              # Trigger Airflow DAG
query               # Launch interactive query CLI
validate            # Run Great Expectations validation
clean               # Remove volumes and artifacts
```

### 17. Requirements Files

**requirements.txt** (for scripts):
- boto3==1.34.69
- chromadb==0.5.3
- sentence-transformers==3.0.1
- pypdf==4.2.0
- psycopg2-binary==2.9.9
- structlog==24.1.0
- great-expectations==0.18.12
- httpx==0.27.0
- rich==13.7.1
- python-dotenv==1.0.1
- pandas==2.2.2

**app/requirements-app.txt** (for FastAPI):
- fastapi==0.111.0
- uvicorn[standard]==0.30.6
- pydantic==2.9.2
- boto3==1.34.69
- chromadb==0.5.3
- sentence-transformers==3.0.1
- pypdf==4.2.0
- psycopg2-binary==2.9.9
- structlog==24.1.0
- httpx==0.27.0
- python-dotenv==1.0.1

---

## Implementation Checkpoints

After each checkpoint, test before moving forward.

### Checkpoint 1: Docker Infrastructure (Day 3)
- [ ] `docker compose up` starts all services without errors
- [ ] `docker compose ps` shows all 8 services healthy
- [ ] All port mappings are correct

### Checkpoint 2: Database Connectivity (Day 4)
- [ ] Can connect to PostgreSQL via psql
- [ ] Can access MinIO console at http://localhost:9101
- [ ] Can connect to ChromaDB via HTTP

### Checkpoint 3: Configuration Management (Day 5)
- [ ] FastAPI /health endpoint returns JSON
- [ ] Config class properly reads .env file
- [ ] Missing required vars raise errors

### Checkpoint 4: MinIO Integration (Day 7)
- [ ] Can upload file to MinIO via MinIOStore
- [ ] Can download file from MinIO
- [ ] raw/, processed/, embeddings/ prefixes created

### Checkpoint 5: Embedding Service (Day 9)
- [ ] Text chunking splits on sentence boundaries
- [ ] Embeddings are 384-dimensional
- [ ] Batch embedding is faster than single

### Checkpoint 6: Document Ingestion (Day 10)
- [ ] Can ingest single document via /ingest endpoint
- [ ] PostgreSQL document_chunks table populated
- [ ] ChromaDB collection has vectors

### Checkpoint 7: Retrieval & Generation (Day 12)
- [ ] `/query` endpoint returns answers
- [ ] Sources are correctly cited
- [ ] Ollama is called only when available

### Checkpoint 8: Airflow Orchestration (Day 13)
- [ ] DAG appears in Airflow webserver
- [ ] Can trigger DAG manually
- [ ] Tasks complete in order with XCom passing

### Checkpoint 9: Full End-to-End (Day 14)
- [ ] Can run full pipeline: seed → ingest → query
- [ ] Validation suite passes
- [ ] All Makefile targets work

---

## Testing Checklist

Before you consider the project complete:

### Unit Testing Equivalent
- [ ] MinIOStore methods handle exceptions
- [ ] EmbeddingService produces consistent embeddings
- [ ] IngestPipeline handles missing files gracefully
- [ ] RetrievalService returns top_k results
- [ ] GenerationService formats prompts correctly

### Integration Testing Equivalent
- [ ] Can ingest document → appears in PostgreSQL → searchable in ChromaDB
- [ ] Can query knowledge base → gets relevant answer
- [ ] Airflow DAG processes all documents without errors
- [ ] Great Expectations validation catches schema violations

### Load Testing Equivalent
- [ ] Can ingest 30+ documents without memory issues
- [ ] Query response time is < 10 seconds
- [ ] Batch embedding is reasonably fast

### Error Handling
- [ ] PDF parsing fails gracefully
- [ ] Ollama unavailability doesn't crash system
- [ ] ChromaDB collection creation is idempotent
- [ ] PostgreSQL schema creation uses IF NOT EXISTS

---

## Key Design Decisions to Make

### 1. Chunking Strategy
**Question:** How do you split documents while preserving semantic meaning?

**Options:**
- Character-based: Simple but may split mid-sentence
- Sentence-based: Semantic boundaries but variable chunk sizes
- Paragraph-based: Large chunks, may miss fine-grained retrieval
- Hybrid (recommended): Sentence first, then character fallback

**Your choice:** _______________
**Reasoning:**

### 2. Vector Storage
**Question:** ChromaDB vs PostgreSQL pgvector for vector storage?

**Options:**
- ChromaDB only: Simpler, purpose-built, but separate DB
- pgvector in PostgreSQL: Unified storage, but adds complexity
- Hybrid (recommended): ChromaDB for retrieval, PostgreSQL for metadata

**Your choice:** _______________
**Reasoning:**

### 3. Embedding Model
**Question:** Which embedding model to use?

**Options:**
- all-MiniLM-L6-v2 (recommended): 384-dim, fast, good quality
- all-mpnet-base-v2: 768-dim, slower, better quality
- Custom fine-tuned: Best for domain, but requires training data

**Your choice:** _______________
**Reasoning:**

### 4. LLM Integration
**Question:** Ollama, OpenAI, Hugging Face?

**Options:**
- Ollama (recommended): Local, no API costs, educational
- OpenAI: Better quality, cloud-hosted
- Hugging Face: Open source, custom deployment

**Your choice:** _______________
**Reasoning:**

### 5. Airflow vs Alternatives
**Question:** Is Airflow the right orchestration tool?

**Options:**
- Airflow (recommended): Powerful, industry standard, learning value
- Celery: Lightweight task queue, better for streaming
- Prefect/Dagster: Modern alternatives, steeper learning curve
- Cron: Simple but hard to monitor

**Your choice:** _______________
**Reasoning:**

---

## Extension Ideas (After Core Completion)

Once the basic system works, consider:

1. **Web UI** - Build a React frontend to replace CLI
2. **Kafka Streaming** - Real-time document ingestion instead of batch
3. **Multi-language Support** - Translate documents before embedding
4. **Advanced Chunking** - Preserve code blocks, tables, headers
5. **Hybrid Retrieval** - BM25 + semantic search for better results
6. **pgvector Migration** - Replace ChromaDB with PostgreSQL pgvector
7. **Monitoring** - Add Prometheus metrics for production readiness
8. **Fine-tuning** - Train embedding model on domain-specific data

---

## Comparing Your Implementation

Once you complete your implementation, compare it with the reference implementation:

**Read through these files in order:**
1. `/11-rag-knowledge-platform/app/config.py` - Configuration approach
2. `/11-rag-knowledge-platform/app/minio_store.py` - MinIO integration
3. `/11-rag-knowledge-platform/app/embed.py` - Embedding logic
4. `/11-rag-knowledge-platform/app/ingest.py` - Full pipeline
5. `/11-rag-knowledge-platform/app/main.py` - API structure
6. `/11-rag-knowledge-platform/dags/rag_ingestion_dag.py` - Airflow DAG

**Questions to ask yourself:**
- What did they do differently than my approach?
- Why might their way be better (or worse) than mine?
- What refactoring would I do if this were production code?
- How would I handle edge cases differently?
- What would break if I scaled this to 1 million documents?

---

## Resources & References

### Documentation
- [ChromaDB Python Client](https://docs.trychroma.com/)
- [MinIO Python SDK](https://docs.min.io/minio/baremetal/sdks/python/API.html)
- [FastAPI Guide](https://fastapi.tiangolo.com/)
- [Airflow Tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/)
- [Great Expectations](https://docs.greatexpectations.io/)
- [sentence-transformers](https://www.sbert.net/)
- [Ollama Documentation](https://github.com/ollama/ollama)

### Debugging Tips
- Use `docker compose logs -f <service>` to watch service logs in real-time
- Test MinIO connectivity: `aws s3 ls --endpoint-url http://localhost:9100 --no-sign-request`
- Query ChromaDB directly: `curl http://localhost:8200/api/v1/heartbeat`
- Check PostgreSQL schema: `docker compose exec -T postgres psql -U raguser -d ragdb -c "\dt"`
- Inspect Airflow DAG: `docker compose exec airflow-webserver airflow dags list`

### Common Pitfalls
1. **Environment variables not loading** - Check .env file is copied from .env.example
2. **Services not healthy** - Check healthcheck scripts, ports, and logs
3. **Embedding dimension mismatch** - Ensure embedding model matches ChromaDB dimension
4. **XCom missing** - DAG tasks must use `ti.xcom_push()` to share data
5. **MinIO bucket missing** - minio-init service must run before rag-api
6. **Ollama timeout** - Ensure `ollama serve` is running on host before querying

---

## Success Criteria

Your implementation is complete when:

- [ ] All 22+ files are created according to specification
- [ ] docker compose up starts all 8 services successfully
- [ ] make setup initializes databases and collections
- [ ] make seed generates 30 synthetic documents
- [ ] make ingest triggers Airflow DAG without errors
- [ ] make query launches interactive CLI
- [ ] API /query endpoint returns relevant answers with sources
- [ ] Great Expectations validation suite passes
- [ ] All Makefile targets work as documented
- [ ] Code has proper error handling and logging
- [ ] README documents the system for others to understand
- [ ] You can explain design decisions for each component

---

## Final Notes

This is an **educational project**, not a production system. That said, the patterns and decisions you make here scale to production:

- Proper separation of concerns (config, storage, compute)
- Idempotent operations (safe to retry without side effects)
- Infrastructure as code (docker-compose, Makefile)
- Data validation (Great Expectations)
- Monitoring and observability (healthchecks, logging)
- Documentation (README, API specs, exercise guides)

The goal is not to copy the reference implementation, but to understand **why** each decision was made. Ask questions. Challenge assumptions. Document your reasoning.

**Good luck! 🚀**
