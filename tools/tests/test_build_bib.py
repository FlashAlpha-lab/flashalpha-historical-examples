from pathlib import Path

import pytest

from flashalpha_examples_tools.build_bib import (
    parse_references, render_bibliography_md, render_bibliography_bib,
)


def test_parse_references_extracts_lines(tmp_path: Path):
    p = tmp_path / "references.md"
    p.write_text(
        "# References\n\n"
        "- Taleb, N. (1997). Dynamic Hedging. Wiley.\n"
        "- Sinclair, E. (2013). Volatility Trading. Wiley.\n"
        "- [Spotgamma — GEX explained](https://spotgamma.com/gex)\n",
        encoding="utf-8",
    )
    refs = parse_references(p)
    assert len(refs) == 3
    assert any("Taleb" in r["raw"] for r in refs)
    assert any(r.get("url") == "https://spotgamma.com/gex" for r in refs)


def test_render_bibliography_md_dedupes(tmp_path: Path):
    refs = [
        {"raw": "Taleb, N. (1997). Dynamic Hedging.", "url": None},
        {"raw": "Taleb, N. (1997). Dynamic Hedging.", "url": None},  # dupe
        {"raw": "Sinclair, E. (2013). Volatility Trading.", "url": None},
    ]
    md = render_bibliography_md(refs)
    assert md.count("Taleb") == 1
    assert "Sinclair" in md


def test_render_bibliography_bib_yields_bibtex(tmp_path: Path):
    refs = [
        {"raw": "Taleb, N. (1997). Dynamic Hedging.", "url": None},
        {"raw": "Spotgamma — GEX explained", "url": "https://spotgamma.com/gex"},
    ]
    bib = render_bibliography_bib(refs)
    assert "@misc{" in bib or "@book{" in bib
    assert "Taleb" in bib
