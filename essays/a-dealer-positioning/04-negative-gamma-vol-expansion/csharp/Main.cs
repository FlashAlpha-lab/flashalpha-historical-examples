using QuantConnect;
using QuantConnect.Algorithm;
using QuantConnect.Data;
using FlashAlpha.QuantConnect;
using FlashAlpha.QuantConnect.Data;

namespace FlashAlphaExamples;

public class Algorithm : QCAlgorithm
{
    private Symbol _spy = null!;
    private Symbol _gex = null!;

    public override void Initialize()
    {
        SetStartDate(2024, 3, 1);
        SetEndDate(2024, 9, 30);
        SetCash(100_000);
        _spy = AddEquity("SPY", Resolution.Daily).Symbol;
        _gex = this.AddFlashAlphaGex("SPY").Symbol;
    }

    public override void OnData(Slice slice)
    {
        throw new System.NotImplementedException(
            "Draft — see README.md. Implement before flipping status to stable.");
    }
}
