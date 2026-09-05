import { useState, useRef, useCallback } from 'react';
import { Message, SourceCitation, Artifact, LLMProvider, ChatMode } from '../lib/types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface UseChatStreamProps {
  sessionId: string;
  onArtifactDetected?: (artifact: Artifact) => void;
  onFinished?: () => void;
}

export function useChatStream({ sessionId, onArtifactDetected, onFinished }: UseChatStreamProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [activeSources, setActiveSources] = useState<SourceCitation[]>([]);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (text: string, mode: ChatMode = 'default', provider: LLMProvider = 'ollama') => {
      if (!text.trim() || isStreaming) return;

      const userMsgId = `user-${Date.now()}`;
      const assistantMsgId = `asst-${Date.now()}`;

      const userMessage: Message = {
        id: userMsgId,
        session_id: sessionId,
        role: 'user',
        content: text,
        mode,
        provider,
        created_at: new Date().toISOString(),
      };

      const initialAssistantMessage: Message = {
        id: assistantMsgId,
        session_id: sessionId,
        role: 'assistant',
        content: '',
        sources: [],
        mode,
        provider,
        created_at: new Date().toISOString(),
        artifacts: [],
      };

      setMessages((prev) => [...prev, userMessage, initialAssistantMessage]);
      setIsStreaming(true);
      setStatusMessage('Connecting to Lenny Intelligence Engine...');
      setActiveSources([]);

      abortControllerRef.current = new AbortController();

      try {
        const response = await fetch(`${API_BASE}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            message: text,
            mode,
            provider,
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${await response.text()}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error('Response body is null');

        const decoder = new TextDecoder();
        let buffer = '';
        let fullAssistantText = '';
        let currentSources: SourceCitation[] = [];

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith('data: ')) continue;
            const dataStr = trimmed.slice(6).trim();

            if (dataStr === '[DONE]') {
              break;
            }

            try {
              const event = JSON.parse(dataStr);
              if (event.type === 'status') {
                setStatusMessage(event.content);
              } else if (event.type === 'sources') {
                currentSources = event.content;
                setActiveSources(currentSources);
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMsgId ? { ...msg, sources: currentSources } : msg
                  )
                );
              } else if (event.type === 'token') {
                fullAssistantText += event.content;
                setStatusMessage(null);
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMsgId ? { ...msg, content: fullAssistantText } : msg
                  )
                );
              } else if (event.type === 'artifact') {
                const newArtifact: Artifact = {
                  identifier: event.identifier,
                  title: event.title,
                  artifact_type: event.artifact_type,
                  content: event.content,
                  created_at: new Date().toISOString(),
                };
                if (onArtifactDetected) {
                  onArtifactDetected(newArtifact);
                }
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMsgId
                      ? { ...msg, artifacts: [...(msg.artifacts || []), newArtifact] }
                      : msg
                  )
                );
              }
            } catch (err) {
              console.error('Error parsing SSE event:', err);
            }
          }
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          console.error('Streaming error:', err);
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMsgId
                ? {
                    ...msg,
                    content:
                      msg.content +
                      `\n\n> ❌ **Connection Error**: ${err.message || 'Failed to complete request.'}`,
                  }
                : msg
            )
          );
        }
      } finally {
        setIsStreaming(false);
        setStatusMessage(null);
        if (onFinished) onFinished();
      }
    },
    [sessionId, isStreaming, onArtifactDetected, onFinished]
  );

  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
      setStatusMessage(null);
    }
  }, []);

  return {
    messages,
    setMessages,
    isStreaming,
    statusMessage,
    activeSources,
    sendMessage,
    stopStreaming,
  };
}
