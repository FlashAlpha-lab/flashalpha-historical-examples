import json
from pathlib import Path

import pytest

from flashalpha_examples_tools._lean_output import (
    BacktestResult, parse_backtest_result,
)


FIXTURE = Path(__file__).parent / "fixtures" / "sample-backtest-result.json"


@pytest.fixture
def fixture_path() -> Path:
    return FIXTURE


def test_parse_extracts_headline_stats(fixture_path: Path):
    r = parse_backtest_result(fixture_path)
    assert isinstance(r, BacktestResult)
    assert r.total_trades == 84
    assert r.sharpe == pytest.approx(0.72, abs=0.01)
    assert r.sortino == pytest.approx(1.05, abs=0.01)
    assert r.max_drawdown == pytest.approx(-0.045, abs=0.001)


def test_parse_extracts_final_equity(fixture_path: Path):
    r = parse_backtest_result(fixture_path)
    assert r.final_equity == pytest.approx(102417.50, rel=1e-4)
    assert r.initial_equity == pytest.approx(100000.0, rel=1e-4)


def test_parse_extracts_equity_curve(fixture_path: Path):
    r = parse_backtest_result(fixture_path)
    assert len(r.equity_curve) == 3
    assert r.equity_curve[0] == (1709251200, 100000.00)
    assert r.equity_curve[-1] == (1727654400, 102417.50)


def test_parse_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        parse_backtest_result(Path("/nonexistent.json"))
