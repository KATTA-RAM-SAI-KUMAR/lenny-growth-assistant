import React, { useState } from 'react';
import { Artifact } from '../../lib/types';
import { SandboxedIframe } from './SandboxedIframe';
import { MarkdownRenderer } from './MarkdownRenderer';
import {
  Eye,
  Code2,
  Copy,
  Check,
  Download,
  Maximize2,
  Minimize2,
  X,
  FileText,
  FileCode,
} from 'lucide-react';

interface ArtifactViewerProps {
  artifact: Artifact | null;
  onClose: () => void;
}

export const ArtifactViewer: React.FC<ArtifactViewerProps> = ({ artifact, onClose }) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
  const [copied, setCopied] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (!artifact) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = artifact.artifact_type === 'html' ? 'html' : 'md';
    const mime = artifact.artifact_type === 'html' ? 'text/html' : 'text/markdown';
    const blob = new Blob([artifact.content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.identifier || 'artifact'}.${ext}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const containerClasses = isFullscreen
    ? 'fixed inset-4 z-50 rounded-2xl shadow-2xl flex flex-col bg-surface-900 border border-surface-700/80 overflow-hidden backdrop-blur-xl'
    : 'h-full flex flex-col bg-surface-900 border-l border-surface-700/60 overflow-hidden';

  return (
    <div className={containerClasses}>
      {/* Top Header Bar */}
      <div className="h-14 border-b border-surface-700/60 px-4 flex items-center justify-between bg-surface-850/90 select-none">
        <div className="flex items-center gap-2.5 min-w-0 pr-3">
          <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            {artifact.artifact_type === 'html' ? (
              <FileCode className="w-4 h-4" />
            ) : (
              <FileText className="w-4 h-4" />
            )}
          </div>
          <div className="truncate">
            <h3 className="text-sm font-semibold text-slate-100 truncate">{artifact.title}</h3>
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">
              {artifact.artifact_type} • Claude Artifact
            </span>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {/* Tab Switcher */}
          <div className="flex bg-surface-800 p-0.5 rounded-lg border border-surface-700/50">
            <button
              onClick={() => setActiveTab('preview')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                activeTab === 'preview'
                  ? 'bg-surface-700 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Preview</span>
            </button>
            <button
              onClick={() => setActiveTab('code')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-all ${
                activeTab === 'code'
                  ? 'bg-surface-700 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code2 className="w-3.5 h-3.5" />
              <span>Code</span>
            </button>
          </div>

          {/* Copy Button */}
          <button
            onClick={handleCopy}
            title="Copy content"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-surface-800 transition-colors border border-transparent hover:border-surface-700/50"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>

          {/* Download Button */}
          <button
            onClick={handleDownload}
            title="Download file"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-surface-800 transition-colors border border-transparent hover:border-surface-700/50"
          >
            <Download className="w-4 h-4" />
          </button>

          {/* Expand Toggle */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            title={isFullscreen ? 'Exit Fullscreen' : 'Expand Fullscreen'}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-surface-800 transition-colors border border-transparent hover:border-surface-700/50"
          >
            {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>

          {/* Close Button */}
          <button
            onClick={onClose}
            title="Close Artifact Viewer"
            className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden p-4">
        {activeTab === 'preview' ? (
          artifact.artifact_type === 'html' ? (
            <SandboxedIframe content={artifact.content} title={artifact.title} />
          ) : (
            <div className="h-full overflow-y-auto pr-2 bg-surface-950/60 p-5 rounded-xl border border-surface-700/60 shadow-inner">
              <MarkdownRenderer content={artifact.content} />
            </div>
          )
        ) : (
          <div className="h-full bg-surface-950 rounded-xl border border-surface-700/70 p-4 overflow-auto font-mono text-xs text-emerald-300 leading-relaxed">
            <pre className="whitespace-pre-wrap">{artifact.content}</pre>
          </div>
        )}
      </div>
    </div>
  );
};
