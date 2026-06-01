from pathlib import Path

import pytest

from flashalpha_examples_tools.build_catalog import (
    build_catalog, render_catalog_md, render_llms_txt,
    render_theme_readme, render_sitemap,
)
from flashalpha_examples_tools._schema import THEMES_DIR_MAP


def _make_essay(repo: Path, theme_slug: str, n: int, title: str, status="draft", **extras):
    import yaml
    theme_dir_name = THEMES_DIR_MAP[theme_slug]
    d = repo / "essays" / theme_dir_name / f"{n:02d}-{title.lower().replace(' ', '-')}"
    d.mkdir(parents=True)
    fm = {
        "title": title, "slug": title.lower().replace(" ", "-"),
        "theme": theme_slug, "difficulty": "beginner", "status": status,
        "summary": f"Summary of {title}",
        "bridge_bars": ["FlashAlphaGexBar"], "data_endpoints": ["exposure/gex"],
        "tickers": ["SPY"], "backtest_window": {"start": "2024-06-01", "end": "2024-06-10"},
        "expected_runtime": {"python": "1m", "csharp": "1m"},
        "golden": {"python": {"final_equity": 100, "total_trades": 1, "sharpe": 0.0, "max_drawdown": -0.0},
                   "csharp": {"final_equity": 100, "total_trades": 1, "sharpe": 0.0, "max_drawdown": -0.0}} if status == "stable" else {"python": {}, "csharp": {}},
        "keywords": [title.lower()], "last_updated": "2026-06-01",
        **extras,
    }
    (d / "meta.yaml").write_text(yaml.safe_dump(fm))
    (d / "README.md").write_text(f"---\n{yaml.safe_dump(fm)}---\n# {title}\n")
    return d


@pytest.fixture
def mock_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    _make_essay(repo, "dealer-positioning", 1, "Gamma Scalping", status="stable")
    _make_essay(repo, "dealer-positioning", 2, "GEX Regime Following")
    _make_essay(repo, "vrp-volatility", 9, "VRP Harvest")
    return repo


def test_render_llms_txt_lists_all_essays(mock_repo: Path):
    text = render_llms_txt(mock_repo)
    assert "Gamma Scalping" in text
    assert "GEX Regime Following" in text
    assert "VRP Harvest" in text
    assert "## Essays" in text


def test_render_catalog_md_groups_by_theme(mock_repo: Path):
    text = render_catalog_md(mock_repo)
    # Themed sections present
    assert "Dealer positioning" in text or "dealer-positioning" in text
    assert "VRP" in text or "vrp-volatility" in text
    assert "Gamma Scalping" in text


def test_render_theme_readme(mock_repo: Path):
    text = render_theme_readme(mock_repo, "dealer-positioning")
    assert "Gamma Scalping" in text
    assert "GEX Regime Following" in text


def test_render_sitemap_includes_essay_urls(mock_repo: Path):
    xml = render_sitemap(mock_repo, base_url="https://examples.flashalpha.com")
    assert "<urlset" in xml
    assert "gamma-scalping" in xml
    assert "vrp-harvest" in xml


def test_build_catalog_writes_all_outputs(mock_repo: Path):
    build_catalog(mock_repo)
    assert (mock_repo / "catalog.md").exists()
    assert (mock_repo / "llms.txt").exists()
    assert (mock_repo / "essays" / "a-dealer-positioning" / "README.md").exists()
    assert (mock_repo / "_sitemap.xml").exists()
