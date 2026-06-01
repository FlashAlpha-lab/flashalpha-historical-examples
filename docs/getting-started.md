# Getting started

Run your first FlashAlpha + QuantConnect LEAN backtest in under ten minutes. This
guide assumes you've cloned the repo and want to verify your local toolchain
works before browsing the [essay catalog](catalog.md) or
[writing your own](what-is-an-essay.md#adding-a-new-essay).

---

## Prerequisites

You need four things installed and one environment variable set.

### 1. Python 3.10+

Verify:

```bash
python --version
# Python 3.10.x or newer (3.10, 3.11, 3.12 all supported)
```

If you don't have it: [python.org/downloads](https://www.python.org/downloads/)
or your platform's package manager.

### 2. .NET 9 SDK

LEAN compiles C# algorithms against .NET 9. Verify:

```bash
dotnet --version
# 9.0.x
```

If missing: [dotnet.microsoft.com/download/dotnet/9.0](https://dotnet.microsoft.com/download/dotnet/9.0).

Python-only contributors still need the .NET SDK installed — the LEAN CLI
shells out to `dotnet` even for Python backtests.

### 3. Docker

LEAN runs every backtest inside a Docker container (the
`quantconnect/lean:latest` image). Docker Desktop on Mac/Windows or `docker`
+ `docker-compose` on Linux both work.

Verify:

```bash
docker --version
docker run hello-world
```

The first `lean backtest` command will pull `quantconnect/lean:latest` —
budget ~2 GB and a few minutes on first run. Subsequent runs use the cached
image.

### 4. LEAN CLI

The LEAN CLI is a Python package:

```bash
pip install lean
lean --version
```

A virtualenv is recommended but not required.

### 5. FlashAlpha API key

Every essay's `config.json` reads `FLASHALPHA_API_KEY` from the environment.
Get a free key at [flashalpha.com](https://flashalpha.com), then:

**macOS / Linux:**

```bash
export FLASHALPHA_API_KEY="fa_live_..."
# Persist by adding the line to ~/.bashrc or ~/.zshrc
```

**Windows (PowerShell):**

```powershell
$env:FLASHALPHA_API_KEY = "fa_live_..."
# Persist via System Properties → Environment Variables
```

Verify the key is visible to the shell you'll run `lean` from:

```bash
echo $FLASHALPHA_API_KEY        # macOS / Linux
echo $env:FLASHALPHA_API_KEY    # Windows PowerShell
```

If the variable is empty, LEAN will still launch the container but the
FlashAlpha bridge will throw `401 Unauthorized` once the algorithm starts
requesting bars.

---

## Run your first essay

Clone the repo and run the flagship gamma-scalping essay's Python project:

```bash
git clone https://github.com/FlashAlpha-lab/flashalpha-historical-examples.git
cd flashalpha-historical-examples
cd essays/a-dealer-positioning/01-gamma-scalping/python/
lean backtest
```

What happens, in order:

1. LEAN CLI reads `config.json` and the project's `*.py` files.
2. Docker pulls `quantconnect/lean:latest` (first run only).
3. The container mounts the project directory, installs the
   `flashalpha-quantconnect` bridge package from PyPI (pinned in
   `requirements.txt` or referenced from `config.json`), and starts the
   algorithm.
4. The algorithm requests historical FlashAlpha bars over the backtest window
   declared in the essay's frontmatter.
5. Trades execute against the LEAN simulator.
6. A timestamped directory appears under `backtests/`.

Total wall-clock for the flagship essay: ~8 minutes on a warm Docker cache.
Cold-pull adds a few minutes the first time.

---

## What is `lean backtest` actually doing?

The CLI is a thin wrapper. Three things happen each invocation.

### 1. Docker

LEAN runs inside `quantconnect/lean:latest` so every contributor gets bit-
for-bit identical results regardless of host OS. The container is pulled
on first run (~2 GB), cached locally afterward.

To force a fresh image:

```bash
docker pull quantconnect/lean:latest
```

To check what's installed:

```bash
docker images | grep quantconnect
```

### 2. Output directory

After the backtest completes, look in `backtests/<timestamp>/` under the
project root. Each run creates a new timestamped folder — old runs are
preserved, not overwritten.

Key files:

| File | What it is |
| --- | --- |
| `BacktestResult.json` | The canonical machine-readable output. Contains equity curve, every trade, statistics, runtime alpha. This is what `tools/capture-golden.py` reads to fingerprint reproducibility. |
| `summary.txt` | One-screen statistics: final equity, total trades, sharpe, sortino, max drawdown, hit rate. |
| `*.html` | LEAN's rendered report (equity curve, drawdown chart, monthly returns). Open in a browser. |
| `log.txt` | Algorithm stdout — `Log()` and `Debug()` calls land here. |
| `*-order-events.json` | Every fill and cancel, useful for slippage forensics. |

### 3. The bridge in action

The essay's `OnData(slice)` (Python) or `OnData(Slice slice)` (C#) handler
receives `FlashAlphaGexBar`, `FlashAlphaSurfaceBar`, etc. as members of
`slice`. The bridge package wraps each FlashAlpha endpoint as a LEAN custom-
data subscription — the algorithm code looks idiomatic, the network
plumbing is invisible.

See [what-is-an-essay.md](what-is-an-essay.md) for the frontmatter
fields that declare which bars an essay subscribes to.

---

## Reading a backtest result

Open `backtests/<timestamp>/summary.txt`:

```
Total Trades             84
Average Win              1.42%
Average Loss             -0.83%
Compounding Annual Ret.  4.83%
Drawdown                 4.50%
Net Profit               2.42%
Sharpe Ratio             0.72
Sortino Ratio            0.94
Win Rate                 61%
Loss Rate                39%
Profit-Loss Ratio        1.71
Total Fees               $98.40
```

Cross-reference these with the essay's `golden` block in
`README.md` frontmatter — the values should match within the
nightly drift tolerance. If they don't, see
[what-is-an-essay.md#what-ci-checks](what-is-an-essay.md#what-ci-checks).

For the HTML report:

```bash
# macOS
open backtests/<timestamp>/*.html
# Linux
xdg-open backtests/<timestamp>/*.html
# Windows PowerShell
Start-Process backtests/<timestamp>/*.html
```

---

## Run the C# version

Every essay ships parallel Python + C# implementations. To run the C# twin:

```bash
cd ../csharp/
lean backtest
```

First run compiles the C# project against the LEAN .NET 9 image — takes
~30 seconds extra. Subsequent runs use the cached DLL.

The two languages diverge only in syntax. They subscribe to the same bars
with the same `config.json` values, so the goldens compare apples-to-apples
across languages. The C# version is typically 2-3x faster wall-clock.

---

## Troubleshooting

### `lean: command not found`

`pip install lean` installed the package but the `lean` script isn't on
`PATH`. On macOS / Linux, try `python -m lean backtest` or check
`pip show lean` for the install location.

### `Cannot connect to the Docker daemon`

Docker isn't running. Start Docker Desktop (Mac/Windows) or
`sudo systemctl start docker` (Linux).

### `401 Unauthorized` during algorithm startup

`FLASHALPHA_API_KEY` is unset or invalid. Re-check with `echo` and confirm
the key works against the FlashAlpha API directly:

```bash
curl -H "Authorization: Bearer $FLASHALPHA_API_KEY" \
  https://api.flashalpha.com/v1/exposure/gex?ticker=SPY
```

### Backtest hangs at "Launching algorithm"

Usually Docker is pulling the image. Watch `docker images` in another
terminal to confirm. If progress stalls for >5 minutes, kill the container
and re-run.

### Out-of-memory inside the container

The default LEAN container has a memory cap. Bump it via Docker Desktop's
Resources → Memory slider, or pass `--lean-config "ram-allocation=4096"`.

### Stale data / 304 from FlashAlpha

The bridge caches responses inside the container. To force a fresh fetch,
remove the cache directory printed in the algorithm's startup log, or
re-run with a one-day-newer `end` date in `config.json`.

---

## Where to next

- **[catalog.md](catalog.md)** — auto-generated index of every essay, themed
  and difficulty-tagged. Built by `tools/build-catalog.py` from the
  frontmatter of each essay. Browse here if you want to pick the next essay
  to run.
- **[what-is-an-essay.md](what-is-an-essay.md)** — the anatomy of an essay
  folder, the frontmatter schema, the draft → stable → deprecated
  lifecycle, what CI enforces, and how to add a new essay.
- **[glossary.md](glossary.md)** — plain-English definitions of every
  options / volatility / dealer-positioning term used across the repo,
  cross-linked to the bridge's data-types reference.
- **[lean-cli-cheatsheet.md](lean-cli-cheatsheet.md)** — the LEAN
  commands you'll actually use, with examples.
- **[compatibility.md](compatibility.md)** — the bridge / LEAN / .NET /
  Python compatibility matrix for this examples repo's current release.

### Outside this repo

- **[FlashAlpha QuantConnect bridge](https://github.com/FlashAlpha-lab/flashalpha-quantconnect)**
  — the package every essay depends on. Source, issues, release notes,
  data-types reference.
- **[examples.flashalpha.com](https://examples.flashalpha.com)** — the
  hosted version of this repo with full-text search, equity-curve previews,
  and per-essay FAQ rich results. Live post-launch.
- **[QuantConnect LEAN docs](https://www.quantconnect.com/docs/v2/lean-cli)**
  — canonical reference for the `lean` CLI and the algorithm framework.

---

## Next steps for contributors

If you're here to add an essay rather than just run them:

1. Read [what-is-an-essay.md](what-is-an-essay.md) end-to-end.
2. Scaffold a new essay with `fa-new-essay --theme <theme> --slug <slug>`
   (installed when you `pip install -e tools/`).
3. Implement the algorithm in `python/` and `csharp/`.
4. Capture a golden with `fa-capture-golden`.
5. Open a PR — CI Layers 0 and 1 will run the gates described in
   [what-is-an-essay.md#what-ci-checks](what-is-an-essay.md#what-ci-checks).
