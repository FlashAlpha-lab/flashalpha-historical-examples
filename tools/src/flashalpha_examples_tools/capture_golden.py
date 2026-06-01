"""Run a LEAN backtest for an essay, capture the golden numbers + render results.

Workflow:
1. Shell out to `lean backtest essays/<essay>/<lang>/ --output <tmp>`.
2. Parse the BacktestResult.json.
3. Write golden.json (final_equity, total_trades, sharpe, max_drawdown).
4. Call render-results to produce equity-curve PNG + monthly CSV + stats JSON.

CI's `release.yml` invokes this with --all to refresh every essay's goldens
at release time. Authors invoke it per-essay during development.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from ._lean_output import BacktestResult, parse_backtest_result
from .render_results import (
    render_equity_curve_png, render_monthly_returns_csv,
    render_trade_stats_json,
)


def write_golden_json(result: BacktestResult, out_path: Path) -> None:
    data = {
        "final_equity": result.final_equity,
        "total_trades": result.total_trades,
        "sharpe": result.sharpe,
        "max_drawdown": result.max_drawdown,
    }
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def capture_golden(essay_dir: Path, language: str) -> None:
    """Run lean backtest, write golden.json + results/ artifacts."""
    lang_dir = essay_dir / language
    if not lang_dir.exists():
        raise FileNotFoundError(lang_dir)

    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td) / "out"
        cmd = ["lean", "backtest", str(lang_dir), "--output", str(out_dir)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print(proc.stdout)
            print(proc.stderr, file=sys.stderr)
            raise RuntimeError(f"lean backtest failed: {essay_dir.name}/{language}")

        # LEAN writes results to <output>/<run-id>/BacktestResult.json; the
        # exact subdir layout varies between LEAN versions, so we scan the
        # whole tempdir for the result file.
        results = list(Path(td).rglob("BacktestResult.json"))
        if not results:
            raise FileNotFoundError(f"No BacktestResult.json under {td}")
        result = parse_backtest_result(results[0])

    write_golden_json(result, lang_dir / "golden.json")

    results_dir = essay_dir / "results"
    results_dir.mkdir(exist_ok=True)
    render_equity_curve_png(result, results_dir / f"equity-curve-{language}.png",
                            title=f"{essay_dir.name} ({language})")
    render_monthly_returns_csv(result, results_dir / "monthly-returns.csv")
    render_trade_stats_json(result, results_dir / "trade-stats.json")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Capture golden numbers + results for an essay")
    p.add_argument("essay_dir")
    p.add_argument("--language", choices=["python", "csharp", "both"], default="both")
    args = p.parse_args(argv)

    essay = Path(args.essay_dir)
    langs = ["python", "csharp"] if args.language == "both" else [args.language]
    for lang in langs:
        print(f"Capturing {essay.name} ({lang})...")
        capture_golden(essay, lang)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
