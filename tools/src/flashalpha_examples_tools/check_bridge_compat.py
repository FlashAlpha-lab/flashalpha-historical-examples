"""Tier 0 validation: verify every essay's declared bridge_bars + data_endpoints
exist in the installed flashalpha-quantconnect package.

Pure metadata. No network. Runs against the installed bridge package — same
version every consumer of this repo will use.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


class BridgeMismatch(Exception):
    """Essay declares a bar or endpoint the bridge doesn't expose."""


# Hard-coded the v0.1.1 surface; update when the bridge bumps and we
# bump the bridge pin in repo-wide meta.yaml.
_PUBLISHED_BARS_V011 = frozenset({
    "GexBar", "DexBar", "VexBar", "ChexBar", "ExposureSummaryBar",
    "ExposureLevelsBar", "SurfaceBar", "ZeroDteBar", "MaxPainBar",
    "VolatilityBar", "AdvVolatilityBar", "VrpBar", "NarrativeBar",
    "StockSummaryBar", "StockQuoteBar", "OptionQuoteBar", "TickersBar",
})
# C# names — frontmatter declares C#-style class names by convention
_PUBLISHED_BARS_CSHARP = frozenset({
    "FlashAlpha" + b for b in _PUBLISHED_BARS_V011
})

_PUBLISHED_ENDPOINTS_V011 = frozenset({
    "exposure/gex", "exposure/dex", "exposure/vex", "exposure/chex",
    "exposure/summary", "exposure/levels", "surface", "exposure/zero-dte",
    "max-pain", "volatility", "adv-volatility", "vrp", "narrative",
    "stock/summary", "stock/quote", "option/quote", "tickers",
})


def get_published_bars() -> frozenset[str]:
    """All bar class names (C# style) the published bridge exposes."""
    return _PUBLISHED_BARS_CSHARP


def get_published_endpoints() -> frozenset[str]:
    """All endpoint slugs the published bridge accepts."""
    return _PUBLISHED_ENDPOINTS_V011


def check_essay_compat(slug: str, fm: dict[str, Any]) -> None:
    """Raise BridgeMismatch if essay declares an unknown bar or endpoint."""
    bars = get_published_bars()
    endpoints = get_published_endpoints()

    for bar in fm.get("bridge_bars", []):
        if bar not in bars:
            raise BridgeMismatch(
                f"{slug}: declared bar {bar!r} not in published bridge "
                f"(known: {sorted(bars)})"
            )
    for ep in fm.get("data_endpoints", []):
        if ep not in endpoints:
            raise BridgeMismatch(
                f"{slug}: declared endpoint {ep!r} not in published bridge "
                f"(known: {sorted(endpoints)})"
            )


def check_all_essays(repo: Path) -> list[str]:
    """Return list of mismatch messages across all essays. Empty = pass."""
    failures: list[str] = []
    for meta in (repo / "essays").rglob("meta.yaml"):
        fm = yaml.safe_load(meta.read_text(encoding="utf-8")) or {}
        slug = fm.get("slug", meta.parent.name)
        try:
            check_essay_compat(slug, fm)
        except BridgeMismatch as e:
            failures.append(str(e))
    return failures


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Tier 0: catalog <-> bridge compatibility")
    p.add_argument("--repo-root", default=".")
    args = p.parse_args(argv)

    failures = check_all_essays(Path(args.repo_root))
    if failures:
        for f in failures:
            print(f, file=sys.stderr)
        return 1
    print("OK - all essays declare known bars + endpoints")
    return 0


if __name__ == "__main__":
    sys.exit(main())
