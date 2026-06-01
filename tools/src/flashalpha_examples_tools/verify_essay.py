"""Compare a LEAN BacktestResult against an essay's committed golden.json within tolerance.

Tolerances per spec §3:
- final_equity: rel=1e-4
- total_trades: exact match (logic drift = test failure)
- sharpe / sortino: abs=0.01
- max_drawdown: abs=0.005
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ._lean_output import BacktestResult, parse_backtest_result


class GoldenMismatch(Exception):
    """Backtest result drifted from the golden file beyond tolerance."""


def _rel_close(actual: float, expected: float, rel: float) -> bool:
    if expected == 0:
        return abs(actual) <= rel
    return abs(actual - expected) / abs(expected) <= rel


def _abs_close(actual: float, expected: float, tol: float) -> bool:
    return abs(actual - expected) <= tol


def verify_against_golden(result: BacktestResult, golden: dict[str, Any]) -> None:
    """Raise GoldenMismatch if result drifts from golden beyond tolerance."""
    if not _rel_close(result.final_equity, golden["final_equity"], rel=1e-4):
        raise GoldenMismatch(
            f"final_equity drift: actual={result.final_equity:.4f} "
            f"vs golden={golden['final_equity']:.4f} "
            f"(>1e-4 relative)"
        )
    if result.total_trades != golden["total_trades"]:
        raise GoldenMismatch(
            f"total_trades drift: actual={result.total_trades} "
            f"vs golden={golden['total_trades']} (exact match required)"
        )
    if not _abs_close(result.sharpe, golden["sharpe"], tol=0.01):
        raise GoldenMismatch(
            f"sharpe drift: actual={result.sharpe:.3f} "
            f"vs golden={golden['sharpe']:.3f} (>0.01 absolute)"
        )
    if not _abs_close(result.max_drawdown, golden["max_drawdown"], tol=0.005):
        raise GoldenMismatch(
            f"max_drawdown drift: actual={result.max_drawdown:.4f} "
            f"vs golden={golden['max_drawdown']:.4f} (>0.005 absolute)"
        )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Verify a LEAN backtest result against committed golden")
    p.add_argument("essay_dir", help="Essay directory containing python/golden.json or csharp/golden.json")
    p.add_argument("backtest_output", help="LEAN BacktestResult.json")
    p.add_argument("--language", choices=["python", "csharp"], required=True)
    args = p.parse_args(argv)

    essay = Path(args.essay_dir)
    golden_path = essay / args.language / "golden.json"
    golden = json.loads(golden_path.read_text(encoding="utf-8"))
    if not golden:
        print(f"{golden_path} is empty — draft essay, skipping verification", file=sys.stderr)
        return 0

    result = parse_backtest_result(Path(args.backtest_output))
    try:
        verify_against_golden(result, golden)
    except GoldenMismatch as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print(f"OK — {essay.name} ({args.language}) matches golden")
    return 0


if __name__ == "__main__":
    sys.exit(main())
