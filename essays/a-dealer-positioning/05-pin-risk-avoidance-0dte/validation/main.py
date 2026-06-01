"""SMOKE algorithm for Pin-risk avoidance (0DTE).

Tier 2 feasibility check, not the real strategy. 20-30 lines, minimal logic.
Goal: prove the data flows + the basic gating produces sensible numbers
over a short window.

Real algorithm lives at ../python/main.py — promoted from this smoke when
the essay flips to status: stable.
"""

from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect import Resolution, SecurityType, Market
from flashalpha_quantconnect import GexBar, add_flashalpha_gex


class Algorithm(QCAlgorithm):
    def Initialize(self):
        # 30-day window — fast, enough to fire gating logic multiple times
        self.SetStartDate(2024, 6, 3)
        self.SetEndDate(2024, 7, 5)
        self.SetCash(100_000)
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.gex_symbol = add_flashalpha_gex(self, "SPY").Symbol

    def OnData(self, slice):
        # Replace with the smoke version of Pin-risk avoidance (0DTE)'s gating logic.
        # Keep it minimal — this is a feasibility check, not a real strategy.
        if self.gex_symbol not in slice:
            return
        gex = slice[self.gex_symbol]
        if not isinstance(gex, GexBar):
            return
        if gex.NetGexLabel == "positive":
            self.SetHoldings(self.spy, 1.0)
        else:
            self.Liquidate(self.spy)
