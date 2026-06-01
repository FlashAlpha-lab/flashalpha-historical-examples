from pathlib import Path
from unittest.mock import patch

import pytest

from flashalpha_examples_tools.smoke_all import smoke_all_essays, SmokeRollup


def test_smoke_all_visits_every_essay(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "essays" / "a-dealer-positioning" / "01-x" / "validation").mkdir(parents=True)
    (repo / "essays" / "a-dealer-positioning" / "02-y" / "validation").mkdir(parents=True)

    calls = []
    def fake_run(d):
        calls.append(d.name)
        from flashalpha_examples_tools._lean_output import BacktestResult
        return BacktestResult(final_equity=101_000, initial_equity=100_000,
                              total_trades=3, sharpe=0.2, sortino=0.3,
                              max_drawdown=-0.01, equity_curve=[])

    with patch("flashalpha_examples_tools.smoke_all.run_smoke", side_effect=fake_run):
        rollup = smoke_all_essays(repo)
    assert isinstance(rollup, SmokeRollup)
    assert set(calls) == {"01-x", "02-y"}
    assert rollup.passed == 2
    assert rollup.failed == 0
