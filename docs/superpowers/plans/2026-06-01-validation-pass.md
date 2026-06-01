# Pre-Implementation Validation Pass

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Validate all 21 essay concepts against the real bridge + real API + real LEAN before sinking the main 40-task implementation plan. Produce evidence (numbers, smoke goldens) so v0.1.0 ships with "21 strategies, all backtested" rather than "1 strategy + 20 unverified stubs."

**Architecture:** Three escalating tiers. **Tier 0** (static) — verify declared bridge bars / endpoints exist in `flashalpha-quantconnect 0.1.1`; metadata-only, no network. **Tier 1** (data) — for each essay, hit the bridge endpoints for 3 trading days; confirm data flows + key fields populated. **Tier 2** (algorithm) — minimal 20-30 line LEAN algorithm per essay, 1-2 month backtest, capture smoke-goldens. Each essay grows a `validation/` subdir alongside `python/` / `csharp/` / `results/`; smoke-golden seeds the eventual stable golden.

**Tech Stack:** Python 3.10+ (`flashalpha-examples-tools`), `flashalpha-quantconnect 0.1.1`, `lean` CLI (Docker-backed). Same toolchain as the main plan.

**Relationship to the main plan:** This validation plan runs FIRST. On completion, the main plan's Phase 2 (Tasks 16+) starts with smoke-validated essays — drafts ship with real numbers, the flagship's full implementation proceeds with confidence in the surrounding catalog.

**Spec reference:** [docs/superpowers/specs/2026-05-30-flashalpha-historical-examples-design.md](../specs/2026-05-30-flashalpha-historical-examples-design.md)
**Main plan reference:** [docs/superpowers/plans/2026-06-01-flashalpha-historical-examples.md](2026-06-01-flashalpha-historical-examples.md)

---

## Conventions

- **TDD cycle per task:** failing test → run → minimal impl → run passes → commit. As in the main plan.
- **Commits:** one per task. `feat(validation):` prefix for tools, `validate(<essay-slug>):` for per-essay smoke tests.
- **Working directory:** `e:/repos/tecware/flashalpha-packages/flashalpha-historical-examples/`.
- **API key:** Tier 1+2 tasks need `FLASHALPHA_API_KEY` in env. CI not used for this plan — runs locally first.
- **Per-essay `validation/` directory:** new subdir under each essay folder, holds `smoke.py` + `smoke-golden.json` + optional `smoke-equity.png`.

---

## Phase V0 — Validation tooling (5 tasks)

### Task V1: bridge-compat tool (Tier 0)

**Files:**
- Create: `tools/src/flashalpha_examples_tools/check_bridge_compat.py`
- Create: `tools/tests/test_check_bridge_compat.py`

Verify every essay's `bridge_bars` + `data_endpoints` exist in the installed `flashalpha-quantconnect` package.

- [ ] **Step 1: Write the failing tests**

`tools/tests/test_check_bridge_compat.py`:

```python
import pytest

from flashalpha_examples_tools.check_bridge_compat import (
    BridgeMismatch, get_published_bars, get_published_endpoints,
    check_essay_compat,
)


def test_get_published_bars_returns_known_set():
    bars = get_published_bars()
    assert "FlashAlphaGexBar" in bars
    assert "FlashAlphaSurfaceBar" in bars
    assert "FlashAlphaZeroDteBar" in bars
    # 17 bars in 0.1.1
    assert len(bars) >= 17


def test_get_published_endpoints_returns_known_set():
    eps = get_published_endpoints()
    assert "exposure/gex" in eps
    assert "exposure/zero-dte" in eps
    assert "max-pain" in eps
    # 17 endpoints
    assert len(eps) >= 17


def test_essay_with_known_bars_passes():
    fm = {"bridge_bars": ["FlashAlphaGexBar"], "data_endpoints": ["exposure/gex"]}
    check_essay_compat("test", fm)  # no exception


def test_essay_with_unknown_bar_fails():
    fm = {"bridge_bars": ["FlashAlphaFakeBar"], "data_endpoints": []}
    with pytest.raises(BridgeMismatch, match="FlashAlphaFakeBar"):
        check_essay_compat("test", fm)


def test_essay_with_unknown_endpoint_fails():
    fm = {"bridge_bars": [], "data_endpoints": ["exposure/nope"]}
    with pytest.raises(BridgeMismatch, match="exposure/nope"):
        check_essay_compat("test", fm)
```

- [ ] **Step 2: Run to fail**

```bash
cd tools && pytest tests/test_check_bridge_compat.py -v
```
Expected: ImportError.

- [ ] **Step 3: Write `check_bridge_compat.py`**

```python
"""Tier 0 validation: verify every essay's declared bridge_bars + data_endpoints
exist in the installed flashalpha-quantconnect package.

Pure metadata. No network. Runs against the installed bridge package — same
version every consumer of this repo will use.
"""

from __future__ import annotations

import argparse
import importlib
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
    p = argparse.ArgumentParser(description="Tier 0: catalog ↔ bridge compatibility")
    p.add_argument("--repo-root", default=".")
    args = p.parse_args(argv)

    failures = check_all_essays(Path(args.repo_root))
    if failures:
        for f in failures:
            print(f, file=sys.stderr)
        return 1
    print("OK — all essays declare known bars + endpoints")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to PASS**

```bash
pytest tests/test_check_bridge_compat.py -v
```
Expected: 5 PASS.

- [ ] **Step 5: Add CLI entry point to pyproject**

Append to `[project.scripts]` in `tools/pyproject.toml`:

```toml
fa-check-bridge-compat = "flashalpha_examples_tools.check_bridge_compat:main"
```

- [ ] **Step 6: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(validation): check-bridge-compat — Tier 0 essay↔bridge metadata check

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task V2: data-smoke tool (Tier 1)

**Files:**
- Create: `tools/src/flashalpha_examples_tools/data_smoke.py`
- Create: `tools/tests/test_data_smoke.py`

For each essay, hit each declared endpoint for 3 known-good trading days. Verify non-empty responses + key fields populated. No LEAN involved.

- [ ] **Step 1: Write the failing tests**

```python
from unittest.mock import MagicMock
import pytest

from flashalpha_examples_tools.data_smoke import (
    smoke_test_essay, DataSmokeReport,
)


@pytest.fixture
def fake_bridge_client():
    """A fake bridge client that returns a populated dict per endpoint."""
    client = MagicMock()
    client.fetch_json.return_value = {"symbol": "SPY", "underlying_price": 540.0, "net_gex": 1e9, "as_of": "2024-06-14T15:30:00"}
    return client


def test_smoke_passes_when_all_endpoints_return_data(fake_bridge_client):
    fm = {"slug": "test", "data_endpoints": ["exposure/gex"], "tickers": ["SPY"]}
    report = smoke_test_essay(fm, fake_bridge_client, dates=["2024-06-14"])
    assert isinstance(report, DataSmokeReport)
    assert report.passed
    assert report.endpoint_results["exposure/gex"]["calls"] == 1


def test_smoke_fails_when_endpoint_returns_empty():
    client = MagicMock()
    client.fetch_json.return_value = {}
    fm = {"slug": "test", "data_endpoints": ["exposure/gex"], "tickers": ["SPY"]}
    report = smoke_test_essay(fm, client, dates=["2024-06-14"])
    assert not report.passed
    assert "empty" in report.failures[0].lower()


def test_smoke_handles_exception_gracefully():
    client = MagicMock()
    client.fetch_json.side_effect = RuntimeError("connection refused")
    fm = {"slug": "test", "data_endpoints": ["exposure/gex"], "tickers": ["SPY"]}
    report = smoke_test_essay(fm, client, dates=["2024-06-14"])
    assert not report.passed
    assert "RuntimeError" in report.failures[0] or "connection refused" in report.failures[0]
```

- [ ] **Step 2: Run to fail**

```bash
cd tools && pytest tests/test_data_smoke.py -v
```
Expected: ImportError.

- [ ] **Step 3: Write `data_smoke.py`**

```python
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
        status = "✅" if r.passed else "❌"
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
```

- [ ] **Step 4: Run tests to PASS**

```bash
pytest tests/test_data_smoke.py -v
```
Expected: 3 PASS.

- [ ] **Step 5: Add CLI entry point**

```toml
fa-data-smoke = "flashalpha_examples_tools.data_smoke:main"
```

- [ ] **Step 6: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(validation): data-smoke — Tier 1 endpoint data-flow check

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task V3: smoke-algorithm harness (Tier 2 scaffold)

**Files:**
- Create: `tools/src/flashalpha_examples_tools/smoke_algo.py`
- Create: `tools/tests/test_smoke_algo.py`

Per-essay smoke-algorithm runner. Each essay gets a `validation/smoke.py` (minimal LEAN algorithm) + `validation/smoke-golden.json`. The harness runs the smoke algorithm, captures the headline numbers, and writes the smoke-golden.

- [ ] **Step 1: Write the failing tests**

```python
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from flashalpha_examples_tools.smoke_algo import (
    write_smoke_golden, evaluate_plausibility, PlausibilityError,
)
from flashalpha_examples_tools._lean_output import BacktestResult


def _bt(**kw):
    base = dict(final_equity=100_500.0, initial_equity=100_000.0,
                total_trades=5, sharpe=0.3, sortino=0.45,
                max_drawdown=-0.015, equity_curve=[])
    base.update(kw)
    return BacktestResult(**base)


def test_write_smoke_golden_includes_tier(tmp_path: Path):
    out = tmp_path / "smoke-golden.json"
    write_smoke_golden(_bt(), out)
    data = json.loads(out.read_text())
    assert data["tier"] == "smoke"
    assert data["final_equity"] == 100_500.0
    assert data["total_trades"] == 5


def test_plausibility_passes_for_sensible_run():
    evaluate_plausibility(_bt())  # no exception


def test_plausibility_fails_when_equity_explodes():
    with pytest.raises(PlausibilityError, match="final_equity"):
        evaluate_plausibility(_bt(final_equity=10_000_000.0))


def test_plausibility_fails_when_equity_zeroed():
    with pytest.raises(PlausibilityError, match="final_equity"):
        evaluate_plausibility(_bt(final_equity=10.0))


def test_plausibility_fails_when_no_trades_and_no_position():
    with pytest.raises(PlausibilityError, match="trades"):
        evaluate_plausibility(_bt(total_trades=0))
```

- [ ] **Step 2: Run to fail**

```bash
cd tools && pytest tests/test_smoke_algo.py -v
```
Expected: ImportError.

- [ ] **Step 3: Write `smoke_algo.py`**

```python
"""Tier 2 validation: minimal LEAN algorithm per essay + plausibility checks.

For each essay, the author writes a small (20-30 LOC) algorithm at
essays/<theme>/<NN-slug>/validation/smoke.py implementing the simplest
version of the technique. The harness:
  1. Runs `lean backtest essays/<essay>/validation/`
  2. Parses the BacktestResult.json
  3. Writes smoke-golden.json (tagged tier: smoke)
  4. Asserts plausibility: equity within [0.5×, 2.0×] of start; non-zero trades
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


# Equity should not 10× or wipe to zero in a small smoke window. Generous
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

        results = list(out.rglob("BacktestResult.json"))
        if not results:
            raise FileNotFoundError(f"No BacktestResult.json under {out}")
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
```

- [ ] **Step 4: Run tests to PASS**

```bash
pytest tests/test_smoke_algo.py -v
```
Expected: 5 PASS.

- [ ] **Step 5: Add CLI entry point**

```toml
fa-smoke = "flashalpha_examples_tools.smoke_algo:main"
```

- [ ] **Step 6: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(validation): smoke-algo — Tier 2 minimal-algorithm runner + plausibility check

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task V4: Per-essay smoke template

**Files:**
- Modify: `tools/src/flashalpha_examples_tools/new_essay.py` (extend scaffolder to create `validation/` subdir)

Extend the new-essay scaffolder to drop a `validation/` subdir with a stub `smoke.py` template ready for the implementer to fill in.

- [ ] **Step 1: Update `scaffold_essay()` in `tools/src/flashalpha_examples_tools/new_essay.py`**

Insert after the existing `(essay_dir / "results").mkdir()` line:

```python
(essay_dir / "validation").mkdir()

# Smoke algorithm template — author fills in the actual logic
(essay_dir / "validation" / "main.py").write_text(
    f'''"""SMOKE algorithm for {title}.

Tier 2 feasibility check, not the real strategy. 20-30 lines, minimal logic.
Goal: prove the data flows + the basic gating produces sensible numbers
over a short window.

Real algorithm lives at ../python/main.py — promoted from this smoke when
the essay flips to status: stable.
"""

from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect import Resolution, SecurityType, Market
from flashalpha_quantconnect import GexBar, add_flashalpha_gex


class Algorithm(QCAlgorithm):
    def Initialize(self):
        # 30-day window — fast, enough to fire gating logic multiple times
        self.SetStartDate(2024, 6, 3)
        self.SetEndDate(2024, 7, 5)
        self.SetCash(100_000)
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.gex_symbol = add_flashalpha_gex(self, "SPY").Symbol

    def OnData(self, slice):
        # Replace with the smoke version of {title}'s gating logic.
        # Keep it minimal — this is a feasibility check, not a real strategy.
        if self.gex_symbol not in slice:
            return
        gex = slice[self.gex_symbol]
        if not isinstance(gex, GexBar):
            return
        if gex.NetGexLabel == "positive":
            self.SetHoldings(self.spy, 1.0)
        else:
            self.Liquidate(self.spy)
''',
    encoding="utf-8",
)

(essay_dir / "validation" / "config.json").write_text(
    '{"environment": "backtesting", "algorithm-language": "Python", "algorithm-location": "main.py"}\n',
    encoding="utf-8",
)
(essay_dir / "validation" / "lean.json").write_text(
    '{"algorithm-language": "Python", "algorithm-location": "main.py"}\n',
    encoding="utf-8",
)
(essay_dir / "validation" / "requirements.txt").write_text(
    "flashalpha-quantconnect==0.1.1\n", encoding="utf-8",
)
# smoke-golden.json starts empty; populated by `fa-smoke`
(essay_dir / "validation" / "smoke-golden.json").write_text("{}\n", encoding="utf-8")
```

Also extend `REQUIRED_DIRS` in `check_orphans.py` to include `validation`:

```python
REQUIRED_DIRS = ["python", "csharp", "results", "validation"]
```

And `REQUIRED_FILES`:

```python
REQUIRED_FILES = [
    "README.md", "meta.yaml", "references.md",
    "python/lean.json", "python/config.json", "python/main.py",
    "python/golden.json", "python/requirements.txt",
    "csharp/lean.json", "csharp/config.json", "csharp/Main.cs",
    "csharp/golden.json",
    "validation/lean.json", "validation/config.json", "validation/main.py",
    "validation/smoke-golden.json",
]
```

- [ ] **Step 2: Update test fixtures**

Update `tools/tests/test_check_orphans.py` fixture `essay_dir` to scaffold `validation/`:

```python
# Add inside the fixture, alongside the python/, csharp/, results/ setup:
(d / "validation").mkdir()
(d / "validation" / "main.py").write_text("# stub\n")
(d / "validation" / "config.json").write_text("{}\n")
(d / "validation" / "lean.json").write_text("{}\n")
(d / "validation" / "smoke-golden.json").write_text("{}\n")
```

- [ ] **Step 3: Run all tools tests**

```bash
cd tools && pytest -v
```
Expected: all PASS, including the existing check_orphans/new_essay tests with the extended shape.

- [ ] **Step 4: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(validation): extend new-essay + check-orphans for validation/ subdir

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task V5: Bulk smoke runner

**Files:**
- Create: `tools/src/flashalpha_examples_tools/smoke_all.py`
- Create: `tools/tests/test_smoke_all.py`

Run `fa-smoke` for every essay sequentially, emit a roll-up report.

- [ ] **Step 1: Write failing test**

```python
from pathlib import Path
from unittest.mock import patch

import pytest

from flashalpha_examples_tools.smoke_all import smoke_all_essays, SmokeRollup


def test_smoke_all_visits_every_essay(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "essays" / "a-dealer-positioning" / "01-x" / "validation").mkdir(parents=True)
    (repo / "essays" / "a-dealer-positioning" / "02-y" / "validation").mkdir(parents=True)

    calls = []
    def fake_run(d):
        calls.append(d.name)
        from flashalpha_examples_tools._lean_output import BacktestResult
        return BacktestResult(final_equity=101_000, initial_equity=100_000,
                              total_trades=3, sharpe=0.2, sortino=0.3,
                              max_drawdown=-0.01, equity_curve=[])

    with patch("flashalpha_examples_tools.smoke_all.run_smoke", side_effect=fake_run):
        rollup = smoke_all_essays(repo)
    assert isinstance(rollup, SmokeRollup)
    assert set(calls) == {"01-x", "02-y"}
    assert rollup.passed == 2
    assert rollup.failed == 0
```

- [ ] **Step 2: Run to fail**

```bash
cd tools && pytest tests/test_smoke_all.py -v
```
Expected: ImportError.

- [ ] **Step 3: Write `smoke_all.py`**

```python
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
```

- [ ] **Step 4: Run test to PASS**

```bash
pytest tests/test_smoke_all.py -v
```

- [ ] **Step 5: Add CLI entry point**

```toml
fa-smoke-all = "flashalpha_examples_tools.smoke_all:main"
```

- [ ] **Step 6: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(validation): smoke-all — bulk Tier 2 runner with roll-up

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase V1 — Run Tier 0 + Tier 1 (2 tasks)

### Task V6: Run Tier 0 (static feasibility) across all 21 essays

- [ ] **Step 1: Scaffold all 21 essays via the existing fa-new-essay** (if not done by main plan Task 16 yet)

```bash
# Same 21 commands as main plan Task 16 — see that for the full list
fa-new-essay --theme dealer-positioning --slug gamma-scalping --title "..." --number 1
# ... 20 more
```

- [ ] **Step 2: Run Tier 0 check**

```bash
fa-check-bridge-compat --repo-root .
```
Expected: `OK — all essays declare known bars + endpoints`.

If FAIL, the essay's `meta.yaml` declares a bar or endpoint not in `flashalpha-quantconnect 0.1.1`. Fix by:
- Renaming the bar to a published one (e.g., `FlashAlphaExpsoreSummaryBar` → `FlashAlphaExposureSummaryBar`)
- Replacing the endpoint with one that exists
- OR: opening a bridge PR to add the missing bar/endpoint, then bumping the bridge pin (out of this plan's scope)

- [ ] **Step 3: Commit any catalog corrections surfaced by Tier 0**

```bash
git add essays/*/[0-9]*/meta.yaml essays/*/[0-9]*/README.md
git commit -m "fix(catalog): align essay frontmatter with published bridge surface

Tier 0 surfaced X essays declaring bars or endpoints the bridge doesn't
expose at v0.1.1. Corrected to match the published surface.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

If Tier 0 passes cleanly, no commit needed.

---

### Task V7: Run Tier 1 (data smoke) across all 21 essays

- [ ] **Step 1: Set API key**

```bash
export FLASHALPHA_API_KEY=$(sed 's/\xef\xbb\xbf//' "e:/repos/tecware/flashalpha-packages/flashalpha-js/.env.test.local" \
  | grep 'FLASHALPHA_API_KEY=' | head -1 | cut -d= -f2- | tr -d '"\r\n' | tr -d "'")
```

- [ ] **Step 2: Run Tier 1 smoke**

```bash
fa-data-smoke --repo-root . --output docs/validation/smoke-data-report.md
```
Expected: takes ~2-5 minutes (21 essays × ~2 endpoints × 3 dates × ~1s per call). Output:
`OK — all 21 essays passed Tier 1 data smoke`.

- [ ] **Step 3: Review the report**

```bash
cat docs/validation/smoke-data-report.md
```
Inspect any ❌ rows. Common failures:
- "endpoint X returned empty for date Y" → API tier restriction (essay needs Alpha+ tier; document in essay README)
- "RuntimeError: …" → network or bridge bug (escalate to bridge issue tracker)

Fix or document per-essay. If unfixable for an essay (e.g., bridge gap), mark essay's frontmatter `status: deprecated` with `replaced_by` pointing at an alternative, OR remove from the catalog entirely.

- [ ] **Step 4: Commit the report + any catalog fixes**

```bash
git add docs/validation/smoke-data-report.md essays/
git commit -m "validate(tier-1): all 21 essays — data smoke report committed

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase V2 — Run Tier 2 (algorithm smoke) per essay (21 tasks)

### Task V8: Tier 2 smoke for `01-gamma-scalping`

The flagship's smoke is the simplest case — same algorithm as the eventual stable, just on a shorter window.

- [ ] **Step 1: Implement `validation/main.py`**

Replace the scaffolder template with the minimal gamma-scalping smoke:

```python
"""SMOKE: gamma scalping — minimal 30-day version.

The real algorithm at ../python/main.py runs the same logic over a longer
window with parameter sweeps. This smoke proves the gate + data + LEAN
plumbing work end-to-end on a short window.
"""

from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect import Resolution
from flashalpha_quantconnect import GexBar, add_flashalpha_gex


class Algorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2024, 6, 3)
        self.SetEndDate(2024, 7, 5)
        self.SetCash(100_000)
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.gex_symbol = add_flashalpha_gex(self, "SPY").Symbol

    def OnData(self, slice):
        if self.gex_symbol not in slice:
            return
        gex = slice[self.gex_symbol]
        if not isinstance(gex, GexBar):
            return
        if gex.NetGexLabel == "positive":
            self.SetHoldings(self.spy, 1.0)
        else:
            self.Liquidate(self.spy)
```

- [ ] **Step 2: Run smoke**

```bash
fa-smoke essays/a-dealer-positioning/01-gamma-scalping/
```
Expected: `OK — 01-gamma-scalping smoke passed. Golden at .../validation/smoke-golden.json`.

If FAIL with PlausibilityError:
- Inspect `final_equity` / `total_trades` / `sharpe` from the captured smoke-golden
- Most likely cause: regime never flipped during the 30-day window → no trades → `PlausibilityError: total_trades=0`
- Mitigation: widen the window, or pick a date range known to span both regimes

- [ ] **Step 3: Inspect + observe**

```bash
cat essays/a-dealer-positioning/01-gamma-scalping/validation/smoke-golden.json
```
Confirm numbers are sensible (final_equity in 100k–110k range, trades > 0, sharpe finite).

- [ ] **Step 4: Commit**

```bash
git add essays/a-dealer-positioning/01-gamma-scalping/validation/
git commit -m "validate(tier-2/gamma-scalping): smoke algorithm + captured smoke-golden

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task V9 – V27: Tier 2 smoke for essays 02-20

For each remaining essay, repeat the V8 workflow with the appropriate minimal algorithm. The technique-specific algorithm is the variable — the workflow is the same.

**Workflow per essay:**
1. Write `validation/main.py` — minimal 20-30 line algorithm implementing the simplest version of the technique. Use 30-day window `2024-06-03 → 2024-07-05` unless the technique needs a specific date range (e.g., earnings, 0DTE Fridays).
2. Run `fa-smoke essays/<theme>/<NN-slug>/`.
3. Inspect smoke-golden + observe whether numbers make sense for the technique.
4. If `PlausibilityError`: diagnose (no trades / equity exploded / equity wiped). Fix the algorithm or widen the window.
5. Commit when smoke passes.

**Per-essay smoke algorithm sketches** — guidance for each, paired with the bridge bars to use:

#### V9: `02-gex-regime-following` (dealer-positioning)
Subscribe `GexBar`. Gate SPY 100% holdings on `NetGexLabel == "positive"`. Identical pattern to gamma-scalping but no surface dependency. (Already done in real form by the earlier smoke test — adapt to 30-day window.)

#### V10: `03-gamma-flip-strike` (dealer-positioning)
Subscribe `GexBar`. Use `GammaFlip` field. When SPY price approaches gamma flip from above, short delta; from below, long delta. Trade SPY around the flip level via SetHoldings ±0.5.

#### V11: `04-negative-gamma-vol-expansion` (dealer-positioning)
Subscribe `GexBar`. When `NetGexLabel == "negative"`, expect vol expansion — hold a long volatility proxy (long SPY straddle would require options; for smoke use simple SPY long when regime negative + drawdown threshold).

#### V12: `05-pin-risk-avoidance-0dte` (dealer-positioning)
Subscribe `ZeroDteBar` + `MaxPainBar`. On Fridays (0DTE day), check `pin_risk` and `max_pain_strike`. If pin risk high and spot within X% of max-pain strike, liquidate SPY overnight.

#### V13: `06-charm-flow-afternoon` (vanna-charm-vex)
Subscribe `ChexBar`. Afternoon time gate (after 14:00 ET) — when `NetChex < threshold`, expect drift towards top OI strike. Trade SPY long in the last hour on those days. (Hourly resolution needed; smoke uses daily and approximates by `NetChex` sign.)

#### V14: `07-vanna-shock-reversal` (vanna-charm-vex)
Subscribe `VexBar` + `GexBar`. When `NetVex` flips sign sharply day-over-day AND regime is negative-gamma, short SPY for 3-day mean reversion. Track previous-day NetVex.

#### V15: `08-combined-greek-regime-grid` (vanna-charm-vex)
Subscribe `GexBar` + `DexBar` + `VexBar`. 8-state regime grid (each greek sign × 2). Long SPY only in the state where GEX positive, DEX positive, VEX positive.

#### V16: `09-vrp-harvest-short-vol` (vrp-volatility)
Subscribe `VrpBar`. When `VrpCore.Vrp > 0.05` (implied richer than realized), proxy short-vol via SPY long (volatility-suppressed regime).

#### V17: `10-iv-rank-entry-filter` (vrp-volatility)
Subscribe `VolatilityBar`. Compute IV rank from `AtmIv` against a rolling window. Long SPY only when IV rank is in bottom quintile (cheap vol).

#### V18: `11-realized-vs-implied-divergence` (vrp-volatility)
Subscribe `VolatilityBar`. Compare `AtmIv` to recent realized vol from SPY price history. When realized > implied by threshold, expect mean reversion in vol — long SPY (long-vol proxy).

#### V19: `12-vol-term-structure-spread` (vrp-volatility)
Subscribe `VolatilityBar`. Use `TermStructure` field. When front-month IV > back-month IV by threshold (backwardation), short SPY (stress regime). When contango steep, long SPY.

#### V20: `13-friday-gamma-squeeze` (zero-dte)
Subscribe `ZeroDteBar`. On Fridays only, when `Hedging.dealer_shares_to_trade > threshold`, long SPY into the close (front-running dealer demand).

#### V21: `14-pin-gravitation` (zero-dte)
Subscribe `MaxPainBar` + `ZeroDteBar`. On Friday open, if SPY price > max_pain_strike + threshold, short SPY (gravitating down). If <, long SPY (gravitating up).

#### V22: `15-intraday-gamma-flip` (zero-dte)
Subscribe `GexBar` at hourly resolution (smoke can use daily). When current price crosses `GammaFlip` strike intraday, fade the move (mean revert).

#### V23: `16-expected-move-straddle` (zero-dte)
Subscribe `ZeroDteBar` + `ExposureSummaryBar`. Use `expected_move` field. Hold SPY only when expected move < realized move recent average (low-realized regime).

#### V24: `17-dispersion-spy-vs-rty` (cross-signal)
Subscribe `VrpBar` for SPY + IWM. When IWM VRP > SPY VRP + threshold (constituents richer than index), long SPY / short IWM dispersion play. Smoke: long SPY when condition met.

#### V25: `18-calendar-carry-positive-gamma` (cross-signal)
Subscribe `GexBar` + `VolatilityBar`. On positive-gamma days, hold a long-front-short-back vol proxy (smoke: long SPY when GEX positive + IV term contango).

#### V26: `19-max-pain-reversion` (cross-signal)
Subscribe `MaxPainBar`. When `signal` is "bullish" and SPY < max_pain_strike, long SPY (expects reversion up). Reverse for bearish + above max-pain.

#### V27: `20-earnings-vol-contraction` (cross-signal)
Subscribe `VolatilityBar` for SPY (proxy — real impl would target specific names with earnings). Smoke: short SPY when AtmIv > rolling-30d average + threshold (high-vol regime, expect contraction).

---

### Task V28: Run bulk Tier 2 + emit roll-up

After V8–V27 are each green, do a clean bulk run:

- [ ] **Step 1: Run bulk smoke**

```bash
fa-smoke-all --repo-root . --output docs/validation/smoke-rollup.md
```
Expected: `Rollup: 21 passed, 0 failed → docs/validation/smoke-rollup.md`.

- [ ] **Step 2: Inspect roll-up**

```bash
cat docs/validation/smoke-rollup.md
```
Confirm every essay row shows pass + sensible numbers + non-zero trades + finite sharpe.

- [ ] **Step 3: Commit roll-up**

```bash
git add docs/validation/smoke-rollup.md
git commit -m "validate(tier-2): roll-up — 21/21 essays passed smoke

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task V29: Seed each draft's `golden.json` with smoke-golden

The point of Tier 2 was so every draft ships with real numbers, not empty `{}`. Copy each essay's `validation/smoke-golden.json` into both `python/golden.json` and `csharp/golden.json` — keeping the `tier: smoke` marker so they're distinguishable from real stable goldens.

- [ ] **Step 1: Seed all draft goldens**

```bash
for essay in essays/*/[0-9]*; do
  # Skip flagship — it gets real goldens in main plan Phase 2
  if [ "$(basename $essay)" = "01-gamma-scalping" ]; then continue; fi
  cp "$essay/validation/smoke-golden.json" "$essay/python/golden.json"
  cp "$essay/validation/smoke-golden.json" "$essay/csharp/golden.json"
done
```

- [ ] **Step 2: Update each draft's frontmatter `golden:` block to reflect the smoke numbers**

(Could be automated by another tool but for v1 just hand-edit or use a one-off script.)

- [ ] **Step 3: Re-run frontmatter sync check**

```bash
fa-verify-frontmatter essays/*/[0-9]*/
```
Expected: every essay OK.

- [ ] **Step 4: Commit**

```bash
git add essays/
git commit -m "validate(seed-goldens): drafts ship with tier=smoke goldens, not empty {}

Each non-flagship draft's golden.json starts populated with the smoke
numbers from validation/smoke-golden.json. Marked tier: smoke so they're
distinguishable from real stable goldens captured in v0.2.0+ promotion.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase V3 — Wrap-up (1 task)

### Task V30: Validation summary document

**Files:**
- Create: `docs/validation/README.md`

Write a single page summarizing what validation proved + what it didn't.

- [ ] **Step 1: Write `docs/validation/README.md`**

```markdown
# Validation evidence

Before v0.1.0 launch, every essay in this catalog was validated in three tiers.

## Tier 0 — Static feasibility

Every essay's declared `bridge_bars` + `data_endpoints` are present in the published
`flashalpha-quantconnect 0.1.1` package. Run via `fa-check-bridge-compat`. CI Layer 0
re-checks this on every PR.

## Tier 1 — Data smoke

Every essay's endpoints return populated data for 3 known-good trading days. See
[smoke-data-report.md](smoke-data-report.md).

## Tier 2 — Algorithm smoke

Every essay has a minimal `validation/main.py` algorithm that runs a 30-day LEAN
backtest with a plausibility envelope (equity within [0.5×, 3.0×] of starting cash,
non-zero trades). See [smoke-rollup.md](smoke-rollup.md).

## What this proves

- The catalog is grounded in the bridge's actual surface.
- Each technique is implementable against real data over a short window.
- Each draft's `golden.json` carries `tier: smoke` numbers — distinguishable from
  the eventual `tier: stable` goldens captured during draft → stable promotion.

## What this does NOT prove

- Smoke algorithms are minimal — they don't reflect the eventual production strategy.
- The 30-day windows may not capture regime transitions a longer backtest would surface.
- Plausibility checks reject obvious failures; they don't assert "this is profitable".
- Real stable algorithms (live in `python/main.py` / `csharp/Main.cs`) are still the v0.2.0+ work.

## Re-running

```bash
fa-check-bridge-compat               # Tier 0
fa-data-smoke                        # Tier 1
fa-smoke-all                         # Tier 2 (bulk)
fa-smoke essays/<theme>/<slug>/      # Tier 2 (single)
```
```

- [ ] **Step 2: Commit**

```bash
git add docs/validation/README.md
git commit -m "docs(validation): wrap-up — what validation proved (and what it didn't)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
git push
```

---

## Self-review checklist

- [ ] 5 new tools shipped (`check-bridge-compat`, `data-smoke`, `smoke-algo`, `smoke-all`, plus the `new-essay` extension to scaffold `validation/`)
- [ ] All 5 tools have tests, all tests pass
- [ ] Tier 0 runs across all 21 essays and passes (Task V6)
- [ ] Tier 1 runs across all 21 essays and report committed (Task V7)
- [ ] Tier 2 runs per-essay (V8-V27) — every essay has `validation/smoke-golden.json` populated
- [ ] Tier 2 bulk roll-up committed (Task V28)
- [ ] Drafts seeded with smoke goldens (Task V29)
- [ ] Validation summary doc committed (Task V30)

## Interaction with the main plan

After this validation plan completes, run the main plan with these adjustments:

1. **Main plan Task 16** (scaffold 21 essays) — already done by this plan's V6. Skip.
2. **Main plan Task 25** (build catalog) — re-run; it'll pick up the new `validation/` paths in the catalog.
3. **Main plan Phase 4 CI Layer 0** (Task 31) — extend to ALSO run `fa-check-bridge-compat` so future PRs adding new essays don't break the bridge-compat invariant.
4. **Each essay's draft → stable promotion** (main plan Task 40) — the flow becomes:
   - Smoke algorithm in `validation/` is the seed
   - Promotion task copies `validation/main.py` → `python/main.py` and rewrites for production (longer window, parameter sweep, full essay text)
   - Capture stable goldens via `fa-capture-golden`
   - Flip `status: stable` in frontmatter
   - Tag v0.X.0

## Estimated effort

- Phase V0 (5 tools): ~3-4 hours (subagent-driven)
- Phase V1 (Tier 0 + Tier 1): ~1 hour
- Phase V2 (21 × Tier 2 smoke): ~6-10 hours (subagent-driven, parallelizable as one-task-per-essay)
- Phase V3 (wrap-up): ~30 min

**Total: ~10-15 hours of execution time.** Cheaper than discovering during Phase 2 of the main plan that 3-4 essays don't work and the catalog needs restructuring.
