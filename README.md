# Forge — AI Agent Evaluation & Orchestration Platform

A production-ready platform for building, evaluating, and securing AI agent workflows. Forge combines multi-agent orchestration, RAG pipelines, LLM evaluation, and guardrails into a single end-to-end system.

**Live Demo:** [forge on Vercel](https://web-lyart-gamma-37.vercel.app)

## Features

### Multi-Agent Workflows (LangGraph)
Orchestrate a 4-agent pipeline — **Planner → Researcher → Executor → Reviewer** — with self-reflection, tool routing, and accumulated context passing between agents.

### RAG Pipeline
Upload documents, chunk and embed them into a vector store, and query with semantic retrieval. Answers are grounded in source documents with citations.

### LLM Evaluation
Compare Claude, GPT, and Gemini side by side on:
- **Relevance** — Does the response address the prompt?
- **Coherence** — Is the response well-structured?
- **Faithfulness** — Is the response grounded in facts?
- **Latency, tokens, cost** — Performance and economics

Uses Claude as an LLM-judge (Ragas-style evaluation).

### Guardrails
Production-grade safety layer:
- **Prompt injection detection** — 14 regex patterns for common attacks
- **PII detection & redaction** — SSN, email, phone, credit card, IP
- **Toxicity filtering** — Keyword-based content safety
- **Hallucination detection** — Source-groundedness scoring

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, Python 3.11+, Pydantic |
| AI/ML | LangGraph, Anthropic SDK (Claude), LLM-as-Judge |
| RAG | Vector embeddings, cosine similarity, chunking pipeline |
| Safety | Regex guardrails, PII redaction, hallucination scoring |
| Testing | Pytest (15 tests), TypeScript strict mode |
| CI/CD | GitHub Actions, Vercel, Docker |

## Architecture

```
forge/
├── web/                    # Next.js 16 dashboard
│   └── src/
│       ├── app/
│       │   ├── agents/     # Multi-agent workflow UI
│       │   ├── rag/        # Document upload & query UI
│       │   ├── eval/       # Model comparison UI
│       │   └── guardrails/ # Safety testing UI
│       └── lib/api.ts      # API client
├── api/                    # FastAPI backend
│   ├── app/
│   │   ├── agents/         # LangGraph multi-agent workflows
│   │   ├── rag/            # RAG pipeline & vector store
│   │   ├── eval/           # LLM evaluation engine
│   │   ├── guardrails/     # Safety & guardrail checks
│   │   ├── models/         # Pydantic schemas
│   │   └── routers/        # API endpoints
│   ├── tests/              # Pytest test suite
│   └── Dockerfile
└── .github/workflows/      # CI pipeline
```

## Quick Start

### Frontend
```bash
cd web
pnpm install
pnpm dev
```

### Backend
```bash
cd api
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Run Tests
```bash
cd api
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agents/run` | Run multi-agent workflow |
| GET | `/api/v1/agents/workflows` | List available workflows |
| POST | `/api/v1/rag/ingest` | Upload & embed document |
| POST | `/api/v1/rag/query` | Semantic RAG query |
| POST | `/api/v1/eval/compare` | Compare models side by side |
| POST | `/api/v1/guardrails/check` | Run input guardrails |
| POST | `/api/v1/guardrails/check-response` | Run output guardrails |

## Skills Demonstrated

This project demonstrates the following production AI engineering skills:

- **Multi-Agent Systems** — LangGraph orchestration with role-based agents
- **RAG Engineering** — Document chunking, embedding, retrieval, grounded generation
- **LLM Evaluation** — Automated scoring with LLM-as-Judge (Ragas-style)
- **Guardrails & Safety** — Prompt injection, PII, toxicity, hallucination detection
- **API Design** — FastAPI with Pydantic schemas, CORS, modular routing
- **Full-Stack Development** — Next.js + TypeScript + Tailwind + shadcn/ui
- **Testing** — 15 unit tests covering guardrails and RAG pipeline
- **CI/CD** — GitHub Actions for lint, typecheck, build, and test
- **Containerization** — Docker support for API deployment

## License

MIT
