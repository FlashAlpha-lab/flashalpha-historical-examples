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
