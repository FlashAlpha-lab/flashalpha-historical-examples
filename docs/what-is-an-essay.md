# What is an essay?

An **essay** in this repo is a self-contained mental unit: prose explaining a
trading idea, machine-readable metadata, two runnable LEAN projects (Python
and C#) that implement it, and the canonical results those projects produce.
One folder, one idea, fully reproducible.

This page covers the folder anatomy, the frontmatter schema, the lifecycle
states an essay moves through, what CI enforces, and how to add a new one.

---

## Anatomy of an essay folder

Every essay lives at `essays/<theme>/<NN>-<slug>/`. Inside:

```
01-gamma-scalping/
├── README.md              # The essay itself — prose + frontmatter
├── meta.yaml              # Machine-readable mirror of the frontmatter
├── references.md          # Citations as markdown
├── python/                # Runnable LEAN Python project
│   ├── main.py
│   ├── config.json
│   └── requirements.txt
├── csharp/                # Runnable LEAN C# project
│   ├── Main.cs
│   ├── config.json
│   └── *.csproj
├── results/               # Committed artifacts produced by the goldens
│   ├── equity-curve-python.png
│   ├── equity-curve-csharp.png
│   ├── monthly-returns.csv
│   ├── trade-stats.json
│   ├── parameter-sweep.csv
│   └── og-card.png
└── golden.json            # Reproducibility fingerprint (committed)
```

### `README.md`

The human-facing prose with strict YAML frontmatter on top. GitHub renders it
on the file page; the hosted site at `examples.flashalpha.com` builds it into
the public-facing essay. Section structure is fixed: `## The intuition` →
`## The setup` → `## The algorithm` → `## Running it` → `## Results` →
`## Sensitivity` → `## Variations` → `## When it fails` → `## FAQ` →
`## Related essays` → `## References`.

### `meta.yaml`

The same fields as the README frontmatter, but in standalone YAML. Catalog
builds, llms.txt, the bibliography aggregator, and the Schema.org Course
emitter all read `meta.yaml` rather than parsing markdown — keeps the build
fast and prevents accidental parser brittleness. Authors edit `README.md`;
`tools/verify-frontmatter.py` asserts `meta.yaml` is in lockstep.

### `references.md`

Citations as a plain markdown bullet list. `tools/build-bib.py` walks every
essay's `references.md` and emits:

- `bibliography.md` — repo-root aggregate, deduplicated, alphabetical.
- `bibliography.bib` — BibTeX form, indexed by Google Scholar.
- Per-essay `references.bib` — academic-style citations for the essay.

### `python/` and `csharp/`

Each language directory is a real `lean` CLI project. The C# and Python
algorithms are hand-written twins (NOT auto-translated). `tools/verify-essay.py`
asserts both projects subscribe to the same bridge bars with the same
`config.json` (dates, cash, ticker, parameters) so the resulting goldens are
directly comparable across languages.

### `results/`

Six committed artifacts so visitors see the equity curve without running the
backtest:

1. `equity-curve-python.png` — strategy vs buy-and-hold.
2. `equity-curve-csharp.png` — same, for the C# twin.
3. `monthly-returns.csv` — month-by-month returns; rendered into the README
   as a markdown table at build time.
4. `trade-stats.json` — sharpe, sortino, max drawdown, hit rate, average
   win/loss.
5. `parameter-sweep.csv` — one canonical parameter swept across a range, to
   support the `## Sensitivity` section.
6. `og-card.png` — Open Graph card, auto-generated from the equity curve +
   title by `tools/gen-og-cards.py`.

### `golden.json`

The reproducibility fingerprint. Captured by `fa-capture-golden` from a
known-good local backtest run. Contains the same five numbers per language
that the frontmatter `golden:` block exposes (final equity, total trades,
sharpe, max drawdown, sortino). CI Layer 1 re-runs the backtest on every PR
that touches the essay and asserts the new output matches `golden.json`
within tolerance.

---

## The frontmatter schema

Annotated example. Required fields marked with `[required]`; optional with
`[optional]`.

```yaml
---
# [required] Display title. Used as <h1>, <title>, og:title.
title: "Gamma scalping in QuantConnect"

# [required] URL-safe slug. Cross-essay links use this, NOT the folder path.
# Must be unique across the entire repo.
slug: gamma-scalping

# [required] One of the five themes defined in essays/<theme>/README.md.
# dealer-positioning | vanna-charm-vex | vrp-volatility | zero-dte | cross-signal
theme: dealer-positioning

# [required] beginner | intermediate | advanced
# Drives the difficulty filter on the hosted catalog.
difficulty: intermediate

# [required] draft | stable | deprecated
# Determines whether the essay is included in catalog.md, llms.txt, and the
# hosted site. See "lifecycle" below.
status: stable

# [required] Single-sentence pitch. <= 240 chars. Used as og:description
# and as the catalog row text.
summary: "Delta-neutral options portfolio gated by FlashAlpha's dealer-GEX regime signal."

# [required] Bridge bar types the algorithm subscribes to. Must match exactly
# the symbols imported in python/ and csharp/. Used by build-catalog.py to
# build the "essays that use FlashAlphaGexBar" reverse index.
bridge_bars:
  - FlashAlphaGexBar
  - FlashAlphaSurfaceBar

# [required] FlashAlpha API endpoint slugs the bridge bars resolve to.
# Cross-referenced against the bridge's data-types.md.
data_endpoints:
  - exposure/gex
  - surface

# [required] Tickers traded. Cross-referenced against the LEAN universe.
tickers: [SPY]

# [required] Backtest window. ISO-8601 dates. Must match config.json in BOTH
# language subdirs (verify-essay.py asserts this).
backtest_window:
  start: "2024-03-01"
  end: "2024-09-30"

# [required] Expected wall-clock on a reference machine. Used by CI Layer 2
# (nightly) to flag essays drifting toward timeout.
expected_runtime:
  python: "8m"
  csharp: "3m"

# [required] Reproducibility fingerprint. Mirrored in golden.json. CI Layer 1
# re-runs the backtest on touched essays and diffs against these values.
golden:
  python:
    final_equity: 102_417.50
    total_trades: 84
    sharpe: 0.72
    max_drawdown: -0.045
  csharp:
    final_equity: 102_390.13
    total_trades: 84
    sharpe: 0.72
    max_drawdown: -0.045

# [optional] Slugs of related essays. Rendered as cross-links at the bottom
# of the README. check-orphans.py asserts every referenced slug exists.
related:
  - gex-regime-following
  - gamma-flip-strike-trading

# [optional] SEO keywords. Used as <meta name="keywords"> and as a fuzzy
# match input for the catalog search.
keywords:
  - gamma scalping
  - QuantConnect
  - GEX
  - delta hedging
  - dealer positioning

# [required] ISO-8601 date this essay was last edited by a human.
last_updated: "2026-05-30"

# [optional, machine-managed] Auto-bumped by the nightly workflow when the
# essay's golden re-runs cleanly. Don't hand-edit.
last_verified_by_nightly: "2026-05-30"

# [optional] Free-form citation strings. Mirrored from references.md.
references:
  - "Dynamic Hedging — Taleb (1997)"
  - "Volatility Trading — Sinclair (2013)"
---
```

`tools/_schema.py` is the canonical source of the field definitions and
their JSON-schema constraints; `verify-frontmatter.py` validates every PR
against it.

---

## The draft → stable → deprecated lifecycle

Every essay carries a `status` field. The status drives three behaviours:

- Inclusion in `catalog.md` and `llms.txt`.
- Inclusion in the hosted site at `examples.flashalpha.com`.
- Severity of CI failures (drafts are allowed to be flaky; stable essays
  are not).

### `draft`

A work in progress. README may be incomplete; the algorithm may not yet
produce a golden. Drafts are still required to pass schema validation
(Layer 0) but are excluded from the nightly sweep (Layer 2) and from the
public catalog. Useful for in-flight PRs where you want CI to validate the
shape before you've nailed down numbers.

### `stable`

The essay is feature-complete and reproducible. CI gates apply at full
strength: schema, backtest, drift, link check. The essay appears in the
catalog, in llms.txt, and on the hosted site. Updating a stable essay's
algorithm requires deliberately re-capturing `golden.json` in the same PR;
a drift > tolerance triggers a Layer 1 failure that blocks merge.

An essay flips draft → stable when:

1. README has every required section.
2. Both language algorithms produce committed `results/`.
3. `golden.json` is captured and re-runs cleanly three times locally.
4. The PR explicitly bumps `status: stable`.

### `deprecated`

The essay is preserved for historical context but no longer supported.
Common triggers: the underlying FlashAlpha bar was retired, the LEAN data
universe changed, or the technique was superseded by a better one in
another essay. Deprecated essays remain in the repo for git-archaeology
but are removed from the catalog and excluded from the nightly sweep. The
README must carry a top-of-page banner pointing to the replacement.

---

## What CI checks

Validation is layered. The earlier the layer fails, the cheaper the
feedback. Detailed gate definitions live in the design spec; the high-
level shape:

### Layer 0 — every PR (~45 s)

Runs on every commit. Fail-fast structural checks:

- **Frontmatter schema** — `verify-frontmatter.py` against `_schema.py`.
- **Frontmatter ↔ meta.yaml sync** — fields must match byte-for-byte
  modulo whitespace.
- **Internal link check** — `check-orphans.py` walks every markdown link
  and asserts target slugs and files exist.
- **Algorithm build** — `lean cloud build` (or local equivalent) compiles
  both language projects without running them.
- **Lint** — `ruff` (Python), `dotnet format --verify-no-changes` (C#),
  `markdownlint` (markdown).
- **Naming** — `test_essay_naming.py` enforces the `NN-slug` folder
  pattern and slug uniqueness.

If Layer 0 fails, no backtest runs. Cheap signal, fast.

### Layer 1 — changed essays only (~3 min per touched essay × language)

If Layer 0 passes and a PR touches `essays/<theme>/<NN>-<slug>/**`, the
backtest matrix runs the touched essays in both languages. Each cell
asserts the output matches `golden.json` within tolerance (default 0.1%
on equity, exact match on trade count). Mismatch blocks merge unless the
PR explicitly re-captures the golden.

### Layer 2 — nightly full sweep (~30 min parallelized)

Cron-triggered. Re-runs every `stable` essay in both languages against
fresh FlashAlpha data. Outputs:

- A drift report (essays whose goldens shifted within the historical
  window — usually means a FlashAlpha endpoint changed semantics).
- An updated `last_verified_by_nightly` field per essay.
- A triage issue auto-filed for any essay that drifted beyond tolerance.

Nightly drift is investigative, not blocking — it surfaces real-world
data drift for human review.

---

## Adding a new essay

The repo ships an `fa-new-essay` CLI that scaffolds the full folder shape:

```bash
pip install -e tools/
fa-new-essay \
  --theme dealer-positioning \
  --slug my-new-technique \
  --title "My new technique in QuantConnect" \
  --difficulty intermediate
```

This creates `essays/a-dealer-positioning/NN-my-new-technique/` (NN
auto-assigned as the next number in the theme), populates a skeleton
`README.md` + `meta.yaml` with required frontmatter fields, drops empty
`python/` and `csharp/` project templates, and creates an empty
`results/` directory.

From there:

1. Fill in the prose sections of `README.md`.
2. Implement `python/main.py` and `csharp/Main.cs`. Keep them in lockstep
   on bars, parameters, and `config.json`.
3. Run both backtests locally until you're happy with the numbers.
4. Capture the golden: `fa-capture-golden essays/a-dealer-positioning/NN-my-new-technique/`.
5. Render the results artifacts: `fa-render-results essays/a-dealer-positioning/NN-my-new-technique/`.
6. Open a PR with `status: draft`.
7. Once the PR is review-clean, flip to `status: stable` in a follow-up
   commit and re-run CI.

CI Layer 0 will give you immediate structural feedback; Layer 1 will
re-run your backtest and confirm reproducibility on the CI runner.

See [getting-started.md](getting-started.md) for prerequisites and
[lean-cli-cheatsheet.md](lean-cli-cheatsheet.md) for the LEAN commands
you'll lean on while iterating.
