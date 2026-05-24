from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings


Base = declarative_base()
engine = create_engine(settings.postgres_dsn, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    from app.db_models import Document, DocumentChunk

    Base.metadata.create_all(bind=engine)


def get_db_session():
    with SessionLocal() as session:
        yield session
