from fastapi import APIRouter

from app.guardrails.engine import run_guardrails
from app.models.schemas import GuardrailResult

router = APIRouter(prefix="/guardrails", tags=["guardrails"])


@router.post("/check", response_model=GuardrailResult)
async def check_input(text: str, sources: list[str] | None = None):
    return run_guardrails(text, sources=sources)


@router.post("/check-response", response_model=GuardrailResult)
async def check_response(text: str, sources: list[str] | None = None):
    return run_guardrails(text, sources=sources, is_response=True)
