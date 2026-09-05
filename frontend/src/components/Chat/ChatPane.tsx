import React, { useState, useRef, useEffect } from 'react';
import { Message, Artifact, LLMProvider, ChatMode } from '../../lib/types';
import { MessageItem } from './MessageItem';
import {
  Send,
  Sparkles,
  Loader2,
  StopCircle,
  TrendingUp,
  Target,
  Compass,
  Code2,
} from 'lucide-react';

interface ChatPaneProps {
  messages: Message[];
  isStreaming: boolean;
  statusMessage: string | null;
  currentMode: ChatMode;
  currentProvider?: LLMProvider;
  onSendMessage: (text: string, mode?: ChatMode) => void;
  onStopStreaming: () => void;
  onOpenArtifact: (artifact: Artifact) => void;
}

const STARTER_PROMPTS = [
  {
    title: 'Brian Chesky on Founder Mode',
    prompt: "What is Brian Chesky's advice on founder mode and product management at Airbnb?",
    icon: <Target className="w-4 h-4 text-emerald-400" />,
  },
  {
    title: 'Elena Verna on B2B PLG',
    prompt: "How does Elena Verna define B2B Product-Led Growth and Product-Led Sales?",
    icon: <TrendingUp className="w-4 h-4 text-teal-400" />,
  },
  {
    title: 'Rahul Vohra PMF Engine',
    prompt: "Explain Rahul Vohra's 4-step quantitative engine to reverse-engineer product-market fit.",
    icon: <Compass className="w-4 h-4 text-sky-400" />,
  },
  {
    title: 'Interactive Retention Calculator',
    prompt: "Generate an interactive customer retention calculator in HTML/CSS based on Lenny's metrics frameworks.",
    icon: <Code2 className="w-4 h-4 text-amber-400" />,
  },
];

export const ChatPane: React.FC<ChatPaneProps> = ({
  messages,
  isStreaming,
  statusMessage,
  currentMode,
  onSendMessage,
  onStopStreaming,
  onOpenArtifact,
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, statusMessage]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isStreaming) return;
    onSendMessage(input.trim(), currentMode);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

const handleTransformToShip30 = (content: string) => {
  onSendMessage(
    `Write a Ship 30 for 30 essay based ONLY on these retrieved Lenny Podcast insights:\n\n${content}`,
    'ship30'
  );
};

  return (
    <div className="flex flex-col h-full bg-surface-950">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center p-6 text-center max-w-2xl mx-auto">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-xl shadow-emerald-500/20 mb-5">
              <Sparkles className="w-7 h-7" />
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white mb-2">
              The Lenny Growth Assistant
            </h2>
            <p className="text-sm text-slate-400 max-w-md mb-8 leading-relaxed">
              Tactical, grounded growth frameworks synthesized directly from 200+ hours of Lenny's Podcast transcripts.
            </p>

            {/* Starter Prompt Chips */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left">
              {STARTER_PROMPTS.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => onSendMessage(item.prompt, currentMode)}
                  className="p-3.5 rounded-xl bg-surface-900 border border-surface-800 hover:border-emerald-500/40 hover:bg-surface-850 transition-all text-xs group flex flex-col justify-between"
                >
                  <div className="flex items-center gap-2 mb-1.5 font-semibold text-slate-200 group-hover:text-emerald-300">
                    {item.icon}
                    <span>{item.title}</span>
                  </div>
                  <p className="text-slate-400 line-clamp-2 leading-relaxed text-[11px]">
                    {item.prompt}
                  </p>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="divide-y divide-surface-800/40">
            {messages.map((msg) => (
              <MessageItem
                key={msg.id}
                message={msg}
                onOpenArtifact={onOpenArtifact}
                onTransformToShip30={handleTransformToShip30}
              />
            ))}

            {/* Live Streaming Status Bar */}
            {statusMessage && (
              <div className="py-4 px-6 bg-surface-900/40 border-y border-surface-800/30">
                <div className="max-w-3xl mx-auto flex items-center gap-2 text-xs text-emerald-400 font-mono">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>{statusMessage}</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Fixed Bottom Input Area */}
      <div className="p-4 border-t border-surface-800/80 bg-surface-900/60 backdrop-blur-md">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative">
          <div className="relative flex items-end bg-surface-850 border border-surface-700/80 rounded-2xl shadow-lg focus-within:border-emerald-500/80 focus-within:ring-1 focus-within:ring-emerald-500/30 transition-all p-2">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = `${Math.min(e.target.scrollHeight, 180)}px`;
              }}
              onKeyDown={handleKeyDown}
              placeholder={
                currentMode === 'ship30'
                  ? 'Enter topic to generate a Ship 30 for 30 atomic essay...'
                  : "Ask anything about Lenny's Podcast transcripts (e.g. founder mode, retention, PLG)..."
              }
              rows={1}
              disabled={isStreaming}
              className="w-full bg-transparent text-slate-100 text-sm focus:outline-none resize-none px-3 py-1.5 min-h-[40px] max-h-[180px] placeholder:text-slate-500"
            />

            <div className="flex items-center gap-1.5 pl-2">
              {isStreaming ? (
                <button
                  type="button"
                  onClick={onStopStreaming}
                  className="p-2 rounded-xl bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                  title="Stop generation"
                >
                  <StopCircle className="w-4 h-4" />
                </button>
              ) : (
                <button
                  type="submit"
                  disabled={!input.trim()}
                  className={`p-2 rounded-xl transition-all ${
                    input.trim()
                      ? 'bg-emerald-600 text-white hover:bg-emerald-500 shadow-md shadow-emerald-600/30'
                      : 'bg-surface-800 text-slate-500 cursor-not-allowed'
                  }`}
                  title="Send message (Enter)"
                >
                  <Send className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
          <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-500 px-2">
            <span>
              Press <kbd className="px-1 py-0.5 rounded bg-surface-800 text-slate-400 font-mono">Enter</kbd> to send, <kbd className="px-1 py-0.5 rounded bg-surface-800 text-slate-400 font-mono">Shift+Enter</kbd> for newline
            </span>
            <span className="font-mono text-emerald-400/80">Strict Transcript Grounding Active</span>
          </div>
        </form>
      </div>
    </div>
  );
};
