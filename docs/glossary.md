# Glossary

Plain-English definitions of every term used across this repo's essays. Each
term links, where relevant, to the matching bar in the
[`flashalpha-quantconnect` bridge's data-types reference](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md).

Organized by topic: greeks → exposures → volatility → strikes/expiries →
dealer mechanics → performance metrics → LEAN concepts.

---

## Options greeks

The partial derivatives that describe how an option's price responds to its
inputs. The first three (delta, gamma, vega) drive most strategies in this
repo; the rest matter for finer-grained hedging.

### Gamma

Rate of change of **delta** with respect to the underlying price. Long gamma
positions become more positively-deltaed as the underlying rises and less
deltaed as it falls — the position "automatically buys low and sells high"
when delta-hedged. Short gamma is the opposite: forced to chase moves.

See [GexBar in the bridge](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphagexbar)
for the aggregated dealer-gamma exposure across the option chain.

### Delta

Rate of change of an option's price with respect to the underlying price.
Roughly the probability the option finishes in-the-money. A delta of 0.5
means a $1 move in the underlying moves the option price ~$0.50. Used to
size offsetting positions in delta-hedged strategies.

See [DexBar in the bridge](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphadexbar)
for aggregated delta exposure.

### Vega

Rate of change of an option's price with respect to implied volatility.
Long vega profits when implied vol rises; short vega profits when it
falls. Central to volatility-risk-premium strategies.

See [VexBar in the bridge](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphavexbar).

### Theta

Rate of price decay with respect to time. Options lose value as expiry
approaches, all else equal. Long options pay theta; short options collect
it. The trade-off short-volatility sellers run.

### Rho

Rate of change with respect to the risk-free rate. Mostly negligible at
short maturities; matters for LEAPs and long-dated structures.

### Charm

Rate of change of delta with respect to time. Also called "delta decay".
Around expiry, charm accelerates — a small time-step moves delta a lot,
which forces dealer hedging into pin-risk territory.

See [CharmBar / CHEX in the bridge](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphachexbar).

### Vanna

Rate of change of delta with respect to implied volatility. When IV moves,
dealers' delta hedge shifts even without an underlying move. Critical
during vol-of-vol events (FOMC, CPI, earnings).

See [VannaBar / VEX in the bridge](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphavexbar).

### Vomma

Rate of change of vega with respect to implied volatility. Long vomma
profits from convexity in vol — gains accelerate as IV rises. Niche
outside of variance-swap and dispersion books.

---

## Exposures

Aggregations of greeks across the entire option chain for a given
underlying, weighted by open interest. These are the bridge's headline
data products.

### GEX — gamma exposure

Total dollar gamma dealers are estimated to hold across all listed strikes
and expiries for an underlying. Positive GEX means dealers are long gamma
overall and will lean against price moves (suppressing realized vol).
Negative GEX means dealers are short gamma and will chase moves
(amplifying realized vol).

See [`exposure/gex` endpoint](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphagexbar)
and the **gamma flip** entry below.

### DEX — delta exposure

Total dollar delta dealers are estimated to hold. Tracks directional
positioning. Useful as a contrarian signal at extremes.

See [`exposure/dex` endpoint](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphadexbar).

### VEX — vega exposure

Total dollar vega dealers are estimated to hold. Tracks how much P&L
dealers gain or lose for a 1-point IV move. Pairs with VRP signals.

See [`exposure/vex` endpoint](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphavexbar).

### CHEX — charm exposure

Total dollar charm exposure dealers carry. Spikes near OPEX as a large
fraction of the chain's notional time-decays into hedging pressure on
expiry day. Drives 0DTE pin and gap mechanics.

See [`exposure/chex` endpoint](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphachexbar).

---

## Volatility

How much the underlying actually moves vs how much the market thinks it
will move.

### IV — implied volatility

The volatility number that, fed into Black-Scholes, recovers the option's
market price. Forward-looking; the market's consensus expectation of how
much the underlying will move between now and expiry.

See [SurfaceBar](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphasurfacebar)
for the full IV surface (strikes × expiries) and
[VolatilityBar](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphavolatilitybar)
for ATM IV term structure.

### RV — realized volatility

How much the underlying actually moved over a past window, annualized.
Backward-looking. The denominator of the volatility-risk-premium ratio.

### VRP — volatility risk premium

`IV - RV`, or sometimes `IV / RV`. The compensation option sellers demand
for warehousing variance risk. Positive on average across most underlyings
most of the time; collapses or inverts in regimes where the market
underprices upcoming realized vol.

See [`vrp` endpoint and VrpBar](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphavrpbar).

### IV rank

Where today's IV sits in its 52-week (or other window) range, as a
percentile. IV rank of 100 means today's IV is the highest in the window;
0 the lowest. Used as a regime filter for short-volatility strategies.

### Term structure

The shape of IV across expiries for a given underlying. In contango
(normal), back-month IV > front-month IV. In backwardation, front-month
IV > back-month IV — usually a stress signal. Calendar-spread strategies
trade the slope.

See [VolatilityBar](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphavolatilitybar).

---

## Strikes and expiries

The discrete grid options trade on.

### 0DTE

Zero-days-to-expiration. Options expiring on the trading session they're
quoted in. SPY, QQQ, and the major index ETFs list 0DTE every weekday;
this is a structural source of intraday gamma + charm flows.

See the **d-zero-dte** theme essays and
[ZeroDteBar](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphazerodte).

### ATM — at-the-money

Strike approximately equal to the current underlying price. Highest
absolute gamma per contract; the focal point of delta-hedging flows.

### OTM — out-of-the-money

Call strike above the underlying (or put strike below). Lower delta,
cheaper, used for directional bets and wings of spreads.

### ITM — in-the-money

Call strike below the underlying (or put strike above). High delta,
behaves close to a stock position.

### Max pain

The strike at which the total open-interest dollar value would be
minimized if the underlying pinned there at expiry. Often (but not
always) coincides with where the underlying actually closes on OPEX,
which is why max-pain reversion is a tradeable signal.

See [MaxPainBar](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md#flashalphamaxpainbar).

---

## Dealer mechanics

How the marketmakers and hedgers who are the counterparty to most option
volume affect realized price behaviour.

### Dealer hedging

Marketmakers warehouse the residual greeks of every option they sell. To
keep their book delta-neutral they trade the underlying continuously.
Most observable structural flows in modern equity markets are echoes of
dealer hedging.

### Pin risk

The tendency of an underlying to "pin" to a high-open-interest strike
into expiry, because dealer delta-hedging at that strike creates a
self-stabilizing flow loop. Most pronounced on monthly OPEX in SPY/SPX.

### Gamma flip

The underlying price at which aggregate dealer gamma crosses zero. Above
the flip, dealers are long gamma and dampen moves; below it, they're
short gamma and amplify them. A single number derived from the GEX
profile.

### Regime (positive / negative)

Shorthand for which side of the gamma flip the underlying sits in.
"Positive regime" = positive GEX = vol-suppressing. "Negative regime" =
negative GEX = vol-amplifying. Many of this repo's essays gate trades on
the regime.

---

## Performance metrics

The numbers a `BacktestResult.json` prints. These show up in every essay's
`golden:` frontmatter block and `summary.txt`.

### Sharpe ratio

`(annualized return - risk-free rate) / annualized volatility`. Risk-
adjusted return assuming returns are normal. Most-cited single-number
benchmark; flawed for fat-tailed strategies.

### Sortino ratio

Same idea as Sharpe but uses downside deviation in the denominator
instead of total deviation. Rewards strategies whose volatility is
mostly upside.

### Max drawdown

The largest peak-to-trough decline in equity over the backtest window,
as a percentage. Captures pain. Critical for sizing leverage.

### Hit rate

Fraction of trades that closed profitable. Doesn't say anything about
P&L distribution — a 90% hit rate with one catastrophic loss can still
lose money. Always paired with average win / average loss for context.

---

## LEAN concepts

The QuantConnect framework primitives every essay's algorithm uses.

### QCAlgorithm

The base class every LEAN algorithm inherits from. Provides the trading
API (`SetCash`, `AddEquity`, `Liquidate`, `MarketOrder`), event hooks
(`Initialize`, `OnData`), and access to the data slice.

### Custom data

Subclasses of `PythonData` / `BaseData` that pull non-default data into a
LEAN backtest. The `flashalpha-quantconnect` bridge ships custom-data
classes (`FlashAlphaGexBar`, etc.) wired to the FlashAlpha REST endpoints.
Each becomes a regular slice subscription from the algorithm's
perspective.

### Slice

The bag of data LEAN delivers each timestep. Contains every subscription
the algorithm holds — bars, quotes, custom data — keyed by symbol.
Passed to `OnData(slice)`.

### OnData

The per-timestep callback every algorithm implements. Fires every time
the slice updates (one bar boundary at a time during backtests). Where
trade decisions happen.

### AddData

Method called from `Initialize` to subscribe to a custom-data type. The
bridge essays call e.g. `self.add_data(FlashAlphaGexBar, "SPY", Resolution.Daily)`
in Python or `AddData<FlashAlphaGexBar>("SPY", Resolution.Daily)` in C#.

---

For the canonical list of every bar the bridge exposes and the FlashAlpha
endpoints behind them, see
[`flashalpha-quantconnect/docs/data-types.md`](https://github.com/FlashAlpha-lab/flashalpha-quantconnect/blob/main/docs/data-types.md).
