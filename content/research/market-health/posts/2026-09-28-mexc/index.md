---
title: "Fixed-$5 aggregate-trade concentration on MEXC AXM/USDT"
description: "Committed MEXC aggregate-trade rows show AXM/USDT concentrating about 41% of observed notional in repeated ~$5 trades. A same-rule XL1/USDT control records no $5 rows in the committed sample."
date: 2026-09-28
entities:
  - MEXC
  - AXM
---

## Summary

AXM/USDT on MEXC shows a persistent fixed-notional concentration that merits market-surveillance attention. Public trade data alone cannot determine whether the pattern comes from benign execution automation, market-making behavior, or artificial turnover.

Across the committed sample, **496 of 802 AXM aggregate-trade rows (61.8%)** have notional between **$4.99 and $5.01**. Those rows carry **$2479.99**, or **40.7%** of observed AXM notional. The selected rows contain **250 taker-buy and 246 taker-sell trades**. ([raw MEXC rows](data/raw_aggtrades.csv), [derived summary](data/summary.csv), [selected AXM rows](data/axm_fixed_notional_events.csv))

A same-venue comparison market, XL1/USDT, has similar activity in the committed 2026-09-27 capture: **612 aggregate-trade rows and about $4.67k notional**, versus AXM's **581 rows and about $4.64k**. Applying the **same $5.00 +/- $0.01 row-level rule** to XL1 produces **zero matching rows** in both committed capture labels. This shows that the specific fixed-$5 concentration seen in AXM is not reproduced by this XL1 sample; it does not establish a venue-wide or low-liquidity baseline. ([raw MEXC rows](data/raw_aggtrades.csv), [derived summary](data/summary.csv))

The committed data do **not** prove wash trading. They do not expose beneficial ownership, account identity, self-trade identifiers, order identity, or intent.

## Repeated fixed-notional rows

The capture has blank aggregate/order-ID fields. Multiple supplied rows can share the same millisecond while differing in side or quantity, so the analysis does **not** merge rows by timestamp. Each committed aggregate-trade row is treated as one observation. The target rule is deliberately simple and identical for target and control: row notional is between **$4.99 and $5.01** inclusive. ([analysis code](scripts/analyze.py))

In the rows labeled **2026-09-27**, **368 of 581 AXM rows (63.3%)** match the rule and carry **39.6%** of observed AXM notional. In the **2026-09-28-partial** rows, **128 of 221 rows (57.9%)** match and carry **44.0%** of observed notional. ([summary](data/summary.csv), [selected rows](data/axm_fixed_notional_events.csv))

{{< figure src="axm-fixed-notional.svg" alt="AXM versus XL1 share of aggregate-trade rows near five USDT" caption="The identical $5.00 +/- $0.01 row-level rule is applied to both markets. AXM repeatedly hits the target window; XL1 has no matching rows in either committed capture." >}}

All table values below are generated from the committed [raw trade rows](data/raw_aggtrades.csv) by [scripts/analyze.py](scripts/analyze.py) and reproduced in [summary.csv](data/summary.csv).

| Capture label | Market | Aggregate-trade rows | ~$5 rows | Row share | Notional share |
| --- | --- | ---: | ---: | ---: | ---: |
| 2026-09-27 captured rows | AXM/USDT | 581 | 368 | 63.3% | 39.6% |
| 2026-09-27 captured rows | XL1/USDT | 612 | 0 | 0.0% | 0.0% |
| 2026-09-28 partial capture | AXM/USDT | 221 | 128 | 57.9% | 44.0% |
| 2026-09-28 partial capture | XL1/USDT | 170 | 0 | 0.0% | 0.0% |

### Capture-window limitation

The raw file preserves trade timestamps but not the original request-boundary metadata. Therefore the period labels above are **capture labels, not claims of complete calendar-day coverage**. In the committed rows, the first/last returned timestamps are:

- AXM/USDT, 2026-09-27 label: **05:12:03Z to 23:59:05Z**.
- XL1/USDT, 2026-09-27 label: **05:02:05Z to 23:58:21Z**.
- AXM/USDT, 2026-09-28-partial label: **00:00:07Z to 04:57:21Z**.
- XL1/USDT, 2026-09-28-partial label: **00:01:14Z to 05:31:26Z**.

These are the first and last trades present in the [committed raw file](data/raw_aggtrades.csv); without preserved request boundaries, absence of rows outside those ranges should not be interpreted as verified absence of trading.

## Aggressor-side balance

Across both committed capture labels, the selected ~$5 AXM rows contain **250 taker-buy and 246 taker-sell trades**. Their selected notional differs by about **$20.00**, or **0.81% of gross selected turnover**. ([selected AXM rows](data/axm_fixed_notional_events.csv), [summary](data/summary.csv))

{{< figure src="axm-side-balance.svg" alt="AXM fixed-notional aggregate-trade taker-buy and taker-sell counts" caption="Descriptive aggressor-side counts within the already-selected ~$5 AXM rows." >}}

| Capture label | ~$5 rows | Taker buys | Taker sells | Selected turnover | Absolute side imbalance |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2026-09-27 captured rows | 368 | 185 | 183 | $1,839.99 | $10.00 |
| 2026-09-28 partial capture | 128 | 65 | 63 | $640.00 | $10.00 |
| **Combined** | **496** | **250** | **246** | **$2,479.99** | **$20.00 (0.81%)** |

The near-even side count is **descriptive, not a separate manipulation test**. Because the selected trades are already constrained to approximately $5, a four-trade count difference mechanically implies a small notional difference. No claim about intent is based on this balance alone.

## What the public tape can and cannot show

The committed evidence supports a narrow anomaly statement: **AXM/USDT has a persistent concentration of aggregate-trade rows near a fixed $5 quote amount, while the same rule yields zero matches in the committed XL1 control sample.** ([raw rows](data/raw_aggtrades.csv), [summary](data/summary.csv))

A manipulation finding requires more than a repetitive public tape. The committed rows contain price, quantity, timestamp and buyer-maker side, but they do not identify accounts, beneficial owners, order identities, self-trade-prevention events, or intent. A benign fixed-notional execution algorithm can also generate repeated $5 rows.

The $5 threshold is an empirical feature of this committed sample. **No claim is made here that $5 corresponds to an exchange-enforced minimum or other historical market-rule constraint**, because a timestamped exchange-info snapshot was not preserved with the capture.

Stronger evidence for an artificial-turnover attribution would require account/order-book information, repeated self-matches, common ownership of both sides, a preserved market-rule snapshot, or another discriminating baseline that separates ordinary automated execution from activity generation.

## Data and reproducibility

- [data/raw_aggtrades.csv](data/raw_aggtrades.csv): **1,584** committed MEXC aggregate-trade rows for AXM/USDT and XL1/USDT.
- [data/summary.csv](data/summary.csv): per-capture metrics using the identical row-level fixed-notional rule.
- [data/axm_fixed_notional_events.csv](data/axm_fixed_notional_events.csv): all AXM rows within the $5.00 +/- $0.01 target; `raw_row_number` maps each result back to the committed raw CSV.
- [scripts/analyze.py](scripts/analyze.py): dependency-free Python that validates the raw sample before writing and deterministically rebuilds the derived CSVs and SVG figures.

Run:

```bash
python3 content/research/market-health/posts/2026-09-28-mexc/scripts/analyze.py
```

The committed rows were collected from MEXC's public aggregate-trades endpoint:

```text
GET https://api.mexc.com/api/v3/aggTrades
```

The captured rows have blank aggregate/trade-ID fields. **No aggregate-ID deduplication is claimed or performed.** The committed sample contains no exact duplicate rows under the available fields. Analysis uses every committed raw row independently; equal timestamps are not treated as proof of shared order/event identity. ([raw rows](data/raw_aggtrades.csv), [analysis code](scripts/analyze.py))

MEXC endpoint documentation: [Compressed/Aggregate Trades List](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints/compressedaggregate-trades-list).

## Scope

The sample is short and exploratory. The $5 target was identified from the observed data and should be treated as an effect description rather than a pre-registered hypothesis. The XL1 comparison controls one similar-activity market, not every MEXC or low-liquidity pair. The capture-boundary metadata and timestamped exchange-info response were not preserved. These limitations are why the article reports a **surveillance anomaly / automation signal**, not a definitive allegation of wash trading.
