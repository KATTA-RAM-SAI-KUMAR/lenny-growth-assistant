import React from 'react';
import { LLMProvider, HealthStatus } from '../../lib/types';
import { Cpu, Cloud, Sparkles, ChevronDown } from 'lucide-react';

interface ModelSelectorProps {
  currentProvider: LLMProvider;
  onProviderChange: (provider: LLMProvider) => void;
  health: HealthStatus | null;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  currentProvider,
  onProviderChange,
  health,
}) => {
  const getProviderIcon = (p: LLMProvider) => {
    switch (p) {
      case 'ollama':
        return <Cpu className="w-3.5 h-3.5 text-emerald-400" />;
      case 'claude':
        return <Sparkles className="w-3.5 h-3.5 text-amber-400" />;
      case 'openai':
        return <Cloud className="w-3.5 h-3.5 text-sky-400" />;
    }
  };

  const isOllamaOnline = health?.ollama?.available ?? false;

  return (
    <div className="relative inline-block text-xs">
      <div className="flex items-center gap-1.5 bg-surface-800/90 border border-surface-700/60 rounded-lg px-2.5 py-1.5 shadow-sm">
        {getProviderIcon(currentProvider)}
        <select
          value={currentProvider}
          onChange={(e) => onProviderChange(e.target.value as LLMProvider)}
          className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer pr-4 appearance-none"
        >
          <option value="ollama" className="bg-surface-900 text-slate-200">
            Ollama (Local: {health?.ollama?.model || 'llama3.2:3b'})
          </option>
          <option value="claude" className="bg-surface-900 text-slate-200">
            Anthropic Claude (3.5 Sonnet)
          </option>
          <option value="openai" className="bg-surface-900 text-slate-200">
            OpenAI (GPT-4o)
          </option>
        </select>
        <ChevronDown className="w-3 h-3 text-slate-400 pointer-events-none -ml-3" />

        {/* Status Indicator */}
        <span
          title={
            currentProvider === 'ollama'
              ? isOllamaOnline
                ? 'Ollama is online and connected'
                : 'Ollama is offline (running resilient fallback mode)'
              : 'Cloud provider configured'
          }
          className={`w-2 h-2 rounded-full ml-1 ${
            currentProvider === 'ollama'
              ? isOllamaOnline
                ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]'
                : 'bg-amber-400'
              : 'bg-emerald-400'
          }`}
        />
      </div>
    </div>
  );
};
