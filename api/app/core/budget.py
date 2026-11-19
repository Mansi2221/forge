import logging
import threading

from app.core.config import settings

logger = logging.getLogger(__name__)

PRICING = {
    "claude-sonnet-5-5": {"input": 3.0 / 1_000_000, "output": 15.0 / 1_000_000},
    "claude-haiku-5-5": {"input": 0.25 / 1_000_000, "output": 1.25 / 1_000_000},
}


class TokenBudget:
    """Track token usage and enforce cost caps per session."""

    def __init__(self, max_cost_usd: float = 10.0, max_tokens: int = 1_000_000):
        self._lock = threading.Lock()
        self.max_cost_usd = max_cost_usd
        self.max_tokens = max_tokens
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_usd = 0.0
        self.call_count = 0

    def record(self, model: str, input_tokens: int, output_tokens: int) -> None:
        pricing = PRICING.get(model, {"input": 3.0 / 1_000_000, "output": 15.0 / 1_000_000})
        cost = input_tokens * pricing["input"] + output_tokens * pricing["output"]

        with self._lock:
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_cost_usd += cost
            self.call_count += 1

        logger.info(
            "Token budget: call=%d cost=$%.4f total=$%.4f tokens=%d",
            self.call_count,
            cost,
            self.total_cost_usd,
            self.total_input_tokens + self.total_output_tokens,
        )

    def check_budget(self) -> None:
        total_tokens = self.total_input_tokens + self.total_output_tokens
        if self.total_cost_usd >= self.max_cost_usd:
            raise BudgetExceededError(
                f"Cost cap exceeded: ${self.total_cost_usd:.2f} >= ${self.max_cost_usd:.2f}"
            )
        if total_tokens >= self.max_tokens:
            raise BudgetExceededError(
                f"Token cap exceeded: {total_tokens} >= {self.max_tokens}"
            )

    def stats(self) -> dict:
        return {
            "call_count": self.call_count,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "max_cost_usd": self.max_cost_usd,
            "max_tokens": self.max_tokens,
            "budget_remaining_usd": round(self.max_cost_usd - self.total_cost_usd, 4),
        }


class BudgetExceededError(Exception):
    pass


budget = TokenBudget()
