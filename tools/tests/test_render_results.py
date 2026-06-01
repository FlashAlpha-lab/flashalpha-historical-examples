import json
from pathlib import Path

import pytest

from flashalpha_examples_tools.render_results import (
    render_equity_curve_png, render_monthly_returns_csv,
    render_trade_stats_json,
)
from flashalpha_examples_tools._lean_output import BacktestResult


@pytest.fixture
def sample_result() -> BacktestResult:
    # 3 months of fake daily equity for monthly-returns + equity-curve
    import time
    start_ts = int(time.mktime((2024, 6, 1, 0, 0, 0, 0, 0, 0)))
    curve = [(start_ts + i * 86400, 100000.0 + i * 50.0) for i in range(90)]
    return BacktestResult(
        final_equity=curve[-1][1], initial_equity=100000.0,
        total_trades=12, sharpe=0.72, sortino=1.05, max_drawdown=-0.045,
        equity_curve=curve,
    )


def test_render_equity_curve_writes_png(tmp_path: Path, sample_result):
    out = tmp_path / "eq.png"
    render_equity_curve_png(sample_result, out, title="Test")
    assert out.exists()
    assert out.stat().st_size > 0


def test_render_monthly_returns_writes_csv(tmp_path: Path, sample_result):
    out = tmp_path / "monthly.csv"
    render_monthly_returns_csv(sample_result, out)
    text = out.read_text()
    assert "month" in text.lower() or "Month" in text
    assert "2024-06" in text or "2024-07" in text


def test_render_trade_stats_json(tmp_path: Path, sample_result):
    out = tmp_path / "stats.json"
    render_trade_stats_json(sample_result, out)
    data = json.loads(out.read_text())
    assert data["total_trades"] == 12
    assert data["sharpe"] == pytest.approx(0.72)
    assert "final_equity" in data
