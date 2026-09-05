import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid() -> str:
    return str(uuid.uuid4())

def get_utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    messages = relationship(
        "MessageModel",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="MessageModel.created_at"
    )

class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(32), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True, default=list)
    mode = Column(String(32), default="default")  # 'default', 'ship30'
    provider = Column(String(32), default="ollama")  # 'ollama', 'claude', 'openai'
    created_at = Column(DateTime, default=get_utc_now)

    session = relationship("SessionModel", back_populates="messages")
    artifacts = relationship(
        "ArtifactModel",
        back_populates="message",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class ArtifactModel(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    message_id = Column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    identifier = Column(String(128), nullable=False)
    title = Column(String(255), nullable=False)
    artifact_type = Column(String(32), nullable=False)  # 'markdown' or 'html'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=get_utc_now)

    message = relationship("MessageModel", back_populates="artifacts")

class TranscriptChunkModel(Base):
    __tablename__ = "transcript_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    episode_title = Column(String(255), nullable=False)
    guest_name = Column(String(255), nullable=False)
    publish_date = Column(String(64), nullable=True)
    timestamp_ref = Column(String(64), nullable=True)
    youtube_url = Column(String(255), nullable=True)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=get_utc_now)
