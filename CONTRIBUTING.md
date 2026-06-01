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
