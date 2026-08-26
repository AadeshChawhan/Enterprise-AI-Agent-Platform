from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.agents import router as agents_router
from backend.app.api.conversations import (
    router as conversations_router,
)
from backend.app.providers.registry import get_provider, list_providers
from backend.app.api.knowledge_bases import (
    router as knowledge_bases_router,
)


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": (
            "Welcome to Enterprise AI Agent Platform 🚀"
        )
    }


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health")
def health():
    provider_status = {
        "ollama": False,
        "groq": False,
    }

    provider_models = {
        "ollama": [],
        "groq": [],
    }

    # --------------------------------------------------
    # OLLAMA
    # --------------------------------------------------

    try:
        ollama = get_provider("ollama")

        provider_models["ollama"] = (
            ollama.list_models()
        )

        provider_status["ollama"] = True

    except Exception as e:
        print(
            f"Ollama health check failed: {e}"
        )

    # --------------------------------------------------
    # GROQ
    # --------------------------------------------------

    try:
        groq = get_provider("groq")

        provider_models["groq"] = (
            groq.list_models()
        )

        provider_status["groq"] = True

    except Exception as e:
        print(
            f"Groq health check failed: {e}"
        )

    return {
        "status": "healthy",
        "server": "running",

        # Keep this for your existing frontend compatibility.
        "ollama": provider_status["ollama"],

        "providers": provider_status,

        "models": provider_models,
    }


# --------------------------------------------------
# MODELS
# --------------------------------------------------

@app.get("/models")
def get_models(
    provider: str = "ollama",
):
    try:
        provider_instance = get_provider(
            provider
        )

        models = provider_instance.list_models()

        return [
            {
                "id": model,
                "provider": provider,
            }
            for model in models
        ]

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Unable to load models for "
                f"provider '{provider}': {str(e)}"
            ),
        )


# --------------------------------------------------
# ROUTERS
# --------------------------------------------------

app.include_router(agents_router)
app.include_router(conversations_router)
app.include_router(knowledge_bases_router)
@app.get("/providers")
def get_providers():
    provider_ids = list_providers()

    provider_metadata = {
        "ollama": {
            "name": "Ollama",
            "type": "local",
            "supports_streaming": True,
            "supports_system_prompt": True,
        },
        "groq": {
            "name": "Groq",
            "type": "cloud",
            "supports_streaming": True,
            "supports_system_prompt": True,
        },
    }

    return [
        {
            "id": provider_id,
            **provider_metadata.get(
                provider_id,
                {
                    "name": provider_id.capitalize(),
                    "type": "cloud",
                    "supports_streaming": True,
                    "supports_system_prompt": True,
                },
            ),
        }
        for provider_id in provider_ids
    ]

