from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from backend.app.services import agent_service
from backend.app.services import conversation_service
from backend.app.services import llm_service

router = APIRouter()


# --------------------------------------------------
# CREATE CONVERSATION
# --------------------------------------------------

@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=201,
)
def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
):
    agent = agent_service.get_agent_by_id(
        db,
        conversation.agent_id,
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    return conversation_service.create_conversation(
        db=db,
        agent_id=conversation.agent_id,
        title=conversation.title,
    )


# --------------------------------------------------
# GET CONVERSATIONS FOR AGENT
# --------------------------------------------------

@router.get(
    "/agents/{agent_id}/conversations",
    response_model=list[ConversationResponse],
)
def get_agent_conversations(
    agent_id: int,
    db: Session = Depends(get_db),
):
    agent = agent_service.get_agent_by_id(
        db,
        agent_id,
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    return conversation_service.get_conversations(
        db,
        agent_id,
    )


# --------------------------------------------------
# GET ONE CONVERSATION
# --------------------------------------------------

@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = conversation_service.get_conversation(
        db,
        conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return conversation


# --------------------------------------------------
# UPDATE CONVERSATION TITLE
# --------------------------------------------------

@router.put(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
)
def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    db: Session = Depends(get_db),
):
    title = conversation_update.title.strip()

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Conversation title cannot be empty",
        )

    conversation = (
        conversation_service.update_conversation_title(
            db=db,
            conversation_id=conversation_id,
            title=title,
        )
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return conversation


# --------------------------------------------------
# DELETE CONVERSATION
# --------------------------------------------------

@router.delete(
    "/conversations/{conversation_id}",
)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = conversation_service.delete_conversation(
        db,
        conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return {
        "message": "Conversation deleted successfully",
        "conversation_id": conversation_id,
    }

# --------------------------------------------------
# GENERATE CONVERSATION TITLE
# --------------------------------------------------

@router.post(
    "/conversations/{conversation_id}/generate-title",
    response_model=ConversationResponse,
)
def generate_conversation_title(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = conversation_service.get_conversation(
        db,
        conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    agent = agent_service.get_agent_by_id(
        db,
        conversation.agent_id,
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    messages = conversation_service.get_messages(
        db,
        conversation_id,
    )

    first_user_message = next(
        (
            message
            for message in messages
            if message.role == "user"
        ),
        None,
    )

    if first_user_message is None:
        raise HTTPException(
            status_code=400,
            detail="Conversation has no user messages",
        )

    try:
        title = llm_service.generate_conversation_title(
    provider=agent.provider,
    prompt=first_user_message.content,
    model=agent.model,
)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Unable to generate conversation title",
        )

    updated_conversation = (
        conversation_service.update_conversation_title(
            db=db,
            conversation_id=conversation_id,
            title=title,
        )
    )

    return updated_conversation


# --------------------------------------------------
# GET MESSAGES
# --------------------------------------------------

@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = conversation_service.get_conversation(
        db,
        conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return conversation_service.get_messages(
        db,
        conversation_id,
    )


# --------------------------------------------------
# ADD MESSAGE
# --------------------------------------------------

@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=201,
)
def add_message(
    conversation_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
):
    conversation = conversation_service.get_conversation(
        db,
        conversation_id,
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    if message.role not in {"user", "assistant"}:
        raise HTTPException(
            status_code=400,
            detail="Role must be 'user' or 'assistant'",
        )

    return conversation_service.add_message(
        db=db,
        conversation_id=conversation_id,
        role=message.role,
        content=message.content,
    )