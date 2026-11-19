import logging
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.budget import BudgetExceededError, budget
from app.core.config import settings
from app.routers import agents, eval, guardrails, rag

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(
    title="Forge API",
    description="AI Agent Evaluation & Orchestration Platform",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(BudgetExceededError)
async def budget_exceeded_handler(request: Request, exc: BudgetExceededError):
    return Response(
        content=f'{{"detail": "{exc}"}}',
        status_code=429,
        media_type="application/json",
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
    return {
        "status": "healthy",
        "version": "0.1.0",
        "dependencies": {
            "llm": {
                "provider": "anthropic",
                "model": settings.llm_default_model,
                "fallback": settings.llm_fallback_model,
                "timeout": settings.llm_timeout,
                "max_retries": settings.llm_max_retries,
                "status": "configured" if settings.anthropic_api_key else "missing_key",
            },
            "vector_store": {"status": "in_memory"},
        },
    }


@app.get("/ready")
async def readiness():
    checks = {
        "api_key_configured": bool(settings.anthropic_api_key),
    }
    all_ready = all(checks.values())
    return {"ready": all_ready, "checks": checks}


@app.get("/api/v1/budget")
async def get_budget():
    return budget.stats()
