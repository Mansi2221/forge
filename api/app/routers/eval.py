from fastapi import APIRouter

from app.eval.evaluator import evaluate
from app.models.schemas import EvalComparison, EvalRequest

router = APIRouter(prefix="/eval", tags=["eval"])


@router.post("/compare", response_model=EvalComparison)
async def compare_models(request: EvalRequest):
    return evaluate(request)
