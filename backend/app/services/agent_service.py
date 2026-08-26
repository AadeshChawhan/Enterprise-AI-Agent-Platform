from sqlalchemy.orm import Session

from backend.app.models.agent_db import AgentDB
from backend.app.models.agent import AgentCreate


def create_agent(
    db: Session,
    agent: AgentCreate,
):
    new_agent = AgentDB(
        name=agent.name,
        provider=agent.provider,
        model=agent.model,
        temperature=agent.temperature,
        system_prompt=agent.system_prompt,
        knowledge_base_id=agent.knowledge_base_id,
    )

    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    return new_agent


def get_all_agents(
    db: Session,
):
    return (
        db.query(AgentDB)
        .order_by(AgentDB.id.asc())
        .all()
    )


def get_agent_by_id(
    db: Session,
    agent_id: int,
):
    return (
        db.query(AgentDB)
        .filter(
            AgentDB.id == agent_id
        )
        .first()
    )


def update_agent(
    db: Session,
    agent_id: int,
    agent: AgentCreate,
):
    existing_agent = (
        db.query(AgentDB)
        .filter(
            AgentDB.id == agent_id
        )
        .first()
    )

    if existing_agent is None:
        return None

    existing_agent.name = agent.name
    existing_agent.provider = agent.provider
    existing_agent.model = agent.model
    existing_agent.temperature = agent.temperature
    existing_agent.system_prompt = agent.system_prompt
    existing_agent.knowledge_base_id = agent.knowledge_base_id

    db.commit()
    db.refresh(existing_agent)

    return existing_agent


def delete_agent(
    db: Session,
    agent_id: int,
):
    existing_agent = (
        db.query(AgentDB)
        .filter(
            AgentDB.id == agent_id
        )
        .first()
    )

    if existing_agent is None:
        return None

    db.delete(existing_agent)
    db.commit()

    return existing_agent