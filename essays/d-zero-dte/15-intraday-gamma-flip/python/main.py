"""Algorithm for 0DTE intraday gamma flip.

This is a DRAFT stub. Replace OnData/Initialize with real logic before flipping to stable.
"""

from QuantConnect.Algorithm import QCAlgorithm
from QuantConnect import Resolution, SecurityType, Market
from flashalpha_quantconnect import GexBar, add_flashalpha_gex


class Algorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2024, 3, 1)
        self.SetEndDate(2024, 9, 30)
        self.SetCash(100_000)
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.gex = add_flashalpha_gex(self, "SPY").Symbol

    def OnData(self, slice):
        raise NotImplementedError(
            "Draft — see README.md for the proposed algorithm. "
            "Implement before flipping status to stable."
        )
