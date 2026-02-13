"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { signOut, auth } from "@/lib/firebase";
import * as api from "@/lib/api";
import type { FileInfo, ChatMessage, SourceChunk } from "@/lib/api";
import toast from "react-hot-toast";
import ReactMarkdown from "react-markdown";
import {
  Send,
  Upload,
  Trash2,
  User,
  LogOut,
  FileText,
  Youtube,
  Table,
  Plus,
  X,
  Loader2,
  MessageSquare,
  ChevronDown,
  Sparkles,
  Zap,
  BookOpen,
  RotateCcw,
  PanelLeftClose,
  PanelLeft,
  Database,
  Terminal,
  Circle,
  Eye,
  EyeOff,
} from "lucide-react";

/* ================================================================
   MAIN CHAT PAGE
   ================================================================ */
export default function ChatPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  // Data
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [models, setModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState("google/gemini-2.5-flash");
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [apiKey, setApiKey] = useState("");
  const [username, setUsername] = useState("");
  const [userEmail, setUserEmail] = useState("");

  // Source chunks from last response
  const [lastSources, setLastSources] = useState<SourceChunk[]>([]);
  const [showSources, setShowSources] = useState(false);

  // PDF viewer
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [showPdf, setShowPdf] = useState(true);

  // UI state
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loadingFiles, setLoadingFiles] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [thinkingPhase, setThinkingPhase] = useState(0);

  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // ── Thinking phases (clean, no emojis) ─────────────────────────
  const thinkingSteps = [
    { label: "Parsing query", tag: "PARSE" },
    { label: "Vectorizing input", tag: "EMBED" },
    { label: "Searching document chunks", tag: "SEARCH" },
    { label: "Ranking relevant passages", tag: "RANK" },
    { label: "Generating response", tag: "GEN" },
  ];

  useEffect(() => {
    if (!sending) {
      setThinkingPhase(0);
      return;
    }
    const interval = setInterval(() => {
      setThinkingPhase((p) => (p < thinkingSteps.length - 1 ? p + 1 : p));
    }, 1800);
    return () => clearInterval(interval);
  }, [sending]);

  // ── Auth guard ──────────────────────────────────────────────────
  useEffect(() => {
    if (!authLoading && !user) router.replace("/login");
  }, [user, authLoading, router]);

  // ── Initial data load ──────────────────────────────────────────
  useEffect(() => {
    if (!user) return;
    setUserEmail(user.email || "");
    const load = async () => {
      try {
        const [filesList, modelsList, profile, key] = await Promise.all([
          api.listFiles(),
          api.getModels(),
          api.getProfile(),
          api.getApiKey(),
        ]);
        setFiles(filesList);
        setModels(modelsList);
        setUsername(profile.username || "");
        setApiKey(key);
      } catch {
        toast.error("Failed to load data");
      } finally {
        setLoadingFiles(false);
      }
    };
    load();
  }, [user]);

  // ── Load chat history when file changes ────────────────────────
  useEffect(() => {
    if (!selectedFile) {
      setMessages([]);
      setLastSources([]);
      setPdfUrl(null);
      return;
    }
    setLoadingHistory(true);
    setLastSources([]);

    // Load PDF URL if it's a PDF file
    const fileInfo = files.find((f) => f.file_name === selectedFile);
    if (fileInfo?.content_type === "pdf") {
      api.getPdfUrl(selectedFile).then(setPdfUrl);
    } else {
      setPdfUrl(null);
    }

    api
      .getChatHistory(selectedFile)
      .then(setMessages)
      .catch(() => toast.error("Failed to load chat history"))
      .finally(() => setLoadingHistory(false));
  }, [selectedFile, files]);

  // ── Auto-scroll ────────────────────────────────────────────────
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  // ── Auto-resize textarea ───────────────────────────────────────
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 120) + "px";
    }
  }, [input]);

  // ── Send message ───────────────────────────────────────────────
  const handleSend = useCallback(async () => {
    if (!input.trim() || !selectedFile || !apiKey || sending) return;
    const question = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setSending(true);
    setLastSources([]);
    setShowSources(false);

    try {
      const response = await api.sendMessage(selectedFile, question, apiKey, selectedModel);
      setMessages((prev) => [...prev, { role: "assistant", content: response.answer }]);
      if (response.sources && response.sources.length > 0) {
        setLastSources(response.sources);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to get response";
      toast.error(msg);
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setSending(false);
    }
  }, [input, selectedFile, apiKey, selectedModel, sending]);

  // ── New chat (deselect file) ───────────────────────────────────
  const handleNewChat = () => {
    setSelectedFile(null);
    setMessages([]);
    setLastSources([]);
  };

  // ── Clear history ──────────────────────────────────────────────
  const handleClear = async () => {
    if (!selectedFile) return;
    try {
      await api.clearChatHistory(selectedFile);
      setMessages([]);
      setLastSources([]);
      toast.success("History cleared");
    } catch {
      toast.error("Failed to clear history");
    }
  };

  // ── Delete file ────────────────────────────────────────────────
  const handleDeleteFile = async (fileName: string) => {
    try {
      await api.deleteFile(fileName);
      setFiles((prev) => prev.filter((f) => f.file_name !== fileName));
      if (selectedFile === fileName) {
        setSelectedFile(null);
        setMessages([]);
        setLastSources([]);
      }
      toast.success("File deleted");
    } catch {
      toast.error("Failed to delete file");
    }
  };

  // ── Upload callback ────────────────────────────────────────────
  const onUploadDone = (newFile: FileInfo) => {
    setFiles((prev) => [...prev, newFile]);
    setSelectedFile(newFile.file_name);
    setShowUpload(false);
    toast.success(`${newFile.file_name} processed!`);
  };

  // ── Logout ─────────────────────────────────────────────────────
  const handleLogout = async () => {
    await signOut(auth);
    router.replace("/login");
  };

  // ── Content type icon ──────────────────────────────────────────
  const fileIcon = (type: string) => {
    if (type === "youtube") return <Youtube className="w-4 h-4 text-red-400 flex-shrink-0" />;
    if (type === "csv") return <Table className="w-4 h-4 text-emerald-400 flex-shrink-0" />;
    return <FileText className="w-4 h-4 text-sky-400 flex-shrink-0" />;
  };

  // ── Sort files: active first ───────────────────────────────────
  const sortedFiles = [...files].sort((a, b) => {
    if (a.file_name === selectedFile) return -1;
    if (b.file_name === selectedFile) return 1;
    return 0;
  });

  if (authLoading || !user) return null;

  return (
    <div className="h-screen flex relative z-10 overflow-hidden">
      {/* ══════════ SIDEBAR ══════════ */}
      <aside
        className={`${
          sidebarOpen ? "w-72" : "w-0"
        } transition-all duration-300 ease-in-out bg-[var(--color-surface)] border-r border-[var(--color-border)] flex flex-col overflow-hidden flex-shrink-0`}
      >
        <div className="flex flex-col h-full min-w-[288px]">
          {/* ── Brand header ─── */}
          <div className="px-5 pt-5 pb-3 flex items-center gap-3">
            <img 
              src="/logo.jpg" 
              alt="OmniMind Logo" 
              className="w-10 h-10 rounded-lg object-cover"
            />
            <h2 className="font-[family-name:var(--font-display)] text-lg font-bold tracking-tight">
              <span className="bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-ember)] bg-clip-text text-transparent">
                Sangam
              </span>
              <span className="text-[var(--color-text)]">AI</span>
            </h2>
          </div>

          {/* ── New Chat button ─── */}
          <div className="px-4 mb-2">
            <button
              onClick={handleNewChat}
              className="w-full flex items-center justify-center gap-2 text-sm py-2.5 rounded-xl border border-dashed border-[var(--color-dim)] text-[var(--color-muted)] hover:border-[var(--color-accent)] hover:text-[var(--color-accent)] transition-all hover:bg-[var(--color-accent)]/5 active:scale-[0.98]"
            >
              <Plus className="w-4 h-4" /> New Chat
            </button>
          </div>

          {/* ── Model selector ─── */}
          <div className="px-4 mb-3">
            <label className="block text-[9px] font-semibold text-[var(--color-muted)] uppercase tracking-[0.15em] mb-1.5">
              Model
            </label>
            <div className="relative">
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full appearance-none bg-[var(--color-card)] border border-[var(--color-dim)]/50 rounded-lg px-3 py-2 text-[12px] text-[var(--color-text)] focus:outline-none focus:border-[var(--color-accent)] transition pr-7"
              >
                {models.map((m) => (
                  <option key={m} value={m}>{m.split("/").pop()}</option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 text-[var(--color-muted)] absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>

          {/* ── API Key status ─── */}
          <div className="px-4 mb-3">
            <div className={`text-[11px] px-3 py-1.5 rounded-lg ${
              apiKey
                ? "bg-[var(--color-success)]/5 text-[var(--color-success)] border border-[var(--color-success)]/10"
                : "bg-[var(--color-accent)]/5 text-[var(--color-accent)] border border-[var(--color-accent)]/10"
            }`}>
              {apiKey ? (
                <span className="flex items-center gap-1.5"><Zap className="w-3 h-3" /> API key active</span>
              ) : (
                <span>
                  Set key in{" "}
                  <button onClick={() => router.push("/profile")} className="underline underline-offset-2 font-medium">Profile</button>
                </span>
              )}
            </div>
          </div>

          <div className="mx-4 h-px bg-gradient-to-r from-transparent via-[var(--color-dim)] to-transparent mb-3" />

          {/* ── Upload button ─── */}
          <div className="px-4 mb-3">
            <button
              onClick={() => setShowUpload(true)}
              className="w-full flex items-center justify-center gap-2 text-[12px] font-semibold py-2.5 rounded-xl bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-accent-dim)] text-white hover:shadow-lg hover:shadow-[var(--color-accent)]/20 transition-all active:scale-[0.98]"
            >
              <Upload className="w-3.5 h-3.5" /> Upload Content
            </button>
          </div>

          {/* ── File list header ─── */}
          <div className="px-4 mb-1">
            <label className="block text-[9px] font-semibold text-[var(--color-muted)] uppercase tracking-[0.15em]">
              Your Files
            </label>
          </div>

          {/* ── File list (own scrollbar) ─── */}
          <div className="flex-1 overflow-y-auto sidebar-scroll px-3 pb-3 min-h-0">
            {loadingFiles ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-4 h-4 animate-spin text-[var(--color-muted)]" />
              </div>
            ) : files.length === 0 ? (
              <p className="text-[11px] text-[var(--color-dim)] py-6 text-center italic">
                No files yet
              </p>
            ) : (
              <div className="space-y-0.5 mt-1.5">
                {sortedFiles.map((f) => (
                  <div
                    key={f.file_name}
                    className={`file-item group flex items-center gap-2 px-2.5 py-2 rounded-lg cursor-pointer border ${
                      selectedFile === f.file_name
                        ? "active"
                        : "border-transparent"
                    }`}
                    onClick={() => setSelectedFile(f.file_name)}
                  >
                    {fileIcon(f.content_type)}
                    <span className="flex-1 truncate text-[12px]">{f.file_name}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteFile(f.file_name);
                      }}
                      className="opacity-0 group-hover:opacity-100 text-[var(--color-dim)] hover:text-red-400 transition flex-shrink-0"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>


          <div className="flex-shrink-0 border-t border-[var(--color-border)] bg-[var(--color-card)]/50 px-4 py-3">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--color-accent)]/20 to-[var(--color-ember)]/10 border border-[var(--color-accent)]/15 flex items-center justify-center flex-shrink-0">
                <User className="w-3.5 h-3.5 text-[var(--color-accent)]" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[12px] font-medium text-[var(--color-text)] truncate leading-tight">
                  {username || "User"}
                </p>
                <p className="text-[10px] text-[var(--color-muted)] truncate leading-tight">
                  {userEmail}
                </p>
              </div>
              <div className="flex gap-1 flex-shrink-0">
                <button
                  onClick={() => router.push("/profile")}
                  className="p-1.5 rounded-md hover:bg-[var(--color-dim)]/40 text-[var(--color-muted)] hover:text-[var(--color-accent)] transition"
                  title="Profile"
                >
                  <User className="w-3 h-3" />
                </button>
                <button
                  onClick={handleLogout}
                  className="p-1.5 rounded-md hover:bg-red-500/10 text-[var(--color-muted)] hover:text-red-400 transition"
                  title="Logout"
                >
                  <LogOut className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* ══════════ MAIN AREA ══════════ */}
      <main className="flex-1 flex flex-col h-screen min-w-0">
        {/* ── Top bar ─── */}
        <header className="h-12 border-b border-[var(--color-border)] flex items-center px-4 gap-3 bg-[var(--color-glass)] backdrop-blur-md flex-shrink-0">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-[var(--color-muted)] hover:text-[var(--color-text)] transition flex-shrink-0"
          >
            {sidebarOpen ? <PanelLeftClose className="w-4.5 h-4.5" /> : <PanelLeft className="w-4.5 h-4.5" />}
          </button>

          <div className="flex items-center gap-2 min-w-0 flex-1">
            {selectedFile ? (
              <>
                {fileIcon(files.find((f) => f.file_name === selectedFile)?.content_type || "pdf")}
                <span className="text-sm font-medium text-[var(--color-text)] truncate">
                  {selectedFile}
                </span>
              </>
            ) : (
              <span className="text-sm text-[var(--color-muted)]">Select a file to start chatting</span>
            )}
          </div>

          {selectedFile && (
            <button
              onClick={handleClear}
              className="flex items-center gap-1 text-[11px] text-[var(--color-muted)] hover:text-red-400 transition flex-shrink-0 px-2 py-1 rounded-md hover:bg-red-400/5"
            >
              <RotateCcw className="w-3 h-3" /> Clear
            </button>
          )}

          {/* PDF toggle */}
          {pdfUrl && (
            <button
              onClick={() => setShowPdf(!showPdf)}
              className={`flex items-center gap-1 text-[11px] transition flex-shrink-0 px-2 py-1 rounded-md ${
                showPdf
                  ? "text-[var(--color-accent)] bg-[var(--color-accent)]/5"
                  : "text-[var(--color-muted)] hover:text-[var(--color-text)] hover:bg-[var(--color-dim)]/20"
              }`}
            >
              {showPdf ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
              PDF
            </button>
          )}
        </header>

        {/* ── Content area (split-view when PDF) ─── */}
        <div className="flex-1 flex min-h-0">
          {/* PDF Panel */}
          {pdfUrl && showPdf && (
            <div className="w-1/2 border-r border-[var(--color-border)] flex-shrink-0 bg-[var(--color-card)]">
              <iframe
                src={pdfUrl}
                className="w-full h-full"
                title="PDF Viewer"
              />
            </div>
          )}

          {/* Chat Panel */}
          <div className="flex-1 flex flex-col min-w-0">

        {/* ── Messages area ─── */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto chat-scroll px-4 py-6 min-h-0">
          {!selectedFile ? (
            <EmptyState />
          ) : loadingHistory ? (
            <div className="flex items-center justify-center h-full">
              <Loader2 className="w-5 h-5 animate-spin text-[var(--color-muted)]" />
            </div>
          ) : messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <BookOpen className="w-8 h-8 mx-auto mb-3 text-[var(--color-dim)]" />
                <p className="text-[var(--color-muted)] text-sm">
                  Ask something about <span className="text-[var(--color-accent)] font-medium">{selectedFile}</span>
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-5 max-w-3xl mx-auto">
              {messages.map((msg, i) => (
                <ChatBubble key={i} msg={msg} />
              ))}

              {/* ── Source chunks from last response ─── */}
              {!sending && lastSources.length > 0 && (
                <div className="max-w-3xl mx-auto">
                  <button
                    onClick={() => setShowSources(!showSources)}
                    className="flex items-center gap-2 text-[11px] text-[var(--color-muted)] hover:text-[var(--color-accent)] transition group"
                  >
                    <Database className="w-3 h-3" />
                    <span>{lastSources.length} source chunks retrieved</span>
                    <ChevronDown className={`w-3 h-3 transition-transform ${showSources ? "rotate-180" : ""}`} />
                  </button>

                  {showSources && (
                    <div className="mt-2 space-y-1.5">
                      {lastSources.map((src, i) => (
                        <div key={i} className="chunk-card rounded-lg px-3 py-2.5">
                          <div className="flex items-center gap-2 mb-1.5">
                            <span className="text-[9px] font-[family-name:var(--font-mono)] font-bold text-[var(--color-accent)] bg-[var(--color-accent)]/8 px-1.5 py-0.5 rounded">
                              CHUNK {i + 1}
                            </span>
                            {src.page !== null && (
                              <span className="text-[9px] font-[family-name:var(--font-mono)] text-[var(--color-muted)]">
                                page {src.page}
                              </span>
                            )}
                          </div>
                          <p className="text-[11px] text-[var(--color-muted)] leading-relaxed font-[family-name:var(--font-mono)]">
                            {src.text}
                            {src.text.length >= 200 && <span className="text-[var(--color-dim)]">...</span>}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {sending && (
            <div className="max-w-3xl mx-auto mt-5">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-[var(--color-surface)] border border-[var(--color-accent)]/20 flex items-center justify-center flex-shrink-0">
                  <Terminal className="w-4 h-4 text-[var(--color-accent)]" />
                </div>
                <div className="flex-1">
                  <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl overflow-hidden">

                    {/* Terminal body */}
                    <div className="px-3 py-3 space-y-1">
                      {thinkingSteps.map((step, i) => (
                        <div
                          key={i}
                          className={`flex items-center gap-2 text-[11px] font-[family-name:var(--font-mono)] transition-all duration-500 ${
                            i < thinkingPhase
                              ? "text-[var(--color-muted)]"
                              : i === thinkingPhase
                              ? "text-[var(--color-text)]"
                              : "text-[var(--color-dim)]/40"
                          }`}
                        >
                          {/* Status indicator */}
                          {i < thinkingPhase ? (
                            <span className="text-[var(--color-success)] w-4 text-center">+</span>
                          ) : i === thinkingPhase ? (
                            <span className="w-4 text-center text-[var(--color-accent)] animate-pulse">_</span>
                          ) : (
                            <span className="w-4 text-center text-[var(--color-dim)]">.</span>
                          )}

                          {/* Tag */}
                          <span className={`text-[9px] px-1 py-px rounded ${
                            i <= thinkingPhase
                              ? "bg-[var(--color-accent)]/8 text-[var(--color-accent)]"
                              : "bg-[var(--color-dim)]/20 text-[var(--color-dim)]"
                          }`}>
                            {step.tag}
                          </span>

                          {/* Label */}
                          <span>{step.label}</span>

                          {/* Done / progress indicator */}
                          {i < thinkingPhase && (
                            <span className="text-[var(--color-success)] text-[9px] ml-auto">done</span>
                          )}
                          {i === thinkingPhase && (
                            <span className="text-[var(--color-accent)] text-[9px] ml-auto flex items-center gap-0.5">
                              <span className="thinking-dot">.</span>
                              <span className="thinking-dot">.</span>
                              <span className="thinking-dot">.</span>
                            </span>
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Progress bar */}
                    <div className="px-3 pb-3">
                      <div className="h-px bg-[var(--color-dim)]/30 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-ember)] rounded-full transition-all duration-1000 ease-out"
                          style={{ width: `${((thinkingPhase + 1) / thinkingSteps.length) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ── Input bar (fixed at bottom) ─── */}
        {selectedFile && apiKey && (
          <div className="flex-shrink-0 border-t border-[var(--color-border)] bg-gradient-to-t from-[var(--color-void)] via-[var(--color-void)] to-[var(--color-glass)] px-4 py-4">
            <div className="max-w-3xl mx-auto">
              <div className="input-glow flex items-end gap-2 bg-[var(--color-card)] border border-[var(--color-dim)]/60 rounded-2xl px-4 py-2.5 transition-all">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  placeholder={
                    files.find((f) => f.file_name === selectedFile)?.content_type === "csv"
                      ? "Ask about the data e.g. 'Average sales by region?'"
                      : "Ask something about the content..."
                  }
                  disabled={sending}
                  rows={1}
                  className="flex-1 bg-transparent text-sm text-[var(--color-text)] placeholder:text-[var(--color-muted)]/60 focus:outline-none resize-none min-h-[24px] max-h-[120px] py-1 disabled:opacity-40"
                />
                <button
                  onClick={handleSend}
                  disabled={sending || !input.trim()}
                  className="flex-shrink-0 w-9 h-9 flex items-center justify-center rounded-xl bg-gradient-to-br from-[var(--color-accent)] to-[var(--color-accent-dim)] text-white hover:shadow-lg hover:shadow-[var(--color-accent)]/25 transition-all disabled:opacity-30 disabled:cursor-not-allowed active:scale-90"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
              <p className="text-[10px] text-[var(--color-dim)] text-center mt-2">
                {selectedModel.split("/").pop()} · Shift+Enter for new line
              </p>
            </div>
          </div>
        )}

        {/* Show hint when no API key */}
        {selectedFile && !apiKey && (
          <div className="flex-shrink-0 border-t border-[var(--color-border)] bg-[var(--color-glass)] px-4 py-4">
            <div className="max-w-3xl mx-auto text-center">
              <p className="text-sm text-[var(--color-accent)]">
                Set your API key in{" "}
                <button onClick={() => router.push("/profile")} className="underline underline-offset-2 font-semibold">
                  Profile
                </button>{" "}
                to start chatting
              </p>
            </div>
          </div>
        )}
          </div>{/* end Chat Panel */}
        </div>{/* end split-view */}
      </main>

      {/* ══════════ UPLOAD MODAL ══════════ */}
      {showUpload && <UploadModal onClose={() => setShowUpload(false)} onDone={onUploadDone} />}
    </div>
  );
}

/* ================================================================
   CHAT BUBBLE
   ================================================================ */
function ChatBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user";

  return (
    <div className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`w-8 h-8 rounded-lg flex items-center justify-center text-[11px] font-bold flex-shrink-0 ${
          isUser
            ? "bg-[var(--color-dim)] text-[var(--color-text)]"
            : "bg-gradient-to-br from-[var(--color-accent)] to-[var(--color-accent-dim)] text-white"
        }`}
      >
        {isUser ? "U" : <Sparkles className="w-3.5 h-3.5" />}
      </div>
      <div
        className={`rounded-xl px-4 py-3 max-w-[80%] ${
          isUser
            ? "bg-[var(--color-accent)]/8 border border-[var(--color-accent)]/15"
            : "bg-[var(--color-card)] border border-[var(--color-border)]"
        }`}
      >
        <div className="prose text-sm text-[var(--color-text)]">
          <ReactMarkdown>{msg.content}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   EMPTY STATE
   ================================================================ */
function EmptyState() {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center max-w-lg">
        <div className="relative mb-6">
          <div className="w-16 h-16 mx-auto rounded-2xl ember-gradient flex items-center justify-center rotate-3 shadow-xl shadow-[var(--color-accent)]/10">
            <MessageSquare className="w-8 h-8 text-white -rotate-3" />
          </div>
        </div>

        <h2 className="font-[family-name:var(--font-display)] text-4xl font-bold mb-2 tracking-tight">
          <span className="bg-gradient-to-r from-[var(--color-accent)] via-[var(--color-ember)] to-[var(--color-accent-glow)] bg-clip-text text-transparent">
            SangamAI
          </span>
        </h2>
        <p className="text-[var(--color-muted)] text-sm mb-8 max-w-sm mx-auto leading-relaxed">
          Upload a document, video, or dataset then have a conversation with your content.
        </p>

        <div className="grid grid-cols-3 gap-3 text-[11px] max-w-xs mx-auto">
          {[
            { icon: <FileText className="w-5 h-5 text-sky-400" />, label: "PDF", desc: "Documents" },
            { icon: <Youtube className="w-5 h-5 text-red-400" />, label: "YouTube", desc: "Transcripts" },
            { icon: <Table className="w-5 h-5 text-emerald-400" />, label: "CSV", desc: "Data analysis" },
          ].map((item) => (
            <div
              key={item.label}
              className="bg-[var(--color-card)] border border-[var(--color-border)] rounded-xl p-3 text-center hover:border-[var(--color-accent)]/20 transition group"
            >
              <div className="flex justify-center mb-1.5 group-hover:scale-110 transition-transform">{item.icon}</div>
              <p className="font-medium text-[var(--color-text)]">{item.label}</p>
              <p className="text-[var(--color-dim)] text-[10px]">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ================================================================
   UPLOAD MODAL
   ================================================================ */
function UploadModal({
  onClose,
  onDone,
}: {
  onClose: () => void;
  onDone: (file: FileInfo) => void;
}) {
  const [tab, setTab] = useState<"pdf" | "youtube" | "csv">("pdf");
  const [uploading, setUploading] = useState(false);
  const [ytUrl, setYtUrl] = useState("");

  const handlePdf = async (file: File) => {
    setUploading(true);
    try {
      const res = await api.uploadPdf(file);
      onDone({ file_name: res.file_name, content_type: "pdf", created_at: "" });
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleYoutube = async () => {
    if (!ytUrl.trim()) return;
    setUploading(true);
    try {
      const res = await api.uploadYoutube(ytUrl.trim());
      onDone({ file_name: res.file_name, content_type: "youtube", created_at: "" });
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Processing failed");
    } finally {
      setUploading(false);
    }
  };

  const handleCsv = async (file: File) => {
    setUploading(true);
    try {
      const res = await api.uploadCsv(file);
      onDone({ file_name: res.file_name, content_type: "csv", created_at: "" });
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const tabs = [
    { key: "pdf" as const, label: "PDF", icon: <FileText className="w-3.5 h-3.5" /> },
    { key: "youtube" as const, label: "YouTube", icon: <Youtube className="w-3.5 h-3.5" /> },
    { key: "csv" as const, label: "CSV", icon: <Table className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div
        className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl shadow-black/50"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-5 pb-3">
          <h3 className="font-[family-name:var(--font-display)] text-lg font-bold tracking-tight">
            Upload Knowledge
          </h3>
          <button onClick={onClose} className="text-[var(--color-muted)] hover:text-[var(--color-text)] transition p-1 rounded-lg hover:bg-[var(--color-dim)]/30">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 px-6 mb-4">
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`flex items-center gap-1.5 text-[12px] font-medium px-3 py-1.5 rounded-lg transition-all ${
                tab === t.key
                  ? "bg-[var(--color-accent)]/10 text-[var(--color-accent)] border border-[var(--color-accent)]/20"
                  : "text-[var(--color-muted)] hover:text-[var(--color-text)] hover:bg-[var(--color-card)] border border-transparent"
              }`}
            >
              {t.icon} {t.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="px-6 pb-6">
          {tab === "pdf" && (
            <div className="space-y-3">
              <p className="text-[11px] text-[var(--color-muted)]">Upload a PDF document for conversational retrieval.</p>
              <label className="block border-2 border-dashed border-[var(--color-dim)] rounded-xl p-10 text-center cursor-pointer hover:border-[var(--color-accent)]/40 transition group">
                <Upload className="w-7 h-7 mx-auto mb-2 text-[var(--color-dim)] group-hover:text-[var(--color-accent)] transition" />
                <p className="text-[12px] text-[var(--color-muted)] group-hover:text-[var(--color-text)] transition">Click to select a PDF</p>
                <input type="file" accept=".pdf" className="hidden" onChange={(e) => e.target.files?.[0] && handlePdf(e.target.files[0])} disabled={uploading} />
              </label>
            </div>
          )}

          {tab === "youtube" && (
            <div className="space-y-3">
              <p className="text-[11px] text-[var(--color-muted)]">Paste a YouTube URL to extract and index the transcript.</p>
              <input
                value={ytUrl}
                onChange={(e) => setYtUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="w-full bg-[var(--color-card)] border border-[var(--color-dim)]/50 rounded-xl px-4 py-2.5 text-sm text-[var(--color-text)] placeholder:text-[var(--color-muted)]/50 focus:outline-none focus:border-[var(--color-accent)] transition"
              />
              <button
                onClick={handleYoutube}
                disabled={uploading || !ytUrl.trim()}
                className="w-full bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-accent-dim)] text-white font-semibold py-2.5 rounded-xl hover:shadow-lg hover:shadow-[var(--color-accent)]/20 transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm active:scale-[0.98]"
              >
                {uploading && <Loader2 className="w-4 h-4 animate-spin" />}
                Process & Save
              </button>
            </div>
          )}

          {tab === "csv" && (
            <div className="space-y-3">
              <p className="text-[11px] text-[var(--color-muted)]">Upload CSV for data analysis via Pandas agent.</p>
              <label className="block border-2 border-dashed border-[var(--color-dim)] rounded-xl p-10 text-center cursor-pointer hover:border-[var(--color-accent)]/40 transition group">
                <Upload className="w-7 h-7 mx-auto mb-2 text-[var(--color-dim)] group-hover:text-[var(--color-accent)] transition" />
                <p className="text-[12px] text-[var(--color-muted)] group-hover:text-[var(--color-text)] transition">Click to select a CSV</p>
                <input type="file" accept=".csv" className="hidden" onChange={(e) => e.target.files?.[0] && handleCsv(e.target.files[0])} disabled={uploading} />
              </label>
            </div>
          )}

          {uploading && (
            <div className="mt-4 flex items-center gap-2 text-[12px] text-[var(--color-accent)]">
              <Loader2 className="w-3.5 h-3.5 animate-spin" /> Processing your content...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
