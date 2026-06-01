"""Tier 2 validation: minimal LEAN algorithm per essay + plausibility checks.

For each essay, the author writes a small (20-30 LOC) algorithm at
essays/<theme>/<NN-slug>/validation/main.py implementing the simplest
version of the technique. The harness:
  1. Runs `lean backtest essays/<essay>/validation/`
  2. Parses the BacktestResult.json
  3. Writes smoke-golden.json (tagged tier: smoke)
  4. Asserts plausibility: equity within [0.5x, 3.0x] of start; non-zero trades
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from ._lean_output import BacktestResult, parse_backtest_result


class PlausibilityError(Exception):
    """Smoke result violates basic sanity envelope."""


# Equity should not 10x or wipe to zero in a small smoke window. Generous
# bounds — this is a "is it broken?" check, not a "is it good?" check.
EQUITY_LOWER_RATIO = 0.5    # 50% of starting cash
EQUITY_UPPER_RATIO = 3.0    # 300% of starting cash


def evaluate_plausibility(r: BacktestResult) -> None:
    """Raise PlausibilityError if result is not a plausible smoke run."""
    if r.initial_equity == 0:
        raise PlausibilityError("initial_equity is zero — config issue")
    ratio = r.final_equity / r.initial_equity
    if ratio < EQUITY_LOWER_RATIO or ratio > EQUITY_UPPER_RATIO:
        raise PlausibilityError(
            f"final_equity ratio {ratio:.3f} outside plausibility envelope "
            f"[{EQUITY_LOWER_RATIO}, {EQUITY_UPPER_RATIO}] — likely algorithm bug"
        )
    if r.total_trades == 0:
        raise PlausibilityError(
            "total_trades=0 — smoke algorithm should produce at least one trade "
            "(else gate logic never fired)"
        )


def write_smoke_golden(r: BacktestResult, out_path: Path) -> None:
    """Write smoke-golden.json with tier marker so it's distinguishable from a real golden."""
    data = {
        "tier": "smoke",
        "final_equity": r.final_equity,
        "initial_equity": r.initial_equity,
        "total_trades": r.total_trades,
        "sharpe": r.sharpe,
        "max_drawdown": r.max_drawdown,
    }
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run_smoke(essay_dir: Path) -> BacktestResult:
    """Run lean backtest on essay/validation/, return BacktestResult."""
    val = essay_dir / "validation"
    if not val.exists():
        raise FileNotFoundError(f"{essay_dir}/validation/ not found")

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out"
        cmd = ["lean", "backtest", str(val), "--output", str(out)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
            raise RuntimeError(f"lean backtest failed: {essay_dir.name}")

        results = list(Path(td).rglob("BacktestResult.json"))
        if not results:
            raise FileNotFoundError(f"No BacktestResult.json under {td}")
        return parse_backtest_result(results[0])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Tier 2: smoke-algorithm runner")
    p.add_argument("essay_dir")
    p.add_argument("--skip-plausibility", action="store_true",
                   help="Capture the smoke golden even if plausibility fails (for inspection)")
    args = p.parse_args(argv)

    essay = Path(args.essay_dir)
    result = run_smoke(essay)
    out = essay / "validation" / "smoke-golden.json"
    write_smoke_golden(result, out)

    try:
        evaluate_plausibility(result)
    except PlausibilityError as e:
        if args.skip_plausibility:
            print(f"WARN: {e}", file=sys.stderr)
            return 0
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print(f"OK — {essay.name} smoke passed. Golden at {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
