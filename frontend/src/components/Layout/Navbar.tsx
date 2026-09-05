import React from 'react';
import { LLMProvider, ChatMode, HealthStatus } from '../../lib/types';
import { ModelSelector } from '../Chat/ModelSelector';
import { ModeSelector } from '../Chat/ModeSelector';
import { Radio, Database, Github, Menu } from 'lucide-react';

interface NavbarProps {
  currentProvider: LLMProvider;
  onProviderChange: (provider: LLMProvider) => void;
  currentMode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
  health: HealthStatus | null;
  onToggleSidebar: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentProvider,
  onProviderChange,
  currentMode,
  onModeChange,
  health,
  onToggleSidebar,
}) => {
  const isDbHealthy = health?.database?.connected ?? false;

  return (
    <header className="h-16 border-b border-surface-800 bg-surface-900/90 backdrop-blur-md px-4 flex items-center justify-between z-20 select-none">
      {/* Brand / Logo */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-surface-800 lg:hidden transition-colors"
          title="Toggle Sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
            <Radio className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <h1 className="text-sm font-bold text-white tracking-tight">
                The Lenny Growth Assistant
              </h1>
              <span className="text-[10px] font-mono font-semibold text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                FDE
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">
              200+ hrs of Lenny's Podcast transcripts • RAG & Ship 30 Engine
            </p>
          </div>
        </div>
      </div>

      {/* Center & Right Controls */}
      <div className="flex items-center gap-3">
        {/* Mode Selector */}
        <div className="hidden md:block">
          <ModeSelector currentMode={currentMode} onModeChange={onModeChange} />
        </div>

        {/* Dynamic Model Selector */}
        <ModelSelector
          currentProvider={currentProvider}
          onProviderChange={onProviderChange}
          health={health}
        />

        {/* Database Health Badge */}
        <div
          title={
            isDbHealthy
              ? `DB Connected: ${health?.database.dialect} (pgvector ready: ${health?.database.pgvector_ready}, chunks: ${health?.retrieval.total_indexed_chunks})`
              : 'Database connecting / initializing...'
          }
          className="hidden sm:flex items-center gap-1.5 text-xs text-slate-400 bg-surface-800/80 border border-surface-700/60 px-2.5 py-1.5 rounded-lg font-mono"
        >
          <Database className="w-3.5 h-3.5 text-slate-400" />
          <span
            className={`w-2 h-2 rounded-full ${
              isDbHealthy ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]' : 'bg-amber-400'
            }`}
          />
          <span className="text-[11px]">{health?.retrieval.total_indexed_chunks || 0} chunks</span>
        </div>

        {/* GitHub / Documentation Link */}
        <a
          href="https://github.com/your-org/lenny-growth-assistant"
          target="_blank"
          rel="noopener noreferrer"
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-surface-800 transition-colors"
          title="View GitHub Repository"
        >
          <Github className="w-4 h-4" />
        </a>
      </div>
    </header>
  );
};
