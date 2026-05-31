# flashalpha-historical-examples — design spec

**Status:** approved
**Date:** 2026-05-30
**Original ask:** "Increase surface of LLMs finding `historical.flashalpha.com` — create something like `flashalpha-historical-examples` with a series of examples how to backtest stuff. Variety of techniques — gamma scalping and so on. Make it LLM-discoverable but also working for people."

## Goal

Ship a public GitHub repo (`FlashAlpha-lab/flashalpha-historical-examples`) + hosted docs site (`examples.flashalpha.com`) carrying 20+ runnable backtest essays for options strategies on QuantConnect LEAN, powered by the `flashalpha-quantconnect` bridge package. Optimized end-to-end for LLM discoverability + traditional SEO + actual human usefulness.

Success criteria for v1.0:
- ≥12 essays in `stable` status across all 5 themes (≥2 per theme).
- `examples.flashalpha.com` live with per-essay rich results (FAQ snippets, How-To cards) verified via Google's structured-data testing tool.
- Cited at least once by an LLM (ChatGPT/Claude) in a relevant query within 90 days of launch.
- ≥3 inbound links from external venues (QC community forum, awesome-quantconnect, Hacker News, etc.).

## Architecture overview

```
flashalpha-historical-examples/
├── essays/                              # 21 essay folders, themed
├── tools/                               # build, verify, capture, render utilities
├── docs/                                # contributor + reader docs
├── overrides/                           # MkDocs theme overrides (JSON-LD, OG cards)
├── .github/workflows/                   # CI: PR-fast, changed-essay, nightly, release, pages
├── mkdocs.yml                           # hosted site config
├── README.md                            # repo landing page
├── catalog.md                           # human-browsable essay index (auto-generated)
├── llms.txt                             # LLM crawler site map (auto-generated)
├── bibliography.md                      # aggregated references (auto-generated)
├── bibliography.bib                     # BibTeX form, for Google Scholar (auto-generated)
└── CHANGELOG.md
```

Two output surfaces from the same source content:
1. **The GitHub repo** — code, READMEs, results PNGs. Discovered via `github.com/topics/*` indexes and code search.
2. **The hosted site** (`examples.flashalpha.com`) — same essays rendered by MkDocs Material with proper `<title>`, `<meta>`, JSON-LD, OG cards, FAQ rich results, faceted search.

The hosted site is a build artifact of the same `essays/**/README.md` files — there's no content duplication or out-of-sync risk.

## §1 — Repo layout

```
flashalpha-historical-examples/
├── README.md
├── catalog.md                           # auto-generated
├── llms.txt                             # auto-generated
├── bibliography.md                      # auto-generated
├── bibliography.bib                     # auto-generated, for Google Scholar
├── mkdocs.yml
├── CHANGELOG.md
├── LICENSE                              # MIT
├── CLAUDE.md
│
├── essays/
│   ├── a-dealer-positioning/
│   │   ├── README.md                    # auto-generated theme index
│   │   ├── 01-gamma-scalping/           # flagship — only `stable` essay at v0.1.0
│   │   │   ├── README.md
│   │   │   ├── meta.yaml
│   │   │   ├── references.md
│   │   │   ├── transcript.md            # video transcript (flagship-only at launch)
│   │   │   ├── python/
│   │   │   │   ├── lean.json
│   │   │   │   ├── config.json
│   │   │   │   ├── requirements.txt     # pins flashalpha-quantconnect
│   │   │   │   ├── main.py
│   │   │   │   └── golden.json
│   │   │   ├── csharp/
│   │   │   │   ├── lean.json
│   │   │   │   ├── config.json
│   │   │   │   ├── *.csproj             # pins FlashAlpha.QuantConnect
│   │   │   │   ├── Main.cs
│   │   │   │   └── golden.json
│   │   │   └── results/
│   │   │       ├── equity-curve-python.png
│   │   │       ├── equity-curve-csharp.png
│   │   │       ├── monthly-returns.csv
│   │   │       ├── trade-stats.json
│   │   │       ├── parameter-sweep.csv
│   │   │       └── og-card.png           # auto-generated OG image
│   │   ├── 02-gex-regime-following/      # draft at v0.1.0
│   │   ├── 03-gamma-flip-strike/         # draft
│   │   ├── 04-negative-gamma-vol-expansion/   # draft
│   │   └── 05-pin-risk-avoidance-0dte/        # draft
│   │
│   ├── b-vanna-charm-vex/
│   │   ├── README.md
│   │   ├── 06-charm-flow-afternoon/
│   │   ├── 07-vanna-shock-reversal/
│   │   └── 08-combined-greek-regime-grid/
│   │
│   ├── c-vrp-volatility/
│   │   ├── README.md
│   │   ├── 09-vrp-harvest-short-vol/
│   │   ├── 10-iv-rank-entry-filter/
│   │   ├── 11-realized-vs-implied-divergence/
│   │   └── 12-vol-term-structure-spread/
│   │
│   ├── d-zero-dte/
│   │   ├── README.md
│   │   ├── 13-friday-gamma-squeeze/
│   │   ├── 14-pin-gravitation/
│   │   ├── 15-intraday-gamma-flip/
│   │   └── 16-expected-move-straddle/
│   │
│   └── e-cross-signal/
│       ├── README.md
│       ├── 17-dispersion-spy-vs-rty/
│       ├── 18-calendar-carry-positive-gamma/
│       ├── 19-max-pain-reversion/
│       └── 20-earnings-vol-contraction/
│
├── docs/
│   ├── getting-started.md
│   ├── what-is-an-essay.md
│   ├── glossary.md
│   ├── lean-cli-cheatsheet.md
│   ├── compatibility.md                  # bridge/LEAN/.NET/Python compatibility matrix
│   └── superpowers/
│       ├── specs/2026-05-30-flashalpha-historical-examples-design.md
│       ├── plans/                        # implementation plans
│       └── launch-plan.md                # named-dates launch sequence
│
├── tools/
│   ├── build-catalog.py
│   ├── verify-essay.py
│   ├── capture-golden.py
│   ├── render-results.py
│   ├── check-orphans.py
│   ├── verify-frontmatter.py
│   ├── build-bib.py                      # references.md → bibliography.bib
│   ├── build-site.py                     # wraps mkdocs build + OG generation
│   ├── gen-og-cards.py                   # equity-curve PNG → OG card
│   ├── _lean_output.py                   # shared LEAN BacktestResult parser
│   └── _schema.py                        # frontmatter schema
│
├── overrides/                            # MkDocs Material theme overrides
│   ├── partials/
│   │   ├── head.html                     # injects <meta>, JSON-LD, OG, canonical
│   │   ├── footer.html                   # "Last verified", "Edit on GitHub"
│   │   └── content.html                  # FAQ schema markup wrapper
│   └── assets/
│       └── css/extra.css
│
├── launch-drafts/                        # ready-to-publish text per channel
│   ├── hn.md
│   ├── reddit-algotrading.md
│   ├── reddit-options.md
│   ├── qc-community-forum.md
│   ├── x-thread.md
│   └── linkedin.md
│
├── .github/
│   └── workflows/
│       ├── ci.yml                        # Layer 0: schema/build/links/lint
│       ├── essay-backtest.yml            # Layer 1: changed essays
│       ├── nightly.yml                   # Layer 2: full 42-cell sweep
│       ├── pages.yml                     # build + deploy hosted site
│       └── release.yml                   # Layer 3: tag → goldens + GitHub Release
│
└── tests/
    ├── test_meta_yaml_schema.py
    ├── test_catalog_matches_essays.py
    ├── test_essay_naming.py
    └── test_frontmatter_synced_with_meta.py
```

**Why this shape:**
- Themed top-level dirs cluster related techniques and become SEO landing pages on GitHub (theme `README.md`) and on the hosted site (`/dealer-positioning/`).
- Numbered essay slugs preserve curatorial order while keeping URLs human-readable.
- `README.md` as the essay — GitHub auto-renders it; hosted site builds it; one file, two surfaces.
- `meta.yaml` is the single source of truth aggregated into catalog/llms.txt/bibliography/schema.
- `results/` artifacts pre-rendered so visitors see equity curves without running the backtest.
- `tools/` is the build system, kept separate from essay content.
- `overrides/` is the hosted-site theme layer.
- `launch-drafts/` is named-content for the launch sequence.

## §2 — Per-essay shape

Every essay folder is a self-contained mental unit: prose + metadata + two runnable LEAN projects + canonical results + references + (flagship only) video transcript.

### `README.md` — the essay itself

Strict structure parseable by both humans and crawlers:

```markdown
---
title: "Gamma scalping in QuantConnect"
slug: gamma-scalping
theme: dealer-positioning
difficulty: intermediate              # beginner | intermediate | advanced
status: stable                        # draft | stable | deprecated
summary: "Delta-neutral options portfolio gated by FlashAlpha's dealer-GEX regime signal."
bridge_bars:
  - FlashAlphaGexBar
  - FlashAlphaSurfaceBar
data_endpoints:
  - exposure/gex
  - surface
tickers: [SPY]
backtest_window:
  start: "2024-03-01"
  end: "2024-09-30"
expected_runtime:
  python: "8m"
  csharp: "3m"
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
related:
  - gex-regime-following
  - gamma-flip-strike-trading
keywords:
  - gamma scalping
  - QuantConnect
  - GEX
  - delta hedging
  - dealer positioning
last_updated: "2026-05-30"
last_verified_by_nightly: "2026-05-30"
references:
  - "Dynamic Hedging — Taleb (1997)"
  - "Volatility Trading — Sinclair (2013)"
---

# Gamma scalping in QuantConnect

> **What you'll build:** A delta-neutral options portfolio that profits from realized
> volatility by continuously hedging gamma exposure, gated by FlashAlpha's dealer-GEX
> regime signal.

## The intuition          ← 2-4 paragraphs, the WHY before the WHAT
## The setup              ← ticker, window, bars, parameters
## The algorithm          ← side-by-side C# + Python code blocks
## Running it             ← `lean backtest python/` + `lean backtest csharp/`
## Results                ← embed results/equity-curve-python.png + monthly-returns table
## Sensitivity            ← embed parameter-sweep.csv as a markdown table
## Variations             ← bullet list of cousin techniques
## When it fails          ← honest section on regime breakdown + drawdown periods
## FAQ                    ← 5-8 Q&A pairs (renders as FAQPage JSON-LD on hosted site)
## Related essays         ← cross-links from `related:` frontmatter
## References             ← from references.md (auto-inlined at build time)
```

### `meta.yaml` vs frontmatter

The README frontmatter is the human-facing form. `meta.yaml` carries the same machine-aggregated fields without prose. Authors edit `README.md`; CI asserts `meta.yaml` is in sync via `tools/verify-frontmatter.py`. Keeps authors editing one file, catalog build resilient (no markdown parser dependency in critical path), drift detectable.

### FAQ block — formalized

Every essay's `## FAQ` section has 5–8 Q&A pairs. Both human-useful AND lifted verbatim by LLMs. Template:

- "What is &lt;technique&gt;?" — 2-paragraph plain-English answer
- "Why use FlashAlpha &lt;bar&gt; for this instead of computing it from raw OI?" — advantage list
- "Does this work in real money?" — honest cost/regime/slippage discussion
- "What does the worst regime period look like?" — historical drawdown example
- "Can I run this in QuantConnect Cloud?" — yes/no/caveats
- "What if I get a 401 from FlashAlpha?" — pointer to bridge troubleshooting

On the hosted site, the FAQ section is wrapped in `FAQPage` JSON-LD — eligible for Google's FAQ rich result.

### `references.md`

Citations as markdown. `tools/build-bib.py` parses every essay's `references.md` and emits:
- `bibliography.md` at repo root (aggregated, deduplicated, alphabetical)
- `bibliography.bib` at repo root (BibTeX form, indexed by Google Scholar)
- Per-essay `references.bib` for academic-style citation

### `python/` and `csharp/` — runnable LEAN projects

Each language subdir is a real `lean` CLI project. Dates/cash/ticker live in `config.json` shared across languages (verified equal by `tools/verify-essay.py`) so C# and Python goldens compare apples-to-apples. Algorithm files are hand-written twins — NOT auto-generated.

### `results/` — six committed artifacts

1. `equity-curve-python.png` — strategy vs buy-and-hold
2. `equity-curve-csharp.png` — same
3. `monthly-returns.csv` — month-by-month, rendered in README as markdown table
4. `trade-stats.json` — sharpe, sortino, max drawdown, hit rate, average win/loss
5. `parameter-sweep.csv` — one canonical parameter swept across a range
6. `og-card.png` — Open Graph card (auto-generated from equity curve + title)

All produced by `tools/render-results.py` from raw LEAN `BacktestResult.json` output.

### `transcript.md` — flagship video transcript

Only the flagship essay (gamma-scalping) ships with a video walkthrough at v0.1.0. The 5–8 min walkthrough's transcript lives as markdown so search engines index the spoken content. Other essays get videos as resources permit (post-v1).

## §3 — CI strategy

Three layers, scaled to scope.

### Layer 0 — every PR (~45s)

No LEAN backtests. Structural validation only:
- `tools/build-catalog.py --check` — every `meta.yaml` validates against schema
- `tools/verify-frontmatter.py` — README frontmatter ≡ meta.yaml
- `tools/check-orphans.py` — no orphan essays, no orphan catalog entries
- `markdown-link-check` — no dead links
- `python -m ruff check essays/**/python/` + `dotnet format --verify-no-changes`
- `mkdocs build --strict` — hosted site builds clean (catches broken refs/templates)

### Layer 1 — changed essays only (~3 min per touched essay × matrix)

Triggered when `essays/**` changes. Detects touched essays from the diff, matrix-runs LEAN backtest for each touched essay × language:

- `lean backtest essays/<essay>/<lang>/ --output /tmp/backtest`
- `tools/verify-essay.py essays/<essay> /tmp/backtest --language <lang>`
- Compares to `golden.json` within tolerances:
  - `final_equity` — `rel=1e-4`
  - `total_trades` — exact
  - `sharpe` / `sortino` — `abs=0.01`
  - `max_drawdown` — `abs=0.005`

If the author intentionally changed the algorithm, they commit fresh `golden.json` in the same PR.

### Layer 2 — nightly full sweep (~30 min parallelized)

42-cell matrix (21 essays × 2 langs). `fail-fast: false` so one drift doesn't cancel the rest. On failure:
- File a GitHub issue labeled `nightly-drift` with the diff
- If multiple essays drift simultaneously → SDK or API schema change → pin SDK, investigate upstream
- If single essay drifts → coverage change for that ticker/date → investigate API tier
- Update `last_verified_by_nightly:` frontmatter on green runs

### Layer 3 — release tag (~45 min, manual)

Triggered by `vX.Y.0` tag (major/minor). Runs full sweep, captures fresh goldens + results/ artifacts, commits back to main, creates GitHub Release with auto-generated notes.

### Layer 4 — Pages deploy (every push to main, ~2 min)

`mkdocs build` → `gh-pages` branch → `examples.flashalpha.com` via Cloudflare CNAME.

### Tools

| File | Purpose |
|---|---|
| `tools/build-catalog.py` | meta.yaml × 21 → catalog.md + llms.txt + theme READMEs + _sitemap.xml + _schema.json |
| `tools/verify-essay.py` | parse LEAN output, compare to golden.json |
| `tools/capture-golden.py` | run LEAN, write golden.json + results/ artifacts |
| `tools/render-results.py` | LEAN BacktestResult JSON → PNGs + CSVs |
| `tools/check-orphans.py` | catalog ↔ filesystem consistency |
| `tools/verify-frontmatter.py` | README frontmatter ≡ meta.yaml |
| `tools/build-bib.py` | references.md × 21 → bibliography.md + bibliography.bib |
| `tools/build-site.py` | wraps mkdocs build + OG card generation + JSON-LD injection |
| `tools/gen-og-cards.py` | equity-curve PNG → OG card PNG (one per essay) |

Shared `tools/_lean_output.py` parses `BacktestResult.json` once; `tools/_schema.py` is the frontmatter schema definition.

### Secrets

- `FLASHALPHA_API_KEY` — read-only key, scoped to historical API. Same as bridge repo.

No NuGet/PyPI tokens — examples repo consumes packages, doesn't publish them.

## §4 — SEO / LLM discoverability layer

Three reinforcing surfaces — machine-readable, human-browsable, off-repo amplification.

### Machine-readable

- **`llms.txt`** — per [llmstxt.org](https://llmstxt.org/), auto-generated from `meta.yaml`. Every essay one line with summary. Crawlers find the whole catalog in one fetch.
- **`_sitemap.xml`** — full sitemap.xml at site root.
- **JSON-LD per page** — `TechArticle` + `HowTo` + `FAQPage` schemas (see §7).
- **BibTeX** — `bibliography.bib` indexed by Google Scholar.

### Human-browsable

- **`catalog.md`** — three sub-indexes: by theme, by difficulty, by bridge bar. Each entry: one-line summary, difficulty badge, bars used, expected runtime, golden equity.
- **Per-theme `README.md`** — `essays/a-dealer-positioning/README.md` is a SEO landing page for the theme. Same shape: title, 1-paragraph framing, essay list, related themes.
- **Repo root `README.md`** — the landing page: hook + install + first-essay link + 5 thumbnails + cross-links to bridge + awesome list + API docs.

### Per-essay SEO patterns

- H1 exact-match: `# Gamma scalping in QuantConnect` (not `# Gamma scalping`)
- H2s are deep-link targets: `## Running it`, `## When it fails`, `## FAQ`
- First paragraph is a tldr blockquote — snippet engines lift this as page summary
- Code blocks language-tagged (` ```python ` / ` ```csharp `)
- Image alt-text descriptive: `![SPY equity curve, gamma scalping strategy, Mar–Sep 2024](results/equity-curve-python.png)`

### Cross-repo linking

Outbound (every essay):
- Bridge package (NuGet + PyPI)
- Bridge data-type reference (deep-link into `flashalpha-quantconnect/docs/data-types.md`)
- FlashAlpha API endpoint docs

Inbound:
- Bridge README → examples (already committed)
- awesome-options-analytics → examples (already committed)
- historical.flashalpha.com docs nav → examples (post-launch, FlashAlpha team wires)

### GitHub topics (16)

`quantconnect`, `lean`, `backtest`, `algorithmic-trading`, `options-trading`, `gamma-scalping`, `gex`, `dealer-positioning`, `vol-surface`, `vrp`, `0dte`, `examples`, `cookbook`, `python`, `csharp`, `flashalpha`.

### Aggregation pipeline

Single `tools/build-catalog.py` pass produces:
```
meta.yaml × 21
    ↓
build-catalog.py
    ↓
├── catalog.md          (human index)
├── llms.txt            (LLM crawler index)
├── essays/*/README.md  (theme indexes)
├── bibliography.md     (aggregated references)
├── bibliography.bib    (BibTeX, Google Scholar)
├── _sitemap.xml        (search-engine sitemap)
└── _schema.json        (JSON-LD structured data)
```

One source of truth, many surfaces. CI runs `build-catalog.py --check` on every PR.

## §5 — Release model & flagship

### Versioning — per-repo semver

| Bump | Trigger |
|---|---|
| `v0.X.0` | New stable essay, OR essay flips draft→stable |
| `v0.X.Y` | Patch in existing stable essay (golden update, prose edit, bug fix) |
| `v1.0.0` | ≥12 stable essays AND every theme has ≥2 stable members |

### Per-essay lifecycle

`draft → stable → deprecated → (deleted in next major)`

- **draft** — README exists with full frontmatter and at minimum the "intuition" + "setup" sections written (so the essay is browseable and indexable). Algorithm files exist as compileable stubs: Python `main.py` defines a `QCAlgorithm` subclass with `Initialize()` and `OnData()` that subscribe to the right bridge bars but raise `NotImplementedError("Draft — see README.md for the proposed algorithm")` in `OnData`; C# `Main.cs` is the analogous compileable stub. `golden.json` is the literal string `{}` (parseable empty object). CI's Layer 0 must pass; Layer 1 backtests are run but failures are tolerated. Listed in catalog with `🚧 draft` badge.
- **stable** — `golden.json` committed, CI deterministic, results/ rendered. Counts toward v1.0 threshold.
- **deprecated** — must declare `replaced_by:` slug. Banner at top of README. Files stay for one major version then removed.

Enforced by `tools/check-orphans.py`.

### Flagship — `01-gamma-scalping` only stable at v0.1.0

Every other essay starts `status: draft`. Reasons:
1. The original ask
2. Richest pedagogical case (GEX + surface + exposure summary + delta hedging)
3. Justifies the bridge end-to-end
4. SEO honeypot — "gamma scalping in QuantConnect" is high-intent

### Cadence

- v0.1.0 — flagship stable + 20 drafts. Public.
- v0.2.0 – v0.10.0 — flip 1–3 essays per release. Roughly weekly.
- v1.0.0 — 12+ stable across all 5 themes. Earliest ~3 months after v0.1.0.

Catalog stays at 21 slots from day one — stability is the variable that changes.

### Bridge pinning

Each essay's `python/requirements.txt` and `csharp/*.csproj` pin `flashalpha-quantconnect` version. Repo-wide minimum supported bridge version in root `meta.yaml`. Single PR bumps every essay's pin in lockstep when bridge updates.

### Compatibility matrix

`docs/compatibility.md`:

| Examples version | Bridge version | LEAN CLI | .NET | Python |
|---|---|---|---|---|
| v0.1.0 | flashalpha-quantconnect 0.1.1 | lean 1.x | 9.0 | 3.10–3.12 |

### v0.1.0 launch ships

- ✅ Full repo scaffolded (catalog, llms.txt, tools, CI, hosted site, 21 essay folders)
- ✅ Gamma scalping stable (full essay, both algorithms, captured goldens, results, video transcript)
- ✅ 20 essays in draft (frontmatter complete, README skeleton, algorithm files stubbed)
- ✅ Cross-repo links wired
- ✅ CI green on main
- ✅ Hosted site live at examples.flashalpha.com
- ✅ GitHub topics + repo description + OG image
- ✅ Launch sequence executing (HN, reddit, QC forum, X) per launch-plan.md

### Out of scope for v0.1.0

- LEAN harness for in-process backtests from xUnit/pytest (bridge follow-up)
- QuantConnect Cloud parallel runs
- Live trading examples
- Custom domain beyond `examples.flashalpha.com`
- Newsletter beyond RSS feed (upgrade post-traction)

## §6 — Hosted docs site

Static site auto-built from `essays/**/README.md`, published on `examples.flashalpha.com`.

**Stack:** MkDocs Material + GitHub Pages + Cloudflare CNAME on `examples.flashalpha.com`.

**Per-essay enhancements over GitHub-only:**
- `<title>Gamma scalping in QuantConnect</title>` — GitHub's `<title>` is `flashalpha-historical-examples/README.md at main`.
- `<meta name="description">` from frontmatter `summary:`.
- OG `og:image` from auto-generated `og-card.png`.
- Algolia DocSearch — instant fuzzy search across all 21 essays.
- Mobile-first responsive rendering.
- `_redirects` for short URLs: `/gamma-scalping` → `/essays/a-dealer-positioning/01-gamma-scalping/`.
- Dark mode toggle.
- "Edit on GitHub" footer link per page.

**Repo additions for hosted site:**
- `mkdocs.yml`
- `overrides/partials/{head,footer,content}.html`
- `tools/build-site.py`
- `tools/gen-og-cards.py`
- `.github/workflows/pages.yml`

**Video walkthrough (flagship-only at v0.1.0):**
5–8 min Loom/Vimeo of gamma-scalping end-to-end (open repo, `lean backtest`, observe equity curve, tweak parameter, observe move). Embedded in flagship hosted page; transcript-as-markdown at `essays/a-dealer-positioning/01-gamma-scalping/transcript.md` so SE indexes spoken content.

## §7 — Structured data layer

JSON-LD on every hosted page, FAQ in every essay, freshness markers everywhere.

### Per-essay JSON-LD (emitted by `tools/build-site.py`)

`TechArticle` + `HowTo` (the algorithm steps) + `FAQPage` (the FAQ section) + `isPartOf: Course`. Schema includes:
- `headline`, `alternativeHeadline`
- `datePublished`, `dateModified` (from `last_updated:`)
- `author`, `publisher`
- `image` (equity-curve)
- `proficiencyLevel`
- `about` (tags from frontmatter `keywords:`)
- `isPartOf` (the Course schema on catalog page)
- `tutorial: [HowToStep…]` (extracted from `## The algorithm` section)

### Catalog-wide `Course` schema

The catalog page emits a top-level `Course` schema linking all 21 essays. Google's "Course" rich-result card competes with Coursera/Udemy on relevant SERPs.

### FAQ markup

Every essay's `## FAQ` section wraps in `FAQPage` JSON-LD. Google's FAQ rich result is one of the highest-CTR result types.

### Freshness machinery

- `last_updated:` field in every frontmatter
- Nightly CI bumps `last_verified_by_nightly:` on green runs
- Hosted site renders visible badge: `🟢 Last verified: 2 days ago — automated nightly check passed.`
- Red badge after 3 consecutive nightly failures: `🔴 Drift detected — see [issue](...)`.

### BibTeX export

`tools/build-bib.py` parses every `references.md` → emits `bibliography.bib` at repo root + per-essay `references.bib`. Google Scholar indexes BibTeX. Researchers find essays in academic search.

## §8 — Amplification

### Launch plan (`docs/superpowers/launch-plan.md`)

Named dates, draft post text checked into `launch-drafts/`, named outreach contacts.

| Day | Channel | Action |
|---|---|---|
| -3 | examples.flashalpha.com | Site live, OG cards verified, dark/light tested |
| -1 | QC Slack/Discord | DM @QuantConnectStaff with preview link |
| 0 | r/algotrading | "I built 21 backtests for options strategies in QuantConnect" |
| 0 | Hacker News | "Show HN: Gamma scalping backtests in QuantConnect" |
| 0 | r/options | Variant focused on dealer positioning |
| 0 | X / Twitter | Thread: equity curve hook → algorithm gist → link |
| +1 | QC Community Forum | Post + offer Q&A |
| +7 | LinkedIn (founder) | Personal post: lessons from building 21 backtests |
| +14 | Quant newsletters | Email outreach (named contacts) |

Each row has a draft in `launch-drafts/<channel>.md`. No "we'll figure out copy at launch."

### Plausible Analytics

Injected as one `<script>` in `overrides/partials/head.html`. Tracks pageviews per essay, referrers, exit rate, 404s. Weekly review drives v0.2.0+ stable-essay prioritization — promotion is data-informed.

### A/B test harness

`<meta name="experiment" content="...">` on rotating versions of the flagship. Plausible's custom-event API tracks scroll depth per variant. Two ready experiments at launch:
1. Hero blockquote vs hero equity-curve image
2. FAQ at top vs FAQ at bottom

After 4 weeks at ≥500 sessions per variant, winner replaces template.

### RSS + newsletter

Hosted site emits `/feed.xml` (Atom). Catalog page links `[Subscribe via RSS](/feed.xml)`. Buttondown newsletter `examples-newsletter@flashalpha.com` republishes RSS + 3-sentence editor note. Free tier <1000 subscribers.

### Schema.org Course (catalog-wide)

Top-level `Course` schema on catalog page linking all 21 essays. Google's Course rich result competes with paid courses for SERP visibility.

## Open questions / known gaps

- **Subdomain DNS** — `examples.flashalpha.com` CNAME must be configured by whoever owns flashalpha.com DNS. Out of repo scope; flag for FlashAlpha ops.
- **Video production** — flagship walkthrough needs recording. Skipped from v0.1.0 if recording slips; transcript-as-markdown still ships with placeholder.
- **Algolia DocSearch application** — free for OSS but requires approval. Submit during scaffolding so it's live by launch.
- **Plausible setup** — needs account, paid tier ($9/mo) or self-hosted. Decide hosting before launch.
- **QuantConnect relationship** — strongest distribution comes from QC's own community surfacing. Worth pre-launch DM to @QuantConnectStaff.

## Success criteria recap

- ≥12 essays in `stable` status across all 5 themes (≥2 per theme) by v1.0.0.
- `examples.flashalpha.com` live with rich results verified.
- Cited by an LLM in a relevant query within 90 days.
- ≥3 inbound links from external venues within 30 days.
- All 21 essays in catalog at v0.1.0 (drafts allowed); 100% pass Layer 0 CI; flagship passes Layers 0+1+2.
