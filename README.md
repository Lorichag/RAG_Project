# RAG Knowledge Platform from Scratch

This project is a local Retrieval-Augmented Generation (RAG) system built with PostgreSQL, MinIO, ChromaDB, and FastAPI.

## Project structure

- `app/`: FastAPI application and business logic
- `dags/`: Airflow DAGs for ingestion orchestration
- `scripts/`: utility scripts for seeding and querying
- `expectations/`: Great Expectations validation suites
- `ollama/`: scripts for managing the LLM model

## Quick start

1. Copy `.env.example` to `.env`, or use the existing `.env` file.
   - If `rag-api` runs in Docker and Ollama is installed on the host, set `OLLAMA_HOST=http://host.docker.internal:11434`.
2. Install dependencies: `make setup`.
   - If `make` is not available on Windows, use `.\setup.ps1`.
3. Start the Docker services: `docker compose up --build`.
   - On Windows, use `.\docker-up.ps1`.
4. Run the API locally (optional): `make run-api`.
   - On Windows without `make`, use `.\run-api.ps1`.
5. Test the ingest endpoint:
   - `curl -X POST http://localhost:8180/ingest -H "Content-Type: application/json" -d "{\"document_name\":\"sample.txt\",\"content\":\"This is a test document.\"}`
6. Test ingestion from MinIO `raw/` storage:
   - `curl -X POST http://localhost:8180/ingest/raw -H "Content-Type: application/json" -d "{\"object_name\":\"sample.txt\"}`
7. Ingest all pending raw documents:
   - `curl -X POST http://localhost:8180/ingest/all`
8. List ingestion runs:
   - `curl http://localhost:8180/documents`
9. Retrieve a specific run:
   - `curl http://localhost:8180/documents/<run_id>`
10. Delete an ingestion run:
   - `curl -X DELETE http://localhost:8180/documents/<run_id>`
11. Test the query endpoint:
   - `curl -X POST http://localhost:8180/query -H "Content-Type: application/json" -d "{\"query\":\"What does the document contain?\"}"`

## Goals

- document ingestion
- chunking and embeddings
- vector indexing
- RAG query support via FastAPI

## Next steps

- implement `app/config.py`
- create the PostgreSQL schema
- add the ingestion pipeline
- configure Docker Compose

## Design choices

1. Chunking Strategy
Question: How do you split documents while preserving semantic meaning?

Answer: Hybrid (recommended)
Reasoning: The hybrid approach starts with sentence-based chunking to preserve semantic boundaries, then falls back to character-based splitting when sentences are too long or exceed the target chunk size. This balances quality and consistency for retrieval.

2. Vector Storage
Question: ChromaDB vs PostgreSQL pgvector for vector storage?

Answer: Hybrid (recommended)
Reasoning: Use ChromaDB for vector retrieval and PostgreSQL for metadata and ingestion tracking. This provides a purpose-built similarity search engine while keeping document and run metadata in the existing relational store.

3. Embedding Model
Question: Which embedding model to use?

Answer: all-MiniLM-L6-v2 (recommended)
Reasoning: `all-MiniLM-L6-v2` is fast, efficient, and good quality for general semantic search, making it suitable for local RAG workloads without excessive compute cost.

4. LLM Integration
Question: Ollama, OpenAI, Hugging Face?

Answer: Ollama (recommended)
Reasoning: Ollama enables local inference with no API costs and is ideal for educational and offline development setups. It avoids external dependency while still supporting useful local generation.

5. Airflow vs Alternatives
Question: Is Airflow the right orchestration tool?

Answer: Airflow (recommended)
Reasoning: Airflow is powerful, widely adopted, and provides strong scheduling, monitoring, and retry capabilities. It also delivers valuable learning experience for production-style data workflows.


Project carried out by Loric Hagard