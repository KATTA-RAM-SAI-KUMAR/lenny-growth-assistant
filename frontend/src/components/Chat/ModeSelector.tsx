import React from 'react';
import { ChatMode } from '../../lib/types';
import { MessageSquare, Feather } from 'lucide-react';

interface ModeSelectorProps {
  currentMode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
}

export const ModeSelector: React.FC<ModeSelectorProps> = ({ currentMode, onModeChange }) => {
  return (
    <div className="flex bg-surface-800/90 border border-surface-700/60 p-0.5 rounded-lg shadow-sm text-xs">
      <button
        onClick={() => onModeChange('default')}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-all ${
          currentMode === 'default'
            ? 'bg-surface-700 text-emerald-300 shadow-sm'
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <MessageSquare className="w-3.5 h-3.5" />
        <span>Grounded Q&A</span>
      </button>

      <button
        onClick={() => onModeChange('ship30')}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-all ${
          currentMode === 'ship30'
            ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-sm'
            : 'text-slate-400 hover:text-slate-200'
        }`}
      >
        <Feather className="w-3.5 h-3.5" />
        <span>Ship 30 for 30</span>
      </button>
    </div>
  );
};
