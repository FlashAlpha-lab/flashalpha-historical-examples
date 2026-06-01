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
