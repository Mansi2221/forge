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

interface EvalMetrics {
  relevance: number;
  coherence: number;
  faithfulness: number;
  latency_ms: number;
  tokens_used: number;
  cost_usd: number;
}

interface EvalResult {
  model: string;
  response: string;
  metrics: EvalMetrics;
  guardrail_flags: string[];
}

interface EvalComparison {
  prompt: string;
  results: EvalResult[];
  winner: string;
}

const modelOptions = [
  { value: "claude", label: "Claude", color: "text-orange-400" },
  { value: "gpt", label: "GPT", color: "text-green-400" },
  { value: "gemini", label: "Gemini", color: "text-blue-400" },
];

function MetricBar({ label, value }: { label: string; value: number }) {
  const pct = Math.round(value * 100);
  const color =
    pct >= 80
      ? "bg-green-500"
      : pct >= 50
        ? "bg-amber-500"
        : "bg-red-500";
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span>{label}</span>
        <span>{pct}%</span>
      </div>
      <div className="h-2 rounded-full bg-muted">
        <div
          className={`h-2 rounded-full ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function EvalPage() {
  const [prompt, setPrompt] = useState("");
  const [selectedModels, setSelectedModels] = useState(["claude"]);
  const [result, setResult] = useState<EvalComparison | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function toggleModel(model: string) {
    setSelectedModels((prev) =>
      prev.includes(model)
        ? prev.filter((m) => m !== model)
        : [...prev, model],
    );
  }

  async function runEval() {
    if (!prompt.trim() || selectedModels.length === 0) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = (await api.eval.compare(
        prompt,
        selectedModels,
      )) as EvalComparison;
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">LLM Evaluation</h1>
        <p className="mt-2 text-muted-foreground">
          Compare models side by side on relevance, coherence, faithfulness,
          latency, and cost.
        </p>
      </div>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Evaluate Prompt</CardTitle>
          <CardDescription>
            Select models and enter a prompt to compare outputs.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            {modelOptions.map((m) => (
              <Button
                key={m.value}
                variant={
                  selectedModels.includes(m.value) ? "default" : "outline"
                }
                size="sm"
                onClick={() => toggleModel(m.value)}
              >
                {m.label}
              </Button>
            ))}
          </div>
          <Textarea
            placeholder="Enter a prompt to evaluate across models..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="min-h-[100px]"
          />
          <Button
            onClick={runEval}
            disabled={loading || !prompt.trim() || selectedModels.length === 0}
          >
            {loading ? "Evaluating..." : "Run Evaluation"}
          </Button>
          {error && <p className="text-sm text-red-400">{error}</p>}
        </CardContent>
      </Card>

      {result && (
        <div className="space-y-6">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Winner:</span>
            <Badge variant="default" className="uppercase">
              {result.winner}
            </Badge>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {result.results.map((r) => (
              <Card
                key={r.model}
                className={
                  r.model === result.winner ? "border-green-500/50" : ""
                }
              >
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="uppercase">{r.model}</CardTitle>
                    {r.model === result.winner && (
                      <Badge className="bg-green-500/20 text-green-400">
                        Winner
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <MetricBar
                      label="Relevance"
                      value={r.metrics.relevance}
                    />
                    <MetricBar
                      label="Coherence"
                      value={r.metrics.coherence}
                    />
                    <MetricBar
                      label="Faithfulness"
                      value={r.metrics.faithfulness}
                    />
                  </div>

                  <Separator />

                  <div className="grid grid-cols-3 gap-2 text-center text-xs">
                    <div>
                      <p className="text-muted-foreground">Latency</p>
                      <p className="font-medium">{r.metrics.latency_ms}ms</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Tokens</p>
                      <p className="font-medium">{r.metrics.tokens_used}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Cost</p>
                      <p className="font-medium">
                        ${r.metrics.cost_usd.toFixed(4)}
                      </p>
                    </div>
                  </div>

                  {r.guardrail_flags.length > 0 && (
                    <div className="flex gap-1">
                      {r.guardrail_flags.map((flag) => (
                        <Badge key={flag} variant="destructive" className="text-xs">
                          {flag}
                        </Badge>
                      ))}
                    </div>
                  )}

                  <Separator />

                  <details>
                    <summary className="cursor-pointer text-sm text-muted-foreground">
                      View response
                    </summary>
                    <pre className="mt-2 max-h-64 overflow-y-auto whitespace-pre-wrap rounded bg-muted p-3 text-xs">
                      {r.response}
                    </pre>
                  </details>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
