#!/usr/bin/env python3
"""
Transcript Ingestion CLI Script
Usage: python backend/scripts/ingest.py
"""

import sys
import asyncio
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import init_db, async_session_factory
from app.api.ingest import run_ingestion

async def main():
    print("=" * 60)
    print("Ingesting transcripts into The Lenny Growth Assistant DB...")
    print("=" * 60)
    await init_db()
    async with async_session_factory() as session:
        count = await run_ingestion(session)
        print(f"\n[SUCCESS] Ingested and indexed {count} chunks.")

if __name__ == "__main__":
    asyncio.run(main())
