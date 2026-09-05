import logging
import json
from typing import List, Dict, Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from app.models.db_models import TranscriptChunkModel
from app.rag.embeddings import cosine_similarity, get_embedding

logger = logging.getLogger("lenny.retriever")


class TranscriptRetriever:
    def __init__(
        self,
        session: AsyncSession,
        embedding_fn: Callable = get_embedding,
    ):
        self.session = session
        self.embedding_fn = embedding_fn

    async def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.60,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant transcript chunks using cosine similarity.

        PostgreSQL uses pgvector when available. If native pgvector search
        fails, the transaction is rolled back and we fall back to Python
        cosine similarity.
        """

        query_vector = await self.embedding_fn(query)

        bind = self.session.bind
        dialect_name = bind.dialect.name if bind else "postgresql"

        # Native pgvector search for PostgreSQL
        if dialect_name == "postgresql":
            try:
                query_stmt = text(
                    """
                    SELECT
                        episode_title,
                        guest_name,
                        chunk_text,
                        timestamp_ref,
                        youtube_url,
                        1 - (embedding <=> CAST(:vector AS vector))
                            AS similarity_score
                    FROM transcript_chunks
                    WHERE 1 - (embedding <=> CAST(:vector AS vector))
                        >= :threshold
                    ORDER BY similarity_score DESC
                    LIMIT :limit
                    """
                )

                result = await self.session.execute(
                    query_stmt,
                    {
                        "vector": str(query_vector),
                        "threshold": similarity_threshold,
                        "limit": top_k,
                    },
                )

                rows = result.fetchall()

                return [
                    {
                        "episode": row.episode_title,
                        "guest": row.guest_name,
                        "text": row.chunk_text,
                        "timestamp": row.timestamp_ref,
                        "youtube_url": row.youtube_url,
                        "score": round(float(row.similarity_score), 4),
                    }
                    for row in rows
                ]

            except Exception as pg_err:
                # PostgreSQL marks the transaction as failed after an error.
                # Roll it back before attempting another query.
                await self.session.rollback()

                logger.warning(
                    "Native pgvector search failed; "
                    "falling back to Python cosine similarity: %s",
                    pg_err,
                )

        # Python fallback search
        stmt = select(TranscriptChunkModel)
        result = await self.session.execute(stmt)
        all_chunks = result.scalars().all()

        if not all_chunks:
            return []

        scored_chunks = []

        for chunk in all_chunks:
            chunk_vec = chunk.embedding

            if isinstance(chunk_vec, str):
                try:
                    chunk_vec = json.loads(chunk_vec)
                except Exception:
                    continue

            try:
                score = cosine_similarity(query_vector, chunk_vec)
            except Exception:
                continue

            if score >= similarity_threshold:
                scored_chunks.append(
                    {
                        "episode": chunk.episode_title,
                        "guest": chunk.guest_name,
                        "text": chunk.chunk_text,
                        "timestamp": chunk.timestamp_ref,
                        "youtube_url": chunk.youtube_url,
                        "score": round(float(score), 4),
                    }
                )

        scored_chunks.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return scored_chunks[:top_k]