import datetime
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, select

from app.database import get_db, engine
from app.models.db_models import TranscriptChunkModel
from app.models.schemas import (
    HealthResponse,
    HealthDatabase,
    HealthOllama,
    HealthCloud,
    HealthRetrieval,
)
from app.providers.ollama_provider import OllamaProvider
from app.config import get_settings

logger = logging.getLogger("lenny.api.health")
settings = get_settings()
router = APIRouter(prefix="/api/health", tags=["Health"])

@router.get("", response_model=HealthResponse)
async def check_system_health(db: AsyncSession = Depends(get_db)):
    # 1. Check Database
    db_connected = False
    dialect_name = "unknown"
    pgvector_ready = False

    try:
        bind = db.bind
        dialect_name = bind.dialect.name if bind else "unknown"
        res = await db.execute(text("SELECT 1;"))
        if res.scalar() == 1:
            db_connected = True

        if dialect_name == "postgresql":
            ext_res = await db.execute(
                text("SELECT count(*) FROM pg_extension WHERE extname = 'vector';")
            )
            pgvector_ready = bool(ext_res.scalar() > 0)
        else:
            pgvector_ready = True
    except Exception as e:
        logger.warning(f"Database health check warning: {e}")

    # 2. Check Ollama
    ollama_prov = OllamaProvider(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
    ollama_available = await ollama_prov.check_health()
    ollama_models = await ollama_prov.get_available_models() if ollama_available else []

    # 3. Check Cloud Providers
    anthropic_ok = bool(settings.ANTHROPIC_API_KEY and len(settings.ANTHROPIC_API_KEY) > 10)
    openai_ok = bool(settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY) > 10)

    # 4. Check Retrieval Chunks Count
    chunk_count = 0
    try:
        count_res = await db.execute(select(func.count(TranscriptChunkModel.id)))
        chunk_count = count_res.scalar() or 0
    except Exception as e:
        logger.warning(f"Chunk count check warning: {e}")

    overall_status = "healthy" if db_connected else "degraded"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        database=HealthDatabase(
            connected=db_connected,
            dialect=dialect_name,
            pgvector_ready=pgvector_ready
        ),
        ollama=HealthOllama(
            available=ollama_available,
            url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            models_available=ollama_models
        ),
        cloud=HealthCloud(
            anthropic_configured=anthropic_ok,
            openai_configured=openai_ok
        ),
        retrieval=HealthRetrieval(
            total_indexed_chunks=chunk_count,
            similarity_threshold=settings.SIMILARITY_THRESHOLD,
            top_k=settings.TOP_K_RETRIEVAL
        )
    )
