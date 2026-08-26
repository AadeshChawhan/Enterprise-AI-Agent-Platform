from datetime import datetime
from backend.app.services import embedding_service
from sqlalchemy.orm import Session

from backend.app.models.knowledge_base_db import (
    KnowledgeBaseDB,
    KnowledgeDocumentDB,
    KnowledgeChunkDB,
)


def create_knowledge_base(
    db: Session,
    name: str,
    description: str = "",
):
    knowledge_base = KnowledgeBaseDB(
        name=name,
        description=description,
    )

    db.add(knowledge_base)
    db.commit()
    db.refresh(knowledge_base)

    return knowledge_base


def get_knowledge_bases(
    db: Session,
):
    return (
        db.query(KnowledgeBaseDB)
        .order_by(
            KnowledgeBaseDB.updated_at.desc()
        )
        .all()
    )


def get_knowledge_base(
    db: Session,
    knowledge_base_id: int,
):
    return (
        db.query(KnowledgeBaseDB)
        .filter(
            KnowledgeBaseDB.id
            == knowledge_base_id
        )
        .first()
    )


def update_knowledge_base(
    db: Session,
    knowledge_base_id: int,
    name: str,
    description: str,
):
    knowledge_base = get_knowledge_base(
        db,
        knowledge_base_id,
    )

    if knowledge_base is None:
        return None

    knowledge_base.name = name
    knowledge_base.description = description
    knowledge_base.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(knowledge_base)

    return knowledge_base


def delete_knowledge_base(
    db: Session,
    knowledge_base_id: int,
):
    knowledge_base = get_knowledge_base(
        db,
        knowledge_base_id,
    )

    if knowledge_base is None:
        return None

    db.delete(knowledge_base)
    db.commit()

    return knowledge_base


def get_documents(
    db: Session,
    knowledge_base_id: int,
):
    return (
        db.query(KnowledgeDocumentDB)
        .filter(
            KnowledgeDocumentDB.knowledge_base_id
            == knowledge_base_id
        )
        .order_by(
            KnowledgeDocumentDB.created_at.desc()
        )
        .all()
    )

def create_document(
    db: Session,
    knowledge_base_id: int,
    filename: str,
    content_type: str | None,
    storage_path: str,
):
    document = KnowledgeDocumentDB(
        knowledge_base_id=knowledge_base_id,
        filename=filename,
        content_type=content_type,
        storage_path=storage_path,
        status="uploaded",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document

def create_chunks(
    db: Session,
    document_id: int,
    chunks: list[str],
):
    if not chunks:
        return []

    embeddings = (
        embedding_service.generate_embeddings(
            chunks
        )
    )

    if len(embeddings) != len(chunks):
        raise RuntimeError(
            "Embedding count does not match chunk count"
        )

    chunk_records = []

    for index, content in enumerate(chunks):
        chunk_record = KnowledgeChunkDB(
            document_id=document_id,
            chunk_index=index,
            content=content,
            embedding=embeddings[index],
        )

        chunk_records.append(
            chunk_record
        )

    db.add_all(
        chunk_records
    )

    db.commit()

    for chunk_record in chunk_records:
        db.refresh(
            chunk_record
        )

    return chunk_records


def get_document_chunks(
    db: Session,
    document_id: int,
):
    return (
        db.query(KnowledgeChunkDB)
        .filter(
            KnowledgeChunkDB.document_id
            == document_id
        )
        .order_by(
            KnowledgeChunkDB.chunk_index.asc()
        )
        .all()
    )


def update_document_status(
    db: Session,
    document_id: int,
    status: str,
):
    document = (
        db.query(KnowledgeDocumentDB)
        .filter(
            KnowledgeDocumentDB.id
            == document_id
        )
        .first()
    )

    if document is None:
        return None

    document.status = status

    db.commit()
    db.refresh(document)

    return document

def search_knowledge_base(
    db: Session,
    knowledge_base_id: int,
    query: str,
    limit: int = 5,
):
    query_embedding = (
        embedding_service.generate_embedding(
            query
        )
    )

    distance = (
        KnowledgeChunkDB.embedding.cosine_distance(
            query_embedding
        )
    )

    results = (
        db.query(
            KnowledgeChunkDB,
            distance.label("distance"),
        )
        .join(
            KnowledgeDocumentDB,
            KnowledgeChunkDB.document_id
            == KnowledgeDocumentDB.id,
        )
        .filter(
            KnowledgeDocumentDB.knowledge_base_id
            == knowledge_base_id,
            KnowledgeChunkDB.embedding.isnot(None),
        )
        .order_by(
            distance
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "filename": chunk.document.filename,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "distance": float(distance_value),
            "similarity": float(
                1 - distance_value
            ),
        }
        for chunk, distance_value in results
    ]