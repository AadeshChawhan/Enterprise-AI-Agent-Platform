from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    KnowledgeDocumentResponse,
    KnowledgeChunkResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
)
from backend.app.services import (
    document_processing_service,
    knowledge_base_service,
)
from pathlib import Path
from uuid import uuid4


router = APIRouter(
    prefix="/knowledge-bases",
    tags=["Knowledge Bases"],
)


@router.post(
    "",
    response_model=KnowledgeBaseResponse,
    status_code=201,
)
def create_knowledge_base(
    request: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
):
    name = request.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Knowledge base name cannot be empty",
        )

    return knowledge_base_service.create_knowledge_base(
        db=db,
        name=name,
        description=request.description.strip(),
    )

@router.post(
    "/{knowledge_base_id}/documents",
    response_model=KnowledgeDocumentResponse,
    status_code=201,
)
async def upload_document(
    knowledge_base_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    knowledge_base = (
        knowledge_base_service.get_knowledge_base(
            db,
            knowledge_base_id,
        )
    )

    if knowledge_base is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge base not found",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required",
        )

    allowed_extensions = {
        ".pdf",
        ".txt",
        ".docx",
    }

    original_filename = Path(
        file.filename
    ).name

    extension = Path(
        original_filename
    ).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Allowed types: PDF, TXT, DOCX"
            ),
        )

    storage_directory = (
        Path("storage")
        / "knowledge_bases"
        / str(knowledge_base_id)
    )

    storage_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = (
        f"{uuid4().hex}{extension}"
    )

    file_path = (
        storage_directory
        / stored_filename
    )

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty",
            )

        # 10 MB maximum for v1.
        max_file_size = (
            10 * 1024 * 1024
        )

        if len(contents) > max_file_size:
            raise HTTPException(
                status_code=413,
                detail=(
                    "File is too large. "
                    "Maximum size is 10 MB."
                ),
            )

        file_path.write_bytes(
            contents
        )

        document = (
            knowledge_base_service.create_document(
                db=db,
                knowledge_base_id=knowledge_base_id,
                filename=original_filename,
                content_type=file.content_type,
                storage_path=str(file_path),
            )
        )
        try:
            # ------------------------------------------
            # EXTRACT TEXT + CREATE CHUNKS
            # ------------------------------------------

            chunks = (
                document_processing_service.extract_and_chunk(
                    file_path=str(file_path),
                    chunk_size=800,
                    overlap=120,
                )
            )

            if not chunks:
                raise ValueError(
                    "No readable content found in document"
                )

            # ------------------------------------------
            # SAVE CHUNKS TO POSTGRESQL
            # ------------------------------------------

            knowledge_base_service.create_chunks(
                db=db,
                document_id=document.id,
                chunks=chunks,
            )

            # ------------------------------------------
            # MARK DOCUMENT AS PROCESSED
            # ------------------------------------------

            document = (
                knowledge_base_service.update_document_status(
                    db=db,
                    document_id=document.id,
                    status="processed",
                )
            )

            return document

        except Exception as exc:
            knowledge_base_service.update_document_status(
                db=db,
                document_id=document.id,
                status="failed",
            )

            raise HTTPException(
                status_code=422,
                detail=(
                    f"Document processing failed: {exc}"
                ),
            )

        return document

    except HTTPException:
        raise

    except Exception as exc:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to upload document: {exc}"
            ),
        )

    finally:
        await file.close()


@router.get(
    "",
    response_model=list[KnowledgeBaseResponse],
)
def get_knowledge_bases(
    db: Session = Depends(get_db),
):
    return knowledge_base_service.get_knowledge_bases(
        db
    )


@router.get(
    "/{knowledge_base_id}",
    response_model=KnowledgeBaseResponse,
)
def get_knowledge_base(
    knowledge_base_id: int,
    db: Session = Depends(get_db),
):
    knowledge_base = (
        knowledge_base_service.get_knowledge_base(
            db,
            knowledge_base_id,
        )
    )

    if knowledge_base is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge base not found",
        )

    return knowledge_base


@router.put(
    "/{knowledge_base_id}",
    response_model=KnowledgeBaseResponse,
)
def update_knowledge_base(
    knowledge_base_id: int,
    request: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
):
    name = request.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Knowledge base name cannot be empty",
        )

    knowledge_base = (
        knowledge_base_service.update_knowledge_base(
            db=db,
            knowledge_base_id=knowledge_base_id,
            name=name,
            description=request.description.strip(),
        )
    )

    if knowledge_base is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge base not found",
        )

    return knowledge_base


@router.delete(
    "/{knowledge_base_id}",
)
def delete_knowledge_base(
    knowledge_base_id: int,
    db: Session = Depends(get_db),
):
    knowledge_base = (
        knowledge_base_service.delete_knowledge_base(
            db,
            knowledge_base_id,
        )
    )

    if knowledge_base is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge base not found",
        )

    return {
        "message": "Knowledge base deleted successfully",
        "knowledge_base_id": knowledge_base_id,
    }


@router.get(
    "/{knowledge_base_id}/documents",
    response_model=list[KnowledgeDocumentResponse],
)
def get_knowledge_base_documents(
    knowledge_base_id: int,
    db: Session = Depends(get_db),
):
    knowledge_base = (
        knowledge_base_service.get_knowledge_base(
            db,
            knowledge_base_id,
        )
    )

    if knowledge_base is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge base not found",
        )

    return knowledge_base_service.get_documents(
        db,
        knowledge_base_id,
    )

# --------------------------------------------------
# GET DOCUMENTS FOR KNOWLEDGE BASE
# --------------------------------------------------

@router.get(
    "/{knowledge_base_id}/documents",
    response_model=list[KnowledgeDocumentResponse],
)
def get_knowledge_base_documents(
    knowledge_base_id: int,
    db: Session = Depends(get_db),
):
    knowledge_base = (
        knowledge_base_service.get_knowledge_base(
            db,
            knowledge_base_id,
        )
    )

    if knowledge_base is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge base not found",
        )

    return knowledge_base_service.get_documents(
        db,
        knowledge_base_id,
    )


# --------------------------------------------------
# GET CHUNKS FOR DOCUMENT
# --------------------------------------------------

@router.get(
    "/documents/{document_id}/chunks",
    response_model=list[KnowledgeChunkResponse],
)
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
):
    return (
        knowledge_base_service.get_document_chunks(
            db,
            document_id,
        )
    )

@router.post(
    "/{knowledge_base_id}/search",
    response_model=list[KnowledgeSearchResult],
)
def search_knowledge_base(
    knowledge_base_id: int,
    request: KnowledgeSearchRequest,
    db: Session = Depends(get_db),
):
    knowledge_base = (
        knowledge_base_service.get_knowledge_base(
            db,
            knowledge_base_id,
        )
    )

    if knowledge_base is None:
        raise HTTPException(
            status_code=404,
            detail="Knowledge base not found",
        )

    query = request.query.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty",
        )

    if request.limit < 1 or request.limit > 20:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 20",
        )

    try:
        return (
            knowledge_base_service.search_knowledge_base(
                db=db,
                knowledge_base_id=knowledge_base_id,
                query=query,
                limit=request.limit,
            )
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Knowledge search failed: {exc}",
        )