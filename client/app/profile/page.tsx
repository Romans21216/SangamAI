"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { signOut, auth } from "@/lib/firebase";
import * as api from "@/lib/api";
import toast from "react-hot-toast";
import { ArrowLeft, LogOut, Loader2, ExternalLink } from "lucide-react";

export default function ProfilePage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();

  const [profile, setProfile] = useState<{
    uid: string;
    email: string;
    username: string;
    has_api_key: boolean;
    api_key_hint: string | null;
  } | null>(null);

  const [newUsername, setNewUsername] = useState("");
  const [newApiKey, setNewApiKey] = useState("");
  const [savingName, setSavingName] = useState(false);
  const [savingKey, setSavingKey] = useState(false);

  useEffect(() => {
    if (!authLoading && !user) router.replace("/login");
  }, [user, authLoading, router]);

  useEffect(() => {
    if (!user) return;
    api
      .getProfile()
      .then((p) => {
        setProfile(p);
        setNewUsername(p.username || "");
      })
      .catch(() => toast.error("Failed to load profile"));
  }, [user]);

  const handleSaveName = async () => {
    if (!newUsername.trim()) return toast.error("Name cannot be empty");
    setSavingName(true);
    try {
      await api.updateUsername(newUsername.trim());
      setProfile((p) => (p ? { ...p, username: newUsername.trim() } : p));
      toast.success("Display name saved");
    } catch {
      toast.error("Failed to save name");
    } finally {
      setSavingName(false);
    }
  };

  const handleSaveKey = async () => {
    if (!newApiKey.trim()) return toast.error("Please enter a key");
    setSavingKey(true);
    try {
      await api.updateApiKey(newApiKey.trim());
      setProfile((p) =>
        p ? { ...p, has_api_key: true, api_key_hint: `...${newApiKey.slice(-8)}` } : p,
      );
      setNewApiKey("");
      toast.success("API key saved");
    } catch {
      toast.error("Failed to save key");
    } finally {
      setSavingKey(false);
    }
  };

  const handleLogout = async () => {
    await signOut(auth);
    router.replace("/login");
  };

  if (authLoading || !user) return null;

  return (
    <div className="min-h-screen flex items-start justify-center px-4 py-12 relative z-10">
      <div className="w-full max-w-xl">
        {/* Back + Logout */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => router.push("/chat")}
            className="flex items-center gap-1.5 text-sm text-[var(--color-muted)] hover:text-[var(--color-accent)] transition"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Chat
          </button>
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 text-sm text-[var(--color-muted)] hover:text-red-400 transition"
          >
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>

        {/* Header */}
        <div className="flex items-center gap-4 mb-2">
          <img 
            src="/logo.jpg" 
            alt="OmniMind Logo" 
            className="w-12 h-12 rounded-lg object-cover"
          />
          <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold tracking-tight">
            Profile
          </h1>
        </div>
        <div className="h-0.5 w-16 bg-gradient-to-r from-[var(--color-accent)] to-transparent mb-8" />

        {!profile ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-[var(--color-muted)]" />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Info card */}
            <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl p-5 grid grid-cols-2 gap-4">
              <div>
                <p className="text-[10px] uppercase tracking-wider text-[var(--color-muted)] mb-1">
                  Email
                </p>
                <p className="text-sm">{profile.email}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-[var(--color-muted)] mb-1">
                  User ID
                </p>
                <p className="text-sm font-[family-name:var(--font-mono)] text-xs">
                  {profile.uid.slice(0, 12)}…
                </p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-[var(--color-muted)] mb-1">
                  Display Name
                </p>
                <p className="text-sm">
                  {profile.username || (
                    <span className="text-[var(--color-dim)] italic">Not set</span>
                  )}
                </p>
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-[var(--color-muted)] mb-1">
                  API Key
                </p>
                <p className="text-sm">
                  {profile.has_api_key ? (
                    <span className="text-[var(--color-success)]">Active · {profile.api_key_hint}</span>
                  ) : (
                    <span className="text-[var(--color-accent)]">Not configured</span>
                  )}
                </p>
              </div>
            </div>

            <div className="h-px bg-[var(--color-dim)]" />

            {/* Update Display Name */}
            <div>
              <h3 className="text-sm font-semibold mb-3">Display Name</h3>
              <div className="flex gap-2">
                <input
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  placeholder="Your display name"
                  className="flex-1 bg-[var(--color-void)] border border-[var(--color-dim)] rounded-lg px-4 py-2.5 text-sm text-[var(--color-text)] placeholder:text-[var(--color-muted)] focus:outline-none focus:border-[var(--color-accent)] transition"
                />
                <button
                  onClick={handleSaveName}
                  disabled={savingName}
                  className="bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-accent-dim)] text-white font-semibold px-5 py-2.5 rounded-lg hover:shadow-lg hover:shadow-[var(--color-accent)]/20 transition-all disabled:opacity-50 flex items-center gap-2"
                >
                  {savingName && <Loader2 className="w-4 h-4 animate-spin" />}
                  Save
                </button>
              </div>
            </div>

            <div className="h-px bg-[var(--color-dim)]" />

            {/* Update API Key */}
            <div>
              <h3 className="text-sm font-semibold mb-3">Update API Key</h3>
              <div className="flex gap-2">
                <input
                  type="password"
                  value={newApiKey}
                  onChange={(e) => setNewApiKey(e.target.value)}
                  placeholder="sk-or-v1-…"
                  className="flex-1 bg-[var(--color-void)] border border-[var(--color-dim)] rounded-lg px-4 py-2.5 text-sm text-[var(--color-text)] placeholder:text-[var(--color-muted)] focus:outline-none focus:border-[var(--color-accent)] transition"
                />
                <button
                  onClick={handleSaveKey}
                  disabled={savingKey}
                  className="bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-accent-dim)] text-white font-semibold px-5 py-2.5 rounded-lg hover:shadow-lg hover:shadow-[var(--color-accent)]/20 transition-all disabled:opacity-50 flex items-center gap-2"
                >
                  {savingKey && <Loader2 className="w-4 h-4 animate-spin" />}
                  Save
                </button>
              </div>
              <a
                href="https://openrouter.ai/keys"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-xs text-[var(--color-muted)] hover:text-[var(--color-accent)] mt-2 transition"
              >
                Get a key <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
