import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.config import get_settings
from app.models.db_models import Base

logger = logging.getLogger("lenny.database")
settings = get_settings()

current_db_url = settings.DATABASE_URL
engine = None
async_session_factory = None

def init_engine():
    global engine, async_session_factory, current_db_url
    try:
        engine = create_async_engine(
            current_db_url,
            echo=False,
            future=True,
            pool_pre_ping=True
        )
        async_session_factory = async_sessionmaker(
            engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
    except Exception as e:
        logger.warning(f"Failed to initialize engine for {current_db_url}: {e}. Falling back to SQLite.")
        current_db_url = "sqlite+aiosqlite:///./lenny_assistant.db"
        engine = create_async_engine(current_db_url, echo=False, future=True)
        async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

init_engine()

async def init_db():
    global engine, current_db_url, async_session_factory
    try:
        async with engine.begin() as conn:
            if "postgresql" in current_db_url:
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    logger.info("pgvector extension initialized.")
                except Exception as ext_err:
                    logger.warning(f"Could not enable vector extension: {ext_err}")
            await conn.run_sync(Base.metadata.create_all)
            logger.info(f"Database schema initialized on {current_db_url}")
    except Exception as e:
        logger.warning(f"Database initialization failed on {current_db_url}: {e}. Switching to resilient SQLite fallback.")
        current_db_url = "sqlite+aiosqlite:///./lenny_assistant.db"
        engine = create_async_engine(current_db_url, echo=False, future=True)
        async_session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Resilient SQLite fallback initialized successfully.")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if async_session_factory is None:
        init_engine()
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
