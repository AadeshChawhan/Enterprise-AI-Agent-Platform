import os

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy import pool

from backend.app.db.database import Base
from backend.app.models.agent_db import AgentDB
from backend.app.models.conversation_db import (
    ConversationDB,
    MessageDB,
)
from backend.app.models.knowledge_base_db import (
    KnowledgeBaseDB,
    KnowledgeDocumentDB,
    KnowledgeChunkDB,
)


# --------------------------------------------------
# ALEMBIC CONFIG
# --------------------------------------------------

config = context.config


# --------------------------------------------------
# DATABASE URL
# --------------------------------------------------

database_url = os.getenv("DATABASE_URL")

if not database_url:
    database_url = config.get_main_option(
        "sqlalchemy.url"
    )

if not database_url:
    raise RuntimeError(
        "DATABASE_URL is not configured"
    )


# --------------------------------------------------
# SQLALCHEMY METADATA
# --------------------------------------------------

target_metadata = Base.metadata


# --------------------------------------------------
# OFFLINE MIGRATIONS
# --------------------------------------------------

def run_migrations_offline() -> None:
    """
    Run migrations without creating
    a database connection.
    """

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


# --------------------------------------------------
# ONLINE MIGRATIONS
# --------------------------------------------------

def run_migrations_online() -> None:
    """
    Connect directly to the database
    specified by DATABASE_URL.
    """

    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# --------------------------------------------------
# RUN
# --------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()