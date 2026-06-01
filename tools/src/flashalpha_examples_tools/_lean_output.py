"""Parse LEAN's BacktestResult.json into a typed Python object.

LEAN's output JSON has many fields; we expose only the ones the examples
repo needs (headline stats, final equity, equity curve). Any tool that
consumes a backtest output should call parse_backtest_result and never
peek directly at the raw JSON.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


def _strip_pct(s: str) -> float:
    s = s.strip().rstrip("%")
    return float(s) / 100.0 if s else 0.0


def _to_float(s: str) -> float:
    return float(s.strip()) if s else 0.0


def _to_int(s: str) -> int:
    return int(float(s.strip())) if s else 0


@dataclass
class BacktestResult:
    """Headline numbers extracted from LEAN's BacktestResult.json."""

    final_equity: float
    initial_equity: float
    total_trades: int
    sharpe: float
    sortino: float
    max_drawdown: float          # signed negative, e.g. -0.045 for -4.5%
    equity_curve: list[tuple[int, float]] = field(default_factory=list)


def parse_backtest_result(path: Path) -> BacktestResult:
    """Parse a LEAN BacktestResult.json file at the given path."""
    if not path.exists():
        raise FileNotFoundError(f"Backtest result not found: {path}")

    raw = json.loads(path.read_text(encoding="utf-8"))

    stats = raw.get("Statistics", {})
    config = raw.get("AlgorithmConfiguration", {})

    initial = _to_float(config.get("InitialCash", "0"))

    # Equity curve from Strategy Equity chart
    equity_curve: list[tuple[int, float]] = []
    chart = raw.get("Charts", {}).get("Strategy Equity", {})
    series = chart.get("Series", {}).get("Equity", {})
    for v in series.get("Values", []):
        equity_curve.append((int(v["x"]), float(v["y"])))

    final_equity = equity_curve[-1][1] if equity_curve else initial

    return BacktestResult(
        final_equity=final_equity,
        initial_equity=initial,
        total_trades=_to_int(stats.get("Total Trades", "0")),
        sharpe=_to_float(stats.get("Sharpe Ratio", "0")),
        sortino=_to_float(stats.get("Sortino Ratio", "0")),
        # LEAN reports drawdown as a positive percent string; we store as
        # signed negative decimal for convention parity with strategy returns.
        max_drawdown=-_strip_pct(stats.get("Drawdown", "0%")),
        equity_curve=equity_curve,
    )
