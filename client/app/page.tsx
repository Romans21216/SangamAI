"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      router.replace(user ? "/chat" : "/login");
    }
  }, [user, loading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="flex justify-center mb-4">
          <img 
            src="/logo.jpg" 
            alt="OmniMind Logo" 
            className="w-20 h-20 rounded-2xl object-cover shadow-lg animate-pulse"
          />
        </div>
        <h1 className="font-[family-name:var(--font-display)] text-4xl font-bold mb-2 tracking-tight">
          <span className="bg-gradient-to-r from-[var(--color-accent)] to-[var(--color-ember)] bg-clip-text text-transparent">Sangam</span>AI
        </h1>
        <div className="w-48 h-0.5 mx-auto bg-gradient-to-r from-transparent via-[var(--color-accent)] to-transparent animate-pulse" />
      </div>
    </div>
  );
}
