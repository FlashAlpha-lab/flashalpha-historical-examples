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
from flashalpha_quantconnect import GexBar, add_flashalpha_gex, config


class Algorithm(QCAlgorithm):
    def Initialize(self):
        # Bridge auth: pass key via lean backtest --parameter flashalpha-api-key:VALUE
        api_key = self.GetParameter("flashalpha-api-key")
        if api_key:
            config.api_key = api_key
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
        "flashalpha-quantconnect==0.1.4\n", encoding="utf-8",
    )
    # smoke-golden.json starts empty; populated by `fa-smoke`
    (essay_dir / "validation" / "smoke-golden.json").write_text("{}\n", encoding="utf-8")

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
        "flashalpha-quantconnect==0.1.4\n", encoding="utf-8",
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
    <PackageReference Include="FlashAlpha.QuantConnect" Version="0.1.4" />
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
