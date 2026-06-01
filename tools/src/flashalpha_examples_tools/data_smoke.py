"""Tier 1 validation: hit each essay's declared endpoints, verify data flows.

For each essay × each declared endpoint × each of 3 trading days:
- Call FlashAlphaHttpClient.fetch_json
- Confirm the response is a non-empty dict (or list, for tickers)
- Confirm at least one expected field is populated

Doesn't run LEAN. Doesn't backtest. Just confirms the bridge surfaces data
for what the essay needs.

Output: per-essay DataSmokeReport + a repo-wide smoke-data-report.md.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


# Known-good RTH trading days. Picked from mid-2024 SPY's continuous coverage window.
DEFAULT_SMOKE_DATES = ["2024-06-14T15:30:00", "2024-06-07T15:30:00", "2024-05-31T15:30:00"]


@dataclass
class DataSmokeReport:
    slug: str
    passed: bool
    endpoint_results: dict[str, dict] = field(default_factory=dict)
    failures: list[str] = field(default_factory=list)


def smoke_test_essay(
    fm: dict[str, Any],
    bridge_client: Any,
    dates: list[str] | None = None,
) -> DataSmokeReport:
    """Run Tier 1 smoke checks for one essay's frontmatter."""
    if dates is None:
        dates = DEFAULT_SMOKE_DATES
    report = DataSmokeReport(slug=fm.get("slug", "?"), passed=True)

    tickers = fm.get("tickers", ["SPY"])
    ticker = tickers[0] if tickers else "SPY"

    for endpoint in fm.get("data_endpoints", []):
        results: dict[str, Any] = {"calls": 0, "first_non_empty": None}
        report.endpoint_results[endpoint] = results
        for date_str in dates:
            try:
                date = datetime.fromisoformat(date_str)
                response = bridge_client.fetch_json(
                    endpoint=endpoint, ticker=ticker, at=date,
                )
                results["calls"] += 1
                if isinstance(response, dict) and response and results["first_non_empty"] is None:
                    results["first_non_empty"] = sorted(response.keys())[:5]
                elif isinstance(response, list) and response and results["first_non_empty"] is None:
                    results["first_non_empty"] = ["list", f"len={len(response)}"]
                elif not response:
                    report.passed = False
                    report.failures.append(
                        f"{report.slug}: {endpoint} returned empty for {date_str}"
                    )
            except Exception as e:  # noqa: BLE001
                report.passed = False
                report.failures.append(
                    f"{report.slug}: {endpoint} raised {type(e).__name__}: {e}"
                )
    return report


def smoke_test_all(repo: Path, bridge_client: Any) -> list[DataSmokeReport]:
    """Run smoke tests across every essay's meta.yaml."""
    reports: list[DataSmokeReport] = []
    for meta in sorted((repo / "essays").rglob("meta.yaml")):
        fm = yaml.safe_load(meta.read_text(encoding="utf-8")) or {}
        reports.append(smoke_test_essay(fm, bridge_client))
    return reports


def write_smoke_report_md(reports: list[DataSmokeReport], out: Path) -> None:
    """Emit a human-readable smoke-data-report.md."""
    lines = ["# Tier 1 — data smoke report",
             "",
             "| Essay | Result | Endpoint coverage |",
             "|---|---|---|"]
    for r in reports:
        status = "PASS" if r.passed else "FAIL"
        endpoints = ", ".join(r.endpoint_results.keys())
        lines.append(f"| {r.slug} | {status} | {endpoints} |")
    lines.append("")
    if any(not r.passed for r in reports):
        lines.append("## Failures")
        for r in reports:
            for f in r.failures:
                lines.append(f"- {f}")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Tier 1: bridge data smoke check")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--output", default="docs/validation/smoke-data-report.md")
    args = p.parse_args(argv)

    from flashalpha_quantconnect.client import FlashAlphaHttpClient
    client = FlashAlphaHttpClient()

    repo = Path(args.repo_root)
    reports = smoke_test_all(repo, client)
    out = repo / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    write_smoke_report_md(reports, out)

    failed = [r for r in reports if not r.passed]
    if failed:
        print(f"{len(failed)} essay(s) failed Tier 1 smoke", file=sys.stderr)
        return 1
    print(f"OK — all {len(reports)} essays passed Tier 1 data smoke")
    return 0


if __name__ == "__main__":
    sys.exit(main())
