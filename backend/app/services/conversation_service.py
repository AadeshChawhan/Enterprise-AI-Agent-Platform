from datetime import datetime

from sqlalchemy.orm import Session

from backend.app.models.conversation_db import (
    ConversationDB,
    MessageDB,
)


def create_conversation(
    db: Session,
    agent_id: int,
    title: str = "New Conversation",
):
    conversation = ConversationDB(
        agent_id=agent_id,
        title=title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_conversations(
    db: Session,
    agent_id: int,
):
    return (
        db.query(ConversationDB)
        .filter(
            ConversationDB.agent_id == agent_id
        )
        .order_by(
            ConversationDB.updated_at.desc()
        )
        .all()
    )


def get_conversation(
    db: Session,
    conversation_id: int,
):
    return (
        db.query(ConversationDB)
        .filter(
            ConversationDB.id == conversation_id
        )
        .first()
    )

def update_conversation_title(
    db: Session,
    conversation_id: int,
    title: str,
):
    conversation = get_conversation(
        db,
        conversation_id
    )

    if conversation is None:
        return None

    conversation.title = title
    conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(conversation)

    return conversation


def delete_conversation(
    db: Session,
    conversation_id: int,
):
    conversation = get_conversation(
        db,
        conversation_id
    )

    if conversation is None:
        return None

    db.delete(conversation)
    db.commit()

    return conversation


def add_message(
    db: Session,
    conversation_id: int,
    role: str,
    content: str,
):
    message = MessageDB(
        conversation_id=conversation_id,
        role=role,
        content=content,
    )

    db.add(message)

    conversation = get_conversation(
        db,
        conversation_id
    )

    if conversation:
        conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(message)

    return message


def get_messages(
    db: Session,
    conversation_id: int,
):
    return (
        db.query(MessageDB)
        .filter(
            MessageDB.conversation_id
            == conversation_id
        )
        .order_by(
            MessageDB.created_at.asc(),
            MessageDB.id.asc()
        )
        .all()
    )