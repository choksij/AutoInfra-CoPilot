// app/layout.tsx
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AutoInfra CoPilot",
  description: "Secure Terraform PR reviews with autonomous checks and patches.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[var(--bg)] text-[var(--fg)]`}
      >
        <div className="min-h-screen">
          {/* Header */}
          <header className="sticky top-0 z-10 border-b border-white/10 bg-[var(--panel)]/70 backdrop-blur">
            <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="size-7 rounded-lg bg-emerald-400/90" />
                <h1 className="text-sm sm:text-base font-semibold tracking-wide">
                  AutoInfra CoPilot
                </h1>
              </div>
              <div className="text-xs text-[var(--muted)]">
                NEXT_PUBLIC_API_BASE:&nbsp;
                <code>
                  {process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000"}
                </code>
              </div>
            </div>
          </header>

          {/* Main */}
          <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>

          {/* Footer */}
          <footer className="mx-auto max-w-6xl px-4 py-8 text-xs text-[var(--muted)]">
            Built for autonomous IaC reviews • {new Date().getFullYear()}
          </footer>
        </div>
      </body>
    </html>
  );
}
