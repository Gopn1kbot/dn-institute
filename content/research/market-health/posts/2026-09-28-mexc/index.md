---
title: "Fixed-$5 turnover concentration on MEXC AXM/USDT"
description: "Committed MEXC aggregate-trade data show AXM/USDT concentrating about 40% of observed notional in repeated ~$5 timestamp-level events. A same-rule XL1/USDT control records no $5 events in the committed sample."
date: 2026-09-28
entities:
  - MEXC
  - AXM
---

## Summary

AXM/USDT on MEXC shows a persistent fixed-notional pattern that merits market-surveillance attention. Public trade data alone cannot determine whether the pattern comes from benign execution automation, market-making behavior, or artificial turnover.

Across the committed sample, **484 of 766 AXM timestamp-level events (63.2%)** total between **$4.99 and $5.01**. Those events carry **$2,419.99**, or **39.7%** of observed AXM notional. The same selected events contain **244 taker-buy events and 240 taker-sell events**. ([raw MEXC rows](data/raw_aggtrades.csv), [derived summary](data/summary.csv), [selected AXM events](data/axm_fixed_notional_events.csv))

A same-venue comparison market, XL1/USDT, has similar activity in the committed 2026-09-27 capture: **612 aggregate trades and about $4.67k notional**, versus AXM's **581 trades and about $4.64k**. Applying the **same $5.00 +/- $0.01 event rule** to XL1 produces **zero matching events** in both committed capture labels. This shows that the specific fixed-$5 concentration seen in AXM is not reproduced by this XL1 sample; it does not establish a venue-wide or low-liquidity baseline. ([raw MEXC rows](data/raw_aggtrades.csv), [derived summary](data/summary.csv))

The committed data do **not** prove wash trading. They do not expose beneficial ownership, account identity, self-trade identifiers, or intent.

## Repeated fixed-notional events

Records sharing the same millisecond timestamp are grouped into one event before notional is measured. This avoids treating multiple fills recorded at the same timestamp as independent event decisions. The target rule is deliberately simple and identical for target and control: event notional is between **$4.99 and $5.01** inclusive. ([analysis code](scripts/analyze.py))

In the rows labeled **2026-09-27**, **366 of 558 AXM events (65.6%)** match the rule and carry **39.4%** of observed AXM notional. In the **2026-09-28-partial** rows, **118 of 208 events (56.7%)** match and carry **40.6%** of observed notional. ([summary](data/summary.csv), [selected event rows](data/axm_fixed_notional_events.csv))

{{< figure src="axm-fixed-notional.svg" alt="AXM versus XL1 share of timestamp events near five USDT" caption="The identical $5.00 +/- $0.01 rule is applied to both markets. AXM repeatedly hits the target window; XL1 has no matching events in either committed capture." >}}

All table values below are generated from the committed [raw trade rows](data/raw_aggtrades.csv) by [scripts/analyze.py](scripts/analyze.py) and reproduced in [summary.csv](data/summary.csv).

| Capture label | Market | Aggregate trades | Timestamp events | ~$5 events | Event share | Notional share |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2026-09-27 captured rows | AXM/USDT | 581 | 558 | 366 | 65.6% | 39.4% |
| 2026-09-27 captured rows | XL1/USDT | 612 | 593 | 0 | 0.0% | 0.0% |
| 2026-09-28 partial capture | AXM/USDT | 221 | 208 | 118 | 56.7% | 40.6% |
| 2026-09-28 partial capture | XL1/USDT | 170 | 166 | 0 | 0.0% | 0.0% |

### Capture-window limitation

The raw file preserves trade timestamps but not the original request-boundary metadata. Therefore the period labels above are **capture labels, not claims of complete calendar-day coverage**. In the committed rows, the first/last returned timestamps are:

- AXM/USDT, 2026-09-27 label: **05:12:03Z to 23:59:05Z**.
- XL1/USDT, 2026-09-27 label: **05:02:05Z to 23:58:21Z**.
- AXM/USDT, 2026-09-28-partial label: **00:00:07Z to 04:57:21Z**.
- XL1/USDT, 2026-09-28-partial label: **00:01:14Z to 05:31:26Z**.

These are the first and last trades present in the [committed raw file](data/raw_aggtrades.csv); without preserved request boundaries, absence of rows outside those ranges should not be interpreted as verified absence of trading.

## Aggressor-side balance

Across both committed capture labels, the selected ~$5 AXM events contain **244 taker-buy events and 240 taker-sell events**. Their selected-event notional differs by about **$20**, or **0.83% of gross selected turnover**. ([selected AXM events](data/axm_fixed_notional_events.csv), [summary](data/summary.csv))

{{< figure src="axm-side-balance.svg" alt="AXM fixed-notional event taker-buy and taker-sell counts" caption="Descriptive aggressor-side counts within the already-selected ~$5 AXM events." >}}

| Capture label | ~$5 events | Taker buys | Taker sells | Selected turnover | Absolute side imbalance |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026-09-27 captured rows | 366 | 184 | 182 | $1,829.99 | $10.00 |
| 2026-09-28 partial capture | 118 | 60 | 58 | $590.00 | $10.00 |
| **Combined** | **484** | **244** | **240** | **$2,419.99** | **$20.00 (0.83%)** |

The near-even side count is **descriptive, not a separate manipulation test**. Because the selected events are already constrained to approximately $5, a four-event count difference mechanically implies a small notional difference. No claim about intent is based on this balance alone.

## What the public tape can and cannot show

The committed evidence supports a narrow anomaly statement: **AXM/USDT has a persistent concentration of timestamp-level events near a fixed $5 quote amount, while the same rule yields zero matches in the committed XL1 control sample.** ([raw rows](data/raw_aggtrades.csv), [summary](data/summary.csv))

A manipulation finding requires more than a repetitive public tape. The committed aggregate-trade rows contain price, quantity, timestamp and buyer-maker side, but they do not identify accounts, beneficial owners, self-trade-prevention events, or intent. A benign fixed-notional execution algorithm can also generate repeated $5 events.

Stronger evidence for an artificial-turnover attribution would require account/order-book information, repeated self-matches, common ownership of both sides, or another discriminating baseline that separates ordinary automated execution from activity generation.

## Data and reproducibility

- [data/raw_aggtrades.csv](data/raw_aggtrades.csv): **1,584** committed MEXC aggregate-trade rows for AXM/USDT and XL1/USDT.
- [data/summary.csv](data/summary.csv): per-capture metrics using the identical fixed-notional rule.
- [data/axm_fixed_notional_events.csv](data/axm_fixed_notional_events.csv): all AXM events within the $5.00 +/- $0.01 target.
- [scripts/analyze.py](scripts/analyze.py): dependency-free Python that validates the raw sample before writing and deterministically rebuilds the derived CSVs and SVG figures.

Run:

```bash
python3 content/research/market-health/posts/2026-09-28-mexc/scripts/analyze.py
```

The committed rows were collected from MEXC's public aggregate-trades endpoint:

```text
GET https://api.mexc.com/api/v3/aggTrades
```

The captured rows have blank aggregate/trade-ID fields. **No aggregate-ID deduplication is claimed or performed.** The committed sample contains no exact duplicate rows under the available fields. Analysis uses every committed row and groups rows sharing the same market, capture label and millisecond timestamp into timestamp-level events. ([raw rows](data/raw_aggtrades.csv), [analysis code](scripts/analyze.py))

MEXC endpoint documentation: [Compressed/Aggregate Trades List](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints/compressedaggregate-trades-list).

## Scope

The sample is short and exploratory. The $5 target was identified from the observed data and should be treated as an effect description rather than a pre-registered hypothesis. The XL1 comparison controls one similar-activity market, not every MEXC or low-liquidity pair. The capture-boundary metadata was not preserved. These limitations are why the article reports a **surveillance anomaly / automation signal**, not a definitive allegation of wash trading.
