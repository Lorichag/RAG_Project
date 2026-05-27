import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = Field("development", env="ENVIRONMENT")
    postgres_host: str = Field(..., env="POSTGRES_HOST")
    postgres_port: int = Field(..., env="POSTGRES_PORT")
    postgres_db: str = Field(..., env="POSTGRES_DB")
    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    minio_endpoint: str = Field(..., env="MINIO_ENDPOINT")
    minio_access_key: str = Field(..., env="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(..., env="MINIO_SECRET_KEY")
    minio_bucket: str = Field(..., env="MINIO_BUCKET")
    chroma_host: str = Field(..., env="CHROMA_HOST")
    chroma_port: int = Field(..., env="CHROMA_PORT")
    ollama_host: str = Field("http://localhost:11434", env="OLLAMA_HOST")
    ollama_model: str = Field(..., env="OLLAMA_MODEL")
    embedding_model: str = Field("all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    chunk_size: int = Field(512, env="CHUNK_SIZE")
    chunk_overlap: int = Field(64, env="CHUNK_OVERLAP")
    airflow_executor: str = Field("LocalExecutor", env="AIRFLOW_EXECUTOR")
    airflow_db_uri: str = Field("sqlite:///airflow.db", env="AIRFLOW_DB_URI")

    @property
    def postgres_dsn(self) -> str:
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def psycopg_dsn(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def is_running_in_docker(self) -> bool:
        return Path("/.dockerenv").exists() or os.getenv("DOCKER_CONTAINER") == "1"

    @property
    def effective_ollama_host(self) -> str:
        if self.is_running_in_docker and "localhost" in self.ollama_host:
            return self.ollama_host.replace("localhost", "host.docker.internal")
        return self.ollama_host

    class Config:
        env_file = Path(".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
