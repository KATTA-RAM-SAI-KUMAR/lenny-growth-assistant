import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <div className="prose prose-invert max-w-none text-slate-200 text-sm leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ node, ...props }) => (
            <h1 className="text-xl font-bold text-white mt-4 mb-3 border-b border-surface-700/60 pb-2" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-lg font-semibold text-emerald-400 mt-4 mb-2" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-base font-semibold text-slate-100 mt-3 mb-1.5" {...props} />
          ),
          p: ({ node, ...props }) => (
            <p className="mb-3 leading-relaxed text-slate-300" {...props} />
          ),
          ul: ({ node, ...props }) => (
            <ul className="list-disc pl-5 space-y-1.5 mb-3 text-slate-300" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="list-decimal pl-5 space-y-1.5 mb-3 text-slate-300" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="text-slate-300" {...props} />
          ),
          blockquote: ({ node, ...props }) => (
            <blockquote className="border-l-4 border-emerald-500/70 bg-emerald-500/5 pl-4 py-1 my-3 text-slate-300 italic rounded-r" {...props} />
          ),
          strong: ({ node, ...props }) => (
            <strong className="font-semibold text-emerald-300" {...props} />
          ),
          code: ({ node, className, children, ...props }) => {
            const isInline = !className;
            return isInline ? (
              <code className="bg-surface-800 text-emerald-400 font-mono text-xs px-1.5 py-0.5 rounded border border-surface-700/60" {...props}>
                {children}
              </code>
            ) : (
              <pre className="bg-surface-900 border border-surface-700/80 rounded-lg p-3 overflow-x-auto text-xs font-mono text-slate-200 my-3">
                <code {...props}>{children}</code>
              </pre>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};
