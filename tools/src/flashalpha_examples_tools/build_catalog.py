"""Aggregate every essay's meta.yaml into catalog.md, llms.txt, theme READMEs, sitemap.xml.

Single pass over essays/**/meta.yaml. Idempotent — running twice produces the same outputs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from ._schema import THEMES_DIR_MAP


def _load_essays(repo: Path) -> list[dict[str, Any]]:
    """Walk essays/<theme>/<n-slug>/meta.yaml and return list of frontmatters."""
    out: list[dict[str, Any]] = []
    essays_root = repo / "essays"
    for theme_dir in sorted(essays_root.iterdir()):
        if not theme_dir.is_dir() or theme_dir.name.startswith("."):
            continue
        for essay_dir in sorted(theme_dir.iterdir()):
            if not essay_dir.is_dir() or essay_dir.name.startswith("."):
                continue
            meta_path = essay_dir / "meta.yaml"
            if not meta_path.exists():
                continue
            fm = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
            fm["_dir"] = essay_dir.relative_to(repo).as_posix()
            fm["_theme_dir"] = theme_dir.name
            out.append(fm)
    return out


def _theme_display_name(theme_slug: str) -> str:
    return {
        "dealer-positioning": "Dealer positioning",
        "vanna-charm-vex": "Vanna / charm / VEX",
        "vrp-volatility": "VRP / volatility",
        "zero-dte": "0DTE",
        "cross-signal": "Cross-signal / multi-asset",
    }[theme_slug]


def _status_badge(s: str) -> str:
    return {"draft": "🚧 draft", "stable": "✅ stable", "deprecated": "⚠️ deprecated"}[s]


def render_llms_txt(repo: Path) -> str:
    essays = _load_essays(repo)
    by_theme: dict[str, list[dict]] = {}
    for e in essays:
        by_theme.setdefault(e["theme"], []).append(e)

    lines = ["# flashalpha-historical-examples",
             "",
             "> 21 backtest essays for options strategies on QuantConnect LEAN.",
             "> Side-by-side C# and Python. Powered by flashalpha-quantconnect.",
             ""]
    for theme_slug in ["dealer-positioning", "vanna-charm-vex", "vrp-volatility", "zero-dte", "cross-signal"]:
        items = by_theme.get(theme_slug, [])
        if not items:
            continue
        lines.append(f"## Essays — {_theme_display_name(theme_slug)}")
        for e in sorted(items, key=lambda x: x["_dir"]):
            link = f"{e['_dir']}/README.md"
            lines.append(f"- [{e['title']}]({link}): {e['summary']}")
        lines.append("")
    lines += [
        "## Bridge package",
        "- [flashalpha-quantconnect on NuGet](https://www.nuget.org/packages/FlashAlpha.QuantConnect/)",
        "- [flashalpha-quantconnect on PyPI](https://pypi.org/project/flashalpha-quantconnect/)",
        "",
        "## Underlying API",
        "- [historical.flashalpha.com](https://historical.flashalpha.com)",
        "",
        "## Optional",
        "- [Glossary](docs/glossary.md)",
        "- [LEAN CLI cheatsheet](docs/lean-cli-cheatsheet.md)",
        "- [Bibliography](bibliography.md)",
    ]
    return "\n".join(lines) + "\n"


def render_catalog_md(repo: Path) -> str:
    essays = _load_essays(repo)
    by_theme: dict[str, list[dict]] = {}
    for e in essays:
        by_theme.setdefault(e["theme"], []).append(e)

    lines = ["# Catalog", "",
             "21 essays grouped by theme. Browse by [difficulty](#by-difficulty) or [bridge bar](#by-bridge-bar) below.",
             "",
             "## By theme", ""]

    for theme_slug in ["dealer-positioning", "vanna-charm-vex", "vrp-volatility", "zero-dte", "cross-signal"]:
        items = by_theme.get(theme_slug, [])
        if not items:
            continue
        lines.append(f"### {_theme_display_name(theme_slug)}")
        lines.append("")
        lines.append("| # | Essay | Status | Difficulty | Bridge bars |")
        lines.append("|---|---|---|---|---|")
        for e in sorted(items, key=lambda x: x["_dir"]):
            n = e["_dir"].split("/")[-1].split("-")[0]
            bars = ", ".join(f"`{b}`" for b in e.get("bridge_bars", []))
            lines.append(f"| {n} | [{e['title']}]({e['_dir']}/) | {_status_badge(e['status'])} | {e['difficulty']} | {bars} |")
        lines.append("")

    # By difficulty
    lines.append("## By difficulty")
    lines.append("")
    for diff in ["beginner", "intermediate", "advanced"]:
        diff_items = [e for e in essays if e.get("difficulty") == diff]
        if not diff_items:
            continue
        lines.append(f"### {diff.title()}")
        for e in sorted(diff_items, key=lambda x: x["_dir"]):
            lines.append(f"- [{e['title']}]({e['_dir']}/) — {e['summary']}")
        lines.append("")

    # By bridge bar
    lines.append("## By bridge bar")
    lines.append("")
    by_bar: dict[str, list[dict]] = {}
    for e in essays:
        for b in e.get("bridge_bars", []):
            by_bar.setdefault(b, []).append(e)
    for bar in sorted(by_bar):
        lines.append(f"### `{bar}`")
        for e in sorted(by_bar[bar], key=lambda x: x["_dir"]):
            lines.append(f"- [{e['title']}]({e['_dir']}/)")
        lines.append("")

    return "\n".join(lines) + "\n"


def render_theme_readme(repo: Path, theme_slug: str) -> str:
    essays = [e for e in _load_essays(repo) if e["theme"] == theme_slug]
    display = _theme_display_name(theme_slug)
    lines = [f"# {display} strategies for QuantConnect",
             "",
             f"{len(essays)} backtest essays in this theme.",
             "",
             "## Essays", ""]
    for e in sorted(essays, key=lambda x: x["_dir"]):
        n = e["_dir"].split("/")[-1].split("-")[0]
        lines.append(f"- {n} [{e['title']}]({e['_dir'].split('/')[-1]}/) — {e['summary']} {_status_badge(e['status'])}")
    lines.append("")
    return "\n".join(lines) + "\n"


def render_sitemap(repo: Path, base_url: str) -> str:
    essays = _load_essays(repo)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines.append(f"  <url><loc>{base_url}/</loc></url>")
    lines.append(f"  <url><loc>{base_url}/catalog/</loc></url>")
    for e in essays:
        loc = f"{base_url}/{e['_dir']}/"
        lastmod = e.get("last_updated", "2026-06-01")
        lines.append(f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod></url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_catalog(repo: Path, base_url: str = "https://examples.flashalpha.com") -> None:
    """Write catalog.md, llms.txt, per-theme READMEs, _sitemap.xml."""
    (repo / "catalog.md").write_text(render_catalog_md(repo), encoding="utf-8")
    (repo / "llms.txt").write_text(render_llms_txt(repo), encoding="utf-8")
    (repo / "_sitemap.xml").write_text(render_sitemap(repo, base_url), encoding="utf-8")
    for theme_slug, theme_dir_name in THEMES_DIR_MAP.items():
        theme_path = repo / "essays" / theme_dir_name
        if theme_path.is_dir():
            (theme_path / "README.md").write_text(
                render_theme_readme(repo, theme_slug), encoding="utf-8"
            )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build catalog.md / llms.txt / theme READMEs / sitemap")
    p.add_argument("--repo-root", default=".")
    p.add_argument("--base-url", default="https://examples.flashalpha.com")
    p.add_argument("--check", action="store_true",
                   help="Build into a temp dir and diff against current; fail on drift.")
    args = p.parse_args(argv)

    if args.check:
        import tempfile, shutil, filecmp
        with tempfile.TemporaryDirectory() as td:
            tmp_root = Path(td) / "repo"
            shutil.copytree(args.repo_root, tmp_root)
            build_catalog(tmp_root, args.base_url)
            # Diff: catalog.md, llms.txt, _sitemap.xml
            for f in ["catalog.md", "llms.txt", "_sitemap.xml"]:
                src = Path(args.repo_root) / f
                dst = tmp_root / f
                if not src.exists() or not filecmp.cmp(dst, src, shallow=False):
                    print(f"DRIFT: {f} would change. Run `fa-build-catalog` and commit.", file=sys.stderr)
                    return 1
        print("OK — no catalog drift")
        return 0

    build_catalog(Path(args.repo_root), args.base_url)
    print("Catalog built.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
