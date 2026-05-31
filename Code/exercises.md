# RAG Exercises

1. Understand the system components: Postgres, MinIO, ChromaDB, FastAPI, Airflow.
2. Implement `app/config.py` to load environment variables.
3. Build the PostgreSQL schema for documents and ingestion tracking.
4. Write an ingestion pipeline that creates chunks, computes embeddings, and stores vectors.
5. Add a FastAPI `/query` endpoint to retrieve results and generate a response.
6. Configure an Airflow DAG to orchestrate ingestion and validation.
7. Create a Great Expectations suite to verify document quality.
