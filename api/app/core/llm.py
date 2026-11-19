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


def validate_input(messages: list[dict], max_length: int | None = None) -> None:
    max_len = max_length or settings.max_input_length
    total_len = sum(len(str(m.get("content", ""))) for m in messages)
    if total_len > max_len:
        raise ValueError(f"Input too long: {total_len} chars (max {max_len})")


def call_claude(
    messages: list[dict],
    system: str = "",
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    fallback: bool = True,
) -> dict:
    validate_input(messages)

    client = get_client()
    model = model or settings.llm_default_model
    max_tokens = max_tokens or settings.llm_max_tokens
    temperature = temperature if temperature is not None else settings.llm_temperature

    start = time.time()
    try:
        return _make_request(client, model, max_tokens, temperature, system, messages, start)
    except (anthropic.APITimeoutError, anthropic.RateLimitError, anthropic.InternalServerError):
        if fallback and model != settings.llm_fallback_model:
            logger.warning(
                "Primary model %s failed, falling back to %s",
                model,
                settings.llm_fallback_model,
            )
            start = time.time()
            return _make_request(
                client, settings.llm_fallback_model, max_tokens, temperature, system, messages, start
            )
        raise
    except anthropic.APIError as e:
        logger.error("LLM API error: %s", e.message)
        raise


def _make_request(
    client: anthropic.Anthropic,
    model: str,
    max_tokens: int,
    temperature: float,
    system: str,
    messages: list[dict],
    start: float,
) -> dict:
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
        "LLM call: model=%s tokens_in=%d tokens_out=%d latency=%dms stop=%s",
        model,
        response.usage.input_tokens,
        response.usage.output_tokens,
        latency_ms,
        response.stop_reason,
    )

    return {
        "text": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "latency_ms": latency_ms,
        "model": model,
        "stop_reason": response.stop_reason,
    }
