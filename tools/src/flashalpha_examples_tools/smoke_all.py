"""Run Tier 2 smoke across every essay; emit roll-up report."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .smoke_algo import run_smoke, evaluate_plausibility, write_smoke_golden, PlausibilityError


@dataclass
class SmokeRollup:
    passed: int = 0
    failed: int = 0
    details: list[dict] = field(default_factory=list)


def smoke_all_essays(repo: Path) -> SmokeRollup:
    rollup = SmokeRollup()
    for theme in sorted((repo / "essays").iterdir()):
        if not theme.is_dir() or theme.name.startswith("."):
            continue
        for essay in sorted(theme.iterdir()):
            if not essay.is_dir() or essay.name.startswith(".") or not (essay / "validation").exists():
                continue
            entry = {"slug": essay.name, "status": "?", "error": None}
            try:
                result = run_smoke(essay)
                write_smoke_golden(result, essay / "validation" / "smoke-golden.json")
                evaluate_plausibility(result)
                entry["status"] = "pass"
                entry["final_equity"] = result.final_equity
                entry["total_trades"] = result.total_trades
                entry["sharpe"] = result.sharpe
                rollup.passed += 1
            except Exception as e:  # noqa: BLE001
                entry["status"] = "fail"
                entry["error"] = f"{type(e).__name__}: {e}"
                rollup.failed += 1
            rollup.details.append(entry)
    return rollup


def write_rollup_md(rollup: SmokeRollup, out: Path) -> None:
    lines = ["# Tier 2 — smoke-algorithm roll-up",
             "",
             f"Passed: {rollup.passed} / {rollup.passed + rollup.failed}",
             "",
             "| Essay | Status | Final equity | Trades | Sharpe | Error |",
             "|---|---|---|---|---|---|"]
    for d in rollup.details:
        eq = f"${d['final_equity']:,.2f}" if d.get("final_equity") else "—"
        trades = d.get("total_trades", "—")
        sh = f"{d['sharpe']:.3f}" if d.get("sharpe") is not None else "—"
        err = d.get("error") or ""
        lines.append(f"| {d['slug']} | {d['status']} | {eq} | {trades} | {sh} | {err} |")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Tier 2: smoke-test every essay")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--output", default="docs/validation/smoke-rollup.md")
    args = p.parse_args(argv)

    repo = Path(args.repo_root)
    rollup = smoke_all_essays(repo)
    out = repo / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    write_rollup_md(rollup, out)

    print(f"Rollup: {rollup.passed} passed, {rollup.failed} failed → {out}")
    return 0 if rollup.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
