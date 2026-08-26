from pydantic import BaseModel, Field, field_validator


class AgentCreate(BaseModel):
    name: str
    provider: str = "ollama"
    model: str
    temperature: float = Field(
        default=0.7,
        ge=0,
        le=2,
    )
    system_prompt: str = ""
    knowledge_base_id: int | None = None


class AgentResponse(BaseModel):
    id: int
    name: str
    provider: str
    model: str
    temperature: float
    system_prompt: str

    class Config:
        from_attributes = True
    knowledge_base_id: int | None = None


class AgentRunRequest(BaseModel):
    prompt: str = Field(
        min_length=1
    )

    conversation_id: int | None = None

    @field_validator("prompt")
    @classmethod
    def validate_prompt(
        cls,
        value: str
    ) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Prompt cannot be empty or whitespace"
            )

        return value
    knowledge_base_id: int | None = None