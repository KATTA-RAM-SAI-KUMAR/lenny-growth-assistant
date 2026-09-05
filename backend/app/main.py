import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import init_db, async_session_factory
from app.api.sessions import router as sessions_router
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.ingest import router as ingest_router, run_ingestion

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("lenny.main")
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting The Lenny Growth Assistant Backend...")
    await init_db()
    # Auto-seed knowledge base if empty
    try:
        async with async_session_factory() as session:
            from sqlalchemy import select, func
            from app.models.db_models import TranscriptChunkModel
            res = await session.execute(select(func.count(TranscriptChunkModel.id)))
            count = res.scalar() or 0
            if count == 0:
                logger.info("Knowledge base is empty. Running automatic initial transcript ingestion...")
                num_chunks = await run_ingestion(session)
                logger.info(f"Initial ingestion complete: {num_chunks} chunks indexed.")
            else:
                logger.info(f"Knowledge base ready with {count} indexed transcript chunks.")
    except Exception as e:
        logger.warning(f"Initial auto-ingestion check: {e}")
    yield
    logger.info("Shutting down The Lenny Growth Assistant Backend...")

app = FastAPI(
    title="The Lenny Growth Assistant API",
    description="Enterprise-grade RAG and Ship 30 for 30 Content Engine for Lenny's Podcast transcripts",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "error": str(exc)}
    )

# Register API routers
app.include_router(health_router)
app.include_router(sessions_router)
app.include_router(chat_router)
app.include_router(ingest_router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs_url": "/docs",
        "health_url": "/api/health"
    }
