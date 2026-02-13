import { auth } from "./firebase";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function headers(json = true): Promise<HeadersInit> {
  const token = await auth.currentUser?.getIdToken();
  const h: Record<string, string> = {};
  if (json) h["Content-Type"] = "application/json";
  if (token) h["Authorization"] = `Bearer ${token}`;
  return h;
}

async function handleRes(res: Response) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || "Request failed");
  }
  return res.json();
}

// ── Auth ─────────────────────────────────────────────────────────────
export async function register(email: string, password: string, username: string) {
  const res = await fetch(`${API}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, username }),
  });
  return handleRes(res);
}

// ── Profile ──────────────────────────────────────────────────────────
export async function getProfile() {
  const res = await fetch(`${API}/api/profile`, { headers: await headers(false) });
  return handleRes(res);
}

export async function updateUsername(username: string) {
  const res = await fetch(`${API}/api/profile/username`, {
    method: "PUT",
    headers: await headers(),
    body: JSON.stringify({ username }),
  });
  return handleRes(res);
}

export async function updateApiKey(api_key: string) {
  const res = await fetch(`${API}/api/profile/api-key`, {
    method: "PUT",
    headers: await headers(),
    body: JSON.stringify({ api_key }),
  });
  return handleRes(res);
}

export async function getApiKey(): Promise<string> {
  const res = await fetch(`${API}/api/profile/api-key`, { headers: await headers(false) });
  const data = await handleRes(res);
  return data.api_key || "";
}

// ── Files ────────────────────────────────────────────────────────────
export interface FileInfo {
  file_name: string;
  content_type: "pdf" | "youtube" | "csv";
  created_at: string;
}

export async function listFiles(): Promise<FileInfo[]> {
  const res = await fetch(`${API}/api/files`, { headers: await headers(false) });
  const data = await handleRes(res);
  return data.files;
}

export async function deleteFile(fileName: string) {
  const res = await fetch(`${API}/api/files/${encodeURIComponent(fileName)}`, {
    method: "DELETE",
    headers: await headers(false),
  });
  return handleRes(res);
}

export async function getPdfUrl(fileName: string): Promise<string> {
  const token = await auth.currentUser?.getIdToken();
  return `${API}/api/files/${encodeURIComponent(fileName)}/pdf?token=${token}`;
}

// ── Upload ───────────────────────────────────────────────────────────
export async function uploadPdf(file: File) {
  const fd = new FormData();
  fd.append("file", file);
  const token = await auth.currentUser?.getIdToken();
  const res = await fetch(`${API}/api/upload/pdf`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: fd,
  });
  return handleRes(res);
}

export async function uploadYoutube(url: string) {
  const res = await fetch(`${API}/api/upload/youtube`, {
    method: "POST",
    headers: await headers(),
    body: JSON.stringify({ url }),
  });
  return handleRes(res);
}

export async function uploadCsv(file: File) {
  const fd = new FormData();
  fd.append("file", file);
  const token = await auth.currentUser?.getIdToken();
  const res = await fetch(`${API}/api/upload/csv`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: fd,
  });
  return handleRes(res);
}

// ── Chat ─────────────────────────────────────────────────────────────
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export async function getChatHistory(fileName: string): Promise<ChatMessage[]> {
  const res = await fetch(`${API}/api/chat/${encodeURIComponent(fileName)}/history`, {
    headers: await headers(false),
  });
  const data = await handleRes(res);
  return data.messages;
}

export interface SourceChunk {
  text: string;
  page: number | null;
  source: string | null;
}

export interface ChatResponse {
  answer: string;
  sources: SourceChunk[];
}

export async function sendMessage(
  fileName: string,
  question: string,
  apiKey: string,
  model: string,
): Promise<ChatResponse> {
  const res = await fetch(`${API}/api/chat/message`, {
    method: "POST",
    headers: await headers(),
    body: JSON.stringify({ file_name: fileName, question, api_key: apiKey, model }),
  });
  const data = await handleRes(res);
  return { answer: data.answer, sources: data.sources || [] };
}

export async function clearChatHistory(fileName: string) {
  const res = await fetch(`${API}/api/chat/${encodeURIComponent(fileName)}/history`, {
    method: "DELETE",
    headers: await headers(false),
  });
  return handleRes(res);
}

// ── Models ───────────────────────────────────────────────────────────
export async function getModels(): Promise<string[]> {
  const res = await fetch(`${API}/api/models`);
  const data = await handleRes(res);
  return data.models;
}
