import json
from pathlib import Path
from unittest.mock import patch

import pytest

from flashalpha_examples_tools.capture_golden import (
    capture_golden, write_golden_json,
)
from flashalpha_examples_tools._lean_output import BacktestResult


def test_write_golden_json_round_trips(tmp_path: Path):
    out = tmp_path / "golden.json"
    r = BacktestResult(final_equity=100_000.0, initial_equity=100_000.0,
                       total_trades=0, sharpe=0.0, sortino=0.0,
                       max_drawdown=-0.0, equity_curve=[])
    write_golden_json(r, out)
    data = json.loads(out.read_text())
    assert data["final_equity"] == 100_000.0
    assert data["total_trades"] == 0


def test_capture_golden_invokes_lean(tmp_path: Path, monkeypatch):
    """capture_golden() shells out to `lean backtest`; verify the call shape."""
    essay = tmp_path / "01-sample"
    (essay / "python").mkdir(parents=True)
    (essay / "results").mkdir()
    # Stub a fake backtest output
    fake_output = essay / "_backtest"
    fake_output.mkdir()
    (fake_output / "1234-backtest").mkdir()
    (fake_output / "1234-backtest" / "BacktestResult.json").write_text(
        '{"Statistics": {"Total Trades": "5", "Sharpe Ratio": "0.5", "Sortino Ratio": "0.7", "Drawdown": "1%"}, '
        '"AlgorithmConfiguration": {"InitialCash": "100000"}, "Charts": {}}'
    )

    calls = []
    def fake_run(cmd, **kw):
        calls.append(cmd)
        class R: returncode = 0
        return R()

    monkeypatch.setattr("subprocess.run", fake_run)

    # Patch tempfile.TemporaryDirectory to use our fake_output as the lean output dir
    import contextlib
    @contextlib.contextmanager
    def fake_tempdir():
        yield str(fake_output)
    monkeypatch.setattr("tempfile.TemporaryDirectory", fake_tempdir)

    # Also patch render functions to be no-ops to avoid matplotlib requirements
    monkeypatch.setattr("flashalpha_examples_tools.capture_golden.render_equity_curve_png", lambda *a, **kw: None)
    monkeypatch.setattr("flashalpha_examples_tools.capture_golden.render_monthly_returns_csv", lambda *a, **kw: None)
    monkeypatch.setattr("flashalpha_examples_tools.capture_golden.render_trade_stats_json", lambda *a, **kw: None)

    capture_golden(essay, "python")
    assert any("lean" in str(c) for c in calls)
    assert (essay / "python" / "golden.json").exists()
