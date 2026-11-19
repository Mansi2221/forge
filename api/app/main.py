from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import agents, eval, guardrails, rag

app = FastAPI(
    title="Forge API",
    description="AI Agent Evaluation & Orchestration Platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router, prefix="/api/v1")
app.include_router(rag.router, prefix="/api/v1")
app.include_router(eval.router, prefix="/api/v1")
app.include_router(guardrails.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"name": "Forge API", "version": "0.1.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
