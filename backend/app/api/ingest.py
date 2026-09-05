import logging
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.database import get_db
from app.models.db_models import TranscriptChunkModel
from app.rag.chunker import parse_transcript_markdown, chunk_transcript
from app.rag.embeddings import get_embedding

logger = logging.getLogger("lenny.api.ingest")
router = APIRouter(prefix="/api/ingest", tags=["Ingestion"])

TRANSCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "transcripts"
)


async def run_ingestion(db: AsyncSession):
    """Parses all transcripts and indexes their embeddings."""
    if not TRANSCRIPTS_DIR.exists():
        logger.warning(f"Directory {TRANSCRIPTS_DIR} does not exist.")
        return 0

    # Clear existing chunks
    await db.execute(delete(TranscriptChunkModel))
    await db.commit()

    total_chunks = 0

    files = list(TRANSCRIPTS_DIR.glob("*.md"))

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8")

            metadata, body = parse_transcript_markdown(content)
            chunks = chunk_transcript(metadata, body)

            for c in chunks:
                # Generate semantic embedding using Ollama all-minilm
                vec = await get_embedding(c["chunk_text"])

                chunk_record = TranscriptChunkModel(
                    episode_title=c["episode_title"],
                    guest_name=c["guest_name"],
                    publish_date=c["publish_date"],
                    timestamp_ref=c["timestamp_ref"],
                    youtube_url=c["youtube_url"],
                    chunk_text=c["chunk_text"],
                    embedding=vec,
                )

                db.add(chunk_record)
                total_chunks += 1

            await db.commit()

            logger.info(
                f"Ingested {len(chunks)} chunks from {file_path.name}"
            )

        except Exception as e:
            logger.error(
                f"Failed to ingest {file_path.name}: {e}"
            )

    return total_chunks


@router.post("")
async def trigger_ingestion(
    db: AsyncSession = Depends(get_db),
):
    count = await run_ingestion(db)

    return {
        "status": "success",
        "indexed_chunks": count,
    }


@router.get("/status")
async def get_ingestion_status(
    db: AsyncSession = Depends(get_db),
):
    count_res = await db.execute(
        select(func.count(TranscriptChunkModel.id))
    )

    count = count_res.scalar() or 0

    files_count = (
        len(list(TRANSCRIPTS_DIR.glob("*.md")))
        if TRANSCRIPTS_DIR.exists()
        else 0
    )

    return {
        "status": "ready",
        "transcript_files": files_count,
        "indexed_chunks": count,
    }