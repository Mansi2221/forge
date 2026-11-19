import logging

import anthropic
from fastapi import APIRouter, HTTPException

from app.eval.evaluator import evaluate
from app.models.schemas import EvalComparison, EvalRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/eval", tags=["eval"])


@router.post("/compare", response_model=EvalComparison)
async def compare_models(request: EvalRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    if len(request.prompt) > 50000:
        raise HTTPException(status_code=400, detail="Prompt exceeds maximum length")
    if not request.models:
        raise HTTPException(status_code=400, detail="At least one model must be selected")
    try:
        return evaluate(request)
    except anthropic.APITimeoutError:
        raise HTTPException(status_code=504, detail="LLM request timed out")
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="LLM rate limit exceeded")
    except anthropic.APIError as e:
        logger.error("Eval failed: %s", e.message)
        raise HTTPException(status_code=502, detail="LLM service error")
