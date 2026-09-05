import os
from typing import List

import httpx


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://host.docker.internal:11434"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-minilm"
)

# Keep each individual embedding request safely below
# all-minilm's 512-token context limit.
WINDOW_SIZE = 700


async def _embed_text(text: str) -> List[float]:
    """Generate one embedding for a short piece of text."""

    url = f"{OLLAMA_BASE_URL}/api/embeddings"

    payload = {
        "model": EMBEDDING_MODEL,
        "prompt": text,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            json=payload,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Ollama embedding failed "
                f"(HTTP {response.status_code}): "
                f"{response.text[:500]}"
            )

        data = response.json()
        embedding = data.get("embedding")

        if not embedding:
            raise RuntimeError(
                "Ollama returned an empty embedding"
            )

        return embedding


async def get_embedding(text: str) -> List[float]:
    """
    Generate a semantic embedding for the complete text.

    Long transcript chunks are divided into smaller windows.
    Each window is embedded separately and the resulting vectors
    are averaged into one final 384-dimensional embedding.
    """

    text = text.strip()

    if not text:
        raise ValueError(
            "Cannot generate an embedding for empty text"
        )

    # Split text into small character windows.
    windows = [
        text[i:i + WINDOW_SIZE]
        for i in range(0, len(text), WINDOW_SIZE)
    ]

    embeddings = []

    for window in windows:
        window = window.strip()

        if window:
            embedding = await _embed_text(window)
            embeddings.append(embedding)

    if not embeddings:
        raise RuntimeError(
            "No embeddings were generated"
        )

    # Average all window embeddings.
    dimension = len(embeddings[0])

    averaged = [
        sum(vector[i] for vector in embeddings) / len(embeddings)
        for i in range(dimension)
    ]

    # Normalize the final vector.
    norm = sum(x * x for x in averaged) ** 0.5

    if norm > 0:
        averaged = [
            x / norm
            for x in averaged
        ]

    return averaged


def cosine_similarity(
    vec1: List[float],
    vec2: List[float],
) -> float:
    """Calculate cosine similarity between two vectors."""

    if not vec1 or not vec2:
        return 0.0

    dot_product = sum(
        a * b for a, b in zip(vec1, vec2)
    )

    norm1 = sum(
        a * a for a in vec1
    ) ** 0.5

    norm2 = sum(
        b * b for b in vec2
    ) ** 0.5

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)