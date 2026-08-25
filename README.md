# flashalpha-historical-examples

> 21 backtest essays for options strategies on QuantConnect LEAN.
> Side-by-side C# and Python. Powered by [flashalpha-quantconnect](https://github.com/FlashAlpha-lab/flashalpha-quantconnect).

> **Point-in-time replay since 2017.** Backtest dealer positioning (GEX, VRP,
> vanna/charm, max pain) at any minute since 2017-01-03, then trade the same
> endpoints live. No look-ahead, no training-serving skew. The Historical API
> is an **Alpha tier** capability.

🚧 Pre-launch. Design spec at [`docs/superpowers/specs/2026-05-30-flashalpha-historical-examples-design.md`](docs/superpowers/specs/2026-05-30-flashalpha-historical-examples-design.md).

## Data provenance: `data_as_of`

Every FlashAlpha API response carries `data_as_of`, reporting when each upstream feed last
delivered to the node that answered, plus `endpoint_version` identifying the deployment
that produced it.

```json
"endpoint_version": "2026.08.25",
"data_as_of": {
  "node": "fa2",
  "equity_feed": "2026-08-25T18:48:58.204Z",
  "equity_options_feed": "2026-08-25T18:48:57.900Z",
  "index_feed": null,
  "index_options_feed": null,
  "futures_feed": null,
  "futures_options_feed": null,
  "flow_feed": "2026-08-25T18:48:55.100Z",
  "oi_feed": "2026-08-22T20:00:00.000Z",
  "macro_feed": "2026-08-25T18:45:00.000Z"
}
```

Spot and options are reported separately because they arrive over different pipes and fail
independently - an index chain can be current while the index level behind it is not, and
one timestamp cannot express that.

Read each feed against its **own cadence**, not against `as_of`. `oi_feed` at the previous
session's close is correct: settled open interest is published once per session, so on a
Monday the newest figure that exists is Friday's. An options feed an hour behind during
the regular session is not correct. A `null` means that node has not seen that feed, not
that it is broken.

The field evidences that a feed delivered recently. It does not assert that every contract
in a chain is equally current: an illiquid strike may not have quoted for hours while its
feed is healthy.

Historical replay responses carry a second object, `archive_as_of`, in the same shape: the
vintage of the archive rows actually replayed for the timestamp requested. Their
every feed in `data_as_of` is `null`, because a replay node reads the archive and consumes no live
feed.

`archive_as_of` is what makes an archive gap detectable. Request a moment with no row and
the query returns the most recent earlier row; nothing else in the response distinguishes
the two. Point-in-time work should read it and drop or flag observations whose inputs
precede the requested instant by more than the study tolerates.

Full reference: <https://flashalpha.com/docs/lab-api-overview#response-envelope>

## Get access

The Historical API requires the **Alpha tier ($1,499/mo)**: the only public source
of aggregate vanna/charm exposure and point-in-time replay since 2017.

Quant teams, prop desks, and vol funds:
**[flashalpha.com/for-quant-teams](https://flashalpha.com/for-quant-teams?utm_source=github&utm_medium=readme&utm_campaign=repo-flashalpha-historical-examples)**
