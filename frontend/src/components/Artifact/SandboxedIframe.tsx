import React, { useMemo } from 'react';
import DOMPurify from 'dompurify';
import { ShieldCheck } from 'lucide-react';

interface SandboxedIframeProps {
  content: string;
  title: string;
}

export const SandboxedIframe: React.FC<SandboxedIframeProps> = ({ content, title }) => {
  // Sanitize markup prior to injecting into iframe srcDoc
  const cleanHtml = useMemo(() => {
    return DOMPurify.sanitize(content, {
      WHOLE_DOCUMENT: true,
      ADD_TAGS: ['style', 'link', 'script'],
      ADD_ATTR: ['target', 'class', 'id', 'onclick'],
    });
  }, [content]);

  return (
    <div className="flex flex-col h-full border border-surface-700/60 rounded-xl overflow-hidden bg-surface-900 shadow-xl">
      <div className="bg-surface-800/80 border-b border-surface-700/60 px-4 py-2.5 flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-300 tracking-wide uppercase truncate">
          Artifact: {title}
        </span>
        <div className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Sandboxed Preview</span>
        </div>
      </div>
      <iframe
        title={title}
        srcDoc={cleanHtml}
        // Strict security isolation: allow scripts to run for interactivity,
        // but omit allow-same-origin to prevent access to parent cookies, local storage, and DOM.
        sandbox="allow-scripts"
        className="w-full h-full border-none bg-white"
      />
    </div>
  );
};
