import json
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.db_models import SessionModel, MessageModel, ArtifactModel
from app.models.schemas import ChatRequest
from app.rag.retriever import TranscriptRetriever
from app.providers.factory import get_llm_provider
from app.skills.grounded_chat import build_grounded_system_prompt
from app.skills.ship30_writer import build_ship30_prompt
from app.skills.artifact_generator import extract_artifacts
from app.config import get_settings

logger = logging.getLogger("lenny.api.chat")
settings = get_settings()
router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("")
async def stream_chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    # 1. Verify session exists or create one
    stmt = select(SessionModel).where(SessionModel.id == req.session_id).options(
        selectinload(SessionModel.messages)
    )
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        session = SessionModel(id=req.session_id, title=req.message[:40] + ("..." if len(req.message) > 40 else ""))
        db.add(session)
        await db.commit()
        await db.refresh(session)
    elif session.title == "New Conversation" or not session.title:
        session.title = req.message[:40] + ("..." if len(req.message) > 40 else "")
        await db.commit()

    # 2. Save user message to database
    user_msg = MessageModel(
        session_id=req.session_id,
        role="user",
        content=req.message,
        mode=req.mode or "default",
        provider=req.provider or "ollama"
    )
    db.add(user_msg)
    await db.commit()

    # Build conversation history
    history = []
    if session.messages:
        for m in session.messages[-8:]:
            history.append({"role": m.role, "content": m.content})
    history.append({"role": "user", "content": req.message})

    # 3. Retrieve relevant chunks
    retriever = TranscriptRetriever(session=db)
    chunks = await retriever.retrieve_relevant_chunks(
        query=req.message,
        top_k=settings.TOP_K_RETRIEVAL,
        similarity_threshold=settings.SIMILARITY_THRESHOLD
    )

    # 4. Determine system prompt and skill template
    if req.mode == "ship30":
        system_prompt = build_ship30_prompt(req.message, chunks)
    else:
        system_prompt = build_grounded_system_prompt(chunks)

    # 5. Resolve LLM provider
    provider = get_llm_provider(req.provider)

    async def sse_event_generator():
        # Step A: Status notification
        yield f"data: {json.dumps({'type': 'status', 'content': 'Searching 260+ transcripts in Lenny archive...'})}\n\n"

        # Step B: Emit retrieved sources
        clean_sources = [
            {
                "episode": c["episode"],
                "guest": c["guest"],
                "timestamp": c.get("timestamp", "00:00:00"),
                "youtube_url": c.get("youtube_url"),
                "score": c["score"],
                "text": c["text"][:300] + "..." if len(c["text"]) > 300 else c["text"]
            }
            for c in chunks
        ]
        yield f"data: {json.dumps({'type': 'sources', 'content': clean_sources})}\n\n"
	        # Do not generate an answer when retrieval found no evidence.
        # This prevents the LLM from answering from general knowledge.
        if not chunks:
            refusal = (
                "I couldn't find enough relevant information in Lenny's "
                "podcast transcripts to answer that question. "
                "Please try a more specific question about a guest, episode, "
                "or topic covered in the archive."
            )

            yield f"data: {json.dumps({'type': 'status', 'content': 'No relevant transcript evidence found.'})}\n\n"
            yield f"data: {json.dumps({'type': 'token', 'content': refusal})}\n\n"

            try:
                assistant_msg = MessageModel(
                    session_id=req.session_id,
                    role="assistant",
                    content=refusal,
                    sources=[],
                    mode=req.mode or "default",
                    provider=req.provider or "ollama"
                )
                db.add(assistant_msg)
                await db.commit()
            except Exception as persist_err:
                logger.error(f"Failed to persist refusal message: {persist_err}")

            yield "data: [DONE]\n\n"
            return


        # Step C: Stream LLM tokens
        yield f"data: {json.dumps({'type': 'status', 'content': f'Generating grounded answer via {req.provider.upper()}...'})}\n\n"

        full_response_text = ""
        try:
            async for token in provider.generate_response(
                messages=history,
                system_prompt=system_prompt,
                temperature=0.3
            ):
                full_response_text += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
        except Exception as gen_err:
            logger.error(f"Error during token generation: {gen_err}")
            yield f"data: {json.dumps({'type': 'token', 'content': f' [Error: {str(gen_err)}]'})}\n\n"

        # Step D: Extract artifacts
        detected_artifacts = extract_artifacts(full_response_text)
        for art in detected_artifacts:
            yield f"data: {json.dumps({'type': 'artifact', 'identifier': art['identifier'], 'title': art['title'], 'artifact_type': art['artifact_type'], 'content': art['content']})}\n\n"

        # Step E: Persist Assistant Message and Artifacts to Database
        try:
            assistant_msg = MessageModel(
                session_id=req.session_id,
                role="assistant",
                content=full_response_text,
                sources=clean_sources,
                mode=req.mode or "default",
                provider=req.provider or "ollama"
            )
            db.add(assistant_msg)
            await db.commit()
            await db.refresh(assistant_msg)

            for art in detected_artifacts:
                art_model = ArtifactModel(
                    message_id=assistant_msg.id,
                    identifier=art["identifier"],
                    title=art["title"],
                    artifact_type=art["artifact_type"],
                    content=art["content"]
                )
                db.add(art_model)
            await db.commit()
        except Exception as persist_err:
            logger.error(f"Failed to persist assistant message: {persist_err}")

        # Finish stream
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
