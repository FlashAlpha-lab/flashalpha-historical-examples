import pytest

from flashalpha_examples_tools.check_bridge_compat import (
    BridgeMismatch, get_published_bars, get_published_endpoints,
    check_essay_compat,
)


def test_get_published_bars_returns_known_set():
    bars = get_published_bars()
    assert "FlashAlphaGexBar" in bars
    assert "FlashAlphaSurfaceBar" in bars
    assert "FlashAlphaZeroDteBar" in bars
    # 17 bars in 0.1.1
    assert len(bars) >= 17


def test_get_published_endpoints_returns_known_set():
    eps = get_published_endpoints()
    assert "exposure/gex" in eps
    assert "exposure/zero-dte" in eps
    assert "max-pain" in eps
    # 17 endpoints
    assert len(eps) >= 17


def test_essay_with_known_bars_passes():
    fm = {"bridge_bars": ["FlashAlphaGexBar"], "data_endpoints": ["exposure/gex"]}
    check_essay_compat("test", fm)  # no exception


def test_essay_with_unknown_bar_fails():
    fm = {"bridge_bars": ["FlashAlphaFakeBar"], "data_endpoints": []}
    with pytest.raises(BridgeMismatch, match="FlashAlphaFakeBar"):
        check_essay_compat("test", fm)


def test_essay_with_unknown_endpoint_fails():
    fm = {"bridge_bars": [], "data_endpoints": ["exposure/nope"]}
    with pytest.raises(BridgeMismatch, match="exposure/nope"):
        check_essay_compat("test", fm)
