# LEAN CLI cheatsheet

The LEAN CLI is a thin wrapper that runs your QuantConnect algorithm inside a
Docker container against a known-good runtime. These are the commands you'll
actually use while iterating on essays in this repo.

Canonical reference: [QuantConnect LEAN CLI docs](https://www.quantconnect.com/docs/v2/lean-cli).

> **Docker is required.** Every command below shells out to a
> `quantconnect/lean:latest` container. Make sure Docker is running before
> you `lean anything`. The first run pulls ~2 GB.

---

## `lean init`

Initialize a new LEAN workspace in the current directory.

```bash
lean init
```

Drops a `lean.json` global config, a `data/` directory, and (optionally) a
sample project. You **only run this once per machine** — every essay project
in this repo already has its own `config.json`, so you don't need to
`lean init` inside an essay folder.

Useful flags:

- `--organization-id <id>` — pre-fill the QC Cloud org ID for `lean cloud`
  commands. Skip if you'll only run locally.

---

## `lean backtest`

Run a backtest locally inside Docker. The bread-and-butter command.

```bash
# From inside an essay's python/ or csharp/ directory:
lean backtest
```

What happens:

1. CLI reads `config.json` and the algorithm files in the current directory.
2. Container is launched with the project mounted.
3. Algorithm runs over the backtest window in `config.json`.
4. Output lands in `backtests/<timestamp>/`.

Key output file: `backtests/<timestamp>/BacktestResult.json` — the canonical
machine-readable result. `tools/capture-golden.py` reads this.

Other files in the same directory:

- `summary.txt` — human-readable statistics.
- `*.html` — LEAN's rendered report (equity curve, drawdown, monthly
  returns).
- `log.txt` — algorithm stdout.
- `*-order-events.json` — per-order audit trail.

Useful flags:

- `--debug ptvsd` / `--debug vsdbg` — attach VS Code / VS debugger to the
  running container. Use `pythontools` for the Python Tools for VS profile.
- `--output <dir>` — change the output directory from the default
  `backtests/<timestamp>/`.
- `--lean-config <path>` — point at a non-default `lean.json`.
- `--detach` — run in the background; useful for long sweeps.

Example with debugger:

```bash
lean backtest --debug ptvsd
```

---

## `lean cloud backtest`

Run a backtest on QuantConnect Cloud instead of locally. Requires a QC
account and `lean login` first.

```bash
lean login                          # one-time, prompts for QC credentials
lean cloud push                     # sync local files up to QC Cloud
lean cloud backtest "Project Name"  # run on QC's infrastructure
```

When to reach for it:

- You want to run against QC's full minute-resolution equities universe
  without downloading data locally.
- Your local machine is overloaded and you'd rather burn QC node-hours.
- You're verifying that a strategy reproduces on QC's infrastructure
  before sharing it with QC's community.

Note: **this repo's CI does not use QC Cloud** — every gate runs `lean
backtest` locally for reproducibility. `lean cloud backtest` is purely a
contributor convenience.

---

## `lean live`

Trade paper or live against a real broker. Out of scope for this
examples repo — every essay is backtest-only.

```bash
lean live --brokerage paper             # paper trade
lean live --brokerage interactivebrokers # live, requires IB creds
```

Don't point this at essays in this repo without reading the algorithm
end-to-end first. Backtest sizing assumptions rarely transfer to live
trading unchanged.

---

## `lean optimize`

Run a parameter optimization sweep. Backtests the algorithm across a
parameter grid and reports which combination produced the best target
metric.

```bash
lean optimize
```

Driven by an `optimization` block in `config.json` declaring the
parameters, ranges, and target. Example block:

```json
"optimization": {
  "target": "Sharpe Ratio",
  "target-direction": "max",
  "parameters": {
    "lookback_days": {"min": 10, "max": 60, "step": 5},
    "threshold": {"min": 0.5, "max": 2.0, "step": 0.25}
  }
}
```

This repo's essays commit a `results/parameter-sweep.csv` produced by a
one-parameter `lean optimize` run, rendered as a markdown table in the
README's `## Sensitivity` section.

---

## `lean report`

Generate an HTML backtest report from a previous run's
`BacktestResult.json`.

```bash
lean report --backtest-results backtests/<timestamp>/BacktestResult.json \
  --output report.html
```

`lean backtest` already drops a report HTML alongside the JSON. Reach for
`lean report` when:

- You want to regenerate the report from CI artifacts.
- You're combining results from multiple backtests into one document.

---

## `lean logs`

View algorithm logs from the most recent local run.

```bash
lean logs
```

Equivalent to `cat backtests/<timestamp>/log.txt` for the most recent
timestamped directory. Useful while debugging algorithm `Log()` /
`Debug()` output.

Flags:

- `--no-follow` — print and exit (default behaviour).
- `--lean-config <path>` — point at a non-default config.

---

## Common patterns

### Re-run after editing the algorithm

```bash
# Make edits to main.py / Main.cs
lean backtest
```

LEAN auto-detects file changes; no rebuild step is needed for Python. C#
projects recompile inside the container on every run.

### Wipe stale results

```bash
rm -rf backtests/
lean backtest
```

Old runs accumulate. Clear them out when a directory listing starts
slowing you down.

### Run both languages back-to-back

```bash
( cd python/  && lean backtest ) && ( cd csharp/ && lean backtest )
```

Useful for checking that a parameter change reproduces across languages
before capturing a new golden.

### Capture a golden from a fresh local run

```bash
fa-capture-golden essays/a-dealer-positioning/01-gamma-scalping/
```

`fa-capture-golden` runs both language backtests, reads each
`BacktestResult.json`, and writes the canonical fingerprint to
`golden.json` plus the matching `golden:` block in the README
frontmatter. See [what-is-an-essay.md](what-is-an-essay.md#adding-a-new-essay)
for the full essay-authoring flow.

---

## When LEAN won't play nice

- **Container exits immediately** — almost always a config.json syntax
  error. `lean backtest` prints the parsed config; eyeball it.
- **`No module named 'flashalpha_quantconnect'`** — `requirements.txt` is
  missing the bridge pin. Confirm `flashalpha-quantconnect == X.Y.Z` is
  present and matches [compatibility.md](compatibility.md).
- **C# build errors about `FlashAlpha.QuantConnect`** — the `*.csproj`
  must reference the bridge NuGet package; check
  [compatibility.md](compatibility.md) for the pinned version.
- **Hangs after "Launching algorithm"** — usually Docker pulling the
  image on first run. `docker images | grep quantconnect` in another
  terminal to confirm progress.

For deeper LEAN troubleshooting see the
[QC LEAN CLI docs](https://www.quantconnect.com/docs/v2/lean-cli) and the
[QC Community forum](https://www.quantconnect.com/forum).
