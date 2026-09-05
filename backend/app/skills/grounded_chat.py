from typing import List, Dict, Any


GROUNDED_SYSTEM_PROMPT = """You are "The Lenny Growth Assistant", an AI advisor trained exclusively on Lenny's Podcast transcripts.

### STRICT GROUNDING RULES

1. Answer ONLY using the transcript evidence provided below.
2. Every factual claim MUST have a citation such as [S1], [S2], etc.
3. Use ONLY the source IDs that appear in the Context Material.
4. If multiple sources support a claim, cite them together, for example [S1][S2].
5. Never invent facts, metrics, quotes, guests, companies, episodes, or recommendations that are not supported by the provided transcripts.
6. Do not use general knowledge to fill missing information.
7. If the provided evidence does not contain enough information to answer the question, respond exactly:
   "I do not have sufficient information in Lenny's podcast archive to answer this."

### RESPONSE STYLE

- Professional and concise.
- Tactical and useful.
- Easy to scan.
- Prefer short paragraphs and bullet points when appropriate.
- Do not unnecessarily repeat the user's question.

### CONTEXT MATERIAL FROM LENNY'S PODCAST ARCHIVE

{context_material}
"""


def build_grounded_system_prompt(
    retrieved_chunks: List[Dict[str, Any]]
) -> str:

    if not retrieved_chunks:
        return GROUNDED_SYSTEM_PROMPT.format(
            context_material=(
                "NO RELEVANT TRANSCRIPT EVIDENCE WAS FOUND. "
                "You must use the required knowledge-gap response."
            )
        )

    formatted_chunks = []

    for i, c in enumerate(retrieved_chunks, 1):
        episode_title = (
            c.get("episode_title")
            or c.get("episode")
            or "Lenny's Podcast"
        )

        guest_name = (
            c.get("guest_name")
            or c.get("guest")
            or "Unknown"
        )

        timestamp = (
            c.get("timestamp_ref")
            or c.get("timestamp")
            or "Transcript section"
        )

        chunk_text = (
            c.get("chunk_text")
            or c.get("text")
            or ""
        )

        formatted_chunks.append(
            f"[S{i}]\n"
            f"Episode: {episode_title}\n"
            f"Guest: {guest_name}\n"
            f"Timestamp/Topic: {timestamp}\n"
            f"Transcript Evidence:\n{chunk_text}"
        )

    context_material = "\n\n".join(formatted_chunks)

    return GROUNDED_SYSTEM_PROMPT.format(
        context_material=context_material
    )