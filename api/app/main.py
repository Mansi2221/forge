import logging
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import agents, eval, guardrails, rag

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)

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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response: Response = await call_next(request)
    duration = int((time.time() - start) * 1000)
    logging.getLogger("forge.access").info(
        "%s %s %d %dms",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


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
