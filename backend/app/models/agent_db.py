from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from backend.app.db.database import Base


class AgentDB(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(255),
        nullable=False,
    )

    provider = Column(
        String(50),
        nullable=False,
        default="ollama",
    )

    model = Column(
        String(255),
        nullable=False,
    )

    temperature = Column(
        Float,
        nullable=False,
        default=0.7,
    )

    system_prompt = Column(
        Text,
        nullable=False,
        default="",
    )

    knowledge_base_id = Column(
    Integer,
    ForeignKey(
        "knowledge_bases.id",
        ondelete="SET NULL",
    ),
    nullable=True,
)