import { useState, useEffect } from 'react';
import { Navbar } from './components/Layout/Navbar';
import { Sidebar } from './components/Layout/Sidebar';
import { ChatPane } from './components/Chat/ChatPane';
import { ArtifactViewer } from './components/Artifact/ArtifactViewer';
import { useChatStream } from './hooks/useChatStream';
import {
  Session,
  Artifact,
  LLMProvider,
  ChatMode,
  HealthStatus,
} from './lib/types';
import {
  fetchHealth,
  fetchSessions,
  fetchSession,
  createSession,
  deleteSession,
  renameSession,
  triggerIngest,
} from './lib/api';

export function App() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>('');
  const [currentProvider, setCurrentProvider] = useState<LLMProvider>('ollama');
  const [currentMode, setCurrentMode] = useState<ChatMode>('default');
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [activeArtifact, setActiveArtifact] = useState<Artifact | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);

  // Health poll
  useEffect(() => {
    const loadHealth = async () => {
      try {
        const h = await fetchHealth();
        setHealth(h);
      } catch (err) {
        console.warn('Health probe poll warning:', err);
      }
    };
    loadHealth();
    const interval = setInterval(loadHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // Chat stream hook
  const {
    messages,
    setMessages,
    isStreaming,
    statusMessage,
    sendMessage,
    stopStreaming,
  } = useChatStream({
    sessionId: currentSessionId,
    onArtifactDetected: (artifact) => {
      setActiveArtifact(artifact);
    },
    onFinished: () => {
      // Refresh sessions to update titles
      fetchSessions().then(setSessions).catch(console.error);
    },
  });

  // Load session list on startup
  useEffect(() => {
    const initSessions = async () => {
      try {
        const list = await fetchSessions();
        setSessions(list);
        if (list.length > 0) {
          setCurrentSessionId(list[0].id);
          const detail = await fetchSession(list[0].id);
          setMessages(detail.messages || []);
        } else {
          const newS = await createSession('New Conversation');
          setSessions([newS]);
          setCurrentSessionId(newS.id);
          setMessages([]);
        }
      } catch (err) {
        console.error('Failed to initialize sessions:', err);
      }
    };
    initSessions();
  }, []);

  // Switch session
  const handleSelectSession = async (sessionId: string) => {
    if (sessionId === currentSessionId) return;
    setCurrentSessionId(sessionId);
    setActiveArtifact(null);
    try {
      const detail = await fetchSession(sessionId);
      setMessages(detail.messages || []);
      // If session had artifacts in latest messages, load the latest one
      if (detail.messages) {
        for (let i = detail.messages.length - 1; i >= 0; i--) {
          const arts = detail.messages[i].artifacts;
          if (arts && arts.length > 0) {
            setActiveArtifact(arts[arts.length - 1]);
            break;
          }
        }
      }
    } catch (err) {
      console.error('Failed to load session:', err);
    }
  };

  // Create new session
  const handleNewSession = async () => {
    try {
      const newS = await createSession('New Conversation');
      setSessions((prev) => [newS, ...prev]);
      setCurrentSessionId(newS.id);
      setMessages([]);
      setActiveArtifact(null);
    } catch (err) {
      console.error('Failed to create session:', err);
    }
  };

  // Delete session
  const handleDeleteSession = async (sessionId: string) => {
    try {
      await deleteSession(sessionId);
      const remaining = sessions.filter((s) => s.id !== sessionId);
      setSessions(remaining);
      if (currentSessionId === sessionId) {
        if (remaining.length > 0) {
          handleSelectSession(remaining[0].id);
        } else {
          handleNewSession();
        }
      }
    } catch (err) {
      console.error('Failed to delete session:', err);
    }
  };

  // Rename session
  const handleRenameSession = async (sessionId: string, title: string) => {
    try {
      const updated = await renameSession(sessionId, title);
      setSessions((prev) =>
        prev.map((s) => (s.id === sessionId ? { ...s, title: updated.title } : s))
      );
    } catch (err) {
      console.error('Failed to rename session:', err);
    }
  };

  // Trigger Knowledge Ingest
  const handleTriggerIngest = async () => {
    setIsIngesting(true);
    try {
      const res = await triggerIngest();
      const h = await fetchHealth();
      setHealth(h);
      alert(`Knowledge base indexed successfully! Total chunks: ${res.indexed_chunks}`);
    } catch (err: any) {
      alert(`Ingestion failed: ${err.message}`);
    } finally {
      setIsIngesting(false);
    }
  };

  const handleSendMessage = (text: string, mode?: ChatMode) => {
    sendMessage(text, mode || currentMode, currentProvider);
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-surface-950 text-slate-100">
      {/* Top Navigation */}
      <Navbar
        currentProvider={currentProvider}
        onProviderChange={setCurrentProvider}
        currentMode={currentMode}
        onModeChange={setCurrentMode}
        health={health}
        onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
      />

      {/* Main Workspace */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Sidebar */}
        <Sidebar
          sessions={sessions}
          activeSessionId={currentSessionId}
          onSelectSession={handleSelectSession}
          onNewSession={handleNewSession}
          onDeleteSession={handleDeleteSession}
          onRenameSession={handleRenameSession}
          onTriggerIngest={handleTriggerIngest}
          isIngesting={isIngesting}
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        {/* Dynamic Split-Pane Content */}
        <main className="flex-1 flex overflow-hidden">
          {/* Chat Pane */}
          <div
            className={`h-full flex flex-col transition-all duration-300 ${
              activeArtifact ? 'w-full lg:w-1/2' : 'w-full'
            }`}
          >
            <ChatPane
              messages={messages}
              isStreaming={isStreaming}
              statusMessage={statusMessage}
              currentMode={currentMode}
              currentProvider={currentProvider}
              onSendMessage={handleSendMessage}
              onStopStreaming={stopStreaming}
              onOpenArtifact={setActiveArtifact}
            />
          </div>

          {/* Claude-Style Artifact Viewer (Right Pane) */}
          {activeArtifact && (
            <div className="w-full lg:w-1/2 h-full fixed lg:static inset-0 z-30 lg:z-10 bg-surface-900/95 lg:bg-transparent">
              <ArtifactViewer
                artifact={activeArtifact}
                onClose={() => setActiveArtifact(null)}
              />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
