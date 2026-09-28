---
title: "Fixed-$5 two-sided turnover on MEXC AXM/USDT"
description: "Primary MEXC aggregate-trade data show AXM/USDT concentrating about 40% of observed notional in repeated ~$5 timestamp-level events with a nearly flat taker-buy/taker-sell split. A same-rule XL1/USDT control records no $5 events in the committed sample."
date: 2026-09-28
entities:
  - MEXC
  - AXM
---

## Summary

AXM/USDT on MEXC shows a persistent fixed-notional pattern that is consistent with wash-like automated turnover and merits market-surveillance attention.

Across the committed sample—2026-09-27 plus the first six UTC hours of 2026-09-28—**484 of 766 AXM timestamp-level events (63.2%)** total between **$4.99 and $5.01**. Those events carry **$2419.99**, or **39.7%** of all observed AXM notional. Their aggressor-side split is almost flat: **244 taker-buy events versus 240 taker-sell events**. The absolute buy/sell notional imbalance is only **$20.00**, or **0.83% of gross target turnover**.

A same-venue comparison market, XL1/USDT, has similar observed activity on 2026-09-27 (612 aggregate trades and about $4.67k notional versus AXM’s 581 trades and about $4.64k). Applying the **same $5.00 +/- $0.01 event rule** to XL1 produces **zero matching events** in either committed window. This comparison shows that the specific AXM pattern is not reproduced by this XL1 sample; it does not by itself establish a venue-wide or low-liquidity baseline.

Public aggregate trades do not expose beneficial ownership or self-trade identifiers. The result is therefore framed as a **wash-like surveillance signal, not proof of wash trading**.

## Repeated fixed-notional events

Records sharing the same millisecond timestamp are grouped into one event before notional is measured. This avoids treating a single aggressive order that fills against several resting orders at one timestamp as several independent event decisions.

The target rule is deliberately simple and identical for target and control: event notional is between **$4.99 and $5.01** inclusive.

On 2026-09-27, **366 of 558 AXM events (65.6%)** match the rule and carry **39.4%** of observed AXM notional. In the first six UTC hours of 2026-09-28, **118 of 208 events (56.7%)** match and carry **40.6%** of observed notional.

{{< figure src="axm-fixed-notional.svg" alt="AXM versus XL1 share of timestamp events near five USDT" caption="The identical $5.00 +/- $0.01 rule is applied to both markets. AXM repeatedly hits the target window; XL1 has no matching events in either committed window." >}}

| Window | Market | Aggregate trades | Timestamp events | ~$5 events | Event share | Notional share |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2026-09-27 | AXM/USDT | 581 | 558 | 366 | 65.6% | 39.4% |
| 2026-09-27 | XL1/USDT | 612 | 593 | 0 | 0.0% | 0.0% |
| 2026-09-28 00:00-05:59 UTC | AXM/USDT | 221 | 208 | 118 | 56.7% | 40.6% |
| 2026-09-28 00:00-05:59 UTC | XL1/USDT | 170 | 166 | 0 | 0.0% | 0.0% |

## Two-sided turnover

Across both windows there are **244 taker-buy events and 240 taker-sell events** in the ~$5 bucket.

{{< figure src="axm-side-balance.svg" alt="AXM fixed-notional event taker-buy and taker-sell counts" caption="The repeated ~$5 AXM events are nearly balanced by aggressor side across the committed sample." >}}

| Window | ~$5 events | Taker buys | Taker sells | Target turnover | Absolute side imbalance |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026-09-27 | 366 | 184 | 182 | $1,829.99 | $10.00 |
| 2026-09-28 00:00-05:59 UTC | 118 | 60 | 58 | $590.00 | $10.00 |
| **Combined** | **484** | **244** | **240** | **$2,419.99** | **$20.00 (0.83%)** |

This combination—a dominant fixed quote amount, persistence across a date boundary, and a near-flat aggressor-side split—is consistent with automated turnover designed to generate activity with little directional imbalance. It is stronger as a surveillance signal than fixed-size recurrence alone.

## Minimum-order check

The pattern is not simply the venue’s minimum market-order amount. The committed MEXC symbol-rule snapshot reports a **1 USDT** minimum market-order quote amount for both AXM/USDT and XL1/USDT. The repeated AXM value is approximately **5 USDT**, five times that minimum.

The snapshot and source URLs are preserved in data/market_rules.csv.

## What the public tape cannot prove

A wash-trading finding requires more than a repetitive tape. Public MEXC aggregate trades provide price, quantity, timestamp and buyer-maker side, but they do not identify accounts, beneficial owners or self-trade-prevention events.

A benign fixed-notional execution algorithm could also generate repeated $5 events. To escalate this surveillance signal to a manipulation attribution, stronger evidence would be needed: common ownership of both sides, repeated self-matches, negligible risk transfer between related accounts, or order-book/account data tying the turnover to artificial volume creation.

The conclusion here is therefore intentionally narrower: **AXM/USDT exhibits persistent, highly concentrated, nearly two-sided fixed-$5 turnover that is consistent with wash-like automation and is absent from the same-rule XL1 control sample.**

## Data and reproducibility

- data/raw_aggtrades.csv: **1,584** raw MEXC aggregate-trade records for AXM/USDT and XL1/USDT.
- data/summary.csv: per-window metrics using the identical fixed-notional rule.
- data/axm_fixed_notional_events.csv: all AXM events within the $5.00 +/- $0.01 target.
- data/market_rules.csv: MEXC symbol-rule snapshots and source URLs.
- scripts/analyze.py: dependency-free Python that rebuilds the derived CSVs and SVG figures from the committed raw sample.

Run:

```bash
python3 content/research/market-health/posts/2026-09-28-mexc/scripts/analyze.py
```

The raw sample was collected from MEXC’s public, key-less aggregate-trades endpoint using non-overlapping hourly windows:

```text
GET https://api.mexc.com/api/v3/aggTrades
```

The endpoint returned blank aggregate/trade-ID fields in the captured rows. **No aggregate-ID deduplication is claimed or performed.** The committed sample contains no exact duplicate rows under the available fields. Analysis uses every committed row and groups rows sharing the same market, period and millisecond timestamp into timestamp-level events.

MEXC endpoint documentation: [Compressed/Aggregate Trades List](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints/compressedaggregate-trades-list). Symbol-rule semantics: [Exchange Information](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints/exchange-information).

## Scope

The sample is short and exploratory. The $5 target was identified from the observed data and should be treated as an effect description rather than a pre-registered hypothesis. The XL1 comparison controls one similar-activity market, not every MEXC or low-liquidity pair. These limitations are why the article reports a surveillance signal rather than a definitive allegation of wash trading.
