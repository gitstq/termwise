"""Cost tracking utility for monitoring LLM API spending."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class CostTracker:
    """Tracks and persists LLM API usage costs.

    Stores usage data in a local JSON file for persistence across sessions.
    """

    DEFAULT_DATA_DIR = Path.home() / ".termwise"
    DEFAULT_COST_FILE = "cost_history.json"

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the cost tracker.

        Args:
            data_dir: Directory to store cost data. Defaults to ~/.termwise.
        """
        self._data_dir = data_dir or self.DEFAULT_DATA_DIR
        self._cost_file = self._data_dir / self.DEFAULT_COST_FILE
        self._history: list[dict] = []
        self._load()

    def _load(self) -> None:
        """Load cost history from file."""
        if self._cost_file.exists():
            try:
                data = json.loads(self._cost_file.read_text(encoding="utf-8"))
                self._history = data.get("history", [])
            except (json.JSONDecodeError, IOError):
                self._history = []

    def _save(self) -> None:
        """Save cost history to file."""
        self._data_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "history": self._history,
            "total_cost": self.get_total_cost(),
            "last_updated": datetime.now().isoformat(),
        }
        self._cost_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def record_usage(
        self,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        model: str = "",
        cost: Optional[float] = None,
    ) -> dict:
        """Record a single API usage event.

        Args:
            provider: The LLM provider name (e.g., 'openai', 'anthropic').
            input_tokens: Number of input tokens used.
            output_tokens: Number of output tokens used.
            model: The model name used.
            cost: Manual cost override. If None, estimated from tokens.

        Returns:
            The recorded usage entry.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": cost or 0.0,
        }
        self._history.append(entry)
        self._save()
        return entry

    def get_total_cost(self) -> float:
        """Get the total cost across all recorded usage.

        Returns:
            Total cost in USD.
        """
        return sum(entry.get("cost", 0) for entry in self._history)

    def get_total_tokens(self) -> int:
        """Get total tokens used across all sessions.

        Returns:
            Total token count.
        """
        return sum(entry.get("total_tokens", 0) for entry in self._history)

    def get_cost_by_provider(self) -> dict[str, float]:
        """Get cost breakdown by provider.

        Returns:
            Dict mapping provider names to total costs.
        """
        costs: dict[str, float] = {}
        for entry in self._history:
            provider = entry.get("provider", "unknown")
            costs[provider] = costs.get(provider, 0) + entry.get("cost", 0)
        return costs

    def get_cost_by_day(self, days: int = 30) -> dict[str, float]:
        """Get daily cost breakdown.

        Args:
            days: Number of days to look back.

        Returns:
            Dict mapping date strings (YYYY-MM-DD) to daily costs.
        """
        daily: dict[str, float] = {}
        cutoff = datetime.now() - timedelta(days=days)
        for entry in self._history:
            try:
                ts = datetime.fromisoformat(entry["timestamp"])
                if ts >= cutoff:
                    date_key = ts.strftime("%Y-%m-%d")
                    daily[date_key] = daily.get(date_key, 0) + entry.get("cost", 0)
            except (KeyError, ValueError):
                continue
        return daily

    def get_session_count(self) -> int:
        """Get the number of recorded API calls.

        Returns:
            Number of usage entries.
        """
        return len(self._history)

    def get_average_cost_per_call(self) -> float:
        """Get the average cost per API call.

        Returns:
            Average cost in USD.
        """
        if not self._history:
            return 0.0
        return self.get_total_cost() / len(self._history)

    def clear_history(self) -> None:
        """Clear all recorded cost history."""
        self._history.clear()
        self._save()

    def get_summary(self) -> str:
        """Get a human-readable cost summary.

        Returns:
            Formatted summary string.
        """
        lines = [
            "💰 Cost Summary",
            "─" * 40,
            f"  Total Cost:      ${self.get_total_cost():.4f}",
            f"  Total Tokens:    {self.get_total_tokens():,}",
            f"  API Calls:       {self.get_session_count()}",
            f"  Avg Cost/Call:   ${self.get_average_cost_per_call():.4f}",
            "",
            "  By Provider:",
        ]

        for provider, cost in sorted(
            self.get_cost_by_provider().items(), key=lambda x: x[1], reverse=True
        ):
            lines.append(f"    {provider}: ${cost:.4f}")

        recent = self.get_cost_by_day(days=7)
        if recent:
            lines.append("")
            lines.append("  Last 7 Days:")
            for date, cost in sorted(recent.items(), reverse=True):
                lines.append(f"    {date}: ${cost:.4f}")

        return "\n".join(lines)

    def export_csv(self, filepath: str) -> None:
        """Export cost history to CSV format.

        Args:
            filepath: Path to save the CSV file.
        """
        import csv

        if not self._history:
            return

        fieldnames = [
            "timestamp",
            "provider",
            "model",
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "cost",
        ]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self._history)
