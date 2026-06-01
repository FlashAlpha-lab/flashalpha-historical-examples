import json
from pathlib import Path
from unittest.mock import patch

import pytest

from flashalpha_examples_tools.smoke_algo import (
    write_smoke_golden, evaluate_plausibility, PlausibilityError,
)
from flashalpha_examples_tools._lean_output import BacktestResult


def _bt(**kw):
    base = dict(final_equity=100_500.0, initial_equity=100_000.0,
                total_trades=5, sharpe=0.3, sortino=0.45,
                max_drawdown=-0.015, equity_curve=[])
    base.update(kw)
    return BacktestResult(**base)


def test_write_smoke_golden_includes_tier(tmp_path: Path):
    out = tmp_path / "smoke-golden.json"
    write_smoke_golden(_bt(), out)
    data = json.loads(out.read_text())
    assert data["tier"] == "smoke"
    assert data["final_equity"] == 100_500.0
    assert data["total_trades"] == 5


def test_plausibility_passes_for_sensible_run():
    evaluate_plausibility(_bt())  # no exception


def test_plausibility_fails_when_equity_explodes():
    with pytest.raises(PlausibilityError, match="final_equity"):
        evaluate_plausibility(_bt(final_equity=10_000_000.0))


def test_plausibility_fails_when_equity_zeroed():
    with pytest.raises(PlausibilityError, match="final_equity"):
        evaluate_plausibility(_bt(final_equity=10.0))


def test_plausibility_fails_when_no_trades_and_no_position():
    with pytest.raises(PlausibilityError, match="trades"):
        evaluate_plausibility(_bt(total_trades=0))
