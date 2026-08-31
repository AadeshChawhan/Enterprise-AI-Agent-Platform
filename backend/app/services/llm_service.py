from backend.app.providers.registry import (
    get_provider,
)


# ==================================================
# RESPONSE CLEANING
# ==================================================

THINK_OPEN_TAG = "<think>"
THINK_CLOSE_TAG = "</think>"


def remove_thinking_content(
    text: str,
) -> str:
    """
    Remove <think>...</think> reasoning blocks from
    a complete model response.

    Some reasoning models, such as certain Qwen
    models, may return internal reasoning inside
    <think> tags.

    The application should expose only the final
    answer to the user.
    """

    if not text:
        return text

    cleaned = text

    while True:
        lower_text = cleaned.lower()

        start_index = lower_text.find(
            THINK_OPEN_TAG
        )

        if start_index == -1:
            break

        end_index = lower_text.find(
            THINK_CLOSE_TAG,
            start_index
            + len(THINK_OPEN_TAG),
        )

        # If the model opened a <think> block
        # but never closed it, remove everything
        # from the opening tag onward.
        if end_index == -1:
            cleaned = cleaned[
                :start_index
            ]
            break

        cleaned = (
            cleaned[:start_index]
            + cleaned[
                end_index
                + len(THINK_CLOSE_TAG):
            ]
        )

    return cleaned.strip()


# ==================================================
# STREAM CLEANING
# ==================================================

def filter_thinking_stream(
    chunks,
):
    """
    Filter <think>...</think> blocks from a streamed
    provider response while preserving real-time
    streaming of the final answer.

    Handles tags even if they are split across
    multiple streaming chunks.
    """

    buffer = ""
    inside_thinking = False

    open_tag = THINK_OPEN_TAG
    close_tag = THINK_CLOSE_TAG

    for chunk in chunks:

        if chunk is None:
            continue

        if not isinstance(chunk, str):
            chunk = str(chunk)

        buffer += chunk

        while buffer:

            lower_buffer = buffer.lower()

            # ------------------------------------------
            # CURRENTLY INSIDE <think>...</think>
            # ------------------------------------------

            if inside_thinking:

                close_index = (
                    lower_buffer.find(
                        close_tag
                    )
                )

                if close_index != -1:

                    buffer = buffer[
                        close_index
                        + len(close_tag):
                    ]

                    inside_thinking = False

                    continue

                # Keep only enough characters to detect
                # a closing tag split between chunks.
                keep_length = (
                    len(close_tag) - 1
                )

                if len(buffer) > keep_length:
                    buffer = buffer[
                        -keep_length:
                    ]

                break

            # ------------------------------------------
            # CURRENTLY OUTSIDE THINKING BLOCK
            # ------------------------------------------

            open_index = (
                lower_buffer.find(
                    open_tag
                )
            )

            if open_index != -1:

                visible_text = buffer[
                    :open_index
                ]

                if visible_text:
                    yield visible_text

                buffer = buffer[
                    open_index
                    + len(open_tag):
                ]

                inside_thinking = True

                continue

            # ------------------------------------------
            # NO COMPLETE OPENING TAG FOUND
            # ------------------------------------------

            # Keep a small suffix so we can detect
            # "<think>" if the tag is split across
            # two streaming chunks.
            keep_length = (
                len(open_tag) - 1
            )

            safe_length = (
                len(buffer)
                - keep_length
            )

            if safe_length > 0:

                visible_text = buffer[
                    :safe_length
                ]

                if visible_text:
                    yield visible_text

                buffer = buffer[
                    safe_length:
                ]

            break

    # ==================================================
    # STREAM FINISHED
    # ==================================================

    # Only expose remaining text if we are NOT
    # inside an unfinished thinking block.
    if (
        not inside_thinking
        and buffer
    ):
        yield buffer


# ==================================================
# MODEL AVAILABILITY
# ==================================================

def model_available(
    provider: str,
    model: str,
) -> bool:

    provider_instance = (
        get_provider(provider)
    )

    return (
        provider_instance.model_available(
            model
        )
    )


# ==================================================
# NORMAL RESPONSE
# ==================================================

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

    response = (
        provider_instance.generate_response(
            prompt=prompt,
            model=model,
            temperature=temperature,
            messages=messages,
            system_prompt=system_prompt,
        )
    )

    return remove_thinking_content(
        response
    )


# ==================================================
# STREAM RESPONSE
# ==================================================

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

    provider_stream = (
        provider_instance.stream_response(
            prompt=prompt,
            model=model,
            temperature=temperature,
            messages=messages,
            system_prompt=system_prompt,
        )
    )

    yield from filter_thinking_stream(
        provider_stream
    )


# ==================================================
# CONVERSATION TITLE
# ==================================================

def generate_conversation_title(
    provider: str,
    prompt: str,
    model: str,
) -> str:

    provider_instance = (
        get_provider(provider)
    )

    title = (
        provider_instance
        .generate_conversation_title(
            prompt=prompt,
            model=model,
        )
    )

    title = remove_thinking_content(
        title
    )

    # Extra safety for conversation titles.
    # Titles should always be one line.
    title = " ".join(
        title.split()
    )

    return title