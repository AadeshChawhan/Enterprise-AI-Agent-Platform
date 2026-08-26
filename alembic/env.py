from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

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

# Alembic Config object
config = context.config


# We are not using Alembic's logging configuration because
# our alembic.ini has been simplified.
# fileConfig(config.config_file_name)


# SQLAlchemy metadata
# Alembic uses this to detect changes in our database models.
from backend.app.db.database import Base

from backend.app.models.agent_db import AgentDB
from backend.app.models.conversation_db import (
    ConversationDB,
    MessageDB,
)
from backend.app.models.knowledge_base_db import (
    KnowledgeBaseDB,
    KnowledgeDocumentDB,
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Offline mode generates SQL without creating a database connection.
    """

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    Online mode connects directly to PostgreSQL and applies migrations.
    """

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()