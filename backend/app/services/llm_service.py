from backend.app.providers.registry import (
    get_provider,
)


def model_available(
    provider: str,
    model: str,
) -> bool:
    provider_instance = (
        get_provider(provider)
    )

    return provider_instance.model_available(
        model
    )


def generate_response(
    provider: str,
    prompt: str,
    model: str,
    temperature: float,
    messages: list | None = None,
    system_prompt: str = "",
):
    provider_instance = (
        get_provider(provider)
    )

    return provider_instance.generate_response(
        prompt=prompt,
        model=model,
        temperature=temperature,
        messages=messages,
        system_prompt=system_prompt,
    )


def stream_response(
    provider: str,
    prompt: str,
    model: str,
    temperature: float,
    messages: list | None = None,
    system_prompt: str = "",
):
    provider_instance = (
        get_provider(provider)
    )

    yield from provider_instance.stream_response(
        prompt=prompt,
        model=model,
        temperature=temperature,
        messages=messages,
        system_prompt=system_prompt,
    )


def generate_conversation_title(
    provider: str,
    prompt: str,
    model: str,
) -> str:
    provider_instance = (
        get_provider(provider)
    )

    return (
        provider_instance
        .generate_conversation_title(
            prompt=prompt,
            model=model,
        )
    )