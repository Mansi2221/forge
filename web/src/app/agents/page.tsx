"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { api } from "@/lib/api";

interface AgentMessage {
  role: string;
  content: string;
  agent: string;
  metadata: Record<string, unknown>;
}

interface WorkflowResult {
  id: string;
  workflow_name: string;
  status: string;
  messages: AgentMessage[];
  result: string;
  duration_ms: number;
  token_usage: { input: number; output: number };
}

const agentColors: Record<string, string> = {
  planner: "bg-blue-500/10 text-blue-400 border-blue-500/30",
  researcher: "bg-purple-500/10 text-purple-400 border-purple-500/30",
  executor: "bg-green-500/10 text-green-400 border-green-500/30",
  reviewer: "bg-amber-500/10 text-amber-400 border-amber-500/30",
  user: "bg-zinc-500/10 text-zinc-400 border-zinc-500/30",
};

export default function AgentsPage() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState<WorkflowResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function runWorkflow() {
    if (!input.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = (await api.agents.run(input)) as WorkflowResult;
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run workflow");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Multi-Agent Workflows</h1>
        <p className="mt-2 text-muted-foreground">
          Orchestrate a 4-agent LangGraph pipeline: Planner &rarr; Researcher
          &rarr; Executor &rarr; Reviewer
        </p>
      </div>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Run Workflow</CardTitle>
          <CardDescription>
            Enter a task and watch four AI agents collaborate to solve it.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Textarea
            placeholder="e.g., Analyze the pros and cons of using LangGraph vs CrewAI for multi-agent orchestration..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="mb-4 min-h-[100px]"
          />
          <Button onClick={runWorkflow} disabled={loading || !input.trim()}>
            {loading ? "Running agents..." : "Run Workflow"}
          </Button>
          {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
        </CardContent>
      </Card>

      {result && (
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <Badge variant="secondary">{result.status}</Badge>
            <span className="text-sm text-muted-foreground">
              {result.duration_ms}ms &bull;{" "}
              {result.token_usage.input + result.token_usage.output} tokens
            </span>
          </div>

          <Separator />

          {result.messages.map((msg, i) => (
            <Card
              key={i}
              className={`border ${agentColors[msg.role] || "border-border"}`}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <Badge
                    variant="outline"
                    className={agentColors[msg.role] || ""}
                  >
                    {msg.role.toUpperCase()}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {msg.agent}
                  </span>
                </div>
              </CardHeader>
              <CardContent>
                <pre className="whitespace-pre-wrap text-sm">{msg.content}</pre>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
