import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured"
    )


engine = create_engine(
    DATABASE_URL,

    # Check pooled connections before handing
    # them to the application. This prevents
    # stale PostgreSQL/Neon connections from
    # causing "SSL connection has been closed
    # unexpectedly" errors.
    pool_pre_ping=True,

    # Periodically replace older connections
    # instead of keeping them in the pool
    # indefinitely.
    pool_recycle=300,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()