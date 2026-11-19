import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";

const features = [
  {
    title: "Multi-Agent Workflows",
    description:
      "Orchestrate LangGraph pipelines with planning, research, execution, and review agents — with self-reflection and tool routing.",
    href: "/agents",
    badge: "LangGraph",
    skills: ["Multi-Agent Systems", "Tool Calling", "Self-Reflection"],
  },
  {
    title: "RAG Pipeline",
    description:
      "Upload documents, generate vector embeddings, and query with contextual retrieval — semantic search with citation.",
    href: "/rag",
    badge: "Retrieval",
    skills: ["Vector Embeddings", "Semantic Search", "pgvector"],
  },
  {
    title: "LLM Evaluation",
    description:
      "Compare Claude, GPT, and Gemini side by side on relevance, coherence, faithfulness, latency, and cost.",
    href: "/eval",
    badge: "Eval",
    skills: ["Ragas", "LLM-as-Judge", "Model Comparison"],
  },
  {
    title: "Guardrails",
    description:
      "Detect prompt injection, PII, toxicity, and hallucination — with automatic sanitization and blocking.",
    href: "/guardrails",
    badge: "Safety",
    skills: ["Prompt Injection", "PII Redaction", "Hallucination Detection"],
  },
];

export default function HomePage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-12">
      <div className="mb-12 text-center">
        <h1 className="text-5xl font-bold tracking-tight">Forge</h1>
        <p className="mt-4 text-lg text-muted-foreground">
          AI Agent Evaluation &amp; Orchestration Platform
        </p>
        <p className="mt-2 text-sm text-muted-foreground">
          Multi-agent workflows &bull; RAG pipelines &bull; LLM evaluation
          &bull; Guardrails &mdash; all in one production-ready system.
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {features.map((f) => (
          <Card key={f.href} className="group relative overflow-hidden">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-xl">{f.title}</CardTitle>
                <Badge variant="secondary">{f.badge}</Badge>
              </div>
              <CardDescription>{f.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4 flex flex-wrap gap-2">
                {f.skills.map((skill) => (
                  <Badge key={skill} variant="outline" className="text-xs">
                    {skill}
                  </Badge>
                ))}
              </div>
              <Link
                href={f.href}
                className={buttonVariants({ variant: "default", size: "sm" })}
              >
                Open
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mt-16 rounded-lg border border-border bg-muted/30 p-8">
        <h2 className="mb-4 text-2xl font-semibold">Architecture</h2>
        <div className="grid gap-4 text-sm text-muted-foreground md:grid-cols-3">
          <div>
            <p className="mb-1 font-medium text-foreground">Frontend</p>
            <p>Next.js 16, TypeScript, Tailwind CSS, shadcn/ui</p>
          </div>
          <div>
            <p className="mb-1 font-medium text-foreground">Backend</p>
            <p>FastAPI, LangGraph, Anthropic SDK, pgvector</p>
          </div>
          <div>
            <p className="mb-1 font-medium text-foreground">Infrastructure</p>
            <p>Vercel, GitHub Actions CI/CD, Docker</p>
          </div>
        </div>
      </div>
    </div>
  );
}
