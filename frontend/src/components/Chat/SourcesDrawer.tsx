import { useState } from 'react';
import { SourceCitation } from '../../lib/types';
import { BookOpen, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';

interface SourcesDrawerProps {
  sources: SourceCitation[];
}

export const SourcesDrawer: React.FC<SourcesDrawerProps> = ({ sources }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 border border-surface-700/50 rounded-xl bg-surface-900/80 overflow-hidden text-xs">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3.5 py-2 flex items-center justify-between hover:bg-surface-800/60 transition-colors text-slate-300"
      >
        <div className="flex items-center gap-2">
          <BookOpen className="w-3.5 h-3.5 text-emerald-400" />
          <span className="font-semibold text-slate-200">
            Retrieved Sources ({sources.length} citations)
          </span>
          <span className="text-[11px] text-emerald-400/90 font-mono bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
            Top Match: {Math.round(sources[0].score * 100)}%
          </span>
        </div>
        {isOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
      </button>

      {isOpen && (
        <div className="px-3.5 py-3 border-t border-surface-700/50 space-y-2.5 bg-surface-950/40">
          {sources.map((src, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded-lg bg-surface-900 border border-surface-700/60 hover:border-emerald-500/40 transition-colors"
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-1.5 font-medium text-slate-200">
                  <span className="text-emerald-400 font-mono font-bold">#{idx + 1}</span>
                  <span className="truncate max-w-[280px]">{src.episode}</span>
                  <span className="text-slate-400 font-normal">({src.guest})</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono text-slate-400 bg-surface-800 px-1.5 py-0.5 rounded">
                    {src.timestamp || '00:00:00'}
                  </span>
                  {src.youtube_url && (
                    <a
                      href={src.youtube_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-slate-400 hover:text-emerald-400"
                      title="Open YouTube Episode"
                    >
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
              <p className="text-slate-400 text-[11px] leading-relaxed line-clamp-3 bg-surface-950/70 p-2 rounded border border-surface-800">
                "{src.text}"
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
