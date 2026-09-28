---
title: "Fixed-clock, fixed-notional execution on MEXC AINETWORK/USDT"
description: "AINETWORK/USDT shows a persistent 20-minute, approximately $20 execution cadence on MEXC spot that is absent from a similar-activity control. The pattern is a strong automation and non-organic-flow signal, but public trade data alone does not prove wash trading."
date: 2026-09-28
entities:
  - MEXC
  - AINETWORK
  - DADDY
---

## Summary

MEXC spot trade data for AINETWORK/USDT shows a highly regular execution process that is difficult to reconcile with discretionary order flow. On 2026-09-27 and into 2026-09-28 UTC, a recurring event lands at second **:49** on the repeating minute sequence **:07, :27, :47**. Each event totals approximately **20 USDT**, even when the venue reports that event as several aggregate trades.

The same test on DADDY/USDT, a MEXC spot pair with a similar number of observed aggregate trades over the comparison window, does not reproduce the pattern.

This is evidence of a scheduled automated execution process and a useful market-health surveillance signal. It is **not sufficient by itself to classify the activity as wash trading**: public aggregate trades do not reveal common beneficial ownership, self-match identifiers, or whether the two sides transfer economic risk.

## Fixed-clock cadence

On 2026-09-27, the analysis observes **37 AINETWORK/USDT cadence events**. All 37 total within 0.10 USDT of 20 USDT. Of the 36 gaps between consecutive observed cadence events, **31 are exactly 20 minutes**. The pattern continues across midnight: in the first six UTC hours of 2026-09-28, all **16 observed cadence events** are again within 0.10 USDT of 20 USDT, and all **15 consecutive gaps are exactly 20 minutes**.

The comparison market does not show the same structure. DADDY/USDT records only one trade event on the tested clock positions in each comparison window, and neither event is close to 20 USDT.

{{< figure src="cadence-summary.svg" alt="AINETWORK versus DADDY fixed-clock cadence events" caption="Observed events at :07:49, :27:49 and :47:49 UTC. AINETWORK repeatedly produces approximately $20 events on the 20-minute cadence; the DADDY control does not." >}}

| Window | Market | Aggregate trades | Cadence events | Events near $20 | Exact 20-minute gaps |
| --- | --- | ---: | ---: | ---: | ---: |
| 2026-09-27 | AINETWORK/USDT | 2,777 | 37 | 37 | 31 / 36 |
| 2026-09-27 | DADDY/USDT | 2,642 | 1 | 0 | 0 / 0 |
| 2026-09-28 00:00-05:59 UTC | AINETWORK/USDT | 809 | 16 | 16 | 15 / 15 |
| 2026-09-28 00:00-05:59 UTC | DADDY/USDT | 710 | 1 | 0 | 0 / 0 |

## Fixed notional despite changing token quantity

The bot-like signature is clearer in notional space than in token quantity. AINETWORK's token price changes over the window, so the quantity required to reach 20 USDT moves with it. The cadence process adjusts the token amount while keeping the event notional tightly pinned near 20 USDT.

{{< figure src="cadence-notional.svg" alt="AINETWORK cadence-event notional stays near 20 USDT" caption="Total notional for each observed AINETWORK cadence event. The event may be split into multiple aggregate trades, but the combined notional remains close to 20 USDT." >}}

This distinction matters for surveillance. A detector that looks only for repeated exact token sizes can miss an automated process that targets a fixed quote-currency amount. A fixed-notional metric can therefore complement exact-size recurrence, first-digit tests and time-of-trade concentration.

## Time-of-trade concentration

Second :49 is also the busiest second of the minute for AINETWORK/USDT in both windows. On 2026-09-27 it contains about **6.2%** of observed aggregate trades, versus about **1.6%** for DADDY/USDT. In the first six hours of 2026-09-28 the AINETWORK share rises to about **7.2%**, while DADDY remains near **2.0%**.

The clock test is intentionally stricter than simply counting second :49. The recurring object is the three-position sequence :07:49, :27:49, :47:49 with a 20-minute spacing and a fixed approximately 20-USDT total. The control can randomly print at second :49, but it does not reproduce the joint timing-and-notional fingerprint.

## Why this is not labelled wash trading

The pattern establishes automation and non-random timing. It does not establish self-trading. The cadence events are not close to a 50/50 buy/sell split, and public MEXC aggregate trades do not expose account identity or self-trade-prevention information. A scheduled liquidity-maintenance, inventory-management or execution algorithm can create a clock signature without manipulating the market.

For that reason the correct classification from this dataset is **non-organic scheduled execution / surveillance alert**, not a finding of wash trading. Escalation to a manipulation label would require additional evidence, such as matched opposite-side flows, negligible net risk transfer, account-level common ownership, repeated round trips that systematically cross the spread, or order-book evidence showing artificial depth/volume.

This negative boundary is useful in a market-manipulation framework: time-of-trade concentration can identify a bot, but it should not be promoted to a wash-trading verdict without an independent risk-transfer or ownership signal.

## Data and reproducibility

The analysis uses MEXC's public, key-less spot aggregate-trade endpoint:

`GET https://api.mexc.com/api/v3/aggTrades`

The committed script queries one-hour windows with `startTime` and `endTime`, deduplicates rows by timestamp, price, quantity and maker-side flag, groups trades on the target clock positions, and writes the processed evidence.

Committed artifacts:

- `data/summary.csv` — headline counts for target and control windows.
- `data/cadence_events.csv` — every observed cadence event, including side counts, total token quantity and USDT notional.
- `scripts/fetch_and_analyze.py` — dependency-free Python reproducer.

The current dataset covers the complete UTC day 2026-09-27 and the first six UTC hours of 2026-09-28. Earlier historical requests through the public endpoint did not return data in this collection run, so no claim is made about persistence before 2026-09-27.

## Scope

This is a venue-level public-tape analysis. It can identify an unusually deterministic execution fingerprint, compare it with a control, and show persistence across a date boundary. It cannot identify the beneficial owner of the trades or prove intent. The result should therefore be read as a reproducible market-health alert and as an example of why fixed-clock signals need a second, independent manipulation test before they are classified as wash trading.
