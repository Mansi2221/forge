import time
from typing import Any

import anthropic

from app.core.config import settings
from app.guardrails.engine import run_guardrails
from app.models.schemas import (
    EvalComparison,
    EvalMetrics,
    EvalRequest,
    EvalResult,
    LLMProvider,
)


PRICING = {
    LLMProvider.CLAUDE: {"input": 3.0 / 1_000_000, "output": 15.0 / 1_000_000},
    LLMProvider.GPT: {"input": 2.5 / 1_000_000, "output": 10.0 / 1_000_000},
    LLMProvider.GEMINI: {"input": 1.25 / 1_000_000, "output": 5.0 / 1_000_000},
}

MODEL_MAP = {
    LLMProvider.CLAUDE: "claude-sonnet-5-5",
}


def call_model(provider: LLMProvider, prompt: str, temperature: float, max_tokens: int) -> dict:
    start = time.time()

    if provider == LLMProvider.CLAUDE:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=MODEL_MAP[provider],
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        latency = int((time.time() - start) * 1000)
        return {
            "text": response.content[0].text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "latency_ms": latency,
        }
    else:
        latency = int((time.time() - start) * 1000) + 50
        return {
            "text": f"[{provider.value} not configured — mock response for comparison]",
            "input_tokens": len(prompt.split()) * 2,
            "output_tokens": 50,
            "latency_ms": latency,
        }


def score_response(prompt: str, response: str) -> dict[str, float]:
    """Score a response on relevance, coherence, and faithfulness using Claude as judge."""
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    judge_response = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=200,
        temperature=0,
        system=(
            "You are an LLM output evaluator. Score the response on three dimensions, "
            "each from 0.0 to 1.0. Return ONLY a JSON object: "
            '{"relevance": 0.0, "coherence": 0.0, "faithfulness": 0.0}'
        ),
        messages=[{
            "role": "user",
            "content": f"Prompt: {prompt}\n\nResponse: {response}\n\nScore this response:",
        }],
    )

    import json
    try:
        text = judge_response.content[0].text.strip()
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
