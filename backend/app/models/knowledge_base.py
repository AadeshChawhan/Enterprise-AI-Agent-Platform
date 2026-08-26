from datetime import datetime
from pgvector.sqlalchemy import Vector

from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str = ""


class KnowledgeBaseUpdate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str = ""


class KnowledgeBaseResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeDocumentResponse(BaseModel):
    id: int
    knowledge_base_id: int
    filename: str
    content_type: str | None
    storage_path: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class KnowledgeChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class KnowledgeSearchRequest(BaseModel):
    query: str
    limit: int = 5


class KnowledgeSearchResult(BaseModel):
    chunk_id: int
    document_id: int
    filename: str
    chunk_index: int
    content: str
    distance: float
    similarity: float