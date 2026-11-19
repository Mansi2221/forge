const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  health: () => apiFetch<{ status: string }>("/health"),

  agents: {
    run: (input: string) =>
      apiFetch("/api/v1/agents/run?user_input=" + encodeURIComponent(input), {
        method: "POST",
      }),
    workflows: () => apiFetch("/api/v1/agents/workflows"),
  },

  rag: {
    ingest: (filename: string, content: string) =>
      apiFetch("/api/v1/rag/ingest", {
        method: "POST",
        body: JSON.stringify({ filename, content }),
      }),
    query: (query: string, top_k: number = 5) =>
      apiFetch("/api/v1/rag/query", {
        method: "POST",
        body: JSON.stringify({ query, top_k }),
      }),
    stats: () => apiFetch<{ total_chunks: number }>("/api/v1/rag/stats"),
  },

  eval: {
    compare: (prompt: string, models: string[]) =>
      apiFetch("/api/v1/eval/compare", {
        method: "POST",
        body: JSON.stringify({ prompt, models }),
      }),
  },

  guardrails: {
    check: (text: string) =>
      apiFetch(
        "/api/v1/guardrails/check?text=" + encodeURIComponent(text),
        { method: "POST" },
      ),
    checkResponse: (text: string, sources?: string[]) =>
      apiFetch(
        "/api/v1/guardrails/check-response?text=" + encodeURIComponent(text),
        { method: "POST" },
      ),
  },
};
