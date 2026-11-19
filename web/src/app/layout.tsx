import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
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
  title: "Forge — AI Agent Evaluation & Orchestration",
  description:
    "Production-ready multi-agent workflows, RAG pipelines, LLM evaluation, and guardrails in one platform.",
};

const navLinks = [
  { href: "/", label: "Dashboard" },
  { href: "/agents", label: "Agents" },
  { href: "/rag", label: "RAG" },
  { href: "/eval", label: "Eval" },
  { href: "/guardrails", label: "Guardrails" },
];

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <header className="border-b border-border">
          <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
            <Link href="/" className="text-xl font-bold tracking-tight">
              Forge
            </Link>
            <div className="flex gap-6 text-sm">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="text-muted-foreground transition-colors hover:text-foreground"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </nav>
        </header>
        <main className="flex-1">{children}</main>
        <footer className="border-t border-border py-4 text-center text-xs text-muted-foreground">
          Forge &copy; 2026 Mansi Patil &mdash; AI Agent Evaluation &
          Orchestration Platform
        </footer>
      </body>
    </html>
  );
}
