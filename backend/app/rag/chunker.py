import re
import yaml
from typing import List, Dict, Any, Tuple

SPEAKER_TIME_REGEX = re.compile(r"([A-Za-z\s]+ \(\d{2}:\d{2}:\d{2}\):|\(\d{2}:\d{2}:\d{2}\):)")

def parse_transcript_markdown(content: str) -> Tuple[Dict[str, Any], str]:
    """Extracts YAML frontmatter metadata and body from a transcript markdown file."""
    metadata = {
        "guest": "Unknown Guest",
        "title": "Lenny's Podcast Episode",
        "publish_date": "",
        "youtube_url": "",
        "duration": "",
        "keywords": []
    }
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                parsed_yaml = yaml.safe_load(parts[1])
                if isinstance(parsed_yaml, dict):
                    metadata.update({k: v for k, v in parsed_yaml.items() if v is not None})
            except Exception:
                pass
            body = parts[2].strip()

    return metadata, body

def chunk_transcript(
    metadata: Dict[str, Any],
    body: str,
    target_tokens: int = 600,
    overlap_tokens: int = 100
) -> List[Dict[str, Any]]:
    """
    Splits transcript text into semantically cohesive chunks of 500-800 tokens with 100-token overlap.
    Preserves speaker turns and timestamp references.
    """
    # Split by double newlines or speaker turns
    raw_paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    
    chunks: List[Dict[str, Any]] = []
    current_tokens = 0
    current_text_segments: List[str] = []
    current_timestamp = "00:00:00"

    for para in raw_paragraphs:
        # Check for timestamp in paragraph
        time_match = re.search(r"\((\d{2}:\d{2}:\d{2})\)", para)
        if time_match:
            current_timestamp = time_match.group(1)

        words = para.split()
        para_tokens = len(words)

        if current_tokens + para_tokens > target_tokens and current_text_segments:
            chunk_content = "\n\n".join(current_text_segments)
            chunks.append({
                "episode_title": metadata.get("title", "Lenny's Podcast Episode"),
                "guest_name": metadata.get("guest", "Unknown Guest"),
                "publish_date": str(metadata.get("publish_date", "")),
                "timestamp_ref": current_timestamp,
                "youtube_url": metadata.get("youtube_url", ""),
                "chunk_text": chunk_content
            })

            # Retain overlap from end of current_text_segments
            overlap_words = " ".join(chunk_content.split()[-overlap_tokens:]) if overlap_tokens > 0 else ""
            current_text_segments = [overlap_words] if overlap_words else []
            current_tokens = len(current_text_segments[0].split()) if current_text_segments else 0

        current_text_segments.append(para)
        current_tokens += para_tokens

    if current_text_segments:
        chunk_content = "\n\n".join(current_text_segments)
        chunks.append({
            "episode_title": metadata.get("title", "Lenny's Podcast Episode"),
            "guest_name": metadata.get("guest", "Unknown Guest"),
            "publish_date": str(metadata.get("publish_date", "")),
            "timestamp_ref": current_timestamp,
            "youtube_url": metadata.get("youtube_url", ""),
            "chunk_text": chunk_content
        })

    return chunks
