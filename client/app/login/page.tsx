"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { useEffect } from "react";
import { signInWithEmailAndPassword, auth } from "@/lib/firebase";
import { register } from "@/lib/api";
import toast from "react-hot-toast";
import { Loader2 } from "lucide-react";

export default function LoginPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<"signin" | "register">("signin");

  // Sign-in state
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  // Register state
  const [regEmail, setRegEmail] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regUsername, setRegUsername] = useState("");
  const [regLoading, setRegLoading] = useState(false);

  useEffect(() => {
    if (!authLoading && user) router.replace("/chat");
  }, [user, authLoading, router]);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await signInWithEmailAndPassword(auth, email, password);
      toast.success("Welcome back!");
      router.push("/chat");
    } catch {
      toast.error("Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegLoading(true);
    try {
      await register(regEmail, regPassword, regUsername);
      toast.success("Account created! Sign in to continue.");
      setTab("signin");
      setEmail(regEmail);
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setRegLoading(false);
    }
  };

  if (authLoading) return null;

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative z-10">
      <div className="w-full max-w-md">
        {/* Hero */}
        <div className="text-center mb-10">
          <div className="flex justify-center mb-4">
            <img 
              src="/logo.jpg" 
              alt="OmniMind Logo" 
              className="w-24 h-24 rounded-2xl object-cover shadow-lg"
            />
          </div>
          <h1 className="font-[family-name:var(--font-display)] text-5xl font-bold mb-2 tracking-tight bg-gradient-to-r from-[var(--color-accent)] via-[var(--color-ember)] to-[var(--color-accent-glow)] bg-clip-text text-transparent">
            SangamAI
          </h1>
          <p className="text-[var(--color-muted)] text-lg">
            Where content meets clarity
          </p>
        </div>

        {/* Card */}
        <div className="bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-8 backdrop-blur-sm">
          {/* Tabs */}
          <div className="flex border-b border-[var(--color-dim)] mb-6">
            <button
              onClick={() => setTab("signin")}
              className={`flex-1 pb-3 text-sm font-medium transition-colors ${
                tab === "signin"
                  ? "text-[var(--color-accent)] border-b-2 border-[var(--color-accent)]"
                  : "text-[var(--color-muted)] hover:text-[var(--color-text)]"
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => setTab("register")}
              className={`flex-1 pb-3 text-sm font-medium transition-colors ${
                tab === "register"
                  ? "text-[var(--color-accent)] border-b-2 border-[var(--color-accent)]"
                  : "text-[var(--color-muted)] hover:text-[var(--color-text)]"
              }`}
            >
              Create Account
            </button>
          </div>

          {tab === "signin" ? (
            <form onSubmit={handleSignIn} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-[var(--color-muted)] mb-1.5 uppercase tracking-wide">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className="w-full bg-[var(--color-void)] border border-[var(--color-dim)] rounded-lg px-4 py-2.5 text-[var(--color-text)] placeholder:text-[var(--color-muted)] focus:outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)]/20 transition"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-[var(--color-muted)] mb-1.5 uppercase tracking-wide">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full bg-[var(--color-void)] border border-[var(--color-dim)] rounded-lg px-4 py-2.5 text-[var(--color-text)] placeholder:text-[var(--color-muted)] focus:outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)]/20 transition"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-accent-dim)] text-white font-semibold py-2.5 rounded-lg hover:shadow-lg hover:shadow-[var(--color-accent)]/20 hover:-translate-y-0.5 active:translate-y-0 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                Sign In
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-[var(--color-muted)] mb-1.5 uppercase tracking-wide">
                  Email
                </label>
                <input
                  type="email"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className="w-full bg-[var(--color-void)] border border-[var(--color-dim)] rounded-lg px-4 py-2.5 text-[var(--color-text)] placeholder:text-[var(--color-muted)] focus:outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)]/20 transition"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-[var(--color-muted)] mb-1.5 uppercase tracking-wide">
                  Password
                </label>
                <input
                  type="password"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  placeholder="Choose a strong password"
                  required
                  className="w-full bg-[var(--color-void)] border border-[var(--color-dim)] rounded-lg px-4 py-2.5 text-[var(--color-text)] placeholder:text-[var(--color-muted)] focus:outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)]/20 transition"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-[var(--color-muted)] mb-1.5 uppercase tracking-wide">
                  Display Name{" "}
                  <span className="text-[var(--color-dim)]">(optional)</span>
                </label>
                <input
                  type="text"
                  value={regUsername}
                  onChange={(e) => setRegUsername(e.target.value)}
                  placeholder="Your name"
                  className="w-full bg-[var(--color-void)] border border-[var(--color-dim)] rounded-lg px-4 py-2.5 text-[var(--color-text)] placeholder:text-[var(--color-muted)] focus:outline-none focus:border-[var(--color-accent)] focus:ring-1 focus:ring-[var(--color-accent)]/20 transition"
                />
              </div>
              <button
                type="submit"
                disabled={regLoading}
                className="w-full bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-accent-dim)] text-white font-semibold py-2.5 rounded-lg hover:shadow-lg hover:shadow-[var(--color-accent)]/20 hover:-translate-y-0.5 active:translate-y-0 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {regLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                Create Account
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
