"""SQLAlchemy engine and request-independent session factory."""

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker


class Database:
    def __init__(self, database_url: str) -> None:
        if make_url(database_url).drivername != "postgresql+psycopg":
            raise ValueError("OPSDESK_DATABASE_URL must use the postgresql+psycopg driver")
        engine = create_engine(database_url, pool_pre_ping=True)
        self.engine = engine
        self.sessions: sessionmaker[Session] = sessionmaker(
            bind=engine, autoflush=False, expire_on_commit=False
        )
