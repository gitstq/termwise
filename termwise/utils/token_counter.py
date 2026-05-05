"""Token counting utility for estimating LLM token usage."""

from __future__ import annotations

import json
import math
from typing import Optional


class TokenCounter:
    """Estimates token counts for text and messages.

    Uses a simple heuristic-based approach when tiktoken is not available,
    and tiktoken for accurate counting when installed.
    """

    # Average characters per token for different models
    CHARS_PER_TOKEN = {
        "gpt-4o": 3.5,
        "gpt-4o-mini": 4.0,
        "gpt-4": 3.5,
        "gpt-3.5-turbo": 4.0,
        "claude": 3.5,
        "default": 3.8,
    }

    def __init__(self, model: str = "default"):
        """Initialize the token counter.

        Args:
            model: The model name to optimize estimation for.
        """
        self._model = model
        self._tiktoken = None
        self._encoding = None
        self._init_tiktoken()

    def _init_tiktoken(self) -> None:
        """Try to initialize tiktoken for accurate counting."""
        try:
            import tiktoken

            self._tiktoken = tiktoken
            encoding_map = {
                "gpt-4o": "o200k_base",
                "gpt-4o-mini": "o200k_base",
                "gpt-4": "cl100k_base",
                "gpt-3.5-turbo": "cl100k_base",
            }
            encoding_name = encoding_map.get(self._model, "cl100k_base")
            self._encoding = tiktoken.get_encoding(encoding_name)
        except ImportError:
            self._tiktoken = None
            self._encoding = None

    def count_text(self, text: str) -> int:
        """Count tokens in a text string.

        Args:
            text: The text to count tokens for.

        Returns:
            Estimated token count.
        """
        if not text:
            return 0

        if self._encoding:
            try:
                return len(self._encoding.encode(text))
            except Exception:
                pass

        return self._heuristic_count(text)

    def count_messages(self, messages: list[dict]) -> int:
        """Count total tokens in a list of chat messages.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.

        Returns:
            Estimated total token count.
        """
        total = 0
        for msg in messages:
            total += self.count_text(msg.get("role", ""))
            total += self.count_text(msg.get("content", ""))
            total += 4  # overhead per message (role, content keys, formatting)
        total += 3  # priming tokens
        return total

    def _heuristic_count(self, text: str) -> int:
        """Estimate token count using character-based heuristic."""
        chars_per_token = self.CHARS_PER_TOKEN.get(self._model, self.CHARS_PER_TOKEN["default"])
        return max(1, math.ceil(len(text) / chars_per_token))

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str = "gpt-4o",
    ) -> float:
        """Estimate the cost of an API call.

        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
            model: The model name.

        Returns:
            Estimated cost in USD.
        """
        pricing = {
            "gpt-4o": (2.5e-6, 10e-6),
            "gpt-4o-mini": (0.15e-6, 0.6e-6),
            "gpt-4": (30e-6, 60e-6),
            "gpt-4-turbo": (10e-6, 30e-6),
            "gpt-3.5-turbo": (0.5e-6, 1.5e-6),
            "claude-sonnet-4-20250514": (3e-6, 15e-6),
            "claude-3-5-sonnet-20241022": (3e-6, 15e-6),
            "claude-3-haiku-20240307": (0.25e-6, 1.25e-6),
            "deepseek-chat": (0.14e-6, 0.28e-6),
            "deepseek-coder": (0.14e-6, 0.28e-6),
        }

        input_price, output_price = pricing.get(model, (3e-6, 15e-6))
        return (input_tokens * input_price) + (output_tokens * output_price)

    def format_tokens(self, count: int) -> str:
        """Format a token count for display.

        Args:
            count: Token count.

        Returns:
            Formatted string like "1.2K" or "456".
        """
        if count >= 1_000_000:
            return f"{count / 1_000_000:.1f}M"
        if count >= 1_000:
            return f"{count / 1_000:.1f}K"
        return str(count)

    def format_cost(self, cost: float) -> str:
        """Format a cost value for display.

        Args:
            cost: Cost in USD.

        Returns:
            Formatted string.
        """
        if cost < 0.01:
            return f"${cost * 1000:.2f}m"
        return f"${cost:.4f}"
