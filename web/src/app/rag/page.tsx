"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { api } from "@/lib/api";

interface Source {
  id: string;
  content: string;
  metadata: Record<string, unknown>;
  similarity: number;
}

interface RAGResult {
  answer: string;
  sources: Source[];
  model: string;
  tokens_used: number;
}

export default function RAGPage() {
  const [filename, setFilename] = useState("");
  const [docContent, setDocContent] = useState("");
  const [query, setQuery] = useState("");
  const [ingestStatus, setIngestStatus] = useState("");
  const [queryResult, setQueryResult] = useState<RAGResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleIngest() {
    if (!filename.trim() || !docContent.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = (await api.rag.ingest(filename, docContent)) as {
        chunks_created: number;
        total_chunks: number;
      };
      setIngestStatus(
        `Ingested ${res.chunks_created} chunks (${res.total_chunks} total)`,
      );
      setDocContent("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ingest failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleQuery() {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setQueryResult(null);
    try {
      const res = (await api.rag.query(query)) as RAGResult;
      setQueryResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">RAG Pipeline</h1>
        <p className="mt-2 text-muted-foreground">
          Upload documents, generate embeddings, and query with semantic
          retrieval.
        </p>
      </div>

      <Tabs defaultValue="ingest">
        <TabsList>
          <TabsTrigger value="ingest">Ingest Documents</TabsTrigger>
          <TabsTrigger value="query">Query</TabsTrigger>
        </TabsList>

        <TabsContent value="ingest">
          <Card>
            <CardHeader>
              <CardTitle>Upload Document</CardTitle>
              <CardDescription>
                Paste document text to chunk, embed, and store in the vector
                store.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="filename">Filename</Label>
                <Input
                  id="filename"
                  placeholder="e.g., company-handbook.txt"
                  value={filename}
                  onChange={(e) => setFilename(e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="content">Document Content</Label>
                <Textarea
                  id="content"
                  placeholder="Paste your document text here..."
                  value={docContent}
                  onChange={(e) => setDocContent(e.target.value)}
                  className="min-h-[200px]"
                />
              </div>
              <Button
                onClick={handleIngest}
                disabled={loading || !filename.trim() || !docContent.trim()}
              >
                {loading ? "Ingesting..." : "Ingest Document"}
              </Button>
              {ingestStatus && (
                <p className="text-sm text-green-400">{ingestStatus}</p>
              )}
              {error && <p className="text-sm text-red-400">{error}</p>}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="query">
          <Card>
            <CardHeader>
              <CardTitle>Semantic Query</CardTitle>
              <CardDescription>
                Ask a question and get an answer grounded in your uploaded
                documents.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="e.g., What is the company's policy on remote work?"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="min-h-[80px]"
              />
              <Button
                onClick={handleQuery}
                disabled={loading || !query.trim()}
              >
                {loading ? "Searching..." : "Query"}
              </Button>
              {error && <p className="text-sm text-red-400">{error}</p>}
            </CardContent>
          </Card>

          {queryResult && (
            <div className="mt-6 space-y-4">
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Answer</CardTitle>
                    <Badge variant="secondary">
                      {queryResult.model} &bull; {queryResult.tokens_used}{" "}
                      tokens
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="whitespace-pre-wrap">{queryResult.answer}</p>
                </CardContent>
              </Card>

              <h3 className="text-lg font-semibold">
                Sources ({queryResult.sources.length})
              </h3>
              {queryResult.sources.map((source, i) => (
                <Card key={source.id} className="border-muted">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        Source {i + 1}
                      </span>
                      <Badge variant="outline">
                        {(source.similarity * 100).toFixed(1)}% match
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      {source.content}
                    </p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
