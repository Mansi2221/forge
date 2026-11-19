import logging
import time

import anthropic
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(
            api_key=settings.anthropic_api_key,
            timeout=httpx.Timeout(settings.llm_timeout, connect=5.0),
            max_retries=settings.llm_max_retries,
        )
    return _client


def call_claude(
    messages: list[dict],
    system: str = "",
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
) -> dict:
    client = get_client()
    model = model or settings.llm_default_model
    max_tokens = max_tokens or settings.llm_max_tokens
    temperature = temperature if temperature is not None else settings.llm_temperature

    start = time.time()
    try:
        kwargs: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system

        response = client.messages.create(**kwargs)
        latency_ms = int((time.time() - start) * 1000)

        logger.info(
            "LLM call: model=%s tokens_in=%d tokens_out=%d latency=%dms",
            model,
            response.usage.input_tokens,
            response.usage.output_tokens,
            latency_ms,
        )

        return {
            "text": response.content[0].text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "latency_ms": latency_ms,
            "model": model,
            "stop_reason": response.stop_reason,
        }
    except anthropic.APITimeoutError:
        logger.error("LLM call timed out after %ds", settings.llm_timeout)
        raise
    except anthropic.RateLimitError:
        logger.warning("LLM rate limited, retries exhausted")
        raise
    except anthropic.APIError as e:
        logger.error("LLM API error: %s", e.message)
        raise
