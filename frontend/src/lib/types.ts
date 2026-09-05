export type LLMProvider = 'ollama' | 'claude' | 'openai';
export type ChatMode = 'default' | 'ship30';

export interface SourceCitation {
  episode: string;
  guest: string;
  timestamp?: string;
  youtube_url?: string;
  score: number;
  text: string;
}

export interface Artifact {
  id?: string;
  message_id?: string;
  identifier: string;
  title: string;
  artifact_type: 'markdown' | 'html';
  content: string;
  created_at?: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: SourceCitation[];
  mode: ChatMode;
  provider: LLMProvider;
  created_at: string;
  artifacts?: Artifact[];
}

export interface Session {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  database: {
    connected: boolean;
    dialect: string;
    pgvector_ready: boolean;
  };
  ollama: {
    available: boolean;
    url: string;
    model: string;
    models_available: string[];
  };
  cloud: {
    anthropic_configured: boolean;
    openai_configured: boolean;
  };
  retrieval: {
    total_indexed_chunks: number;
    similarity_threshold: number;
    top_k: number;
  };
}
