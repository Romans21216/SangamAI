import type { Metadata } from "next";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "@/lib/auth-context";
import "./globals.css";

export const metadata: Metadata = {
  title: "SangamAI | Where content meets clarity",
  description:
    "Transform PDFs, YouTube videos, and CSV datasets into interactive, conversational knowledge bases.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <AuthProvider>
          {children}
          <Toaster
            position="bottom-right"
            toastOptions={{
              style: {
                background: "#0e0e12",
                color: "#E8E4DD",
                border: "1px solid rgba(232,83,46,0.15)",
                fontFamily: "General Sans, sans-serif",
                fontSize: "0.85rem",
              },
            }}
          />
        </AuthProvider>
      </body>
    </html>
  );
}
