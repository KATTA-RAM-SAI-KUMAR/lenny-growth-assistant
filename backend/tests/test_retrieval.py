import pytest
from app.rag.embeddings import compute_deterministic_embedding, cosine_similarity
from app.rag.chunker import parse_transcript_markdown, chunk_transcript

def test_embedding_dimensions_and_normalization():
    text = "Brian Chesky discusses founder mode and single company roadmap at Airbnb."
    vec = compute_deterministic_embedding(text)
    assert len(vec) == 384
    import numpy as np
    norm = np.linalg.norm(vec)
    assert 0.99 <= norm <= 1.01

def test_cosine_similarity_identical_and_orthogonal():
    vec1 = compute_deterministic_embedding("Product-led growth and freemium loops")
    vec2 = compute_deterministic_embedding("Product-led growth and freemium loops")
    assert pytest.approx(cosine_similarity(vec1, vec2), rel=1e-3) == 1.0

    # Query with identical terms should have positive similarity
    query_vec = compute_deterministic_embedding("freemium loops in PLG")
    score = cosine_similarity(vec1, query_vec)
    assert score > 0.2

def test_chunker_metadata_extraction():
    sample_md = """---
guest: Brian Chesky
title: Brian Chesky’s new playbook
publish_date: 2023-11-12
---

Brian Chesky (00:00:00):
Leaders must be in the details. Micromanagement is telling people what to do.
"""
    metadata, body = parse_transcript_markdown(sample_md)
    assert metadata["guest"] == "Brian Chesky"
    assert metadata["title"] == "Brian Chesky’s new playbook"
    assert "Leaders must be in the details" in body

def test_chunker_chunk_generation():
    metadata = {"guest": "Sean Ellis", "title": "Growth Hacking"}
    body = "Sean Ellis (00:01:00):\nThe North Star Metric aligns the entire company around value.\n\n" * 15
    chunks = chunk_transcript(metadata, body, target_tokens=100, overlap_tokens=20)
    assert len(chunks) >= 2
    assert chunks[0]["guest_name"] == "Sean Ellis"
    assert chunks[0]["episode_title"] == "Growth Hacking"
    assert "North Star Metric" in chunks[0]["chunk_text"]
