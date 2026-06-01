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
