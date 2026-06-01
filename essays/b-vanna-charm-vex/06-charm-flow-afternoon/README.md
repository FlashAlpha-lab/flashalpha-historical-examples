---
title: Charm-flow afternoon timing
slug: charm-flow-afternoon
theme: vanna-charm-vex
difficulty: intermediate
status: draft
summary: _(One-sentence summary of Charm-flow afternoon timing.)_
bridge_bars:
- FlashAlphaGexBar
data_endpoints:
- exposure/gex
tickers:
- SPY
backtest_window:
  start: '2024-03-01'
  end: '2024-09-30'
expected_runtime:
  python: 5m
  csharp: 2m
golden:
  python: {}
  csharp: {}
keywords:
- charm-flow afternoon timing
- QuantConnect
- LEAN
last_updated: '2026-06-01'
related: []
references: []
---

# Charm-flow afternoon timing

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

### What is charm-flow afternoon timing?
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
