from datetime import datetime, timezone
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field

class SourceCitation(BaseModel):
    episode: str
    guest: str
    timestamp: Optional[str] = None
    youtube_url: Optional[str] = None
    score: float
    text: str

class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    message_id: str
    identifier: str
    title: str
    artifact_type: str
    content: str
    created_at: datetime

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    role: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = None
    mode: str = "default"
    provider: str = "ollama"
    created_at: datetime
    artifacts: Optional[List[ArtifactResponse]] = Field(default_factory=list)

class SessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class SessionUpdate(BaseModel):
    title: str

class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageResponse]] = Field(default_factory=list)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    mode: Optional[str] = "default"  # 'default' or 'ship30'
    provider: Optional[str] = "ollama"  # 'ollama', 'claude', 'openai'

class HealthDatabase(BaseModel):
    connected: bool
    dialect: str
    pgvector_ready: bool

class HealthOllama(BaseModel):
    available: bool
    url: str
    model: str
    models_available: List[str] = []

class HealthCloud(BaseModel):
    anthropic_configured: bool
    openai_configured: bool

class HealthRetrieval(BaseModel):
    total_indexed_chunks: int
    similarity_threshold: float
    top_k: int

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database: HealthDatabase
    ollama: HealthOllama
    cloud: HealthCloud
    retrieval: HealthRetrieval
