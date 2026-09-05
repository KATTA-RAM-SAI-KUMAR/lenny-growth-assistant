from typing import List, Dict, Any


SHIP_30_PROMPT_TEMPLATE = """You are an expert executive ghostwriter trained in the Ship 30 for 30 methodology by Nicolas Cole & Dickie Bush.

Your task is to transform ONLY the provided Lenny's Podcast transcript evidence into a high-impact, high-retention essay for product leaders.

### STRICT GROUNDING RULES

1. Use ONLY the transcript evidence provided in the Context Material.
2. Every factual claim, insight, metric, example, or recommendation derived from the transcripts MUST include a citation such as [S1], [S2].
3. Use ONLY the source IDs provided in the Context Material.
4. Explicitly attribute ideas to the relevant guest.
5. Never invent facts, quotes, metrics, examples, guests, companies, or recommendations.
6. Do not use general knowledge to fill gaps.
7. If the evidence is insufficient, do not create the essay. Respond exactly:
   "I do not have sufficient information in Lenny's podcast archive to create this essay."

### Core Ship 30 for 30 Heuristics

1. **The Hook**
   - The first 2-3 lines must immediately create tension, curiosity, or a counterintuitive product insight.
   - Avoid generic introductions.

2. **Formatting & High Skimmability**
   - Use short paragraphs of 1-3 sentences.
   - Use descriptive Markdown headings (`##` and `###`).
   - Use bullet points where useful.
   - Start important bullets with bold anchor words.

3. **Substance & Grounded Attribution**
   - Ground every core insight in the provided transcript evidence.
   - Clearly attribute ideas to the respective guests.
   - Use citations such as [S1] and [S2] immediately after supported claims.

4. **Target Depth**
   - Aim for approximately 1,000-1,250 words.
   - Prioritize high-signal operational insights over filler.

5. **The Takeaway**
   - Conclude with a numbered 5-step operational checklist that a VP of Product or Founder can implement tomorrow.
   - Every transcript-derived recommendation must remain grounded in the evidence.

6. **Artifact Encapsulation**
   - Wrap the complete essay inside an `<artifact>` container exactly like this:

<artifact identifier="ship30-essay" type="markdown" title="Ship 30 for 30: [Descriptive Title]">
[Full Essay Markdown Content]
</artifact>

### Context Material from Lenny's Podcast

{context_material}

### User Prompt

{user_query}
"""


def build_ship30_prompt(
    user_query: str,
    retrieved_chunks: List[Dict[str, Any]]
) -> str:

    if not retrieved_chunks:
        return SHIP_30_PROMPT_TEMPLATE.format(
            context_material=(
                "No relevant transcript chunks were retrieved. "
                "[INSUFFICIENT_CONTEXT_REFUSAL]"
            ),
            user_query=user_query,
        )

    formatted_chunks = []

    for index, chunk in enumerate(retrieved_chunks, start=1):
        episode = (
            chunk.get("episode_title")
            or chunk.get("episode")
            or "Lenny's Podcast"
        )

        guest = (
            chunk.get("guest_name")
            or chunk.get("guest")
            or "Unknown"
        )

        timestamp = (
            chunk.get("timestamp_ref")
            or chunk.get("timestamp")
            or "Transcript section"
        )

        text = (
            chunk.get("chunk_text")
            or chunk.get("text")
            or ""
        )

        formatted_chunks.append(
            f"[S{index}]\n"
            f"Episode: {episode}\n"
            f"Guest: {guest}\n"
            f"Timestamp/Topic: {timestamp}\n"
            f"Transcript Evidence:\n{text}"
        )

    formatted_context = "\n\n".join(formatted_chunks)

    return SHIP_30_PROMPT_TEMPLATE.format(
        context_material=formatted_context,
        user_query=user_query,
    )