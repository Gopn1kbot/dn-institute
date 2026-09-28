---
title: "Two automation fingerprints on low-cap MEXC spot markets: fixed-$5 turnover and a fixed-clock $20 bot"
description: "Primary MEXC aggregate-trade data for AXM/USDT and AINETWORK/USDT show two distinct non-organic execution signatures: AXM concentrates about 40% of observed notional in repeated $5 timestamp-level events with nearly flat taker-side balance, while AINETWORK prints approximately $20 bursts on a 20-minute clock. Same-venue controls do not reproduce either pattern."
date: 2026-09-28
entities:
  - MEXC
  - AXM
  - AINETWORK
---

## Summary

Two low-cap MEXC spot markets show execution patterns that are difficult to explain as ordinary discretionary order flow.

**AXM/USDT** repeatedly trades almost exactly **$5 per timestamp-level event**. Across the committed sample (2026-09-27 and the first six UTC hours of 2026-09-28), 484 of 766 timestamp events, or **63.2%**, fall within one cent of $5. Those events carry **$2,419.99**, or **39.7%** of all observed AXM notional. They are almost perfectly two-sided: **244 taker-buy events versus 240 taker-sell events**. Gross target turnover is about $2,420 while the absolute buy/sell notional imbalance is only about **$20 (0.83% of gross)**.

A same-venue control, **XL1/USDT**, is closely matched on observed activity on 2026-09-27: 612 aggregate trades and $4,668 of notional versus AXM's 581 trades and $4,643. Yet XL1's most common rounded event notional appears in only **7 of 593 events (1.18%)** and carries **1.10%** of observed notional. AXM's concentration is therefore not a generic consequence of low liquidity or the MEXC venue.

**AINETWORK/USDT** shows a different signature. The tape repeatedly prints at **second :49 of minutes :07, :27 and :47**, i.e. a 20-minute schedule. The committed sample contains **55** such timestamp events; every one totals between **$19.945 and $20.056**. The longest uninterrupted run is **45 consecutive events exactly 20 minutes apart**, from 2026-09-27 14:47:49 UTC through 2026-09-28 05:27:49 UTC. The activity-matched control **DADDY/USDT** produces only two timestamp events on those same clock slots across the sample.

These are surveillance signals, not identity evidence. The public trade feed cannot show whether the same beneficial owner stood on both sides, whether self-trade prevention was active, or whether risk was transferred between related accounts. AXM's fixed-notional, nearly flat two-sided turnover is **consistent with wash-like automated activity**, but not proof of wash trading. AINETWORK demonstrates scheduled automation much more directly than it demonstrates manipulation.

## AXM/USDT: repeated $5 turnover with almost no side imbalance

MEXC's aggregate-trade endpoint exposes price, quantity, execution timestamp and whether the buyer was the maker. For this analysis, records sharing the same millisecond timestamp are collapsed into one event before notional is measured. That matters because one aggressive order can execute against multiple resting orders and appear as several aggregate-trade records at the same timestamp.

On 2026-09-27, AXM produced 558 timestamp events. **366 (65.6%)** total approximately $5 and account for **39.4%** of all observed notional. The same pattern continues in the first six UTC hours of 2026-09-28: **118 of 208 events (56.7%)** are approximately $5 and account for **40.6%** of notional.

{{< figure src="axm-fixed-notional.svg" alt="AXM versus XL1 exact-notional concentration" caption="Repeated exact-notional concentration on 2026-09-27. AXM/USDT puts 65.6% of timestamp events and 39.4% of observed notional into approximately $5 events. The activity-matched XL1/USDT control puts only 1.18% of events and 1.10% of notional into its most common rounded event size." >}}

The side balance is unusually flat:

| Window | ~$5 events | Taker buys | Taker sells | ~$5 gross turnover | Absolute buy/sell imbalance | Imbalance / gross |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-09-27 | 366 | 184 | 182 | $1,829.99 | $10.00 | 0.55% |
| 2026-09-28 00:00-05:59 UTC | 118 | 60 | 58 | $590.00 | $10.00 | 1.69% |
| **Combined** | **484** | **244** | **240** | **$2,419.99** | **$20.00** | **0.83%** |

The repeated value is not simply MEXC's minimum market-order amount. The venue's public `exchangeInfo` response reports `quoteAmountPrecisionMarket = 1` for AXM/USDT; MEXC documents that field as the **minimum order amount in a market order**. The same value is present for the controls in this sample. The committed [`market_rules.csv`](data/market_rules.csv) preserves those responses and source URLs.

The public tape still leaves an important ambiguity. A strategy that intentionally trades in fixed quote amounts can create this pattern without self-trading. What makes AXM surveillance-worthy is the combination: a dominant exact quote size, persistence across the day boundary, a near-perfect split between aggressive buys and sells, and almost zero net side imbalance while roughly 40% of observed notional passes through the repeated size. Account identifiers or exchange self-trade logs would be needed to turn that footprint into a wash-trading attribution.

## AINETWORK/USDT: a $20 event every 20 minutes

AINETWORK carries a different automation fingerprint. Rather than repeating one event size at arbitrary times, the target activity is synchronized to the clock.

The scheduled slots are:

- `hh:07:49`
- `hh:27:49`
- `hh:47:49`

At each active slot, one or more aggregate-trade records share the exact millisecond timestamp; their summed notional is approximately **$20**.

{{< figure src="ainetwork-fixed-clock.svg" alt="AINETWORK fixed-clock event notional" caption="AINETWORK/USDT timestamp events on the :07:49, :27:49 and :47:49 schedule. All 55 committed events total within roughly six cents of $20. The dashed reference is $20." >}}

Across the committed window there are **55** scheduled events. Their notional ranges only from **$19.945455 to $20.056105**. The strongest run begins at 2026-09-27 14:47:49 UTC and continues without a missed 20-minute slot through 2026-09-28 05:27:49 UTC: **45 events, 44 exact 20-minute intervals**.

For comparison, DADDY/USDT has a similar order of observed activity in the same sample (3,228 aggregate trades versus AINETWORK's 3,746) but produces only **two** timestamp events on those exact three-per-hour clock slots, and neither forms a repeating $20 sequence.

The scheduled activity is clearly automated. Its economic purpose is less clear. Unlike AXM, the AINETWORK sequence is sell-heavy over this short sample, so it should not be described as balanced self-trading. A scheduled execution algorithm, treasury sale, liquidity-management routine, or other legitimate automation could produce fixed-time prints. The useful market-health result is therefore narrower: **time-of-trade plus fixed-notional analysis can identify a deterministic participant that would be nearly invisible to a simple repeated-quantity test**.

## Why the two signatures complement each other

The two markets illustrate why no single wash-trading metric is sufficient.

| Signal | AXM/USDT | AINETWORK/USDT |
| --- | --- | --- |
| Dominant fixed quote notional | Very strong: ~$5 | Scheduled events are ~$20 |
| Taker-side balance | 244 buy / 240 sell target events | Sell-heavy in this window |
| Net target imbalance | 0.83% of gross | Not wash-like |
| Fixed clock | Weak | Very strong: 20-minute schedule |
| Same-venue control reproduces pattern | No | No |
| Interpretation | Wash-like two-sided automation; identity evidence still required | Deterministic automation; manipulation not established |

AXM is the stronger wash-trading surveillance candidate because the repeated activity is both concentrated and nearly flat by side. AINETWORK is the cleaner example of a time-of-trade detector finding automation that a volume-distribution test alone would miss.

## Data and reproducibility

The evidence is committed with this article rather than depending on a live API remaining historically queryable:

- [`data/raw_aggtrades.csv`](data/raw_aggtrades.csv): **8,558** MEXC aggregate-trade records for AXM/USDT, XL1/USDT, AINETWORK/USDT and DADDY/USDT.
- [`data/summary.csv`](data/summary.csv): per-window headline metrics.
- [`data/axm_fixed_notional_events.csv`](data/axm_fixed_notional_events.csv): the approximately $5 AXM timestamp events.
- [`data/ainetwork_fixed_clock_events.csv`](data/ainetwork_fixed_clock_events.csv): the scheduled AINETWORK timestamp events.
- [`data/market_rules.csv`](data/market_rules.csv): MEXC symbol rules used to check the minimum-order explanation.
- [`scripts/analyze.py`](scripts/analyze.py): standard-library Python that rebuilds the derived CSVs, figures and validation checks from the committed raw sample.

Run:

```bash
python3 content/research/market-health/posts/2026-09-28-mexc/scripts/analyze.py
```

The primary market data comes from MEXC's public, key-less aggregate-trades endpoint:

```text
GET https://api.mexc.com/api/v3/aggTrades
```

The sample uses hourly `startTime`/`endTime` requests for 2026-09-27 and for 2026-09-28 00:00-05:59 UTC, with `limit=1000`, then deduplicates by aggregate-trade ID/timestamp/price/quantity. MEXC's official endpoint documentation is [Compressed/Aggregate Trades List](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints/compressedaggregate-trades-list); the symbol-rule interpretation is documented under [Exchange Information](https://www.mexc.com/api-docs/spot-v3/market-data-endpoints/exchange-information).

Aggressor side is derived from the public `m` field: when the buyer is the maker, the aggressor is a seller; otherwise the aggressor is a buyer. The analysis does **not** infer account ownership from that field.

## Scope and limitations

This is a short, venue-specific executed-trade sample, not labelled ground truth. The detection process was exploratory, so the fixed schedules and quote sizes should be treated as effect descriptions rather than post-hoc hypothesis-test p-values. The control pairs reduce the risk of confusing a venue-wide microstructure quirk with a pair-specific signal, but they do not eliminate alternative strategy explanations.

Most importantly, executed trades do not expose beneficial ownership. The data can show repetitive two-sided turnover, clock synchronization and fixed quote amounts; it cannot prove that one entity controlled both sides of a trade. The appropriate conclusion is therefore **non-organic or highly automated activity worthy of surveillance**, with AXM showing a particularly wash-like footprint—not a definitive allegation about the trader or venue.
