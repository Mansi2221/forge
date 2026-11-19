import hashlib
import time
from dataclasses import dataclass, field

import anthropic

from app.core.config import settings
from app.models.schemas import DocumentChunk, RAGQuery, RAGResponse


@dataclass
class VectorStore:
    """In-memory vector store using cosine similarity. Swap for pgvector/Pinecone in production."""

    chunks: list[dict] = field(default_factory=list)

    def add(self, chunk_id: str, content: str, embedding: list[float], metadata: dict):
        self.chunks.append({
            "id": chunk_id,
            "content": content,
            "embedding": embedding,
            "metadata": metadata,
        })

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        scored = []
        for chunk in self.chunks:
            sim = self._cosine_similarity(query_embedding, chunk["embedding"])
            scored.append({**chunk, "similarity": sim})
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def clear(self):
        self.chunks = []

    @property
    def count(self) -> int:
        return len(self.chunks)


vector_store = VectorStore()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
    return chunks


def generate_embedding(text: str) -> list[float]:
    """Generate a simple hash-based embedding for demo. Replace with real embeddings in production."""
    text_hash = hashlib.sha256(text.lower().encode()).hexdigest()
    embedding = []
    for i in range(0, min(len(text_hash), 128), 2):
        val = int(text_hash[i:i+2], 16) / 255.0
        embedding.append(val * 2 - 1)
    while len(embedding) < 64:
        embedding.append(0.0)
    norm = sum(x * x for x in embedding) ** 0.5
    if norm > 0:
        embedding = [x / norm for x in embedding]
    return embedding


def ingest_document(filename: str, content: str, metadata: dict | None = None) -> int:
    chunks = chunk_text(content)
    for i, chunk in enumerate(chunks):
        chunk_id = hashlib.md5(f"{filename}:{i}".encode()).hexdigest()
        embedding = generate_embedding(chunk)
        vector_store.add(
            chunk_id=chunk_id,
            content=chunk,
            embedding=embedding,
            metadata={"filename": filename, "chunk_index": i, **(metadata or {})},
        )
    return len(chunks)


def retrieve(query: RAGQuery) -> list[DocumentChunk]:
    query_embedding = generate_embedding(query.query)
    results = vector_store.search(query_embedding, top_k=query.top_k)
    return [
        DocumentChunk(
            id=r["id"],
            content=r["content"],
            metadata=r["metadata"],
            similarity=r["similarity"],
        )
        for r in results
    ]


def rag_query(query: RAGQuery) -> RAGResponse:
    sources = retrieve(query)

    if not sources:
        return RAGResponse(
            answer="No relevant documents found. Please upload documents first.",
            sources=[],
            model="none",
        )

    context = "\n\n---\n\n".join([s.content for s in sources])

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    start = time.time()
    response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1024,
        system="You are a helpful assistant. Answer questions based ONLY on the provided context. If the context doesn't contain the answer, say so. Cite your sources.",
        messages=[
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query.query}",
            }
        ],
    )
    latency = int((time.time() - start) * 1000)

    answer = response.content[0].text
    tokens = response.usage.input_tokens + response.usage.output_tokens

    return RAGResponse(
        answer=answer,
        sources=sources,
        model="claude-sonnet-5-5",
        tokens_used=tokens,
    )
