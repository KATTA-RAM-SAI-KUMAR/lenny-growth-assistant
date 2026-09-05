import React, { useState } from 'react';
import { Session } from '../../lib/types';
import {
  Plus,
  MessageSquare,
  Trash2,
  Edit2,
  Check,
  X,
  RefreshCw,
  Library,
} from 'lucide-react';

interface SidebarProps {
  sessions: Session[];
  activeSessionId: string;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
  onRenameSession: (id: string, newTitle: string) => void;
  onTriggerIngest: () => void;
  isIngesting: boolean;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  onRenameSession,
  onTriggerIngest,
  isIngesting,
  isOpen,
  onClose,
}) => {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');

  const startRename = (s: Session, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(s.id);
    setEditTitle(s.title);
  };

  const saveRename = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (editTitle.trim()) {
      onRenameSession(id, editTitle.trim());
    }
    setEditingId(null);
  };

  const cancelRename = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(null);
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/60 z-30 lg:hidden backdrop-blur-sm"
        />
      )}

      <aside
        className={`fixed lg:static top-0 bottom-0 left-0 w-64 bg-surface-900 border-r border-surface-800 flex flex-col z-40 transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* New Chat Button */}
        <div className="p-3 border-b border-surface-800">
          <button
            onClick={() => {
              onNewSession();
              onClose();
            }}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm transition-all shadow-md shadow-emerald-600/20"
          >
            <Plus className="w-4 h-4" />
            <span>New Conversation</span>
          </button>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Conversations
          </div>

          {sessions.length === 0 ? (
            <div className="px-3 py-6 text-center text-xs text-slate-500">
              No previous chats found. Start one above!
            </div>
          ) : (
            sessions.map((s) => {
              const isActive = s.id === activeSessionId;
              const isEditing = editingId === s.id;

              return (
                <div
                  key={s.id}
                  onClick={() => {
                    onSelectSession(s.id);
                    onClose();
                  }}
                  className={`group relative flex items-center justify-between px-3 py-2.5 rounded-xl text-xs cursor-pointer transition-all ${
                    isActive
                      ? 'bg-surface-800 text-white font-medium shadow-sm border border-surface-700/60'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-surface-850'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0 flex-1 pr-2">
                    <MessageSquare
                      className={`w-3.5 h-3.5 flex-shrink-0 ${
                        isActive ? 'text-emerald-400' : 'text-slate-500'
                      }`}
                    />
                    {isEditing ? (
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        onClick={(e) => e.stopPropagation()}
                        autoFocus
                        className="bg-surface-950 text-white px-2 py-0.5 rounded text-xs border border-emerald-500 focus:outline-none w-full"
                      />
                    ) : (
                      <span className="truncate">{s.title || 'New Conversation'}</span>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {isEditing ? (
                      <>
                        <button
                          onClick={(e) => saveRename(s.id, e)}
                          className="p-1 hover:text-emerald-400"
                          title="Save Title"
                        >
                          <Check className="w-3 h-3" />
                        </button>
                        <button
                          onClick={cancelRename}
                          className="p-1 hover:text-slate-300"
                          title="Cancel"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          onClick={(e) => startRename(s, e)}
                          className="p-1 hover:text-slate-200"
                          title="Rename"
                        >
                          <Edit2 className="w-3 h-3" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteSession(s.id);
                          }}
                          className="p-1 hover:text-red-400"
                          title="Delete Session"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Knowledge Ingestion Footer Button */}
        <div className="p-3 border-t border-surface-800 bg-surface-900/90">
          <button
            onClick={onTriggerIngest}
            disabled={isIngesting}
            className="w-full flex items-center justify-between px-3 py-2 rounded-lg bg-surface-800/80 hover:bg-surface-700/80 border border-surface-700/60 text-slate-300 text-xs font-medium transition-colors"
          >
            <div className="flex items-center gap-2">
              <Library className="w-3.5 h-3.5 text-emerald-400" />
              <span>Re-index Archive</span>
            </div>
            <RefreshCw
              className={`w-3.5 h-3.5 text-slate-400 ${isIngesting ? 'animate-spin text-emerald-400' : ''}`}
            />
          </button>
        </div>
      </aside>
    </>
  );
};
