import React, { useState } from 'react';
import { Message, Artifact } from '../../lib/types';
import { MarkdownRenderer } from '../Artifact/MarkdownRenderer';
import { SourcesDrawer } from './SourcesDrawer';
import {
  User,
  Sparkles,
  Feather,
  FileCode,
  Copy,
  Check,
} from 'lucide-react';

interface MessageItemProps {
  message: Message;
  onOpenArtifact: (artifact: Artifact) => void;
  onTransformToShip30: (content: string) => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({
  message,
  onOpenArtifact,
  onTransformToShip30,
}) => {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={`group py-5 px-4 sm:px-6 transition-colors ${
        isUser ? 'bg-surface-950' : 'bg-surface-900/50 border-y border-surface-800/40'
      }`}
    >
      <div className="max-w-3xl mx-auto flex gap-4">
        {/* Avatar */}
        <div className="flex-shrink-0 mt-0.5">
          {isUser ? (
            <div className="w-8 h-8 rounded-xl bg-surface-800 flex items-center justify-center text-slate-300 border border-surface-700/60 shadow-sm">
              <User className="w-4 h-4" />
            </div>
          ) : (
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 flex items-center justify-center text-white shadow-md shadow-emerald-500/20">
              <Sparkles className="w-4 h-4" />
            </div>
          )}
        </div>

        {/* Content Body */}
        <div className="flex-1 min-w-0 space-y-2">
          {/* Header row */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-200">
                {isUser ? 'You' : 'The Lenny Growth Assistant'}
              </span>
              {!isUser && (
                <>
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 uppercase">
                    {message.provider}
                  </span>
                  {message.mode === 'ship30' && (
                    <span className="text-[10px] font-mono text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/20">
                      Ship 30 for 30
                    </span>
                  )}
                </>
              )}
            </div>

            {/* Quick Actions */}
            <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
              <button
                onClick={handleCopy}
                title="Copy message"
                className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-surface-800 transition-colors"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
          </div>

          {/* Rendered Text */}
          <div className="text-slate-200 text-sm leading-relaxed">
            <MarkdownRenderer content={message.content} />
          </div>

          {/* Sources Drawer */}
          {message.sources && message.sources.length > 0 && (
            <SourcesDrawer sources={message.sources} />
          )}

          {/* Detected Artifacts Badges */}
          {message.artifacts && message.artifacts.length > 0 && (
            <div className="pt-2 flex flex-wrap gap-2">
              {message.artifacts.map((art, idx) => (
                <button
                  key={idx}
                  onClick={() => onOpenArtifact(art)}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-800 hover:bg-surface-700 text-emerald-400 border border-emerald-500/30 text-xs font-medium transition-all shadow-sm group/btn"
                >
                  <FileCode className="w-3.5 h-3.5 text-emerald-400 group-hover/btn:scale-110 transition-transform" />
                  <span>Open Artifact: {art.title}</span>
                </button>
              ))}
            </div>
          )}

          {/* Transform to Ship 30 for 30 Action */}
          {!isUser && message.mode !== 'ship30' && message.content.length > 100 && (
            <div className="pt-2">
              <button
                onClick={() => onTransformToShip30(message.content)}
                className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-emerald-300 font-medium transition-colors"
              >
                <Feather className="w-3 h-3 text-emerald-400" />
                <span>Transform to Ship 30 for 30 essay</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
