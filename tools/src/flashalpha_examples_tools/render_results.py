"""Render LEAN BacktestResult into the four committed artifacts:
equity-curve-<lang>.png, monthly-returns.csv, trade-stats.json, parameter-sweep.csv.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import pandas as pd

from ._lean_output import BacktestResult, parse_backtest_result


def render_equity_curve_png(result: BacktestResult, out_path: Path, title: str = "") -> None:
    if not result.equity_curve:
        # Write a placeholder image so the file exists for the README embed
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.text(0.5, 0.5, "No equity curve yet (draft essay)",
                ha="center", va="center", fontsize=14)
        ax.axis("off")
        fig.savefig(out_path, dpi=120, bbox_inches="tight")
        plt.close(fig)
        return

    ts = [datetime.fromtimestamp(t, tz=timezone.utc) for t, _ in result.equity_curve]
    eq = [v for _, v in result.equity_curve]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(ts, eq, linewidth=1.4)
    ax.axhline(result.initial_equity, color="gray", linestyle="--", linewidth=0.8, label="Initial cash")
    ax.set_title(title or "Strategy equity curve")
    ax.set_xlabel("Date")
    ax.set_ylabel("Equity (USD)")
    ax.legend(loc="best")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def render_monthly_returns_csv(result: BacktestResult, out_path: Path) -> None:
    if not result.equity_curve:
        out_path.write_text("month,return\n", encoding="utf-8")
        return
    df = pd.DataFrame(result.equity_curve, columns=["ts", "equity"])
    df["date"] = pd.to_datetime(df["ts"], unit="s", utc=True)
    df = df.set_index("date").drop(columns=["ts"])
    monthly = df["equity"].resample("ME").last().pct_change().dropna()
    monthly.index = monthly.index.strftime("%Y-%m")
    monthly.index.name = "month"
    monthly.to_csv(out_path, header=["return"])


def render_trade_stats_json(result: BacktestResult, out_path: Path) -> None:
    data = {
        "final_equity": result.final_equity,
        "initial_equity": result.initial_equity,
        "total_trades": result.total_trades,
        "sharpe": result.sharpe,
        "sortino": result.sortino,
        "max_drawdown": result.max_drawdown,
        "total_return_pct": (result.final_equity / result.initial_equity - 1.0) * 100 if result.initial_equity else 0.0,
    }
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def render_parameter_sweep_csv(rows: list[dict], out_path: Path) -> None:
    """Each row: {parameter_value: ..., final_equity: ..., sharpe: ...}."""
    if not rows:
        out_path.write_text("parameter_value,final_equity,sharpe\n", encoding="utf-8")
        return
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Render LEAN backtest output into committed artifacts")
    p.add_argument("essay_dir")
    p.add_argument("backtest_output")
    p.add_argument("--language", choices=["python", "csharp"], required=True)
    args = p.parse_args(argv)

    essay = Path(args.essay_dir)
    result = parse_backtest_result(Path(args.backtest_output))
    results_dir = essay / "results"
    results_dir.mkdir(exist_ok=True)

    render_equity_curve_png(result, results_dir / f"equity-curve-{args.language}.png",
                            title=f"{essay.name} ({args.language})")
    render_monthly_returns_csv(result, results_dir / "monthly-returns.csv")
    render_trade_stats_json(result, results_dir / "trade-stats.json")
    print(f"Rendered results for {essay.name} ({args.language})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
