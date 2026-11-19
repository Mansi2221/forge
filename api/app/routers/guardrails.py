from fastapi import APIRouter, HTTPException

from app.guardrails.engine import run_guardrails
from app.models.schemas import GuardrailResult

router = APIRouter(prefix="/guardrails", tags=["guardrails"])


@router.post("/check", response_model=GuardrailResult)
async def check_input(text: str, sources: list[str] | None = None):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if len(text) > 50000:
        raise HTTPException(status_code=400, detail="Text exceeds maximum length")
    return run_guardrails(text, sources=sources)


@router.post("/check-response", response_model=GuardrailResult)
async def check_response(text: str, sources: list[str] | None = None):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    return run_guardrails(text, sources=sources, is_response=True)
