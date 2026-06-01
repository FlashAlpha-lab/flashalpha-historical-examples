import json
from pathlib import Path

import pytest

from flashalpha_examples_tools.verify_essay import (
    GoldenMismatch, verify_against_golden,
)
from flashalpha_examples_tools._lean_output import BacktestResult


def _golden():
    return {"final_equity": 102417.50, "total_trades": 84, "sharpe": 0.72, "max_drawdown": -0.045}


def _result(**overrides):
    base = dict(final_equity=102417.50, initial_equity=100000.0, total_trades=84,
                sharpe=0.72, sortino=1.05, max_drawdown=-0.045)
    base.update(overrides)
    return BacktestResult(**base, equity_curve=[])


def test_exact_match_passes():
    verify_against_golden(_result(), _golden())  # no exception


def test_equity_drift_within_tolerance_passes():
    verify_against_golden(_result(final_equity=102417.50 * 1.00005), _golden())


def test_equity_drift_outside_tolerance_fails():
    with pytest.raises(GoldenMismatch, match="final_equity"):
        verify_against_golden(_result(final_equity=102417.50 * 1.01), _golden())


def test_trade_count_exact_match_required():
    with pytest.raises(GoldenMismatch, match="total_trades"):
        verify_against_golden(_result(total_trades=83), _golden())


def test_sharpe_drift_within_tolerance_passes():
    verify_against_golden(_result(sharpe=0.72 + 0.005), _golden())


def test_sharpe_drift_outside_tolerance_fails():
    with pytest.raises(GoldenMismatch, match="sharpe"):
        verify_against_golden(_result(sharpe=0.72 + 0.05), _golden())
