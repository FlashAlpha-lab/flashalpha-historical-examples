from unittest.mock import MagicMock
import pytest

from flashalpha_examples_tools.data_smoke import (
    smoke_test_essay, DataSmokeReport,
)


@pytest.fixture
def fake_bridge_client():
    """A fake bridge client that returns a populated dict per endpoint."""
    client = MagicMock()
    client.fetch_json.return_value = {"symbol": "SPY", "underlying_price": 540.0, "net_gex": 1e9, "as_of": "2024-06-14T15:30:00"}
    return client


def test_smoke_passes_when_all_endpoints_return_data(fake_bridge_client):
    fm = {"slug": "test", "data_endpoints": ["exposure/gex"], "tickers": ["SPY"]}
    report = smoke_test_essay(fm, fake_bridge_client, dates=["2024-06-14T15:30:00"])
    assert isinstance(report, DataSmokeReport)
    assert report.passed
    assert report.endpoint_results["exposure/gex"]["calls"] == 1


def test_smoke_fails_when_endpoint_returns_empty():
    client = MagicMock()
    client.fetch_json.return_value = {}
    fm = {"slug": "test", "data_endpoints": ["exposure/gex"], "tickers": ["SPY"]}
    report = smoke_test_essay(fm, client, dates=["2024-06-14T15:30:00"])
    assert not report.passed
    assert "empty" in report.failures[0].lower()


def test_smoke_handles_exception_gracefully():
    client = MagicMock()
    client.fetch_json.side_effect = RuntimeError("connection refused")
    fm = {"slug": "test", "data_endpoints": ["exposure/gex"], "tickers": ["SPY"]}
    report = smoke_test_essay(fm, client, dates=["2024-06-14T15:30:00"])
    assert not report.passed
    assert "RuntimeError" in report.failures[0] or "connection refused" in report.failures[0]
