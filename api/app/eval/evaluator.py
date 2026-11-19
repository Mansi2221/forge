import json
import logging
import time

from app.core.llm import call_claude
from app.guardrails.engine import run_guardrails
from app.models.schemas import (
    EvalComparison,
    EvalMetrics,
    EvalRequest,
    EvalResult,
    LLMProvider,
)

logger = logging.getLogger(__name__)

PRICING = {
    LLMProvider.CLAUDE: {"input": 3.0 / 1_000_000, "output": 15.0 / 1_000_000},
    LLMProvider.GPT: {"input": 2.5 / 1_000_000, "output": 10.0 / 1_000_000},
    LLMProvider.GEMINI: {"input": 1.25 / 1_000_000, "output": 5.0 / 1_000_000},
}


def call_model(provider: LLMProvider, prompt: str, temperature: float, max_tokens: int) -> dict:
    if provider == LLMProvider.CLAUDE:
        result = call_claude(
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return {
            "text": result["text"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "latency_ms": result["latency_ms"],
        }
    else:
        return {
            "text": f"[{provider.value} not configured — mock response for comparison]",
            "input_tokens": len(prompt.split()) * 2,
            "output_tokens": 50,
            "latency_ms": 50,
        }


def score_response(prompt: str, response: str) -> dict[str, float]:
    """Score a response on relevance, coherence, and faithfulness using Claude as judge."""
    try:
        result = call_claude(
            messages=[{
                "role": "user",
                "content": f"Prompt: {prompt}\n\nResponse: {response}\n\nScore this response:",
            }],
            system=(
                "You are an LLM output evaluator. Score the response on three dimensions, "
                "each from 0.0 to 1.0. Return ONLY a JSON object: "
                '{"relevance": 0.0, "coherence": 0.0, "faithfulness": 0.0}'
            ),
            max_tokens=200,
            temperature=0,
        )
        text = result["text"].strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        scores = json.loads(text)
        return {
            "relevance": float(scores.get("relevance", 0)),
            "coherence": float(scores.get("coherence", 0)),
            "faithfulness": float(scores.get("faithfulness", 0)),
        }
    except (json.JSONDecodeError, ValueError, KeyError):
        logger.warning("Failed to parse eval scores, returning zeros")
        return {"relevance": 0.0, "coherence": 0.0, "faithfulness": 0.0}


def evaluate(request: EvalRequest) -> EvalComparison:
    results: list[EvalResult] = []

    for provider in request.models:
        model_result = call_model(
            provider=provider,
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        pricing = PRICING.get(provider, {"input": 0, "output": 0})
        cost = (
            model_result["input_tokens"] * pricing["input"]
            + model_result["output_tokens"] * pricing["output"]
        )

        scores = score_response(request.prompt, model_result["text"])

        guardrail_result = run_guardrails(model_result["text"], is_response=True)
        flags = [c.type.value for c in guardrail_result.checks if not c.passed]

        metrics = EvalMetrics(
            relevance=scores["relevance"],
            coherence=scores["coherence"],
            faithfulness=scores["faithfulness"],
            latency_ms=model_result["latency_ms"],
            tokens_used=model_result["input_tokens"] + model_result["output_tokens"],
            cost_usd=cost,
        )

        results.append(EvalResult(
            model=provider,
            response=model_result["text"],
            metrics=metrics,
            guardrail_flags=flags,
        ))

    winner = ""
    if results:
        best = max(results, key=lambda r: (r.metrics.relevance + r.metrics.coherence + r.metrics.faithfulness) / 3)
        winner = best.model.value

    return EvalComparison(
        prompt=request.prompt,
        results=results,
        winner=winner,
    )
