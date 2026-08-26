from backend.app.providers.ollama_provider import (
    OllamaProvider,
)
from backend.app.providers.groq_provider import (
    GroqProvider,
)

def list_providers():
    return list(providers.keys())


providers = {
    "ollama": OllamaProvider(),
    "groq": GroqProvider(),
}


def get_provider(
    provider_name: str
):
    normalized_name = (
        provider_name
        .strip()
        .lower()
    )

    provider = providers.get(
        normalized_name
    )

    if provider is None:
        raise ValueError(
            f"Unsupported provider: {provider_name}"
        )

    return provider