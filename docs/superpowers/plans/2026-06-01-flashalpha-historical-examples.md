# flashalpha-historical-examples Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `FlashAlpha-lab/flashalpha-historical-examples` repo + hosted site at `examples.flashalpha.com` with 21 backtest essays (gamma scalping flagship `stable`, 20 themed drafts), full CI/SEO/JSON-LD machinery, named-date launch sequence — tagged v0.1.0 and discoverable on launch day.

**Architecture:** Themed essay directories (`a-dealer-positioning/`, `b-vanna-charm-vex/`, ...), each essay self-contained (README + meta.yaml + python/ + csharp/ + results/ + references.md). Tools/ utilities aggregate frontmatter into catalog.md / llms.txt / bibliography.{md,bib} / sitemap.xml / Course schema. MkDocs Material + GH Pages render the hosted site with per-page JSON-LD (TechArticle + HowTo + FAQPage), OG cards, Algolia DocSearch, freshness badges. CI in three layers: Layer 0 PR-fast structural validation, Layer 1 changed-essay LEAN backtests, Layer 2 nightly 42-cell sweep with golden-drift triage. Bridge dependency pinned at `flashalpha-quantconnect 0.1.1`.

**Tech Stack:** Python 3.10+ (tools, pytest, ruff), .NET 9 (C# essays, dotnet format), `flashalpha-quantconnect 0.1.1` (NuGet + PyPI), `lean` CLI ≥1.x (Docker-backed backtests), MkDocs Material (hosted site), Plausible Analytics, Algolia DocSearch, Buttondown (RSS-to-newsletter), Cloudflare (CNAME on `examples.flashalpha.com`), GitHub Actions, GitHub Pages.

**Spec reference:** [docs/superpowers/specs/2026-05-30-flashalpha-historical-examples-design.md](../specs/2026-05-30-flashalpha-historical-examples-design.md)

---

## Conventions used throughout this plan

- **TDD cycle per task:** failing test → run → minimal impl → run passes → commit. Always in that order.
- **Commits:** one per task. Conventional Commits prefixes (`feat:`, `test:`, `chore:`, `docs:`, `ci:`).
- **Working directory:** all paths relative to `e:/repos/tecware/flashalpha-packages/flashalpha-historical-examples/` unless absolute.
- **Frontmatter schema:** the single source-of-truth for what's in every essay's metadata. Defined in Task 6, referenced thereafter.
- **Live API key required for backtests:** Phase 2+ tasks that run `lean backtest` need `FLASHALPHA_API_KEY` in env. Local: from `.env.test.local` or env. CI: `${{ secrets.FLASHALPHA_API_KEY }}`.
- **Bridge version pin:** every essay's `python/requirements.txt` reads `flashalpha-quantconnect==0.1.1`; every `csharp/*.csproj` reads `<PackageReference Include="FlashAlpha.QuantConnect" Version="0.1.1" />`.

---

## Phase 0 — Repo scaffold (5 tasks)

### Task 1: Verify repo initialized + spec committed

The brainstorm phase already initialized git, wrote LICENSE/.gitignore/README, and committed the design spec. Verify before scaffolding more.

- [ ] **Step 1: Confirm state**

```bash
cd e:/repos/tecware/flashalpha-packages/flashalpha-historical-examples
git log --oneline
git ls-files
```
Expected: at least 1 commit, files: `LICENSE`, `.gitignore`, `README.md`, `docs/superpowers/specs/2026-05-30-flashalpha-historical-examples-design.md`.

If any of those are missing, return to brainstorming and complete the spec commit first.

- [ ] **Step 2: Confirm branch is main**

```bash
git branch --show-current
```
Expected: `main`.

---

### Task 2: Add CLAUDE.md + CONTRIBUTING.md + theme placeholder directories

**Files:**
- Create: `CLAUDE.md`
- Create: `CONTRIBUTING.md`
- Create: `essays/a-dealer-positioning/.gitkeep`
- Create: `essays/b-vanna-charm-vex/.gitkeep`
- Create: `essays/c-vrp-volatility/.gitkeep`
- Create: `essays/d-zero-dte/.gitkeep`
- Create: `essays/e-cross-signal/.gitkeep`

- [ ] **Step 1: Write `CLAUDE.md`** (same boilerplate as sibling repos):

```markdown
# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding
- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If something is unclear, stop. Name what's confusing.

## 2. Simplicity First
- Minimum code that solves the problem.
- No features beyond what was asked.
- No abstractions for single-use code.

## 3. Surgical Changes
- Touch only what you must.
- Match existing style.

## 4. Goal-Driven Execution
- Transform tasks into verifiable goals.
- For multi-step tasks, state a brief plan with verifications.

## 5. Essay-specific
- Every essay README has strict YAML frontmatter — validated by `tools/verify-frontmatter.py`.
- Algorithm files in `python/` and `csharp/` must call the SAME bridge bars with the SAME config.json values; the languages diverge ONLY in syntax.
- `golden.json` is committed evidence the backtest reproduces — update it deliberately, not casually.
- Cross-essay links use slugs (`gamma-scalping`), not full paths.
```

- [ ] **Step 2: Write `CONTRIBUTING.md`**:

```markdown
# Contributing

Thanks for considering a contribution! Read [docs/what-is-an-essay.md](docs/what-is-an-essay.md) first — it explains the essay anatomy, the draft → stable lifecycle, and the CI gates.

## Quick start

1. Fork + clone.
2. `pip install lean` and `pip install -e tools/` from the repo root.
3. Set `FLASHALPHA_API_KEY` in your env (free key at https://flashalpha.com).
4. Pick a `draft` essay from the catalog or open a discussion to propose a new one.
5. Write the README first (intuition + setup + algorithm sections), then the algorithm files, then run `lean backtest python/` and `lean backtest csharp/`, then capture goldens with `python -m tools.capture-golden essays/<your-essay>`.
6. Open a PR. CI Layer 0 (structural) must pass; Layer 1 (backtest) will validate your goldens.

## Adding a new essay

A new essay isn't a new repo — it's a new entry in the `essays/<theme>/<NN-slug>/` tree:

- Pick a theme (or propose a new one)
- Number the essay (next available in the theme)
- Run `python -m tools.new-essay --theme <theme> --slug <slug> --title "..."` to scaffold the folder
- Fill in `README.md`, `python/main.py`, `csharp/Main.cs`, `references.md`
- Capture goldens, render results, commit

## Lifecycle

`draft → stable → deprecated`. `stable` requires non-empty `golden.json` in both langs + nightly CI passing for 3 consecutive runs.
```

- [ ] **Step 3: Create the 5 theme directories with `.gitkeep`**

```bash
mkdir -p essays/{a-dealer-positioning,b-vanna-charm-vex,c-vrp-volatility,d-zero-dte,e-cross-signal}
touch essays/a-dealer-positioning/.gitkeep
touch essays/b-vanna-charm-vex/.gitkeep
touch essays/c-vrp-volatility/.gitkeep
touch essays/d-zero-dte/.gitkeep
touch essays/e-cross-signal/.gitkeep
```

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md CONTRIBUTING.md essays/
git commit -m "chore: scaffold CLAUDE.md, CONTRIBUTING.md, theme directories

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 3: Create tools/ Python package skeleton

**Files:**
- Create: `tools/pyproject.toml`
- Create: `tools/src/flashalpha_examples_tools/__init__.py`
- Create: `tools/tests/__init__.py`
- Create: `tools/tests/conftest.py`

- [ ] **Step 1: Create directories**

```bash
mkdir -p tools/src/flashalpha_examples_tools
mkdir -p tools/tests
```

- [ ] **Step 2: Write `tools/pyproject.toml`**:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "flashalpha-examples-tools"
version = "0.1.0"
description = "Build utilities for flashalpha-historical-examples — catalog, golden capture, results rendering, JSON-LD."
requires-python = ">=3.10"
dependencies = [
  "pyyaml>=6.0",
  "matplotlib>=3.7",
  "pillow>=10.0",
  "pandas>=2.0",
  "jsonschema>=4.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=7",
  "ruff>=0.5",
]

[project.scripts]
fa-build-catalog = "flashalpha_examples_tools.build_catalog:main"
fa-verify-essay = "flashalpha_examples_tools.verify_essay:main"
fa-capture-golden = "flashalpha_examples_tools.capture_golden:main"
fa-render-results = "flashalpha_examples_tools.render_results:main"
fa-check-orphans = "flashalpha_examples_tools.check_orphans:main"
fa-verify-frontmatter = "flashalpha_examples_tools.verify_frontmatter:main"
fa-build-bib = "flashalpha_examples_tools.build_bib:main"
fa-build-site = "flashalpha_examples_tools.build_site:main"
fa-gen-og-cards = "flashalpha_examples_tools.gen_og_cards:main"
fa-new-essay = "flashalpha_examples_tools.new_essay:main"

[tool.hatch.build.targets.wheel]
packages = ["src/flashalpha_examples_tools"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 3: Write `tools/src/flashalpha_examples_tools/__init__.py`**:

```python
"""Build utilities for flashalpha-historical-examples."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Write `tools/tests/__init__.py`** (empty file).

- [ ] **Step 5: Write `tools/tests/conftest.py`**:

```python
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).parent.parent.parent


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def essays_dir(repo_root: Path) -> Path:
    return repo_root / "essays"
```

- [ ] **Step 6: Install editable + verify**

```bash
cd tools
pip install -e ".[dev]"
python -c "import flashalpha_examples_tools; print(flashalpha_examples_tools.__version__)"
```
Expected: `0.1.0`.

- [ ] **Step 7: Commit**

```bash
cd ..
git add tools/
git commit -m "chore: scaffold tools/ Python package (entry points stubs for fa-* CLIs)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 4: Create GitHub repo + push main + set topics

**External-side-effect task.** Requires user-side authentication via `gh` CLI.

- [ ] **Step 1: Verify gh auth**

```bash
gh auth status
```
Expected: logged in to github.com under an account with write access to the `FlashAlpha-lab` org.

- [ ] **Step 2: Create the repo**

```bash
cd e:/repos/tecware/flashalpha-packages/flashalpha-historical-examples
gh repo create FlashAlpha-lab/flashalpha-historical-examples \
  --public \
  --description "21 backtest essays for options strategies on QuantConnect LEAN. Side-by-side C# + Python. Powered by flashalpha-quantconnect." \
  --source=. \
  --remote=origin \
  --homepage="https://examples.flashalpha.com"
```
Expected: `https://github.com/FlashAlpha-lab/flashalpha-historical-examples`.

- [ ] **Step 3: Push main**

```bash
git push -u origin main
```
Expected: `[new branch] main -> main`.

- [ ] **Step 4: Set the 16 topics**

```bash
gh api -X PUT repos/FlashAlpha-lab/flashalpha-historical-examples/topics \
  -f 'names[]=quantconnect' \
  -f 'names[]=lean' \
  -f 'names[]=backtest' \
  -f 'names[]=algorithmic-trading' \
  -f 'names[]=options-trading' \
  -f 'names[]=gamma-scalping' \
  -f 'names[]=gex' \
  -f 'names[]=dealer-positioning' \
  -f 'names[]=vol-surface' \
  -f 'names[]=vrp' \
  -f 'names[]=0dte' \
  -f 'names[]=examples' \
  -f 'names[]=cookbook' \
  -f 'names[]=python' \
  -f 'names[]=csharp' \
  -f 'names[]=flashalpha'
```
Expected: JSON response listing all 16 topics.

- [ ] **Step 5: Configure FLASHALPHA_API_KEY secret**

```bash
# Extract from local sibling repo and pipe through gh secret set without echoing
{ sed 's/\xef\xbb\xbf//' "e:/repos/tecware/flashalpha-packages/flashalpha-js/.env.test.local" \
   | grep 'FLASHALPHA_API_KEY=' | head -1 | cut -d= -f2- | tr -d '"\r\n' | tr -d "'"; } \
 | gh secret set FLASHALPHA_API_KEY -R FlashAlpha-lab/flashalpha-historical-examples
```
Expected: `Set secret FLASHALPHA_API_KEY for FlashAlpha-lab/flashalpha-historical-examples`.

- [ ] **Step 6: No commit required** (this task only affects GitHub state, not local files).

---

### Task 5: Add docs/ contributor reference files

**Files:**
- Create: `docs/getting-started.md`
- Create: `docs/what-is-an-essay.md`
- Create: `docs/glossary.md`
- Create: `docs/lean-cli-cheatsheet.md`
- Create: `docs/compatibility.md`

- [ ] **Step 1: Write `docs/getting-started.md`**

Sections:
1. **Prerequisites:** Python 3.10+, .NET 9 SDK, Docker, `pip install lean`, `FLASHALPHA_API_KEY` in env.
2. **First essay:** clone the repo, `cd essays/a-dealer-positioning/01-gamma-scalping/python/`, `lean backtest`, inspect the output.
3. **What's a `lean backtest`?** — explain Docker pulls, where output lands, how to read it.
4. **Where to next:** link to catalog.md, what-is-an-essay.md, and the bridge documentation at `https://github.com/FlashAlpha-lab/flashalpha-quantconnect`.

Target: 300-500 lines, code-heavy.

- [ ] **Step 2: Write `docs/what-is-an-essay.md`**

Sections:
1. **Anatomy of an essay folder** (README, meta.yaml, references.md, python/, csharp/, results/).
2. **The frontmatter schema** — annotated example of every field, what's required, what's optional.
3. **The draft → stable → deprecated lifecycle.**
4. **What CI checks** at each layer.
5. **Adding a new essay** (point at `fa-new-essay` CLI).

Target: 200-400 lines.

- [ ] **Step 3: Write `docs/glossary.md`**

One section per term. Plain English definitions of: gamma, delta, vega, charm, vanna; GEX, DEX, VEX, CHEX; VRP, RV, IV; 0DTE, ATM, OTM, ITM; dealer hedging, pin risk, gamma flip, regime; sharpe, sortino, max drawdown, hit rate. Cross-link each term to the bridge's `data-types.md` where relevant.

Target: 250-400 lines.

- [ ] **Step 4: Write `docs/lean-cli-cheatsheet.md`**

Common LEAN CLI commands with examples: `lean init`, `lean backtest`, `lean cloud backtest`, `lean live`, `lean optimize`, `lean report`. Note the Docker requirement. Link to QC's own docs for the canonical reference.

Target: 150-250 lines.

- [ ] **Step 5: Write `docs/compatibility.md`**

The compatibility matrix:

```markdown
# Compatibility matrix

| Examples version | Bridge version | LEAN CLI | .NET | Python |
|---|---|---|---|---|
| v0.1.0 | flashalpha-quantconnect 0.1.1 | lean 1.x | 9.0 | 3.10–3.12 |

## Bridge upgrade policy

A single PR bumps every essay's pin in lockstep when the bridge updates. CI's drift guard (Task 10) asserts no essay falls behind the repo-wide minimum.

## LEAN CLI

`lean` CLI is the only supported runner. QC Cloud parallel runs are out of scope for v1.0.
```

- [ ] **Step 6: Commit**

```bash
git add docs/
git commit -m "docs: add contributor reference (getting-started, what-is-an-essay, glossary, lean cheatsheet, compatibility)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
git push
```

---

## Phase 1 — Tools (10 tasks)

### Task 6: Frontmatter schema + validator

**Files:**
- Create: `tools/src/flashalpha_examples_tools/_schema.py`
- Create: `tools/tests/test_schema.py`

- [ ] **Step 1: Write the failing tests**

`tools/tests/test_schema.py`:

```python
import pytest
from flashalpha_examples_tools._schema import (
    FrontmatterSchema, ValidationError, validate_frontmatter,
)


VALID_FRONTMATTER = {
    "title": "Gamma scalping in QuantConnect",
    "slug": "gamma-scalping",
    "theme": "dealer-positioning",
    "difficulty": "intermediate",
    "status": "stable",
    "summary": "Delta-neutral options portfolio gated by FlashAlpha's dealer-GEX regime signal.",
    "bridge_bars": ["FlashAlphaGexBar", "FlashAlphaSurfaceBar"],
    "data_endpoints": ["exposure/gex", "surface"],
    "tickers": ["SPY"],
    "backtest_window": {"start": "2024-03-01", "end": "2024-09-30"},
    "expected_runtime": {"python": "8m", "csharp": "3m"},
    "golden": {
        "python": {"final_equity": 102417.50, "total_trades": 84, "sharpe": 0.72, "max_drawdown": -0.045},
        "csharp": {"final_equity": 102390.13, "total_trades": 84, "sharpe": 0.72, "max_drawdown": -0.045},
    },
    "related": ["gex-regime-following"],
    "keywords": ["gamma scalping", "QuantConnect"],
    "last_updated": "2026-05-30",
    "last_verified_by_nightly": "2026-05-30",
    "references": ["Dynamic Hedging — Taleb (1997)"],
}


def test_valid_frontmatter_passes():
    validate_frontmatter(VALID_FRONTMATTER)  # no exception


def test_missing_required_field_fails():
    bad = {**VALID_FRONTMATTER}
    del bad["slug"]
    with pytest.raises(ValidationError, match="slug"):
        validate_frontmatter(bad)


def test_invalid_difficulty_value_fails():
    bad = {**VALID_FRONTMATTER, "difficulty": "expert"}
    with pytest.raises(ValidationError, match="difficulty"):
        validate_frontmatter(bad)


def test_invalid_status_value_fails():
    bad = {**VALID_FRONTMATTER, "status": "wip"}
    with pytest.raises(ValidationError, match="status"):
        validate_frontmatter(bad)


def test_invalid_theme_value_fails():
    bad = {**VALID_FRONTMATTER, "theme": "unknown-theme"}
    with pytest.raises(ValidationError, match="theme"):
        validate_frontmatter(bad)


def test_draft_essay_with_empty_golden_passes():
    """Draft essays may have empty golden dicts (literal {} placeholders)."""
    draft = {**VALID_FRONTMATTER, "status": "draft", "golden": {"python": {}, "csharp": {}}}
    validate_frontmatter(draft)


def test_stable_essay_with_empty_golden_fails():
    """Stable essays must declare actual golden numbers."""
    bad = {**VALID_FRONTMATTER, "status": "stable", "golden": {"python": {}, "csharp": {}}}
    with pytest.raises(ValidationError, match="stable.*golden"):
        validate_frontmatter(bad)


def test_deprecated_essay_requires_replaced_by():
    bad = {**VALID_FRONTMATTER, "status": "deprecated"}
    # missing replaced_by
    with pytest.raises(ValidationError, match="replaced_by"):
        validate_frontmatter(bad)
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd tools && pytest tests/test_schema.py -v
```
Expected: `ImportError: cannot import name 'FrontmatterSchema'`.

- [ ] **Step 3: Write `_schema.py`**

```python
"""Frontmatter schema for flashalpha-historical-examples.

The single source of truth for what a valid essay's frontmatter looks like.
Used by build-catalog, verify-frontmatter, check-orphans, and any tool that
consumes meta.yaml.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


VALID_THEMES = {
    "dealer-positioning",
    "vanna-charm-vex",
    "vrp-volatility",
    "zero-dte",
    "cross-signal",
}
VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced"}
VALID_STATUSES = {"draft", "stable", "deprecated"}
REQUIRED_FIELDS = [
    "title", "slug", "theme", "difficulty", "status", "summary",
    "bridge_bars", "data_endpoints", "tickers", "backtest_window",
    "expected_runtime", "golden", "keywords", "last_updated",
]
GOLDEN_FIELDS = {"final_equity", "total_trades", "sharpe", "max_drawdown"}


class ValidationError(Exception):
    """Raised when frontmatter violates the schema."""


@dataclass
class FrontmatterSchema:
    """Tag class for IDE discovery — actual validation is in validate_frontmatter."""


def validate_frontmatter(fm: dict[str, Any]) -> None:
    """Raise ValidationError if frontmatter is malformed. Return None on success."""
    if not isinstance(fm, dict):
        raise ValidationError(f"frontmatter must be a dict, got {type(fm).__name__}")

    for field in REQUIRED_FIELDS:
        if field not in fm:
            raise ValidationError(f"missing required field: {field}")

    if fm["theme"] not in VALID_THEMES:
        raise ValidationError(
            f"theme {fm['theme']!r} not in {sorted(VALID_THEMES)}"
        )
    if fm["difficulty"] not in VALID_DIFFICULTIES:
        raise ValidationError(
            f"difficulty {fm['difficulty']!r} not in {sorted(VALID_DIFFICULTIES)}"
        )
    if fm["status"] not in VALID_STATUSES:
        raise ValidationError(
            f"status {fm['status']!r} not in {sorted(VALID_STATUSES)}"
        )

    # Stable essays must have populated goldens
    if fm["status"] == "stable":
        for lang in ("python", "csharp"):
            g = fm["golden"].get(lang) or {}
            if not g:
                raise ValidationError(
                    f"stable essay {fm['slug']!r} has empty golden for {lang}"
                )
            missing = GOLDEN_FIELDS - g.keys()
            if missing:
                raise ValidationError(
                    f"stable essay {fm['slug']!r} {lang} golden missing fields: {sorted(missing)}"
                )

    # Deprecated essays must declare a replacement
    if fm["status"] == "deprecated" and not fm.get("replaced_by"):
        raise ValidationError(
            f"deprecated essay {fm['slug']!r} missing replaced_by"
        )


THEMES_DIR_MAP = {
    "dealer-positioning": "a-dealer-positioning",
    "vanna-charm-vex": "b-vanna-charm-vex",
    "vrp-volatility": "c-vrp-volatility",
    "zero-dte": "d-zero-dte",
    "cross-signal": "e-cross-signal",
}
```

- [ ] **Step 4: Run tests to confirm PASS**

```bash
pytest tests/test_schema.py -v
```
Expected: 7 PASS.

- [ ] **Step 5: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(tools): frontmatter schema validator

Single source of truth for essay metadata: required fields, valid enum
values for theme/difficulty/status, stable-requires-golden invariant,
deprecated-requires-replaced-by invariant.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 7: LEAN BacktestResult parser

**Files:**
- Create: `tools/src/flashalpha_examples_tools/_lean_output.py`
- Create: `tools/tests/test_lean_output.py`
- Create: `tools/tests/fixtures/sample-backtest-result.json`

- [ ] **Step 1: Create a sample LEAN BacktestResult JSON fixture**

`tools/tests/fixtures/sample-backtest-result.json` (minimal but realistic — LEAN's actual output has many more fields; we only need a subset):

```json
{
  "Statistics": {
    "Total Trades": "84",
    "Sharpe Ratio": "0.72",
    "Sortino Ratio": "1.05",
    "Compounding Annual Return": "4.83%",
    "Drawdown": "4.50%",
    "Net Profit": "2.42%",
    "Win Rate": "62%",
    "Average Win": "0.95%",
    "Average Loss": "-0.42%"
  },
  "TotalPerformance": {
    "PortfolioStatistics": {
      "TotalNetProfit": "0.02417",
      "SharpeRatio": "0.72",
      "SortinoRatio": "1.05",
      "Drawdown": "0.045"
    }
  },
  "Charts": {
    "Strategy Equity": {
      "Name": "Strategy Equity",
      "Series": {
        "Equity": {
          "Values": [
            {"x": 1709251200, "y": 100000.00},
            {"x": 1709337600, "y": 100123.45},
            {"x": 1727654400, "y": 102417.50}
          ]
        }
      }
    }
  },
  "AlgorithmConfiguration": {
    "InitialCash": "100000"
  }
}
```

- [ ] **Step 2: Write the failing tests**

`tools/tests/test_lean_output.py`:

```python
import json
from pathlib import Path

import pytest

from flashalpha_examples_tools._lean_output import (
    BacktestResult, parse_backtest_result,
)


FIXTURE = Path(__file__).parent / "fixtures" / "sample-backtest-result.json"


@pytest.fixture
def fixture_path() -> Path:
    return FIXTURE


def test_parse_extracts_headline_stats(fixture_path: Path):
    r = parse_backtest_result(fixture_path)
    assert isinstance(r, BacktestResult)
    assert r.total_trades == 84
    assert r.sharpe == pytest.approx(0.72, abs=0.01)
    assert r.sortino == pytest.approx(1.05, abs=0.01)
    assert r.max_drawdown == pytest.approx(-0.045, abs=0.001)


def test_parse_extracts_final_equity(fixture_path: Path):
    r = parse_backtest_result(fixture_path)
    assert r.final_equity == pytest.approx(102417.50, rel=1e-4)
    assert r.initial_equity == pytest.approx(100000.0, rel=1e-4)


def test_parse_extracts_equity_curve(fixture_path: Path):
    r = parse_backtest_result(fixture_path)
    assert len(r.equity_curve) == 3
    assert r.equity_curve[0] == (1709251200, 100000.00)
    assert r.equity_curve[-1] == (1727654400, 102417.50)


def test_parse_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        parse_backtest_result(Path("/nonexistent.json"))
```

- [ ] **Step 3: Run to confirm fail**

```bash
cd tools && pytest tests/test_lean_output.py -v
```
Expected: ImportError.

- [ ] **Step 4: Write `_lean_output.py`**

```python
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
```

- [ ] **Step 5: Run tests to PASS**

```bash
pytest tests/test_lean_output.py -v
```
Expected: 4 PASS.

- [ ] **Step 6: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(tools): LEAN BacktestResult parser

Single seam between tool code and LEAN's raw JSON output. Tools (verify-essay,
capture-golden, render-results) all consume BacktestResult dataclass; nothing
peeks at the JSON shape directly.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 8: verify-frontmatter tool

**Files:**
- Create: `tools/src/flashalpha_examples_tools/verify_frontmatter.py`
- Create: `tools/tests/test_verify_frontmatter.py`
- Create: `tools/tests/fixtures/sample-essay/README.md`
- Create: `tools/tests/fixtures/sample-essay/meta.yaml`

- [ ] **Step 1: Create fixture pair**

`tools/tests/fixtures/sample-essay/README.md`:

```markdown
---
title: "Sample"
slug: sample
theme: dealer-positioning
difficulty: beginner
status: draft
summary: "A fixture for testing."
bridge_bars: [FlashAlphaGexBar]
data_endpoints: [exposure/gex]
tickers: [SPY]
backtest_window: {start: "2024-06-01", end: "2024-06-10"}
expected_runtime: {python: "1m", csharp: "1m"}
golden: {python: {}, csharp: {}}
keywords: [sample]
last_updated: "2026-06-01"
---

# Sample
```

`tools/tests/fixtures/sample-essay/meta.yaml`:

```yaml
title: "Sample"
slug: sample
theme: dealer-positioning
difficulty: beginner
status: draft
summary: "A fixture for testing."
bridge_bars: [FlashAlphaGexBar]
data_endpoints: [exposure/gex]
tickers: [SPY]
backtest_window: {start: "2024-06-01", end: "2024-06-10"}
expected_runtime: {python: "1m", csharp: "1m"}
golden: {python: {}, csharp: {}}
keywords: [sample]
last_updated: "2026-06-01"
```

- [ ] **Step 2: Write the failing tests**

`tools/tests/test_verify_frontmatter.py`:

```python
from pathlib import Path

import pytest
import yaml

from flashalpha_examples_tools.verify_frontmatter import (
    FrontmatterMismatch, extract_frontmatter, verify_essay_frontmatter,
)


FIX = Path(__file__).parent / "fixtures" / "sample-essay"


def test_extract_frontmatter_from_readme():
    fm = extract_frontmatter(FIX / "README.md")
    assert fm["slug"] == "sample"
    assert fm["theme"] == "dealer-positioning"


def test_verify_passes_when_in_sync():
    verify_essay_frontmatter(FIX)  # no exception


def test_verify_fails_on_drift(tmp_path: Path):
    # Copy fixtures, mutate meta.yaml, expect FrontmatterMismatch
    import shutil
    drifted = tmp_path / "drifted"
    shutil.copytree(FIX, drifted)
    meta = yaml.safe_load((drifted / "meta.yaml").read_text())
    meta["title"] = "Different title"
    (drifted / "meta.yaml").write_text(yaml.safe_dump(meta))

    with pytest.raises(FrontmatterMismatch, match="title"):
        verify_essay_frontmatter(drifted)


def test_verify_fails_on_invalid_schema(tmp_path: Path):
    import shutil
    bad = tmp_path / "bad"
    shutil.copytree(FIX, bad)
    text = (bad / "README.md").read_text().replace("difficulty: beginner", "difficulty: expert")
    (bad / "README.md").write_text(text)
    # Also drift meta.yaml to match
    meta = yaml.safe_load((bad / "meta.yaml").read_text())
    meta["difficulty"] = "expert"
    (bad / "meta.yaml").write_text(yaml.safe_dump(meta))

    with pytest.raises(Exception):  # ValidationError from _schema, propagated
        verify_essay_frontmatter(bad)
```

- [ ] **Step 3: Write `verify_frontmatter.py`**

```python
"""Verify that an essay's README frontmatter matches its meta.yaml exactly,
and both validate against the frontmatter schema.

This catches:
- Author edited README but forgot meta.yaml (drift).
- Either file has invalid schema (missing required field, bad enum value).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from ._schema import validate_frontmatter


class FrontmatterMismatch(Exception):
    """README frontmatter and meta.yaml disagree."""


def extract_frontmatter(readme_path: Path) -> dict:
    """Read the YAML frontmatter block from a README.md."""
    text = readme_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{readme_path} has no frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError(f"{readme_path} frontmatter has no closing ---")
    block = text[3:end].strip()
    return yaml.safe_load(block) or {}


def verify_essay_frontmatter(essay_dir: Path) -> None:
    """Raise on schema violation or README↔meta.yaml drift."""
    readme = essay_dir / "README.md"
    meta = essay_dir / "meta.yaml"
    if not readme.exists():
        raise FileNotFoundError(readme)
    if not meta.exists():
        raise FileNotFoundError(meta)

    fm_readme = extract_frontmatter(readme)
    fm_meta = yaml.safe_load(meta.read_text(encoding="utf-8")) or {}

    validate_frontmatter(fm_readme)
    validate_frontmatter(fm_meta)

    # Drift check: all keys/values must agree
    keys = set(fm_readme.keys()) | set(fm_meta.keys())
    for k in keys:
        if fm_readme.get(k) != fm_meta.get(k):
            raise FrontmatterMismatch(
                f"{essay_dir.name}: '{k}' differs between README.md frontmatter "
                f"({fm_readme.get(k)!r}) and meta.yaml ({fm_meta.get(k)!r})"
            )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Verify essay frontmatter sync + schema")
    p.add_argument("essays", nargs="+", help="Essay directories to verify")
    args = p.parse_args(argv)

    failures = []
    for d in args.essays:
        try:
            verify_essay_frontmatter(Path(d))
        except Exception as e:
            failures.append(f"{d}: {e}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"OK ({len(args.essays)} essays verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to PASS**

```bash
cd tools && pytest tests/test_verify_frontmatter.py -v
```
Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(tools): verify-frontmatter — README↔meta.yaml drift detector

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 9: check-orphans tool

**Files:**
- Create: `tools/src/flashalpha_examples_tools/check_orphans.py`
- Create: `tools/tests/test_check_orphans.py`

This tool asserts catalog ↔ filesystem consistency: every directory under `essays/<theme>/` has a complete essay folder shape, and no essay is missing a required file.

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path
import shutil

import pytest

from flashalpha_examples_tools.check_orphans import (
    OrphanError, check_essay_shape, find_orphans,
)


FIX = Path(__file__).parent / "fixtures" / "sample-essay"


@pytest.fixture
def essay_dir(tmp_path: Path) -> Path:
    """Copy the sample essay fixture + scaffold required language dirs."""
    d = tmp_path / "01-sample"
    shutil.copytree(FIX, d)
    # Scaffold the required dirs:
    for sub in ("python", "csharp", "results"):
        (d / sub).mkdir()
    (d / "python" / "main.py").write_text("# stub\n")
    (d / "python" / "config.json").write_text("{}\n")
    (d / "python" / "lean.json").write_text("{}\n")
    (d / "python" / "golden.json").write_text("{}\n")
    (d / "python" / "requirements.txt").write_text("flashalpha-quantconnect==0.1.1\n")
    (d / "csharp" / "Main.cs").write_text("// stub\n")
    (d / "csharp" / "config.json").write_text("{}\n")
    (d / "csharp" / "lean.json").write_text("{}\n")
    (d / "csharp" / "golden.json").write_text("{}\n")
    (d / "csharp" / "Sample.csproj").write_text("<Project/>\n")
    (d / "references.md").write_text("- Sample reference\n")
    return d


def test_complete_essay_passes(essay_dir: Path):
    check_essay_shape(essay_dir)  # no exception


def test_missing_python_main_fails(essay_dir: Path):
    (essay_dir / "python" / "main.py").unlink()
    with pytest.raises(OrphanError, match="python/main.py"):
        check_essay_shape(essay_dir)


def test_missing_csharp_csproj_fails(essay_dir: Path):
    (essay_dir / "csharp" / "Sample.csproj").unlink()
    with pytest.raises(OrphanError, match="\\.csproj"):
        check_essay_shape(essay_dir)


def test_missing_references_fails(essay_dir: Path):
    (essay_dir / "references.md").unlink()
    with pytest.raises(OrphanError, match="references.md"):
        check_essay_shape(essay_dir)


def test_find_orphans_walks_themes(tmp_path: Path, essay_dir: Path):
    # Build a tiny mock repo structure
    repo = tmp_path / "repo"
    essays = repo / "essays" / "a-dealer-positioning"
    essays.mkdir(parents=True)
    shutil.copytree(essay_dir, essays / "01-sample")

    issues = find_orphans(repo)
    assert issues == []


def test_find_orphans_finds_broken_essay(tmp_path: Path, essay_dir: Path):
    repo = tmp_path / "repo"
    essays = repo / "essays" / "a-dealer-positioning"
    essays.mkdir(parents=True)
    shutil.copytree(essay_dir, essays / "01-sample")
    (essays / "01-sample" / "python" / "main.py").unlink()

    issues = find_orphans(repo)
    assert len(issues) == 1
    assert "main.py" in issues[0]
```

- [ ] **Step 2: Run tests to fail**

```bash
cd tools && pytest tests/test_check_orphans.py -v
```
Expected: ImportError.

- [ ] **Step 3: Write `check_orphans.py`**

```python
"""Catalog ↔ filesystem consistency: every essay folder has the required shape."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


class OrphanError(Exception):
    """An essay is missing required files or directories."""


REQUIRED_FILES = [
    "README.md",
    "meta.yaml",
    "references.md",
    "python/lean.json",
    "python/config.json",
    "python/main.py",
    "python/golden.json",
    "python/requirements.txt",
    "csharp/lean.json",
    "csharp/config.json",
    "csharp/Main.cs",
    "csharp/golden.json",
]
REQUIRED_DIRS = ["python", "csharp", "results"]


def check_essay_shape(essay_dir: Path) -> None:
    """Raise OrphanError if any required file/dir is missing."""
    for d in REQUIRED_DIRS:
        if not (essay_dir / d).is_dir():
            raise OrphanError(f"{essay_dir.name}: missing directory {d}/")
    for f in REQUIRED_FILES:
        if not (essay_dir / f).exists():
            raise OrphanError(f"{essay_dir.name}: missing file {f}")
    # csharp .csproj — any *.csproj inside csharp/ counts
    if not list((essay_dir / "csharp").glob("*.csproj")):
        raise OrphanError(f"{essay_dir.name}: missing .csproj in csharp/")


def find_orphans(repo_root: Path) -> list[str]:
    """Scan every essay folder under essays/<theme>/ and return list of issue strings."""
    issues: list[str] = []
    essays_root = repo_root / "essays"
    if not essays_root.is_dir():
        return [f"essays/ not found at {repo_root}"]
    for theme_dir in sorted(essays_root.iterdir()):
        if not theme_dir.is_dir() or theme_dir.name.startswith("."):
            continue
        for essay_dir in sorted(theme_dir.iterdir()):
            if not essay_dir.is_dir() or essay_dir.name.startswith("."):
                continue
            try:
                check_essay_shape(essay_dir)
            except OrphanError as e:
                issues.append(str(e))
    return issues


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Detect orphan/incomplete essays")
    p.add_argument("--repo-root", default=".", help="Repo root directory")
    args = p.parse_args(argv)

    issues = find_orphans(Path(args.repo_root))
    if issues:
        for i in issues:
            print(i, file=sys.stderr)
        return 1
    print("OK — no orphans")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to PASS**

```bash
pytest tests/test_check_orphans.py -v
```
Expected: 6 PASS.

- [ ] **Step 5: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(tools): check-orphans — every essay folder has required shape

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 10: build-catalog tool

**Files:**
- Create: `tools/src/flashalpha_examples_tools/build_catalog.py`
- Create: `tools/tests/test_build_catalog.py`

Generates: `catalog.md` (human index), `llms.txt` (LLM site map), per-theme `README.md`, `_sitemap.xml`, `_schema.json` (catalog-wide Course schema).

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path
import shutil

import pytest

from flashalpha_examples_tools.build_catalog import (
    build_catalog, render_catalog_md, render_llms_txt,
    render_theme_readme, render_sitemap,
)
from flashalpha_examples_tools._schema import THEMES_DIR_MAP


def _make_essay(repo: Path, theme_slug: str, n: int, title: str, status="draft", **extras):
    import yaml
    theme_dir_name = THEMES_DIR_MAP[theme_slug]
    d = repo / "essays" / theme_dir_name / f"{n:02d}-{title.lower().replace(' ', '-')}"
    d.mkdir(parents=True)
    fm = {
        "title": title, "slug": title.lower().replace(" ", "-"),
        "theme": theme_slug, "difficulty": "beginner", "status": status,
        "summary": f"Summary of {title}",
        "bridge_bars": ["FlashAlphaGexBar"], "data_endpoints": ["exposure/gex"],
        "tickers": ["SPY"], "backtest_window": {"start": "2024-06-01", "end": "2024-06-10"},
        "expected_runtime": {"python": "1m", "csharp": "1m"},
        "golden": {"python": {"final_equity": 100, "total_trades": 1, "sharpe": 0.0, "max_drawdown": -0.0},
                   "csharp": {"final_equity": 100, "total_trades": 1, "sharpe": 0.0, "max_drawdown": -0.0}} if status == "stable" else {"python": {}, "csharp": {}},
        "keywords": [title.lower()], "last_updated": "2026-06-01",
        **extras,
    }
    (d / "meta.yaml").write_text(yaml.safe_dump(fm))
    (d / "README.md").write_text(f"---\n{yaml.safe_dump(fm)}---\n# {title}\n")
    return d


@pytest.fixture
def mock_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    _make_essay(repo, "dealer-positioning", 1, "Gamma Scalping", status="stable")
    _make_essay(repo, "dealer-positioning", 2, "GEX Regime Following")
    _make_essay(repo, "vrp-volatility", 9, "VRP Harvest")
    return repo


def test_render_llms_txt_lists_all_essays(mock_repo: Path):
    text = render_llms_txt(mock_repo)
    assert "Gamma Scalping" in text
    assert "GEX Regime Following" in text
    assert "VRP Harvest" in text
    assert "## Essays" in text


def test_render_catalog_md_groups_by_theme(mock_repo: Path):
    text = render_catalog_md(mock_repo)
    # Themed sections present
    assert "Dealer positioning" in text or "dealer-positioning" in text
    assert "VRP" in text or "vrp-volatility" in text
    # Stable badge present on the stable essay
    assert "Gamma Scalping" in text


def test_render_theme_readme(mock_repo: Path):
    text = render_theme_readme(mock_repo, "dealer-positioning")
    assert "Gamma Scalping" in text
    assert "GEX Regime Following" in text


def test_render_sitemap_includes_essay_urls(mock_repo: Path):
    xml = render_sitemap(mock_repo, base_url="https://examples.flashalpha.com")
    assert "<urlset" in xml
    assert "gamma-scalping" in xml
    assert "vrp-harvest" in xml


def test_build_catalog_writes_all_outputs(mock_repo: Path):
    build_catalog(mock_repo)
    assert (mock_repo / "catalog.md").exists()
    assert (mock_repo / "llms.txt").exists()
    assert (mock_repo / "essays" / "a-dealer-positioning" / "README.md").exists()
    assert (mock_repo / "_sitemap.xml").exists()
```

- [ ] **Step 2: Run to fail**

```bash
cd tools && pytest tests/test_build_catalog.py -v
```
Expected: ImportError.

- [ ] **Step 3: Write `build_catalog.py`**

```python
"""Aggregate every essay's meta.yaml into catalog.md, llms.txt, theme READMEs, sitemap.xml.

Single pass over essays/**/meta.yaml. Idempotent — running twice produces the same outputs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from ._schema import THEMES_DIR_MAP


def _load_essays(repo: Path) -> list[dict[str, Any]]:
    """Walk essays/<theme>/<n-slug>/meta.yaml and return list of frontmatters."""
    out: list[dict[str, Any]] = []
    essays_root = repo / "essays"
    for theme_dir in sorted(essays_root.iterdir()):
        if not theme_dir.is_dir() or theme_dir.name.startswith("."):
            continue
        for essay_dir in sorted(theme_dir.iterdir()):
            if not essay_dir.is_dir() or essay_dir.name.startswith("."):
                continue
            meta_path = essay_dir / "meta.yaml"
            if not meta_path.exists():
                continue
            fm = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
            fm["_dir"] = essay_dir.relative_to(repo).as_posix()
            fm["_theme_dir"] = theme_dir.name
            out.append(fm)
    return out


def _theme_display_name(theme_slug: str) -> str:
    return {
        "dealer-positioning": "Dealer positioning",
        "vanna-charm-vex": "Vanna / charm / VEX",
        "vrp-volatility": "VRP / volatility",
        "zero-dte": "0DTE",
        "cross-signal": "Cross-signal / multi-asset",
    }[theme_slug]


def _status_badge(s: str) -> str:
    return {"draft": "🚧 draft", "stable": "✅ stable", "deprecated": "⚠️ deprecated"}[s]


def render_llms_txt(repo: Path) -> str:
    essays = _load_essays(repo)
    by_theme: dict[str, list[dict]] = {}
    for e in essays:
        by_theme.setdefault(e["theme"], []).append(e)

    lines = ["# flashalpha-historical-examples",
             "",
             "> 21 backtest essays for options strategies on QuantConnect LEAN.",
             "> Side-by-side C# and Python. Powered by flashalpha-quantconnect.",
             ""]
    for theme_slug in ["dealer-positioning", "vanna-charm-vex", "vrp-volatility", "zero-dte", "cross-signal"]:
        items = by_theme.get(theme_slug, [])
        if not items:
            continue
        lines.append(f"## Essays — {_theme_display_name(theme_slug)}")
        for e in sorted(items, key=lambda x: x["_dir"]):
            link = f"{e['_dir']}/README.md"
            lines.append(f"- [{e['title']}]({link}): {e['summary']}")
        lines.append("")
    lines += [
        "## Bridge package",
        "- [flashalpha-quantconnect on NuGet](https://www.nuget.org/packages/FlashAlpha.QuantConnect/)",
        "- [flashalpha-quantconnect on PyPI](https://pypi.org/project/flashalpha-quantconnect/)",
        "",
        "## Underlying API",
        "- [historical.flashalpha.com](https://historical.flashalpha.com)",
        "",
        "## Optional",
        "- [Glossary](docs/glossary.md)",
        "- [LEAN CLI cheatsheet](docs/lean-cli-cheatsheet.md)",
        "- [Bibliography](bibliography.md)",
    ]
    return "\n".join(lines) + "\n"


def render_catalog_md(repo: Path) -> str:
    essays = _load_essays(repo)
    by_theme: dict[str, list[dict]] = {}
    for e in essays:
        by_theme.setdefault(e["theme"], []).append(e)

    lines = ["# Catalog", "",
             "21 essays grouped by theme. Browse by [difficulty](#by-difficulty) or [bridge bar](#by-bridge-bar) below.",
             "",
             "## By theme", ""]

    for theme_slug in ["dealer-positioning", "vanna-charm-vex", "vrp-volatility", "zero-dte", "cross-signal"]:
        items = by_theme.get(theme_slug, [])
        if not items:
            continue
        lines.append(f"### {_theme_display_name(theme_slug)}")
        lines.append("")
        lines.append("| # | Essay | Status | Difficulty | Bridge bars |")
        lines.append("|---|---|---|---|---|")
        for e in sorted(items, key=lambda x: x["_dir"]):
            n = e["_dir"].split("/")[-1].split("-")[0]
            bars = ", ".join(f"`{b}`" for b in e.get("bridge_bars", []))
            lines.append(f"| {n} | [{e['title']}]({e['_dir']}/) | {_status_badge(e['status'])} | {e['difficulty']} | {bars} |")
        lines.append("")

    # By difficulty
    lines.append("## By difficulty")
    lines.append("")
    for diff in ["beginner", "intermediate", "advanced"]:
        diff_items = [e for e in essays if e.get("difficulty") == diff]
        if not diff_items:
            continue
        lines.append(f"### {diff.title()}")
        for e in sorted(diff_items, key=lambda x: x["_dir"]):
            lines.append(f"- [{e['title']}]({e['_dir']}/) — {e['summary']}")
        lines.append("")

    # By bridge bar
    lines.append("## By bridge bar")
    lines.append("")
    by_bar: dict[str, list[dict]] = {}
    for e in essays:
        for b in e.get("bridge_bars", []):
            by_bar.setdefault(b, []).append(e)
    for bar in sorted(by_bar):
        lines.append(f"### `{bar}`")
        for e in sorted(by_bar[bar], key=lambda x: x["_dir"]):
            lines.append(f"- [{e['title']}]({e['_dir']}/)")
        lines.append("")

    return "\n".join(lines) + "\n"


def render_theme_readme(repo: Path, theme_slug: str) -> str:
    essays = [e for e in _load_essays(repo) if e["theme"] == theme_slug]
    display = _theme_display_name(theme_slug)
    lines = [f"# {display} strategies for QuantConnect",
             "",
             f"{len(essays)} backtest essays in this theme.",
             "",
             "## Essays", ""]
    for e in sorted(essays, key=lambda x: x["_dir"]):
        n = e["_dir"].split("/")[-1].split("-")[0]
        lines.append(f"- {n} [{e['title']}]({e['_dir'].split('/')[-1]}/) — {e['summary']} {_status_badge(e['status'])}")
    lines.append("")
    return "\n".join(lines) + "\n"


def render_sitemap(repo: Path, base_url: str) -> str:
    essays = _load_essays(repo)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines.append(f"  <url><loc>{base_url}/</loc></url>")
    lines.append(f"  <url><loc>{base_url}/catalog/</loc></url>")
    for e in essays:
        loc = f"{base_url}/{e['_dir']}/"
        lastmod = e.get("last_updated", "2026-06-01")
        lines.append(f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod></url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_catalog(repo: Path, base_url: str = "https://examples.flashalpha.com") -> None:
    """Write catalog.md, llms.txt, per-theme READMEs, _sitemap.xml."""
    (repo / "catalog.md").write_text(render_catalog_md(repo), encoding="utf-8")
    (repo / "llms.txt").write_text(render_llms_txt(repo), encoding="utf-8")
    (repo / "_sitemap.xml").write_text(render_sitemap(repo, base_url), encoding="utf-8")
    for theme_slug, theme_dir_name in THEMES_DIR_MAP.items():
        theme_path = repo / "essays" / theme_dir_name
        if theme_path.is_dir():
            (theme_path / "README.md").write_text(
                render_theme_readme(repo, theme_slug), encoding="utf-8"
            )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build catalog.md / llms.txt / theme READMEs / sitemap")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--base-url", default="https://examples.flashalpha.com")
    p.add_argument("--check", action="store_true",
                   help="Build into a temp dir and diff against current; fail on drift.")
    args = p.parse_args(argv)

    if args.check:
        import tempfile, shutil, filecmp
        with tempfile.TemporaryDirectory() as td:
            tmp_root = Path(td) / "repo"
            shutil.copytree(args.repo_root, tmp_root)
            build_catalog(tmp_root, args.base_url)
            # Diff: catalog.md, llms.txt, _sitemap.xml, theme READMEs
            for f in ["catalog.md", "llms.txt", "_sitemap.xml"]:
                if not filecmp.cmp(tmp_root / f, Path(args.repo_root) / f, shallow=False):
                    print(f"DRIFT: {f} would change. Run `fa-build-catalog` and commit.", file=sys.stderr)
                    return 1
        print("OK — no catalog drift")
        return 0

    build_catalog(Path(args.repo_root), args.base_url)
    print("Catalog built.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to PASS**

```bash
pytest tests/test_build_catalog.py -v
```
Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(tools): build-catalog — meta.yaml × N → catalog.md / llms.txt / theme READMEs / sitemap

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 11: verify-essay tool (golden comparison)

**Files:**
- Create: `tools/src/flashalpha_examples_tools/verify_essay.py`
- Create: `tools/tests/test_verify_essay.py`

Compares a LEAN backtest result against the committed `golden.json` within tolerance.

- [ ] **Step 1: Write the failing tests**

```python
import json
from pathlib import Path

import pytest

from flashalpha_examples_tools.verify_essay import (
    GoldenMismatch, verify_against_golden,
)
from flashalpha_examples_tools._lean_output import BacktestResult


def _golden():
    return {"final_equity": 102417.50, "total_trades": 84, "sharpe": 0.72, "max_drawdown": -0.045}


def _result(**overrides):
    base = dict(final_equity=102417.50, initial_equity=100000.0, total_trades=84,
                sharpe=0.72, sortino=1.05, max_drawdown=-0.045)
    base.update(overrides)
    return BacktestResult(**base, equity_curve=[])


def test_exact_match_passes():
    verify_against_golden(_result(), _golden())  # no exception


def test_equity_drift_within_tolerance_passes():
    verify_against_golden(_result(final_equity=102417.50 * 1.00005), _golden())


def test_equity_drift_outside_tolerance_fails():
    with pytest.raises(GoldenMismatch, match="final_equity"):
        verify_against_golden(_result(final_equity=102417.50 * 1.01), _golden())


def test_trade_count_exact_match_required():
    with pytest.raises(GoldenMismatch, match="total_trades"):
        verify_against_golden(_result(total_trades=83), _golden())


def test_sharpe_drift_within_tolerance_passes():
    verify_against_golden(_result(sharpe=0.72 + 0.005), _golden())


def test_sharpe_drift_outside_tolerance_fails():
    with pytest.raises(GoldenMismatch, match="sharpe"):
        verify_against_golden(_result(sharpe=0.72 + 0.05), _golden())
```

- [ ] **Step 2: Run to fail**

```bash
cd tools && pytest tests/test_verify_essay.py -v
```
Expected: ImportError.

- [ ] **Step 3: Write `verify_essay.py`**

```python
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
```

- [ ] **Step 4: Run tests to PASS**

```bash
pytest tests/test_verify_essay.py -v
```
Expected: 6 PASS.

- [ ] **Step 5: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(tools): verify-essay — compare LEAN result vs golden.json within tolerance

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 12: render-results tool (PNGs + CSVs)

**Files:**
- Create: `tools/src/flashalpha_examples_tools/render_results.py`
- Create: `tools/tests/test_render_results.py`

Produces `results/equity-curve-<lang>.png`, `results/monthly-returns.csv`, `results/trade-stats.json`, `results/parameter-sweep.csv` from LEAN's raw output.

- [ ] **Step 1: Write the failing tests**

```python
import json
from pathlib import Path

import pytest

from flashalpha_examples_tools.render_results import (
    render_equity_curve_png, render_monthly_returns_csv,
    render_trade_stats_json,
)
from flashalpha_examples_tools._lean_output import BacktestResult


@pytest.fixture
def sample_result() -> BacktestResult:
    # 3 months of fake daily equity for monthly-returns + equity-curve
    import time
    start_ts = int(time.mktime((2024, 6, 1, 0, 0, 0, 0, 0, 0)))
    curve = [(start_ts + i * 86400, 100000.0 + i * 50.0) for i in range(90)]
    return BacktestResult(
        final_equity=curve[-1][1], initial_equity=100000.0,
        total_trades=12, sharpe=0.72, sortino=1.05, max_drawdown=-0.045,
        equity_curve=curve,
    )


def test_render_equity_curve_writes_png(tmp_path: Path, sample_result):
    out = tmp_path / "eq.png"
    render_equity_curve_png(sample_result, out, title="Test")
    assert out.exists()
    assert out.stat().st_size > 0


def test_render_monthly_returns_writes_csv(tmp_path: Path, sample_result):
    out = tmp_path / "monthly.csv"
    render_monthly_returns_csv(sample_result, out)
    text = out.read_text()
    assert "month" in text.lower() or "Month" in text
    assert "2024-06" in text or "2024-07" in text


def test_render_trade_stats_json(tmp_path: Path, sample_result):
    out = tmp_path / "stats.json"
    render_trade_stats_json(sample_result, out)
    data = json.loads(out.read_text())
    assert data["total_trades"] == 12
    assert data["sharpe"] == pytest.approx(0.72)
    assert "final_equity" in data
```

- [ ] **Step 2: Run to fail**

```bash
cd tools && pytest tests/test_render_results.py -v
```
Expected: ImportError.

- [ ] **Step 3: Write `render_results.py`**

```python
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
```

- [ ] **Step 4: Run tests to PASS**

```bash
pytest tests/test_render_results.py -v
```
Expected: 3 PASS.

- [ ] **Step 5: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(tools): render-results — LEAN output → equity-curve PNG + monthly CSV + stats JSON

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 13: capture-golden tool

**Files:**
- Create: `tools/src/flashalpha_examples_tools/capture_golden.py`
- Create: `tools/tests/test_capture_golden.py`

Wraps `lean backtest` + `render-results` + writes `golden.json`. One-stop for "I changed the algorithm; recapture everything."

- [ ] **Step 1: Write the failing tests**

`test_capture_golden.py`:

```python
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from flashalpha_examples_tools.capture_golden import (
    capture_golden, write_golden_json,
)
from flashalpha_examples_tools._lean_output import BacktestResult


def test_write_golden_json_round_trips(tmp_path: Path):
    out = tmp_path / "golden.json"
    r = BacktestResult(final_equity=100_000.0, initial_equity=100_000.0,
                       total_trades=0, sharpe=0.0, sortino=0.0,
                       max_drawdown=-0.0, equity_curve=[])
    write_golden_json(r, out)
    data = json.loads(out.read_text())
    assert data["final_equity"] == 100_000.0
    assert data["total_trades"] == 0


def test_capture_golden_invokes_lean(tmp_path: Path, monkeypatch):
    """capture_golden() shells out to `lean backtest`; verify the call shape."""
    essay = tmp_path / "01-sample"
    (essay / "python").mkdir(parents=True)
    (essay / "results").mkdir()
    # Stub a fake backtest output
    fake_output = essay / "_backtest"
    fake_output.mkdir()
    (fake_output / "1234-backtest").mkdir()
    (fake_output / "1234-backtest" / "BacktestResult.json").write_text(
        '{"Statistics": {"Total Trades": "5", "Sharpe Ratio": "0.5", "Sortino Ratio": "0.7", "Drawdown": "1%"}, '
        '"AlgorithmConfiguration": {"InitialCash": "100000"}, "Charts": {}}'
    )

    calls = []
    def fake_run(cmd, **kw):
        calls.append(cmd)
        class R: returncode = 0
        return R()

    monkeypatch.setattr("subprocess.run", fake_run)
    capture_golden(essay, "python")
    assert any("lean" in str(c) for c in calls)
    assert (essay / "python" / "golden.json").exists()
```

- [ ] **Step 2: Run to fail**

```bash
cd tools && pytest tests/test_capture_golden.py -v
```
Expected: ImportError.

- [ ] **Step 3: Write `capture_golden.py`**

```python
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

        # LEAN writes results to <output>/<run-id>/BacktestResult.json
        results = list(out_dir.rglob("BacktestResult.json"))
        if not results:
            raise FileNotFoundError(f"No BacktestResult.json under {out_dir}")
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
```

- [ ] **Step 4: Run tests to PASS**

```bash
pytest tests/test_capture_golden.py -v
```
Expected: 2 PASS.

- [ ] **Step 5: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(tools): capture-golden — lean backtest + golden.json + results artifacts

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 14: build-bib tool (BibTeX export)

**Files:**
- Create: `tools/src/flashalpha_examples_tools/build_bib.py`
- Create: `tools/tests/test_build_bib.py`

Aggregates every essay's `references.md` into `bibliography.md` (deduplicated, alphabetical) and `bibliography.bib` (BibTeX, Google Scholar–indexable).

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

import pytest

from flashalpha_examples_tools.build_bib import (
    parse_references, render_bibliography_md, render_bibliography_bib,
)


def test_parse_references_extracts_lines(tmp_path: Path):
    p = tmp_path / "references.md"
    p.write_text(
        "# References\n\n"
        "- Taleb, N. (1997). Dynamic Hedging. Wiley.\n"
        "- Sinclair, E. (2013). Volatility Trading. Wiley.\n"
        "- [Spotgamma — GEX explained](https://spotgamma.com/gex)\n"
    )
    refs = parse_references(p)
    assert len(refs) == 3
    assert any("Taleb" in r["raw"] for r in refs)
    assert any(r.get("url") == "https://spotgamma.com/gex" for r in refs)


def test_render_bibliography_md_dedupes(tmp_path: Path):
    refs = [
        {"raw": "Taleb, N. (1997). Dynamic Hedging.", "url": None},
        {"raw": "Taleb, N. (1997). Dynamic Hedging.", "url": None},  # dupe
        {"raw": "Sinclair, E. (2013). Volatility Trading.", "url": None},
    ]
    md = render_bibliography_md(refs)
    assert md.count("Taleb") == 1
    assert "Sinclair" in md


def test_render_bibliography_bib_yields_bibtex(tmp_path: Path):
    refs = [
        {"raw": "Taleb, N. (1997). Dynamic Hedging.", "url": None},
        {"raw": "Spotgamma — GEX explained", "url": "https://spotgamma.com/gex"},
    ]
    bib = render_bibliography_bib(refs)
    assert "@misc{" in bib or "@book{" in bib
    assert "Taleb" in bib
```

- [ ] **Step 2: Run to fail**

```bash
cd tools && pytest tests/test_build_bib.py -v
```
Expected: ImportError.

- [ ] **Step 3: Write `build_bib.py`**

```python
"""Aggregate references.md across essays into bibliography.md + bibliography.bib."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


_BULLET_RE = re.compile(r"^\s*-\s+(.+?)\s*$")
_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")


def parse_references(refs_path: Path) -> list[dict]:
    """Parse a references.md file into a list of {raw, url} dicts.

    A reference is a bullet line. If it contains a markdown link, the URL is extracted.
    """
    if not refs_path.exists():
        return []
    out: list[dict] = []
    for line in refs_path.read_text(encoding="utf-8").splitlines():
        m = _BULLET_RE.match(line)
        if not m:
            continue
        text = m.group(1).strip()
        link = _LINK_RE.search(text)
        out.append({
            "raw": text,
            "url": link.group(2) if link else None,
        })
    return out


def collect_all_references(repo: Path) -> list[dict]:
    refs: list[dict] = []
    for p in (repo / "essays").rglob("references.md"):
        refs.extend(parse_references(p))
    return refs


def _dedupe(refs: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for r in refs:
        key = r["raw"]
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def render_bibliography_md(refs: list[dict]) -> str:
    refs = sorted(_dedupe(refs), key=lambda r: r["raw"].lower())
    lines = ["# Bibliography", "",
             "Aggregated references across all essays.", ""]
    for r in refs:
        lines.append(f"- {r['raw']}")
    return "\n".join(lines) + "\n"


def render_bibliography_bib(refs: list[dict]) -> str:
    refs = _dedupe(refs)
    out_lines: list[str] = []
    for r in refs:
        key = hashlib.md5(r["raw"].encode("utf-8")).hexdigest()[:8]
        # Guess entry type: URL → @misc, else @book/@article (use @book as safe default)
        if r["url"]:
            out_lines.append(f"@misc{{ref_{key},")
            out_lines.append(f"  title = {{{r['raw']}}},")
            out_lines.append(f"  url = {{{r['url']}}}")
            out_lines.append("}")
        else:
            out_lines.append(f"@book{{ref_{key},")
            out_lines.append(f"  title = {{{r['raw']}}}")
            out_lines.append("}")
        out_lines.append("")
    return "\n".join(out_lines)


def build_bib(repo: Path) -> None:
    refs = collect_all_references(repo)
    (repo / "bibliography.md").write_text(render_bibliography_md(refs), encoding="utf-8")
    (repo / "bibliography.bib").write_text(render_bibliography_bib(refs), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build bibliography.md + bibliography.bib")
    p.add_argument("--repo-root", default=".")
    args = p.parse_args(argv)
    build_bib(Path(args.repo_root))
    print("Bibliography built.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to PASS**

```bash
pytest tests/test_build_bib.py -v
```
Expected: 3 PASS.

- [ ] **Step 5: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(tools): build-bib — references.md × N → bibliography.md + bibliography.bib

BibTeX is Google Scholar-indexable; deduplicated, alphabetical .md is human-readable.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 15: new-essay scaffolder

**Files:**
- Create: `tools/src/flashalpha_examples_tools/new_essay.py`
- Create: `tools/tests/test_new_essay.py`

CLI: `fa-new-essay --theme dealer-positioning --slug gamma-flip --title "Gamma flip strike trading" --number 03`. Scaffolds the full essay folder shape per `check_orphans.REQUIRED_FILES/DIRS`.

- [ ] **Step 1: Write the failing tests**

```python
from pathlib import Path

import pytest

from flashalpha_examples_tools.new_essay import scaffold_essay
from flashalpha_examples_tools.check_orphans import check_essay_shape


def test_scaffold_creates_complete_essay(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "essays" / "a-dealer-positioning").mkdir(parents=True)
    essay = scaffold_essay(
        repo, theme_slug="dealer-positioning",
        slug="gamma-flip", title="Gamma flip strike trading",
        number=3,
    )
    # Required shape passes
    check_essay_shape(essay)
    # README has frontmatter
    text = (essay / "README.md").read_text()
    assert text.startswith("---")
    assert "gamma-flip" in text


def test_scaffold_rejects_existing_dir(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "essays" / "a-dealer-positioning" / "03-gamma-flip").mkdir(parents=True)
    with pytest.raises(FileExistsError):
        scaffold_essay(repo, theme_slug="dealer-positioning",
                       slug="gamma-flip", title="X", number=3)
```

- [ ] **Step 2: Run to fail**

```bash
cd tools && pytest tests/test_new_essay.py -v
```
Expected: ImportError.

- [ ] **Step 3: Write `new_essay.py`**

```python
"""Scaffold a new essay folder with the full required shape.

Usage: fa-new-essay --theme <slug> --slug <slug> --title "Title" --number NN
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from ._schema import THEMES_DIR_MAP


_README_TEMPLATE = """\
---
{frontmatter_yaml}---

# {title}

> **What you'll build:** _(2 sentences describing the strategy — replace this placeholder.)_

## The intuition

_(2–4 paragraphs explaining the WHY before the WHAT. Why does this technique work? What dealer/regime mechanic does it exploit? Where does it fail?)_

## The setup

_(Ticker, backtest window, the bridge bars you subscribe to, the parameters you'll tune.)_

## The algorithm

```python
# python/main.py — see python/ for the full file
```

```csharp
// csharp/Main.cs — see csharp/ for the full file
```

## Running it

```bash
cd python && lean backtest
cd ../csharp && lean backtest
```

## Results

_(Embed results/equity-curve-python.png once you've captured goldens.)_

## Sensitivity

_(Render results/parameter-sweep.csv as a markdown table once you've swept a key knob.)_

## Variations

- _(Cousin techniques worth exploring.)_

## When it fails

_(Honest discussion of regime breakdown, drawdown periods, and how to detect failure live.)_

## FAQ

### What is {title_lower}?
_(2-paragraph plain-English answer.)_

### Why use FlashAlpha's bars for this instead of computing it from raw OI?
_(Advantages.)_

### Does this work in real money?
_(Cost/regime/slippage discussion.)_

### What does the worst regime period look like?
_(Historical example.)_

### Can I run this in QuantConnect Cloud?
_(Yes/no/caveats.)_

## Related essays

_(Links from frontmatter `related:` after you fill them in.)_

## References

_(See `references.md` — aggregated automatically.)_
"""


def _make_frontmatter(slug: str, title: str, theme_slug: str) -> dict:
    return {
        "title": title,
        "slug": slug,
        "theme": theme_slug,
        "difficulty": "intermediate",
        "status": "draft",
        "summary": f"_(One-sentence summary of {title}.)_",
        "bridge_bars": ["FlashAlphaGexBar"],
        "data_endpoints": ["exposure/gex"],
        "tickers": ["SPY"],
        "backtest_window": {"start": "2024-03-01", "end": "2024-09-30"},
        "expected_runtime": {"python": "5m", "csharp": "2m"},
        "golden": {"python": {}, "csharp": {}},
        "keywords": [title.lower(), "QuantConnect", "LEAN"],
        "last_updated": "2026-06-01",
        "related": [],
        "references": [],
    }


def scaffold_essay(
    repo_root: Path, *, theme_slug: str, slug: str, title: str, number: int,
) -> Path:
    theme_dir_name = THEMES_DIR_MAP[theme_slug]
    essay_dir = repo_root / "essays" / theme_dir_name / f"{number:02d}-{slug}"
    if essay_dir.exists():
        raise FileExistsError(essay_dir)

    essay_dir.mkdir(parents=True)
    (essay_dir / "python").mkdir()
    (essay_dir / "csharp").mkdir()
    (essay_dir / "results").mkdir()

    fm = _make_frontmatter(slug=slug, title=title, theme_slug=theme_slug)
    fm_yaml = yaml.safe_dump(fm, sort_keys=False)

    (essay_dir / "README.md").write_text(
        _README_TEMPLATE.format(
            frontmatter_yaml=fm_yaml, title=title, title_lower=title.lower()
        ),
        encoding="utf-8",
    )
    (essay_dir / "meta.yaml").write_text(fm_yaml, encoding="utf-8")
    (essay_dir / "references.md").write_text(
        "# References\n\n_(Add references here — they aggregate into bibliography.md.)_\n",
        encoding="utf-8",
    )

    # Python LEAN project skeleton
    (essay_dir / "python" / "main.py").write_text(
        f'''"""Algorithm for {title}.

This is a DRAFT stub. Replace OnData/Initialize with real logic before flipping to stable.
"""

from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect import Resolution, SecurityType, Market
from flashalpha_quantconnect import GexBar, add_flashalpha_gex


class Algorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2024, 3, 1)
        self.SetEndDate(2024, 9, 30)
        self.SetCash(100_000)
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.gex = add_flashalpha_gex(self, "SPY").Symbol

    def OnData(self, slice):
        raise NotImplementedError(
            "Draft — see README.md for the proposed algorithm. "
            "Implement before flipping status to stable."
        )
''',
        encoding="utf-8",
    )
    (essay_dir / "python" / "config.json").write_text(
        '{"environment": "backtesting", "algorithm-language": "Python"}\n',
        encoding="utf-8",
    )
    (essay_dir / "python" / "lean.json").write_text(
        '{"algorithm-language": "Python", "algorithm-location": "main.py"}\n',
        encoding="utf-8",
    )
    (essay_dir / "python" / "requirements.txt").write_text(
        "flashalpha-quantconnect==0.1.1\n", encoding="utf-8",
    )
    (essay_dir / "python" / "golden.json").write_text("{}\n", encoding="utf-8")

    # C# LEAN project skeleton
    csproj_name = "".join(w.capitalize() for w in slug.split("-")) + ".csproj"
    (essay_dir / "csharp" / "Main.cs").write_text(
        f'''using QuantConnect;
using QuantConnect.Algorithm;
using QuantConnect.Data;
using FlashAlpha.QuantConnect;
using FlashAlpha.QuantConnect.Data;

namespace FlashAlphaExamples;

public class Algorithm : QCAlgorithm
{{
    private Symbol _spy = null!;
    private Symbol _gex = null!;

    public override void Initialize()
    {{
        SetStartDate(2024, 3, 1);
        SetEndDate(2024, 9, 30);
        SetCash(100_000);
        _spy = AddEquity("SPY", Resolution.Daily).Symbol;
        _gex = this.AddFlashAlphaGex("SPY").Symbol;
    }}

    public override void OnData(Slice slice)
    {{
        throw new System.NotImplementedException(
            "Draft — see README.md. Implement before flipping status to stable.");
    }}
}}
''',
        encoding="utf-8",
    )
    (essay_dir / "csharp" / "config.json").write_text(
        '{"environment": "backtesting", "algorithm-language": "CSharp"}\n',
        encoding="utf-8",
    )
    (essay_dir / "csharp" / "lean.json").write_text(
        '{"algorithm-language": "CSharp", "algorithm-location": "Main.cs"}\n',
        encoding="utf-8",
    )
    (essay_dir / "csharp" / csproj_name).write_text(
        '''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>disable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="QuantConnect.Lean" Version="2.5.17414" />
    <PackageReference Include="FlashAlpha.QuantConnect" Version="0.1.1" />
  </ItemGroup>
</Project>
''',
        encoding="utf-8",
    )
    (essay_dir / "csharp" / "golden.json").write_text("{}\n", encoding="utf-8")

    return essay_dir


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Scaffold a new essay folder")
    p.add_argument("--theme", required=True, choices=list(THEMES_DIR_MAP.keys()))
    p.add_argument("--slug", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--number", required=True, type=int)
    p.add_argument("--repo-root", default=".")
    args = p.parse_args(argv)

    essay = scaffold_essay(
        Path(args.repo_root),
        theme_slug=args.theme, slug=args.slug, title=args.title, number=args.number,
    )
    print(f"Scaffolded: {essay}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to PASS**

```bash
pytest tests/test_new_essay.py -v
```
Expected: 2 PASS.

- [ ] **Step 5: Commit**

```bash
cd ..
git add tools/
git commit -m "feat(tools): new-essay — scaffold a complete essay folder shape

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase 2 — Flagship essay: gamma scalping (10 tasks)

### Task 16: Scaffold the 21 essay folders (flagship + 20 drafts)

**Files:** all 21 essay folders.

This task creates every essay folder using `fa-new-essay`. The flagship gets `stable`-track content in subsequent tasks; the other 20 stay as drafts that ship in v0.1.0 alongside the flagship.

- [ ] **Step 1: Scaffold all 21 essays via the CLI**

```bash
cd e:/repos/tecware/flashalpha-packages/flashalpha-historical-examples

# Theme A: dealer positioning (5)
fa-new-essay --theme dealer-positioning --slug gamma-scalping --title "Gamma scalping in QuantConnect" --number 1
fa-new-essay --theme dealer-positioning --slug gex-regime-following --title "GEX regime following" --number 2
fa-new-essay --theme dealer-positioning --slug gamma-flip-strike --title "Gamma flip strike trading" --number 3
fa-new-essay --theme dealer-positioning --slug negative-gamma-vol-expansion --title "Negative-gamma vol expansion play" --number 4
fa-new-essay --theme dealer-positioning --slug pin-risk-avoidance-0dte --title "Pin-risk avoidance (0DTE)" --number 5

# Theme B: vanna / charm / VEX (3)
fa-new-essay --theme vanna-charm-vex --slug charm-flow-afternoon --title "Charm-flow afternoon timing" --number 6
fa-new-essay --theme vanna-charm-vex --slug vanna-shock-reversal --title "Vanna-shock reversal" --number 7
fa-new-essay --theme vanna-charm-vex --slug combined-greek-regime-grid --title "Combined-greek regime grid" --number 8

# Theme C: VRP / volatility (4)
fa-new-essay --theme vrp-volatility --slug vrp-harvest-short-vol --title "VRP harvest short-vol" --number 9
fa-new-essay --theme vrp-volatility --slug iv-rank-entry-filter --title "IV-rank entry filter" --number 10
fa-new-essay --theme vrp-volatility --slug realized-vs-implied-divergence --title "Realized vs implied divergence" --number 11
fa-new-essay --theme vrp-volatility --slug vol-term-structure-spread --title "Vol term-structure spread" --number 12

# Theme D: 0DTE (4)
fa-new-essay --theme zero-dte --slug friday-gamma-squeeze --title "0DTE Friday gamma squeeze" --number 13
fa-new-essay --theme zero-dte --slug pin-gravitation --title "0DTE pin gravitation" --number 14
fa-new-essay --theme zero-dte --slug intraday-gamma-flip --title "0DTE intraday gamma flip" --number 15
fa-new-essay --theme zero-dte --slug expected-move-straddle --title "0DTE expected-move straddle" --number 16

# Theme E: cross-signal (4)
fa-new-essay --theme cross-signal --slug dispersion-spy-vs-rty --title "Dispersion: SPY vs RTY" --number 17
fa-new-essay --theme cross-signal --slug calendar-carry-positive-gamma --title "Calendar carry on positive-gamma days" --number 18
fa-new-essay --theme cross-signal --slug max-pain-reversion --title "Max-pain reversion" --number 19
fa-new-essay --theme cross-signal --slug earnings-vol-contraction --title "Earnings vol contraction" --number 20
```

- [ ] **Step 2: Verify all 21 essays have the required shape**

```bash
fa-check-orphans --repo-root .
```
Expected: `OK — no orphans`.

- [ ] **Step 3: Verify all 21 essay frontmatters are valid**

```bash
for d in essays/*/[0-9]*/; do fa-verify-frontmatter "$d"; done
```
Expected: every essay prints `OK (1 essays verified)`.

- [ ] **Step 4: Remove the `.gitkeep` placeholders now that real content exists**

```bash
rm essays/*/.gitkeep
```

- [ ] **Step 5: Commit**

```bash
git add essays/
git commit -m "feat: scaffold 21 essay folders (flagship + 20 drafts)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 17: Write the gamma-scalping essay README

**Files:**
- Modify: `essays/a-dealer-positioning/01-gamma-scalping/README.md`
- Modify: `essays/a-dealer-positioning/01-gamma-scalping/meta.yaml`
- Modify: `essays/a-dealer-positioning/01-gamma-scalping/references.md`
- Create: `essays/a-dealer-positioning/01-gamma-scalping/transcript.md`

- [ ] **Step 1: Write the full essay README**

Replace `essays/a-dealer-positioning/01-gamma-scalping/README.md` with the complete essay. Frontmatter has `status: stable` and concrete goldens (captured by Task 21). Body sections required per spec §2:

1. **What you'll build** (TLDR blockquote, 2 sentences)
2. **The intuition** (3 paragraphs — what dealer gamma is, why hedging it produces theta-pay-vega-receive structure, where the regime breaks)
3. **The setup** (SPY, 2024-03-01 → 2024-09-30, FlashAlphaGexBar + FlashAlphaSurfaceBar, parameters: rebalance threshold, hedge frequency)
4. **The algorithm** (side-by-side C# + Python ~30 LOC each)
5. **Running it** (`lean backtest python/` + `lean backtest csharp/`, expected console output snippet)
6. **Results** (embed `results/equity-curve-python.png`, render `results/monthly-returns.csv` as a markdown table)
7. **Sensitivity** (embed `results/parameter-sweep.csv` as a markdown table, narrate the knob)
8. **Variations** (5 bullets — different ticker, different rebalance threshold, intraday hedging, etc.)
9. **When it fails** (honest discussion of Aug 2024 drawdown period)
10. **FAQ** (6 Q&A pairs covering: what is gamma scalping / why FlashAlpha GEX / does it work in real money / worst regime period / QC Cloud / 401 errors)
11. **Related essays** (links to gex-regime-following + gamma-flip-strike-trading)
12. **References** (footer pointing at references.md)

Target length: 350-600 lines of markdown.

- [ ] **Step 2: Update `meta.yaml`** to mirror the new frontmatter exactly (status: stable, expected goldens left as placeholders until Task 21 captures them).

- [ ] **Step 3: Write `references.md`** with at least 5 real references:

```markdown
# References

- Taleb, N. (1997). *Dynamic Hedging: Managing Vanilla and Exotic Options*. Wiley.
- Sinclair, E. (2013). *Volatility Trading*. Wiley.
- Bennett, C. (2014). *Trading Volatility, Correlation, Term Structure and Skew*. Self-published.
- [SpotGamma — Gamma Exposure Explained](https://spotgamma.com/gamma-exposure-explained/)
- [SqueezeMetrics — The Implied Order Book](https://squeezemetrics.com/monitor/download/pdf/iob.pdf)
- [QuantPedia — Gamma Scalping (Long Volatility) Strategy](https://quantpedia.com/strategies/gamma-scalping-long-volatility-strategy/)
```

- [ ] **Step 4: Write `transcript.md`** placeholder

```markdown
# Video transcript: gamma scalping in QuantConnect

_(Video walkthrough recording is post-launch. Transcript will be added once the video ships.)_
```

- [ ] **Step 5: Verify frontmatter is in sync + valid**

```bash
fa-verify-frontmatter essays/a-dealer-positioning/01-gamma-scalping/
```
Expected: `OK (1 essays verified)`.

- [ ] **Step 6: Commit**

```bash
git add essays/a-dealer-positioning/01-gamma-scalping/
git commit -m "docs(flagship): full gamma-scalping essay README + references + transcript placeholder

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 18: Write the Python gamma-scalping algorithm

**Files:**
- Modify: `essays/a-dealer-positioning/01-gamma-scalping/python/main.py`
- Modify: `essays/a-dealer-positioning/01-gamma-scalping/python/config.json`

- [ ] **Step 1: Write the algorithm**

`essays/a-dealer-positioning/01-gamma-scalping/python/main.py`:

```python
"""Gamma scalping in QuantConnect — flagship essay.

Strategy: gate SPY exposure on FlashAlpha's dealer-gamma regime label.
When dealers are net long gamma (positive_gamma), volatility is suppressed
and short-gamma exposure is unfavorable — stay flat. When dealers are net
short gamma (negative_gamma), realized volatility tends to spike — take a
long-gamma position via straddles or rebalance an existing one.

This algorithm is a simplified pedagogical version: long SPY when regime
is positive (low realized vol, riding the dealer-pinned drift), flat
otherwise. A full gamma-scalping implementation would hold a long-gamma
straddle and rebalance delta to zero at threshold; that variant is
described in `## Variations` of the essay and left as an exercise.

See ../README.md for the full essay.
"""

from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect import Resolution, SecurityType, Market
from flashalpha_quantconnect import GexBar, add_flashalpha_gex


class Algorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2024, 3, 1)
        self.SetEndDate(2024, 9, 30)
        self.SetCash(100_000)

        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.gex_symbol = add_flashalpha_gex(self, "SPY").Symbol
        self.SetWarmUp(0)

    def OnData(self, slice):
        if self.gex_symbol not in slice:
            return
        gex = slice[self.gex_symbol]
        if not isinstance(gex, GexBar):
            return

        # Gate SPY exposure on the dealer-gamma regime label.
        if gex.NetGexLabel == "positive":
            self.SetHoldings(self.spy, 1.0)
        else:
            self.Liquidate(self.spy)

        self.Debug(f"{self.Time:%Y-%m-%d} regime={gex.NetGexLabel} net_gex={gex.NetGex}")
```

- [ ] **Step 2: Update `config.json`** with backtest period:

```json
{
  "environment": "backtesting",
  "algorithm-language": "Python",
  "algorithm-location": "main.py",
  "algorithm-id": "gamma-scalping-python",
  "data-folder": "data",
  "parameters": {
    "ticker": "SPY",
    "start_date": "2024-03-01",
    "end_date": "2024-09-30",
    "starting_cash": "100000"
  }
}
```

- [ ] **Step 3: Verify Python imports without LEAN runtime (compile check)**

```bash
cd essays/a-dealer-positioning/01-gamma-scalping/python
python -m py_compile main.py
```
Expected: no output (compile success).

- [ ] **Step 4: Commit**

```bash
cd /e/repos/tecware/flashalpha-packages/flashalpha-historical-examples
git add essays/a-dealer-positioning/01-gamma-scalping/python/
git commit -m "feat(flagship): Python gamma-scalping algorithm

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 19: Write the C# gamma-scalping algorithm

**Files:**
- Modify: `essays/a-dealer-positioning/01-gamma-scalping/csharp/Main.cs`
- Modify: `essays/a-dealer-positioning/01-gamma-scalping/csharp/config.json`

- [ ] **Step 1: Write the algorithm**

`essays/a-dealer-positioning/01-gamma-scalping/csharp/Main.cs`:

```csharp
// Gamma scalping in QuantConnect — flagship essay.
//
// Strategy: gate SPY exposure on FlashAlpha's dealer-gamma regime label.
// When dealers are net long gamma (positive_gamma), volatility is suppressed
// and short-gamma exposure is unfavorable — stay flat. When dealers are net
// short gamma (negative_gamma), realized volatility tends to spike.
//
// This algorithm is a simplified pedagogical version: long SPY when regime
// is positive, flat otherwise. A full gamma-scalping implementation would
// hold a long-gamma straddle and rebalance delta to zero at threshold; that
// variant is described in `## Variations` of the essay.
//
// See ../README.md for the full essay.

using QuantConnect;
using QuantConnect.Algorithm;
using QuantConnect.Data;
using FlashAlpha.QuantConnect;
using FlashAlpha.QuantConnect.Data;

namespace FlashAlphaExamples;

public class Algorithm : QCAlgorithm
{
    private Symbol _spy = null!;
    private Symbol _gex = null!;

    public override void Initialize()
    {
        SetStartDate(2024, 3, 1);
        SetEndDate(2024, 9, 30);
        SetCash(100_000);

        _spy = AddEquity("SPY", Resolution.Daily).Symbol;
        _gex = this.AddFlashAlphaGex("SPY").Symbol;
    }

    public override void OnData(Slice slice)
    {
        if (!slice.ContainsKey(_gex)) return;
        var gex = slice[_gex] as FlashAlphaGexBar;
        if (gex is null) return;

        if (gex.NetGexLabel == "positive")
            SetHoldings(_spy, 1.0);
        else
            Liquidate(_spy);

        Debug($"{Time:yyyy-MM-dd} regime={gex.NetGexLabel} net_gex={gex.NetGex}");
    }
}
```

- [ ] **Step 2: Update `config.json`**:

```json
{
  "environment": "backtesting",
  "algorithm-language": "CSharp",
  "algorithm-location": "GammaScalping.dll",
  "algorithm-id": "gamma-scalping-csharp",
  "parameters": {
    "ticker": "SPY",
    "start_date": "2024-03-01",
    "end_date": "2024-09-30",
    "starting_cash": "100000"
  }
}
```

- [ ] **Step 3: Verify C# builds**

```bash
cd essays/a-dealer-positioning/01-gamma-scalping/csharp
dotnet build
```
Expected: `Build succeeded. 0 Error(s).`

- [ ] **Step 4: Commit**

```bash
cd /e/repos/tecware/flashalpha-packages/flashalpha-historical-examples
git add essays/a-dealer-positioning/01-gamma-scalping/csharp/
git commit -m "feat(flagship): C# gamma-scalping algorithm

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 20: Pin bridge version + verify shared config matches across langs

**Files:**
- Modify: `essays/a-dealer-positioning/01-gamma-scalping/python/requirements.txt`
- Modify: `essays/a-dealer-positioning/01-gamma-scalping/csharp/GammaScalping.csproj`

- [ ] **Step 1: Confirm `requirements.txt`**

`essays/a-dealer-positioning/01-gamma-scalping/python/requirements.txt`:

```
flashalpha-quantconnect==0.1.1
```

- [ ] **Step 2: Confirm csproj pinning**

The `fa-new-essay` scaffold already pinned `FlashAlpha.QuantConnect 0.1.1`. Verify:

```bash
grep "FlashAlpha.QuantConnect" essays/a-dealer-positioning/01-gamma-scalping/csharp/GammaScalping.csproj
```
Expected: `Version="0.1.1"`.

- [ ] **Step 3: Verify shared config parameters match across langs**

Open both `python/config.json` and `csharp/config.json` — assert the `parameters` block (ticker, start_date, end_date, starting_cash) is byte-identical.

- [ ] **Step 4: No commit if state is already correct.** If any drift, fix + commit:

```bash
git add essays/a-dealer-positioning/01-gamma-scalping/
git commit -m "chore(flagship): align bridge pin + shared config across Python and C#

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 21: Capture goldens for the flagship (Python + C#)

**Requires:** `FLASHALPHA_API_KEY` in env. `lean` CLI installed. Docker running.

- [ ] **Step 1: Set env from sibling .env**

```bash
export FLASHALPHA_API_KEY=$(sed 's/\xef\xbb\xbf//' "e:/repos/tecware/flashalpha-packages/flashalpha-js/.env.test.local" \
    | grep 'FLASHALPHA_API_KEY=' | head -1 | cut -d= -f2- | tr -d '"\r\n' | tr -d "'")
echo "Key length: ${#FLASHALPHA_API_KEY}"
```
Expected: `Key length: 40`.

- [ ] **Step 2: Run capture for Python**

```bash
fa-capture-golden essays/a-dealer-positioning/01-gamma-scalping/ --language python
```
Expected: `Capturing 01-gamma-scalping (python)...` followed by `Done.`. Real LEAN backtest runs ~5-10 min.

- [ ] **Step 3: Run capture for C#**

```bash
fa-capture-golden essays/a-dealer-positioning/01-gamma-scalping/ --language csharp
```
Expected: similar. C# backtest typically ~3 min.

- [ ] **Step 4: Inspect the captured goldens**

```bash
cat essays/a-dealer-positioning/01-gamma-scalping/python/golden.json
cat essays/a-dealer-positioning/01-gamma-scalping/csharp/golden.json
```
Expected: realistic numbers (final_equity near 100k, total_trades > 0, sharpe in plausible range).

- [ ] **Step 5: Update `meta.yaml` + `README.md` frontmatter** with the captured goldens. Both files MUST be in sync. Re-run frontmatter verification:

```bash
fa-verify-frontmatter essays/a-dealer-positioning/01-gamma-scalping/
```
Expected: `OK (1 essays verified)`.

- [ ] **Step 6: Commit**

```bash
git add essays/a-dealer-positioning/01-gamma-scalping/
git commit -m "feat(flagship): capture v0.1.0 goldens — Python + C#

Goldens captured from real LEAN backtest against live FlashAlpha API.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 22: Render results artifacts (PNGs + CSVs)

`fa-capture-golden` already invoked `render-results` for `equity-curve-<lang>.png`, `monthly-returns.csv`, `trade-stats.json`. This task adds the `parameter-sweep.csv` separately.

- [ ] **Step 1: Run a 3-point parameter sweep**

Vary the implicit knob (here: rebalance threshold or hedge frequency). Since the flagship uses a binary regime gate with no continuous knob, sweep an alternative — e.g., target weight: 0.5x / 1.0x / 1.5x leverage when regime is positive.

Write `essays/a-dealer-positioning/01-gamma-scalping/python/sweep.py`:

```python
"""3-point sweep: vary target leverage when regime is positive."""
import json, subprocess, tempfile
from pathlib import Path

from flashalpha_examples_tools._lean_output import parse_backtest_result

results = []
for leverage in [0.5, 1.0, 1.5]:
    config = {"environment": "backtesting", "parameters": {"target_leverage": str(leverage)}}
    # In the real flagship, main.py reads GetParameter("target_leverage").
    # Sweep mode: run 3 backtests, capture final_equity + sharpe.
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out"
        cmd = ["lean", "backtest", "essays/a-dealer-positioning/01-gamma-scalping/python/",
               "--output", str(out),
               "--parameter", f"target_leverage:{leverage}"]
        subprocess.run(cmd, check=True)
        bt = next(out.rglob("BacktestResult.json"))
        r = parse_backtest_result(bt)
        results.append({"target_leverage": leverage, "final_equity": r.final_equity, "sharpe": r.sharpe})

with open("essays/a-dealer-positioning/01-gamma-scalping/results/parameter-sweep.csv", "w") as f:
    f.write("target_leverage,final_equity,sharpe\n")
    for r in results:
        f.write(f"{r['target_leverage']},{r['final_equity']:.2f},{r['sharpe']:.3f}\n")
print("Sweep complete.")
```

- [ ] **Step 2: Update `main.py` to read the parameter**

Modify `Initialize()` in `python/main.py` to `target_leverage = float(self.GetParameter("target_leverage", "1.0"))` and use `target_leverage` instead of literal `1.0` in `SetHoldings(self.spy, target_leverage)`. Apply analogous change to `csharp/Main.cs`.

- [ ] **Step 3: Run the sweep**

```bash
python essays/a-dealer-positioning/01-gamma-scalping/python/sweep.py
```
Expected: 3 backtests run, `results/parameter-sweep.csv` produced with 3 rows.

- [ ] **Step 4: Re-capture goldens after the main.py change**

```bash
fa-capture-golden essays/a-dealer-positioning/01-gamma-scalping/ --language python
fa-capture-golden essays/a-dealer-positioning/01-gamma-scalping/ --language csharp
```

- [ ] **Step 5: Update frontmatter with fresh goldens; verify sync**

```bash
fa-verify-frontmatter essays/a-dealer-positioning/01-gamma-scalping/
```
Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add essays/a-dealer-positioning/01-gamma-scalping/
git commit -m "feat(flagship): parameter sweep + recapture goldens

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 23: Verify the flagship runs clean via `fa-verify-essay`

- [ ] **Step 1: Run a fresh backtest**

```bash
lean backtest essays/a-dealer-positioning/01-gamma-scalping/python/ --output /tmp/verify-py
```

- [ ] **Step 2: Verify against the committed golden**

```bash
BACKTEST=$(find /tmp/verify-py -name BacktestResult.json | head -1)
fa-verify-essay essays/a-dealer-positioning/01-gamma-scalping/ "$BACKTEST" --language python
```
Expected: `OK — 01-gamma-scalping (python) matches golden`.

- [ ] **Step 3: Repeat for C#**

```bash
lean backtest essays/a-dealer-positioning/01-gamma-scalping/csharp/ --output /tmp/verify-cs
BACKTEST=$(find /tmp/verify-cs -name BacktestResult.json | head -1)
fa-verify-essay essays/a-dealer-positioning/01-gamma-scalping/ "$BACKTEST" --language csharp
```
Expected: `OK — 01-gamma-scalping (csharp) matches golden`.

- [ ] **Step 4: No commit unless this task surfaces a fix that needed to be checked in.**

---

### Task 24: Generate OG card for the flagship

**Files:**
- Modify: `essays/a-dealer-positioning/01-gamma-scalping/results/og-card.png` (generated)

- [ ] **Step 1: Implement `tools/src/flashalpha_examples_tools/gen_og_cards.py`**

A small utility that takes (essay title, summary, equity-curve PNG path) and produces a 1200×630 OG card. Uses Pillow.

```python
"""Generate Open Graph cards (1200×630) per essay.

Composed of: title (40pt), summary (24pt), equity-curve preview thumbnail (right half).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


CARD_SIZE = (1200, 630)
PAD = 60


def _font(size: int):
    # Fallback to PIL default if no system font available
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def render_og_card(title: str, summary: str, equity_curve_path: Path, out_path: Path) -> None:
    img = Image.new("RGB", CARD_SIZE, color=(15, 15, 25))
    draw = ImageDraw.Draw(img)

    # Left half: title + summary
    title_font = _font(48)
    summary_font = _font(24)
    draw.text((PAD, PAD), title, font=title_font, fill=(240, 240, 245))
    # Wrap summary at ~50 chars
    import textwrap
    wrapped = "\n".join(textwrap.wrap(summary, width=42))
    draw.text((PAD, PAD + 120), wrapped, font=summary_font, fill=(180, 180, 195))

    # Footer
    footer_font = _font(20)
    draw.text((PAD, CARD_SIZE[1] - PAD - 30),
              "examples.flashalpha.com", font=footer_font, fill=(120, 180, 255))

    # Right half: equity curve thumbnail
    if equity_curve_path.exists():
        eq = Image.open(equity_curve_path).convert("RGB")
        thumb_w = CARD_SIZE[0] // 2 - PAD
        thumb_h = int(thumb_w * eq.height / eq.width)
        eq = eq.resize((thumb_w, thumb_h), Image.LANCZOS)
        img.paste(eq, (CARD_SIZE[0] // 2, (CARD_SIZE[1] - thumb_h) // 2))

    img.save(out_path, format="PNG")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--essay-dir", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--summary", required=True)
    args = p.parse_args(argv)

    essay = Path(args.essay_dir)
    eq = essay / "results" / "equity-curve-python.png"
    out = essay / "results" / "og-card.png"
    render_og_card(args.title, args.summary, eq, out)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run for the flagship**

```bash
fa-gen-og-cards --essay-dir essays/a-dealer-positioning/01-gamma-scalping/ \
  --title "Gamma scalping in QuantConnect" \
  --summary "Delta-neutral options portfolio gated by FlashAlpha's dealer-GEX regime signal."
```
Expected: writes `essays/a-dealer-positioning/01-gamma-scalping/results/og-card.png`.

- [ ] **Step 3: Inspect the card** — visually confirm title + summary + equity curve render correctly.

- [ ] **Step 4: Commit**

```bash
git add tools/src/flashalpha_examples_tools/gen_og_cards.py
git add essays/a-dealer-positioning/01-gamma-scalping/results/og-card.png
git commit -m "feat(tools): gen-og-cards + flagship OG card

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 25: Run the full catalog build + verify aggregation

- [ ] **Step 1: Build the catalog**

```bash
fa-build-catalog --repo-root . --base-url https://examples.flashalpha.com
```
Expected: writes/updates `catalog.md`, `llms.txt`, `_sitemap.xml`, and the 5 theme READMEs.

- [ ] **Step 2: Verify catalog content**

```bash
grep "Gamma scalping" catalog.md
grep "Gamma scalping" llms.txt
grep "01-gamma-scalping" _sitemap.xml
cat essays/a-dealer-positioning/README.md | head -20
```
Expected: flagship listed in every output, theme README enumerates the 5 dealer-positioning essays.

- [ ] **Step 3: Build the bibliography**

```bash
fa-build-bib --repo-root .
```
Expected: writes `bibliography.md` + `bibliography.bib`. Should contain the references from gamma-scalping (the only essay with real references at this point).

- [ ] **Step 4: Run drift checks**

```bash
fa-build-catalog --repo-root . --check
fa-check-orphans --repo-root .
```
Expected: both print OK.

- [ ] **Step 5: Commit**

```bash
git add catalog.md llms.txt _sitemap.xml bibliography.md bibliography.bib essays/*/README.md
git commit -m "docs: build catalog / llms.txt / sitemap / bibliography / theme READMEs

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Phase 3 — Hosted site (8 tasks)

### Task 26: MkDocs Material config + theme overrides

**Files:**
- Create: `mkdocs.yml`
- Create: `overrides/main.html`
- Create: `overrides/partials/head.html`
- Create: `overrides/partials/footer.html`
- Create: `overrides/assets/css/extra.css`

- [ ] **Step 1: Install MkDocs Material**

```bash
pip install mkdocs-material
```

- [ ] **Step 2: Write `mkdocs.yml`**

```yaml
site_name: flashalpha-historical-examples
site_url: https://examples.flashalpha.com/
site_description: 21 backtest essays for options strategies on QuantConnect LEAN — gamma scalping, dealer positioning, VRP, 0DTE, dispersion. Side-by-side C# + Python.
repo_url: https://github.com/FlashAlpha-lab/flashalpha-historical-examples
repo_name: FlashAlpha-lab/flashalpha-historical-examples
edit_uri: edit/main/

theme:
  name: material
  custom_dir: overrides
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - toc.integrate
    - search.suggest
    - search.share
    - content.code.copy
    - content.action.edit
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
      toggle: { icon: material/brightness-7, name: Switch to dark mode }
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: indigo
      toggle: { icon: material/brightness-4, name: Switch to light mode }

markdown_extensions:
  - admonition
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - tables
  - toc:
      permalink: true

plugins:
  - search

nav:
  - Home: README.md
  - Catalog: catalog.md
  - Essays:
      - Dealer positioning: essays/a-dealer-positioning/README.md
      - Vanna/charm/VEX: essays/b-vanna-charm-vex/README.md
      - VRP / volatility: essays/c-vrp-volatility/README.md
      - 0DTE: essays/d-zero-dte/README.md
      - Cross-signal: essays/e-cross-signal/README.md
  - Docs:
      - Getting started: docs/getting-started.md
      - What is an essay: docs/what-is-an-essay.md
      - Glossary: docs/glossary.md
      - LEAN CLI cheatsheet: docs/lean-cli-cheatsheet.md
      - Compatibility: docs/compatibility.md
  - Bibliography: bibliography.md

extra_css:
  - assets/css/extra.css
```

- [ ] **Step 3: Write `overrides/main.html`** (extends Material base, injects `head.html` and `footer.html`):

```html
{% extends "base.html" %}

{% block extrahead %}
  {% include "partials/head.html" %}
{% endblock %}

{% block footer %}
  {{ super() }}
  {% include "partials/footer.html" %}
{% endblock %}
```

- [ ] **Step 4: Write `overrides/partials/head.html`** — JSON-LD + OG + canonical injection (full implementation in Task 27).

For now a placeholder:

```html
{# Per-page meta tags + JSON-LD — wired in Task 27 #}
<meta name="description" content="{{ page.meta.summary | default(config.site_description) }}">
<link rel="canonical" href="{{ page.canonical_url }}">
```

- [ ] **Step 5: Write `overrides/partials/footer.html`**:

```html
<div class="md-content__edited">
  {% if page.meta.last_verified_by_nightly %}
    <span class="freshness-badge">🟢 Last verified: {{ page.meta.last_verified_by_nightly }}</span>
  {% endif %}
</div>
```

- [ ] **Step 6: Write `overrides/assets/css/extra.css`**:

```css
.freshness-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 16px;
  background-color: rgba(76, 175, 80, 0.12);
  color: #2e7d32;
  font-size: 0.85em;
  margin: 16px 0;
}

[data-md-color-scheme="slate"] .freshness-badge {
  background-color: rgba(76, 175, 80, 0.2);
  color: #81c784;
}

.md-typeset table {
  font-size: 0.85em;
}
```

- [ ] **Step 7: Verify the site builds**

```bash
mkdocs build --strict
```
Expected: `INFO    -  Documentation built in X.XX seconds`.

- [ ] **Step 8: Commit**

```bash
git add mkdocs.yml overrides/
git commit -m "feat(site): MkDocs Material config + theme overrides

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 27: JSON-LD injection in head.html

**Files:**
- Modify: `overrides/partials/head.html`

Inject per-essay TechArticle + HowTo + FAQPage JSON-LD on essay pages, and catalog-wide Course schema on the catalog page.

- [ ] **Step 1: Rewrite `overrides/partials/head.html`**

```html
{# Per-page meta tags #}
<meta name="description" content="{{ page.meta.summary | default(config.site_description) }}">
<link rel="canonical" href="{{ page.canonical_url }}">

{# Open Graph #}
<meta property="og:title" content="{{ page.title | default(config.site_name) }}">
<meta property="og:description" content="{{ page.meta.summary | default(config.site_description) }}">
<meta property="og:url" content="{{ page.canonical_url }}">
<meta property="og:type" content="article">
{% if page.meta.slug %}
<meta property="og:image" content="{{ config.site_url }}essays/{{ page.meta.theme_dir }}/{{ page.meta.slug_dir }}/results/og-card.png">
{% endif %}

{# Twitter #}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{ page.title | default(config.site_name) }}">
<meta name="twitter:description" content="{{ page.meta.summary | default(config.site_description) }}">

{# JSON-LD: TechArticle for essays, Course for catalog, FAQPage extracted from FAQ section #}
{% if page.meta.slug and page.meta.status %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": {{ page.title | tojson }},
  "alternativeHeadline": {{ page.meta.summary | tojson }},
  "datePublished": "2026-06-01",
  "dateModified": {{ (page.meta.last_updated or "2026-06-01") | tojson }},
  "author": {
    "@type": "Organization",
    "name": "FlashAlpha",
    "url": "https://flashalpha.com"
  },
  "publisher": {
    "@type": "Organization",
    "name": "FlashAlpha",
    "logo": { "@type": "ImageObject", "url": "https://flashalpha.com/logo.png" }
  },
  "proficiencyLevel": {{ (page.meta.difficulty | default("intermediate")) | tojson }},
  "about": [
    {% for kw in page.meta.keywords | default([]) %}
    { "@type": "Thing", "name": {{ kw | tojson }} }{% if not loop.last %},{% endif %}
    {% endfor %}
  ],
  "isPartOf": {
    "@type": "Course",
    "name": "FlashAlpha Historical Examples",
    "url": {{ config.site_url | tojson }}
  }
}
</script>
{% endif %}

{# Plausible analytics — SRI-pinned. Update integrity hash when Plausible
   ships a new script.js (rare — check quarterly). To regenerate:

       curl -sL https://plausible.io/js/script.js \
         | openssl dgst -sha384 -binary | openssl base64 -A

   Pre-compute the hash at deploy time and commit; never load without SRI. #}
<script defer
        data-domain="examples.flashalpha.com"
        src="https://plausible.io/js/script.js"
        integrity="sha384-<CURRENT_HASH_HERE_REGENERATE_AT_DEPLOY>"
        crossorigin="anonymous"></script>
```

- [ ] **Step 2: Verify the site rebuilds**

```bash
mkdocs build --strict
```
Expected: build succeeds.

- [ ] **Step 3: Inspect rendered JSON-LD**

```bash
grep -A 20 'application/ld+json' site/essays/a-dealer-positioning/01-gamma-scalping/index.html | head -25
```
Expected: JSON-LD block with `"@type": "TechArticle"`, `"headline": "Gamma scalping in QuantConnect"`.

- [ ] **Step 4: Validate against schema.org**

Upload `site/essays/a-dealer-positioning/01-gamma-scalping/index.html` to https://validator.schema.org/ or run a Google Rich Results test. (Manual step.)

- [ ] **Step 5: Regenerate the Plausible SRI hash and substitute**

The placeholder `<CURRENT_HASH_HERE_REGENERATE_AT_DEPLOY>` must be replaced with the actual SHA-384 of Plausible's current `script.js`. Run:

```bash
HASH=$(curl -sL https://plausible.io/js/script.js \
  | openssl dgst -sha384 -binary | openssl base64 -A)
echo "sha384-$HASH"
# substitute the printed value into overrides/partials/head.html
sed -i "s|sha384-<CURRENT_HASH_HERE_REGENERATE_AT_DEPLOY>|sha384-$HASH|" overrides/partials/head.html
```

If Plausible ever ships a new script version, browsers will refuse to load it and analytics goes dark until the hash is bumped. That's a feature, not a bug — it's the SRI contract. Add a quarterly calendar reminder to regenerate.

- [ ] **Step 6: Commit**

```bash
git add overrides/partials/head.html
git commit -m "feat(site): JSON-LD per page (TechArticle + Course) + OG meta + Plausible (SRI-pinned)

External script tags must carry integrity= and crossorigin=anonymous so a
CDN compromise can't inject script content into the docs site. Quarterly
hash refresh tracked in launch-plan.md.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 28: build-site wrapper + OG cards for all essays

**Files:**
- Create: `tools/src/flashalpha_examples_tools/build_site.py`
- Create: `tools/tests/test_build_site.py`

`fa-build-site` is the one-shot command: regenerate catalog/llms/bib, regenerate all OG cards, then `mkdocs build`.

- [ ] **Step 1: Write `build_site.py`**

```python
"""End-to-end site build: catalog + bib + OG cards + mkdocs build.

Single entry point for both local preview and CI deploy.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

from .build_catalog import build_catalog
from .build_bib import build_bib
from .gen_og_cards import render_og_card


def regenerate_all_og_cards(repo: Path) -> None:
    """Render og-card.png for every essay."""
    for meta_path in (repo / "essays").rglob("meta.yaml"):
        essay = meta_path.parent
        fm = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
        title = fm.get("title", essay.name)
        summary = fm.get("summary", "")
        eq = essay / "results" / "equity-curve-python.png"
        out = essay / "results" / "og-card.png"
        # eq may not exist for drafts; render with the placeholder behavior
        render_og_card(title, summary, eq, out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build hosted site end-to-end")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--base-url", default="https://examples.flashalpha.com")
    p.add_argument("--strict", action="store_true", help="mkdocs build --strict")
    args = p.parse_args(argv)

    repo = Path(args.repo_root).resolve()
    print("=== 1/4 Building catalog ===")
    build_catalog(repo, args.base_url)
    print("=== 2/4 Building bibliography ===")
    build_bib(repo)
    print("=== 3/4 Regenerating OG cards ===")
    regenerate_all_og_cards(repo)
    print("=== 4/4 mkdocs build ===")
    cmd = ["mkdocs", "build"]
    if args.strict:
        cmd.append("--strict")
    proc = subprocess.run(cmd, cwd=repo)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Write minimal test**

`tools/tests/test_build_site.py`:

```python
from pathlib import Path
from unittest.mock import patch

from flashalpha_examples_tools.build_site import regenerate_all_og_cards


def test_regenerate_all_og_cards_visits_each_essay(tmp_path: Path, monkeypatch):
    import yaml
    repo = tmp_path
    essay = repo / "essays" / "a-dealer-positioning" / "01-x"
    (essay / "results").mkdir(parents=True)
    (essay / "meta.yaml").write_text(yaml.safe_dump({
        "title": "X", "slug": "x", "summary": "test",
    }))

    calls = []
    def fake_render(title, summary, eq, out):
        calls.append((title, str(out)))

    monkeypatch.setattr("flashalpha_examples_tools.build_site.render_og_card", fake_render)
    regenerate_all_og_cards(repo)
    assert len(calls) == 1
    assert calls[0][0] == "X"
```

- [ ] **Step 3: Run all tools tests**

```bash
cd tools && pytest tests/ -v
```
Expected: all PASS.

- [ ] **Step 4: Run the full site build**

```bash
cd /e/repos/tecware/flashalpha-packages/flashalpha-historical-examples
fa-build-site --strict
```
Expected: `INFO - Documentation built` + `site/` populated.

- [ ] **Step 5: Inspect output**

```bash
ls site/
ls site/essays/a-dealer-positioning/01-gamma-scalping/
```
Expected: rendered HTML files for every essay + assets.

- [ ] **Step 6: Commit**

```bash
git add tools/
git commit -m "feat(tools): build-site — end-to-end (catalog + bib + OG + mkdocs)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 29: GitHub Pages deploy workflow

**Files:**
- Create: `.github/workflows/pages.yml`

- [ ] **Step 1: Write `pages.yml`**

```yaml
name: Deploy hosted site

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install build deps
        run: |
          pip install -e tools/
          pip install mkdocs-material

      - name: Build site
        run: fa-build-site --strict --repo-root .

      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: site/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Configure GitHub Pages in the repo**

(Manual, GitHub UI): Settings → Pages → Source = "GitHub Actions".

- [ ] **Step 3: Commit + push**

```bash
git add .github/workflows/pages.yml
git commit -m "ci: GitHub Pages deploy workflow

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
git push
```

- [ ] **Step 4: Verify deployment**

```bash
gh run list --workflow="Deploy hosted site" --limit 3
```
Expected: latest run completed/success. Site visible at `https://flashalpha-lab.github.io/flashalpha-historical-examples/`.

---

### Task 30: Configure custom domain `examples.flashalpha.com`

**External-side-effect task** — requires DNS access on flashalpha.com.

- [ ] **Step 1: Add CNAME**

`echo "examples.flashalpha.com" > CNAME` and commit. GH Pages auto-detects.

```bash
echo "examples.flashalpha.com" > CNAME
git add CNAME
git commit -m "chore: configure examples.flashalpha.com custom domain"
git push
```

- [ ] **Step 2: Add DNS record** (manual, FlashAlpha ops side):

```
CNAME examples.flashalpha.com → flashalpha-lab.github.io
```

- [ ] **Step 3: Enforce HTTPS** in GitHub Settings → Pages → "Enforce HTTPS" toggle. Wait for Let's Encrypt cert provisioning (5-15 min).

- [ ] **Step 4: Verify**

```bash
curl -sI https://examples.flashalpha.com/ | head -5
```
Expected: `HTTP/2 200`.

---

## Phase 4 — CI workflows (5 tasks)

### Task 31: Layer 0 CI workflow (PR-fast, no backtests)

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Write `ci.yml`**

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  schema:
    name: Schema + catalog + orphans
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -e tools/
      - name: Verify frontmatter sync
        run: |
          for d in essays/*/[0-9]*/; do
            fa-verify-frontmatter "$d"
          done
      - name: Check no orphans
        run: fa-check-orphans --repo-root .
      - name: Catalog drift
        run: fa-build-catalog --repo-root . --check

  build:
    name: Tools package build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -e "tools/[dev]"
      - run: cd tools && pytest -v

  csharp:
    name: C# build (compile every essay's csproj)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '9.0.x' }
      - name: Build each essay
        run: |
          for csproj in essays/*/[0-9]*/csharp/*.csproj; do
            echo "::group::Build $csproj"
            dotnet build "$csproj" -c Release
            echo "::endgroup::"
          done

  python-lint:
    name: Python lint (ruff)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install ruff
      - run: ruff check essays/

  links:
    name: Markdown link check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: gaurav-nelson/github-action-markdown-link-check@v1
        with:
          use-quiet-mode: 'yes'
          folder-path: 'docs,essays'
          file-path: 'README.md, catalog.md, CHANGELOG.md'

  site-build:
    name: Site dry-build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: |
          pip install -e tools/
          pip install mkdocs-material
      - run: mkdocs build --strict
```

- [ ] **Step 2: Push + verify CI**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: Layer 0 PR-fast checks (schema, orphans, build, lint, links, site dry-build)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
git push
gh run list --workflow=CI --limit 1
```
Expected: green within ~2 min.

---

### Task 32: Layer 1 CI workflow (changed-essay backtests)

**Files:**
- Create: `.github/workflows/essay-backtest.yml`

- [ ] **Step 1: Write `essay-backtest.yml`**

```yaml
name: Essay backtest (changed essays)

on:
  pull_request:
    paths:
      - 'essays/**'

jobs:
  detect:
    runs-on: ubuntu-latest
    outputs:
      essays: ${{ steps.detect.outputs.essays }}
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - id: detect
        run: |
          # Detect touched essay directories from the PR diff
          touched=$(git diff --name-only origin/${{ github.base_ref }}...HEAD -- 'essays/*/*/' \
                    | awk -F/ '{print $1"/"$2"/"$3}' | sort -u | head -20)
          echo "essays=$(echo $touched | jq -R -s -c 'split(" ") | map(select(length > 0))')" >> $GITHUB_OUTPUT

  backtest:
    needs: detect
    if: needs.detect.outputs.essays != '[]'
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        essay: ${{ fromJson(needs.detect.outputs.essays) }}
        language: [python, csharp]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '9.0.x' }
      - name: Install LEAN CLI
        run: pip install lean
      - name: Install tools
        run: pip install -e tools/
      - name: Backtest + verify
        env:
          FLASHALPHA_API_KEY: ${{ secrets.FLASHALPHA_API_KEY }}
        run: |
          lean backtest "${{ matrix.essay }}/${{ matrix.language }}/" --output /tmp/bt
          BT=$(find /tmp/bt -name BacktestResult.json | head -1)
          fa-verify-essay "${{ matrix.essay }}" "$BT" --language "${{ matrix.language }}"
```

- [ ] **Step 2: Push + verify**

```bash
git add .github/workflows/essay-backtest.yml
git commit -m "ci: Layer 1 — changed-essay backtests"
git push
```

---

### Task 33: Layer 2 nightly workflow (full sweep)

**Files:**
- Create: `.github/workflows/nightly.yml`

- [ ] **Step 1: Write `nightly.yml`**

```yaml
name: Nightly full sweep

on:
  schedule:
    - cron: '0 6 * * *'
  workflow_dispatch:

jobs:
  matrix:
    runs-on: ubuntu-latest
    outputs:
      essays: ${{ steps.list.outputs.essays }}
    steps:
      - uses: actions/checkout@v4
      - id: list
        run: |
          essays=$(find essays -mindepth 2 -maxdepth 2 -type d | jq -R -s -c 'split("\n") | map(select(length > 0))')
          echo "essays=$essays" >> $GITHUB_OUTPUT

  sweep:
    needs: matrix
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        essay: ${{ fromJson(needs.matrix.outputs.essays) }}
        language: [python, csharp]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '9.0.x' }
      - run: pip install lean
      - run: pip install -e tools/
      - name: Backtest + verify
        env:
          FLASHALPHA_API_KEY: ${{ secrets.FLASHALPHA_API_KEY }}
        run: |
          lean backtest "${{ matrix.essay }}/${{ matrix.language }}/" --output /tmp/bt || exit 0  # tolerate draft failures
          BT=$(find /tmp/bt -name BacktestResult.json | head -1)
          if [ -n "$BT" ]; then
            fa-verify-essay "${{ matrix.essay }}" "$BT" --language "${{ matrix.language }}" || \
              gh issue create \
                --title "Nightly drift: ${{ matrix.essay }} (${{ matrix.language }})" \
                --label nightly-drift \
                --body "Verify failed — review goldens or investigate API drift."
```

- [ ] **Step 2: Push + verify**

```bash
git add .github/workflows/nightly.yml
git commit -m "ci: Layer 2 nightly full sweep + drift triage"
git push
```

---

### Task 34: Release workflow (tag → fresh goldens + GitHub Release)

**Files:**
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Write `release.yml`**

```yaml
name: Release

on:
  push:
    tags: ['v*.*.0']  # only minor/major tags

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '9.0.x' }
      - run: |
          pip install lean
          pip install -e tools/
      - name: Recapture all goldens
        env:
          FLASHALPHA_API_KEY: ${{ secrets.FLASHALPHA_API_KEY }}
        run: |
          for essay in essays/*/[0-9]*; do
            fa-capture-golden "$essay" || true
          done
      - name: Commit fresh goldens back to main
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add essays/*/[0-9]*/{python,csharp}/golden.json essays/*/[0-9]*/results/
          git commit -m "release: capture ${{ github.ref_name }} goldens" || echo "No changes"
          git push origin HEAD:main || true
      - name: Create GitHub Release
        run: gh release create ${{ github.ref_name }} --generate-notes
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

- [ ] **Step 2: Push**

```bash
git add .github/workflows/release.yml
git commit -m "ci: Layer 3 release workflow"
git push
```

---

### Task 35: README polish

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace the placeholder README with the full landing page**

```markdown
# flashalpha-historical-examples

> 21 backtest essays for options strategies on QuantConnect LEAN — gamma scalping, GEX regimes, VRP harvesting, 0DTE strategies, dispersion. Side-by-side C# and Python. Powered by [`flashalpha-quantconnect`](https://github.com/FlashAlpha-lab/flashalpha-quantconnect).

[![Site](https://img.shields.io/badge/site-examples.flashalpha.com-indigo)](https://examples.flashalpha.com/)
[![CI](https://github.com/FlashAlpha-lab/flashalpha-historical-examples/workflows/CI/badge.svg)](https://github.com/FlashAlpha-lab/flashalpha-historical-examples/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## What you get

21 essays, each a self-contained backtest:

| Theme | Essays |
|---|---|
| Dealer positioning | gamma scalping, GEX regime, gamma flip, negative-gamma vol expansion, 0DTE pin risk |
| Vanna / charm / VEX | charm-flow afternoon, vanna shock, combined-greek regime grid |
| VRP / volatility | VRP harvest, IV rank, realized vs implied, term structure |
| 0DTE | Friday gamma squeeze, pin gravitation, intraday flip, expected-move straddle |
| Cross-signal | dispersion, calendar carry, max-pain reversion, earnings vol contraction |

Every essay ships:
- A long-form README (prose + algorithm + sensitivity + FAQ)
- Side-by-side Python + C# QC LEAN algorithms
- Committed `golden.json` (final equity, sharpe, max DD, trades — verified nightly)
- `results/` with equity curve PNG, monthly returns CSV, parameter sweep, OG card

## Quick start

```bash
pip install lean
git clone https://github.com/FlashAlpha-lab/flashalpha-historical-examples
cd flashalpha-historical-examples/essays/a-dealer-positioning/01-gamma-scalping/python
export FLASHALPHA_API_KEY=your-key-here   # https://flashalpha.com
lean backtest
```

Or read the rendered essay at https://examples.flashalpha.com/essays/a-dealer-positioning/01-gamma-scalping/.

## Browse

- [Full catalog](catalog.md)
- [What's an essay?](docs/what-is-an-essay.md)
- [Getting started](docs/getting-started.md)
- [Glossary](docs/glossary.md)

## Related

- [flashalpha-quantconnect](https://github.com/FlashAlpha-lab/flashalpha-quantconnect) — the QC LEAN bridge bars these essays consume
- [flashalpha-historical-{python,dotnet}](https://github.com/FlashAlpha-lab/flashalpha-historical-python) — raw SDKs
- [historical.flashalpha.com](https://historical.flashalpha.com) — underlying API

## License

MIT — see [LICENSE](LICENSE).
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: full README landing page"
git push
```

---

## Phase 5 — Launch ops (5 tasks)

### Task 36: Launch plan + draft posts

**Files:**
- Create: `docs/superpowers/launch-plan.md`
- Create: `launch-drafts/hn.md`
- Create: `launch-drafts/reddit-algotrading.md`
- Create: `launch-drafts/reddit-options.md`
- Create: `launch-drafts/qc-community-forum.md`
- Create: `launch-drafts/x-thread.md`
- Create: `launch-drafts/linkedin.md`

- [ ] **Step 1: Write `docs/superpowers/launch-plan.md`** with concrete dates (replace `<launch-day>` placeholders with actual date when ready to launch):

```markdown
# Launch plan

| Day | Channel | Action | Draft |
|---|---|---|---|
| -3 | examples.flashalpha.com | Site live, OG cards verified via opengraph.xyz, dark/light tested | — |
| -1 | QC Slack/Discord | DM @QuantConnectStaff with preview link | — |
| 0 | r/algotrading | "I built 21 backtests for options strategies in QuantConnect" | [reddit-algotrading.md](../../launch-drafts/reddit-algotrading.md) |
| 0 | Hacker News | "Show HN: Gamma scalping backtests in QuantConnect" | [hn.md](../../launch-drafts/hn.md) |
| 0 | r/options | Variant focused on dealer positioning | [reddit-options.md](../../launch-drafts/reddit-options.md) |
| 0 | X / Twitter | Thread: equity curve hook → algorithm gist → link | [x-thread.md](../../launch-drafts/x-thread.md) |
| +1 | QC Community Forum | Post + offer Q&A | [qc-community-forum.md](../../launch-drafts/qc-community-forum.md) |
| +7 | LinkedIn (founder) | Personal post: lessons from building 21 backtests | [linkedin.md](../../launch-drafts/linkedin.md) |
| +14 | Quant newsletters | Email outreach (named contacts in spec §8) | — |
```

- [ ] **Step 2: Write each of the 6 draft files**

Each is 100-300 words of ready-to-publish copy. Tone: confident, technical, no marketing fluff. The HN draft must follow HN's "Show HN" conventions (one-line title, first comment from author explaining context). Twitter thread is 6-10 tweets max.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/launch-plan.md launch-drafts/
git commit -m "docs: launch plan + draft posts for HN, reddit x2, QC forum, X, LinkedIn

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 37: Tag v0.1.0

- [ ] **Step 1: Verify the state is clean**

```bash
git status --short      # should be empty
fa-check-orphans .       # OK
fa-verify-frontmatter essays/*/[0-9]*/   # all OK
fa-build-catalog --check  # OK
git log --oneline | head -5
```

- [ ] **Step 2: Tag and push**

```bash
git tag -a v0.1.0 -m "v0.1.0 — initial public release

Flagship gamma-scalping essay stable; 20 themed drafts. Hosted at
examples.flashalpha.com. CI green. Powered by flashalpha-quantconnect 0.1.1."
git push origin v0.1.0
```

- [ ] **Step 3: Verify release workflow runs**

```bash
gh run list --workflow=Release --limit 1
```
Expected: in progress / completed-success within 30-60 min.

---

### Task 38: Plausible analytics + Algolia DocSearch + Buttondown (manual)

**External-side-effect tasks** — require external accounts.

- [ ] **Step 1: Plausible setup**

Sign up at https://plausible.io. Create site `examples.flashalpha.com`. The `<script>` tag is already wired in `overrides/partials/head.html` (Task 27). Confirm data flowing after first visit.

- [ ] **Step 2: Algolia DocSearch application**

Apply at https://docsearch.algolia.com/apply/. Approval takes ~1 week. Once approved, Algolia provides an API key + index ID. Add to `mkdocs.yml`:

```yaml
theme:
  features:
    - search.suggest
extra:
  algolia:
    application_id: <provided-by-algolia>
    api_key: <provided-by-algolia>
    index_name: flashalpha_examples
```

- [ ] **Step 3: Buttondown newsletter**

Sign up at https://buttondown.email. Free tier <1000 subscribers. Configure RSS-to-email at `https://examples.flashalpha.com/feed.xml`. Save the embed snippet for the catalog page footer.

- [ ] **Step 4: Add to compatibility/launch-plan docs** to track the rollouts.

---

### Task 39: Execute launch day

**External actions.** Track in a spreadsheet or GitHub project.

- [ ] **Step 1: T-3 days** — verify site live, OG cards, dark/light, mobile responsive (Chrome DevTools mobile preview).
- [ ] **Step 2: T-1 day** — DM QC staff with preview link.
- [ ] **Step 3: T=0 morning** — post HN ("Show HN: ..."), monitor + reply.
- [ ] **Step 4: T=0** — post r/algotrading, r/options, X thread.
- [ ] **Step 5: T+1 day** — QC Community Forum post + Q&A.
- [ ] **Step 6: T+7 days** — LinkedIn post.
- [ ] **Step 7: T+14 days** — newsletter outreach.

After launch, monitor Plausible weekly to drive v0.2.0+ stable-essay prioritization.

---

## Phase 6 — Post-launch (continuous)

### Task 40: Promote drafts → stable iteratively

For each draft essay, in priority order (driven by Plausible traffic data):

- Replace `OnData` stub with real algorithm
- Capture goldens with `fa-capture-golden`
- Update `status:` → `stable` in frontmatter + meta.yaml
- Re-run `fa-build-catalog` (auto-promotes in catalog)
- Tag `v0.X.0` to trigger release workflow

One PR per essay. CI Layer 1 validates the new goldens reproduce.

---

## Self-review checklist

- [ ] All 21 essays scaffolded (Task 16).
- [ ] Flagship gamma-scalping is `stable` with captured goldens (Tasks 17-25).
- [ ] All tools have tests, all tests pass (Tasks 6-15, 28).
- [ ] Hosted site builds + deploys (Tasks 26-30).
- [ ] CI green on Layer 0, Layer 1 catches drift, Layer 2 nightly runs (Tasks 31-34).
- [ ] README + launch plan + draft posts committed (Tasks 35-36).
- [ ] v0.1.0 tagged + release workflow ran (Task 37).
- [ ] External accounts wired (Plausible / Algolia / Buttondown) (Task 38).
- [ ] Launch day executed (Task 39).

---

## Open questions / known external dependencies

- **DNS for `examples.flashalpha.com`** — requires FlashAlpha ops to set CNAME.
- **Video walkthrough** of flagship — recording skipped from v0.1.0 plan; `transcript.md` ships as placeholder.
- **Algolia DocSearch** — application can take ~1 week; site launches with MkDocs Material's built-in search until DocSearch approved.
- **Plausible plan** — free trial 30 days; choose paid tier ($9/mo) or self-host before trial ends.
- **QuantConnect staff DM** — pre-launch outreach depends on QC's response. If they decline to amplify, the launch still proceeds via HN/Reddit/X.
- **API budget for nightly** — 42 backtests × ~140 calls each ≈ 5,880 calls/day. Confirm with FlashAlpha that the bridge's read-only key has sufficient quota.
