from datetime import datetime

from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    agent_id: int

    title: str = Field(
        default="New Conversation",
        min_length=1,
        max_length=255,
    )


class ConversationUpdate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )


class ConversationResponse(BaseModel):
    id: int
    agent_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    role: str
    content: str = Field(
        min_length=1
    )


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True