from datetime import datetime
from backend.app.services import embedding_service
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.app.db.database import Base


class KnowledgeBaseDB(Base):
    __tablename__ = "knowledge_bases"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=False,
        default="",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    documents = relationship(
        "KnowledgeDocumentDB",
        back_populates="knowledge_base",
        cascade="all, delete-orphan",
    )


class KnowledgeDocumentDB(Base):
    __tablename__ = "knowledge_documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    knowledge_base_id = Column(
        Integer,
        ForeignKey(
            "knowledge_bases.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    filename = Column(
        String(255),
        nullable=False,
    )

    content_type = Column(
        String(100),
        nullable=True,
    )

    storage_path = Column(
        String(500),
        nullable=True,
    )

    status = Column(
        String(50),
        nullable=False,
        default="uploaded",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    knowledge_base = relationship(
        "KnowledgeBaseDB",
        back_populates="documents",
    )

    chunks = relationship(
        "KnowledgeChunkDB",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="KnowledgeChunkDB.chunk_index",
    )


class KnowledgeChunkDB(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    document_id = Column(
        Integer,
        ForeignKey(
            "knowledge_documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    chunk_index = Column(
        Integer,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    embedding = Column(
        Vector(384),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    document = relationship(
        "KnowledgeDocumentDB",
        back_populates="chunks",
    )