"""Aggregate references.md across essays into bibliography.md + bibliography.bib."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


_BULLET_RE = re.compile(r"^\s*-\s+(.+?)\s*$")
_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")


def parse_references(refs_path: Path) -> list[dict]:
    """Parse a references.md file into a list of {raw, url} dicts.

    A reference is a bullet line. If it contains a markdown link, the URL is extracted.
    """
    if not refs_path.exists():
        return []
    out: list[dict] = []
    for line in refs_path.read_text(encoding="utf-8").splitlines():
        m = _BULLET_RE.match(line)
        if not m:
            continue
        text = m.group(1).strip()
        link = _LINK_RE.search(text)
        out.append({
            "raw": text,
            "url": link.group(2) if link else None,
        })
    return out


def collect_all_references(repo: Path) -> list[dict]:
    refs: list[dict] = []
    for p in (repo / "essays").rglob("references.md"):
        refs.extend(parse_references(p))
    return refs


def _dedupe(refs: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for r in refs:
        key = r["raw"]
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def render_bibliography_md(refs: list[dict]) -> str:
    refs = sorted(_dedupe(refs), key=lambda r: r["raw"].lower())
    lines = ["# Bibliography", "",
             "Aggregated references across all essays.", ""]
    for r in refs:
        lines.append(f"- {r['raw']}")
    return "\n".join(lines) + "\n"


def render_bibliography_bib(refs: list[dict]) -> str:
    refs = _dedupe(refs)
    out_lines: list[str] = []
    for r in refs:
        key = hashlib.md5(r["raw"].encode("utf-8")).hexdigest()[:8]
        # Guess entry type: URL → @misc, else @book/@article (use @book as safe default)
        if r["url"]:
            out_lines.append(f"@misc{{ref_{key},")
            out_lines.append(f"  title = {{{r['raw']}}},")
            out_lines.append(f"  url = {{{r['url']}}}")
            out_lines.append("}")
        else:
            out_lines.append(f"@book{{ref_{key},")
            out_lines.append(f"  title = {{{r['raw']}}}")
            out_lines.append("}")
        out_lines.append("")
    return "\n".join(out_lines)


def build_bib(repo: Path) -> None:
    refs = collect_all_references(repo)
    (repo / "bibliography.md").write_text(render_bibliography_md(refs), encoding="utf-8")
    (repo / "bibliography.bib").write_text(render_bibliography_bib(refs), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build bibliography.md + bibliography.bib")
    p.add_argument("--repo-root", default=".")
    args = p.parse_args(argv)
    build_bib(Path(args.repo_root))
    print("Bibliography built.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
