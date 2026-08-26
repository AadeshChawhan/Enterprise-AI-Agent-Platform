from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from fastapi.responses import StreamingResponse
import json
from backend.app.db.database import get_db
from backend.app.models.agent import (
    AgentCreate,
    AgentResponse,
    AgentRunRequest
)
from backend.app.services import agent_service
from backend.app.services import llm_service
from backend.app.services import conversation_service
from backend.app.services import knowledge_base_service
from backend.app.services import rag_service


router = APIRouter()

logger = logging.getLogger(__name__)


# --------------------------------------------------
# CREATE AGENT
# --------------------------------------------------

@router.post(
    "/agents",
    status_code=201,
    response_model=AgentResponse
)
def create_agent(
    agent: AgentCreate,
    db: Session = Depends(get_db)
):
    new_agent = agent_service.create_agent(
        db,
        agent
    )

    return new_agent


# --------------------------------------------------
# GET ALL AGENTS
# --------------------------------------------------

@router.get(
    "/agents",
    response_model=list[AgentResponse]
)
def get_agents(
    db: Session = Depends(get_db)
):
    return agent_service.get_all_agents(db)


# --------------------------------------------------
# GET ONE AGENT
# --------------------------------------------------

@router.get(
    "/agents/{agent_id}",
    response_model=AgentResponse
)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):
    agent = agent_service.get_agent_by_id(
        db,
        agent_id
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    return agent


# --------------------------------------------------
# UPDATE AGENT
# --------------------------------------------------

@router.put(
    "/agents/{agent_id}",
    response_model=AgentResponse
)
def update_agent(
    agent_id: int,
    agent: AgentCreate,
    db: Session = Depends(get_db)
):
    updated_agent = agent_service.update_agent(
        db,
        agent_id,
        agent
    )

    if updated_agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    return updated_agent


# --------------------------------------------------
# DELETE AGENT
# --------------------------------------------------

@router.delete(
    "/agents/{agent_id}",
    response_model=AgentResponse
)
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db)
):
    deleted_agent = agent_service.delete_agent(
        db,
        agent_id
    )

    if deleted_agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    return deleted_agent


# --------------------------------------------------
# RUN AGENT WITH CONVERSATION MEMORY
# --------------------------------------------------

@router.post("/agents/{agent_id}/run")
def run_agent(
    agent_id: int,
    request: AgentRunRequest,
    db: Session = Depends(get_db)
):
    agent = agent_service.get_agent_by_id(
        db,
        agent_id
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    try:
        if not llm_service.model_available(
    provider=agent.provider,
    model=agent.model,
):
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Model '{agent.model}' "
                    "is not available in Ollama."
                )
            )

        conversation_history = []

        if request.conversation_id is not None:
            conversation = conversation_service.get_conversation(
                db,
                request.conversation_id
            )

            if conversation is None:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found"
                )

            if conversation.agent_id != agent_id:
                raise HTTPException(
                    status_code=400,
                    detail="Conversation does not belong to this agent."
                )

            stored_messages = conversation_service.get_messages(
                db,
                request.conversation_id
            )

            conversation_history = [
                {
                    "role": message.role,
                    "content": message.content
                }
                for message in stored_messages
            ]

    # ----------------------------------------------
    # BUILD SYSTEM PROMPT + RAG CONTEXT
    # ----------------------------------------------

        system_prompt = (
            rag_service.build_agent_system_prompt(
                db=db,
                agent=agent,
                query=request.prompt,
            )
        )

        response = llm_service.generate_response(

            provider=agent.provider,
            prompt=request.prompt,
            model=agent.model,
            temperature=agent.temperature,
            messages=conversation_history,
            system_prompt=system_prompt,
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "LLM service failed for agent %s",
            agent_id
        )

        raise HTTPException(
            status_code=503,
            detail="LLM service is currently unavailable."
        )

    return {
        "agent_id": agent.id,
        "agent_name": agent.name,
        "conversation_id": request.conversation_id,
        "prompt": request.prompt,
        "response": response
    }


@router.post("/agents/{agent_id}/stream")
def stream_agent(
    agent_id: int,
    request: AgentRunRequest,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------
    # FIND AGENT
    # --------------------------------------------------

    agent = agent_service.get_agent_by_id(
        db,
        agent_id,
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    # --------------------------------------------------
    # CHECK PROVIDER + MODEL
    # --------------------------------------------------

    try:
        model_available = llm_service.model_available(
            provider=agent.provider,
            model=agent.model,
        )

    except Exception:
        logger.exception(
            "Unable to check provider model"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                f"Unable to connect to provider "
                f"'{agent.provider}'."
            ),
        )

    if not model_available:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Model '{agent.model}' is not available "
                f"for provider '{agent.provider}'."
            ),
        )

    # --------------------------------------------------
    # LOAD CONVERSATION HISTORY
    # --------------------------------------------------

    conversation_history = []

    if request.conversation_id is not None:
        conversation = (
            conversation_service.get_conversation(
                db,
                request.conversation_id,
            )
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found",
            )

        if conversation.agent_id != agent_id:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Conversation does not belong "
                    "to this agent."
                ),
            )

        stored_messages = (
            conversation_service.get_messages(
                db,
                request.conversation_id,
            )
        )

        conversation_history = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in stored_messages
        ]

    # --------------------------------------------------
    # BUILD SYSTEM PROMPT + RAG CONTEXT
    # --------------------------------------------------

    try:
        system_prompt = (
            rag_service.build_agent_system_prompt(
                db=db,
                agent=agent,
                query=request.prompt,
            )
        )

    except Exception:
        logger.exception(
            "RAG retrieval failed for agent %s",
            agent.id,
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to retrieve knowledge "
                "for this agent."
            ),
        )

    # --------------------------------------------------
    # STREAMING GENERATOR
    # --------------------------------------------------

    def generate():
        try:
            for chunk in llm_service.stream_response(
                provider=agent.provider,
                prompt=request.prompt,
                model=agent.model,
                temperature=agent.temperature,
                messages=conversation_history,
                system_prompt=system_prompt,
            ):
                yield chunk

        except Exception:
            logger.exception(
                "LLM streaming failed for agent %s",
                agent_id,
            )

    # --------------------------------------------------
    # RESPONSE
    # --------------------------------------------------

    return StreamingResponse(
        generate(),
        media_type="text/plain",
    )