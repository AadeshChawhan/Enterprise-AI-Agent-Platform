from functools import lru_cache

from fastembed import TextEmbedding


EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIMENSION = 384


@lru_cache(maxsize=1)
def get_embedding_model():
    return TextEmbedding(
        model_name=EMBEDDING_MODEL
    )


def generate_embedding(
    text: str,
) -> list[float]:
    cleaned_text = text.strip()

    if not cleaned_text:
        raise ValueError(
            "Cannot generate embedding for empty text"
        )

    model = get_embedding_model()

    embeddings = list(
        model.embed([cleaned_text])
    )

    if not embeddings:
        raise RuntimeError(
            "Embedding model returned no embedding"
        )

    return embeddings[0].tolist()


def generate_embeddings(
    texts: list[str],
) -> list[list[float]]:
    cleaned_texts = [
        text.strip()
        for text in texts
        if text.strip()
    ]

    if not cleaned_texts:
        return []

    model = get_embedding_model()

    return [
        embedding.tolist()
        for embedding in model.embed(
            cleaned_texts
        )
    ]
