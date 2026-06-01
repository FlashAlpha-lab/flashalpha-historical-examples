"""Verify that an essay's README frontmatter matches its meta.yaml exactly,
and both validate against the frontmatter schema.

This catches:
- Author edited README but forgot meta.yaml (drift).
- Either file has invalid schema (missing required field, bad enum value).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from ._schema import validate_frontmatter


class FrontmatterMismatch(Exception):
    """README frontmatter and meta.yaml disagree."""


def extract_frontmatter(readme_path: Path) -> dict:
    """Read the YAML frontmatter block from a README.md."""
    text = readme_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{readme_path} has no frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError(f"{readme_path} frontmatter has no closing ---")
    block = text[3:end].strip()
    return yaml.safe_load(block) or {}


def verify_essay_frontmatter(essay_dir: Path) -> None:
    """Raise on schema violation or README<->meta.yaml drift."""
    readme = essay_dir / "README.md"
    meta = essay_dir / "meta.yaml"
    if not readme.exists():
        raise FileNotFoundError(readme)
    if not meta.exists():
        raise FileNotFoundError(meta)

    fm_readme = extract_frontmatter(readme)
    fm_meta = yaml.safe_load(meta.read_text(encoding="utf-8")) or {}

    validate_frontmatter(fm_readme)
    validate_frontmatter(fm_meta)

    # Drift check: all keys/values must agree
    keys = set(fm_readme.keys()) | set(fm_meta.keys())
    for k in keys:
        if fm_readme.get(k) != fm_meta.get(k):
            raise FrontmatterMismatch(
                f"{essay_dir.name}: '{k}' differs between README.md frontmatter "
                f"({fm_readme.get(k)!r}) and meta.yaml ({fm_meta.get(k)!r})"
            )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Verify essay frontmatter sync + schema")
    p.add_argument("essays", nargs="+", help="Essay directories to verify")
    args = p.parse_args(argv)

    failures = []
    for d in args.essays:
        try:
            verify_essay_frontmatter(Path(d))
        except Exception as e:
            failures.append(f"{d}: {e}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"OK ({len(args.essays)} essays verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
