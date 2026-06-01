"""Catalog ↔ filesystem consistency: every essay folder has the required shape."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


class OrphanError(Exception):
    """An essay is missing required files or directories."""


REQUIRED_FILES = [
    "README.md",
    "meta.yaml",
    "references.md",
    "python/lean.json",
    "python/config.json",
    "python/main.py",
    "python/golden.json",
    "python/requirements.txt",
    "csharp/lean.json",
    "csharp/config.json",
    "csharp/Main.cs",
    "csharp/golden.json",
]
REQUIRED_DIRS = ["python", "csharp", "results"]


def check_essay_shape(essay_dir: Path) -> None:
    """Raise OrphanError if any required file/dir is missing."""
    for d in REQUIRED_DIRS:
        if not (essay_dir / d).is_dir():
            raise OrphanError(f"{essay_dir.name}: missing directory {d}/")
    for f in REQUIRED_FILES:
        if not (essay_dir / f).exists():
            raise OrphanError(f"{essay_dir.name}: missing file {f}")
    # csharp .csproj — any *.csproj inside csharp/ counts
    if not list((essay_dir / "csharp").glob("*.csproj")):
        raise OrphanError(f"{essay_dir.name}: missing .csproj in csharp/")


def find_orphans(repo_root: Path) -> list[str]:
    """Scan every essay folder under essays/<theme>/ and return list of issue strings."""
    issues: list[str] = []
    essays_root = repo_root / "essays"
    if not essays_root.is_dir():
        return [f"essays/ not found at {repo_root}"]
    for theme_dir in sorted(essays_root.iterdir()):
        if not theme_dir.is_dir() or theme_dir.name.startswith("."):
            continue
        for essay_dir in sorted(theme_dir.iterdir()):
            if not essay_dir.is_dir() or essay_dir.name.startswith("."):
                continue
            try:
                check_essay_shape(essay_dir)
            except OrphanError as e:
                issues.append(str(e))
    return issues


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Detect orphan/incomplete essays")
    p.add_argument("--repo-root", default=".", help="Repo root directory")
    args = p.parse_args(argv)

    issues = find_orphans(Path(args.repo_root))
    if issues:
        for i in issues:
            print(i, file=sys.stderr)
        return 1
    print("OK — no orphans")
    return 0


if __name__ == "__main__":
    sys.exit(main())
