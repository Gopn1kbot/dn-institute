#!/usr/bin/env python3
"""Reproduce the MEXC market-health figures and headline metrics from committed raw trades.

No third-party dependencies and no network access are required.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

POST_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = POST_DIR / "data"
RAW = DATA_DIR / "raw_aggtrades.csv"

AXM_TARGET = 5.00
CADENCE_MINUTES = {7, 27, 47}
CADENCE_SECOND = 49


def read_raw():
    rows = []
    with RAW.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(
                {
                    "period": r["period"],
                    "symbol": r["symbol"],
                    "agg_id": r["agg_id"],
                    "price": float(r["price"]),
                    "qty": float(r["qty"]),
                    "timestamp_ms": int(r["timestamp_ms"]),
                    "buyer_is_maker": r["buyer_is_maker"].lower() == "true",
                }
            )
    return rows


def build_events(rows):
    grouped = {}
    for r in rows:
        key = (r["period"], r["symbol"], r["timestamp_ms"])
        e = grouped.setdefault(
            key,
            {
                "period": r["period"],
                "symbol": r["symbol"],
                "timestamp_ms": r["timestamp_ms"],
                "trade_count": 0,
                "buy_count": 0,
                "sell_count": 0,
                "qty": 0.0,
                "notional": 0.0,
            },
        )
        e["trade_count"] += 1
        if r["buyer_is_maker"]:
            e["sell_count"] += 1
        else:
            e["buy_count"] += 1
        e["qty"] += r["qty"]
        e["notional"] += r["price"] * r["qty"]
    return sorted(grouped.values(), key=lambda x: x["timestamp_ms"])


def side(e):
    if e["buy_count"] and not e["sell_count"]:
        return "BUY"
    if e["sell_count"] and not e["buy_count"]:
        return "SELL"
    return "MIXED"


def is_cadence(e):
    dt = datetime.fromtimestamp(e["timestamp_ms"] / 1000, tz=timezone.utc)
    return dt.second == CADENCE_SECOND and dt.minute in CADENCE_MINUTES


def rounded_notional(e):
    return round(e["notional"] + 1e-12, 2)


def pick_target(events, symbol):
    if symbol == "AXMUSDT":
        return [e for e in events if abs(e["notional"] - AXM_TARGET) <= 0.01], "5.00 USDT"
    if symbol == "AINETWORKUSDT":
        return [e for e in events if is_cadence(e)], "minute 07/27/47, second 49"

    counts = Counter(rounded_notional(e) for e in events)
    if not counts:
        return [], ""
    top, _ = counts.most_common(1)[0]
    return [e for e in events if rounded_notional(e) == top], f"{top:.2f} USDT"


def compute_summary(rows, events):
    out = []
    periods = sorted(set(r["period"] for r in rows))
    symbols = ["AXMUSDT", "XL1USDT", "AINETWORKUSDT", "DADDYUSDT"]

    for period in periods:
        for symbol in symbols:
            rr = [r for r in rows if r["period"] == period and r["symbol"] == symbol]
            ee = [e for e in events if e["period"] == period and e["symbol"] == symbol]
            target, label = pick_target(ee, symbol)

            total_notional = sum(r["price"] * r["qty"] for r in rr)
            target_notional = sum(e["notional"] for e in target)
            buy_events = [e for e in target if side(e) == "BUY"]
            sell_events = [e for e in target if side(e) == "SELL"]
            buy_notional = sum(e["notional"] for e in buy_events)
            sell_notional = sum(e["notional"] for e in sell_events)
            gaps = [
                (target[i]["timestamp_ms"] - target[i - 1]["timestamp_ms"]) / 60000
                for i in range(1, len(target))
            ]

            out.append(
                {
                    "period": period,
                    "symbol": symbol,
                    "target_label": label,
                    "trades": len(rr),
                    "events": len(ee),
                    "total_notional": total_notional,
                    "target_events": len(target),
                    "target_event_share": len(target) / len(ee) if ee else 0.0,
                    "target_notional": target_notional,
                    "target_notional_share": target_notional / total_notional if total_notional else 0.0,
                    "target_buy_events": len(buy_events),
                    "target_sell_events": len(sell_events),
                    "target_buy_notional": buy_notional,
                    "target_sell_notional": sell_notional,
                    "net_to_gross": abs(buy_notional - sell_notional) / (buy_notional + sell_notional)
                    if (buy_notional + sell_notional)
                    else 0.0,
                    "exact_20m_intervals": sum(g == 20 for g in gaps),
                    "total_intervals": len(gaps),
                }
            )
    return out


def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def event_export(events):
    return [
        {
            "period": e["period"],
            "time_utc": datetime.fromtimestamp(e["timestamp_ms"] / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
            "trade_count": e["trade_count"],
            "buy_count": e["buy_count"],
            "sell_count": e["sell_count"],
            "total_qty": f'{e["qty"]:.8f}',
            "notional_usdt": f'{e["notional"]:.6f}',
        }
        for e in events
    ]


def second_of_minute(rows):
    result = []
    for period in sorted(set(r["period"] for r in rows)):
        for symbol in ["AINETWORKUSDT", "DADDYUSDT"]:
            rr = [r for r in rows if r["period"] == period and r["symbol"] == symbol]
            counts = Counter(
                datetime.fromtimestamp(r["timestamp_ms"] / 1000, tz=timezone.utc).second for r in rr
            )
            for second in range(60):
                result.append(
                    {
                        "period": period,
                        "symbol": symbol,
                        "second": second,
                        "count": counts[second],
                        "share": counts[second] / len(rr) if rr else 0.0,
                    }
                )
    return result


def svg_start(width, height, title):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2:.0f}" y="28" text-anchor="middle" font-family="sans-serif" font-size="18">{title}</text>',
    ]


def chart_axm(summary):
    rows = [r for r in summary if r["period"] == "2026-09-27" and r["symbol"] in {"AXMUSDT", "XL1USDT"}]
    by = {r["symbol"]: r for r in rows}
    width, height = 760, 430
    svg = svg_start(width, height, "Repeated exact-notional concentration, 2026-09-27")
    svg += [
        '<text x="90" y="390" font-family="sans-serif" font-size="12">AXM/USDT</text>',
        '<text x="410" y="390" font-family="sans-serif" font-size="12">XL1/USDT control</text>',
    ]
    metrics = [("target_event_share", "share of timestamp events"), ("target_notional_share", "share of observed notional")]
    xs = {"AXMUSDT": 130, "XL1USDT": 450}
    for j, (key, label) in enumerate(metrics):
        for symbol in ["AXMUSDT", "XL1USDT"]:
            v = by[symbol][key]
            x = xs[symbol] + j * 90
            h = v * 280
            y = 350 - h
            svg.append(f'<rect x="{x}" y="{y:.1f}" width="58" height="{h:.1f}" fill="none" stroke="black" stroke-width="2"/>')
            svg.append(f'<text x="{x+29}" y="{y-8:.1f}" text-anchor="middle" font-family="sans-serif" font-size="12">{v*100:.1f}%</text>')
        svg.append(f'<text x="{210 + j*90}" y="414" text-anchor="middle" font-family="sans-serif" font-size="10">{label}</text>')
    svg += ['<line x1="70" y1="350" x2="700" y2="350" stroke="black"/>', "</svg>"]
    (POST_DIR / "axm-fixed-notional.svg").write_text("\n".join(svg) + "\n", encoding="utf-8")


def chart_cadence(events):
    ai = [e for e in events if e["symbol"] == "AINETWORKUSDT" and is_cadence(e)]
    daddy = [e for e in events if e["symbol"] == "DADDYUSDT" and is_cadence(e)]
    start = min(e["timestamp_ms"] for e in ai + daddy)
    end = max(e["timestamp_ms"] for e in ai + daddy)
    width, height = 900, 420
    left, right, top, bottom = 70, 30, 55, 70
    plot_w, plot_h = width-left-right, height-top-bottom
    ymax = 22.0
    svg = svg_start(width, height, "Fixed-clock event notional across the committed sample")
    svg += [
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="black"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="black"/>',
        f'<text x="{width/2}" y="{height-18}" text-anchor="middle" font-family="sans-serif" font-size="12">UTC time (2026-09-27 to 2026-09-28)</text>',
        f'<text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" text-anchor="middle" font-family="sans-serif" font-size="12">event notional (USDT)</text>',
    ]
    y20 = top + plot_h * (1 - 20 / ymax)
    svg.append(f'<line x1="{left}" y1="{y20:.1f}" x2="{width-right}" y2="{y20:.1f}" stroke="black" stroke-dasharray="5,5"/>')
    for e in ai:
        x = left + (e["timestamp_ms"] - start) / (end - start) * plot_w
        y = top + plot_h * (1 - min(e["notional"], ymax) / ymax)
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="black"/>')
    for e in daddy:
        x = left + (e["timestamp_ms"] - start) / (end - start) * plot_w
        y = top + plot_h * (1 - min(e["notional"], ymax) / ymax)
        svg.append(f'<rect x="{x-3:.1f}" y="{y-3:.1f}" width="6" height="6" fill="white" stroke="black"/>')
    svg += [
        '<text x="95" y="75" font-family="sans-serif" font-size="11">black circles: AINETWORK scheduled slots</text>',
        '<text x="95" y="92" font-family="sans-serif" font-size="11">open squares: DADDY control at same clock slots</text>',
        "</svg>",
    ]
    (POST_DIR / "ainetwork-fixed-clock.svg").write_text("\n".join(svg) + "\n", encoding="utf-8")


def chart_seconds(rows):
    width, height = 900, 420
    left, right, top, bottom = 70, 30, 55, 70
    plot_w, plot_h = width-left-right, height-top-bottom
    sample = [r for r in rows if r["period"] == "2026-09-27" and r["symbol"] in {"AINETWORKUSDT", "DADDYUSDT"}]
    counts = {}
    totals = {}
    for symbol in ["AINETWORKUSDT", "DADDYUSDT"]:
        rr = [r for r in sample if r["symbol"] == symbol]
        totals[symbol] = len(rr)
        counts[symbol] = Counter(datetime.fromtimestamp(r["timestamp_ms"]/1000, tz=timezone.utc).second for r in rr)
    ymax = max(counts["AINETWORKUSDT"].values()) / totals["AINETWORKUSDT"] * 1.15
    svg = svg_start(width, height, "Second-of-minute distribution, 2026-09-27")
    svg += [
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="black"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="black"/>',
    ]
    for sec in range(60):
        x = left + sec/59*plot_w
        va = counts["AINETWORKUSDT"][sec] / totals["AINETWORKUSDT"]
        vd = counts["DADDYUSDT"][sec] / totals["DADDYUSDT"]
        ya = top + plot_h*(1-va/ymax)
        yd = top + plot_h*(1-vd/ymax)
        svg.append(f'<circle cx="{x:.1f}" cy="{ya:.1f}" r="2.3" fill="black"/>')
        svg.append(f'<circle cx="{x:.1f}" cy="{yd:.1f}" r="2.3" fill="white" stroke="black"/>')
    x49 = left + 49/59*plot_w
    svg.append(f'<line x1="{x49:.1f}" y1="{top}" x2="{x49:.1f}" y2="{height-bottom}" stroke="black" stroke-dasharray="3,4"/>')
    svg += [
        '<text x="90" y="75" font-family="sans-serif" font-size="11">black: AINETWORK/USDT; open: DADDY/USDT</text>',
        '<text x="90" y="92" font-family="sans-serif" font-size="11">dashed line: second :49</text>',
        "</svg>",
    ]
    (POST_DIR / "second-of-minute.svg").write_text("\n".join(svg) + "\n", encoding="utf-8")


def longest_exact_20m_streak(events):
    events = sorted(events, key=lambda e: e["timestamp_ms"])
    if not events:
        return 0
    best = cur = 1
    for i in range(1, len(events)):
        if events[i]["timestamp_ms"] - events[i-1]["timestamp_ms"] == 20 * 60 * 1000:
            cur += 1
        else:
            cur = 1
        best = max(best, cur)
    return best


def validate(rows, events, summary):
    sm = {(r["period"], r["symbol"]): r for r in summary}

    ax27 = sm[("2026-09-27", "AXMUSDT")]
    ax28 = sm[("2026-09-28-partial", "AXMUSDT")]
    assert ax27["target_events"] == 366
    assert ax27["target_buy_events"] == 184 and ax27["target_sell_events"] == 182
    assert abs(ax27["target_event_share"] - 0.6559) < 0.0002
    assert abs(ax27["target_notional_share"] - 0.3941) < 0.0002
    assert ax28["target_events"] == 118
    assert ax28["target_buy_events"] == 60 and ax28["target_sell_events"] == 58

    ai = [e for e in events if e["symbol"] == "AINETWORKUSDT" and is_cadence(e)]
    assert len(ai) == 53
    assert all(abs(e["notional"] - 20) <= 0.10 for e in ai)
    assert longest_exact_20m_streak(ai) == 44

    d = [e for e in events if e["symbol"] == "DADDYUSDT" and is_cadence(e)]
    assert len(d) == 2


def main():
    rows = read_raw()
    events = build_events(rows)
    summary = compute_summary(rows, events)

    write_csv(DATA_DIR / "summary.csv", summary, list(summary[0].keys()))

    axm = [e for e in events if e["symbol"] == "AXMUSDT" and abs(e["notional"] - AXM_TARGET) <= 0.01]
    ai = [e for e in events if e["symbol"] == "AINETWORKUSDT" and is_cadence(e)]
    fields = ["period", "time_utc", "trade_count", "buy_count", "sell_count", "total_qty", "notional_usdt"]
    write_csv(DATA_DIR / "axm_fixed_notional_events.csv", event_export(axm), fields)
    write_csv(DATA_DIR / "ainetwork_fixed_clock_events.csv", event_export(ai), fields)

    seconds = second_of_minute(rows)
    write_csv(DATA_DIR / "second_of_minute.csv", seconds, ["period", "symbol", "second", "count", "share"])

    chart_axm(summary)
    chart_cadence(events)
    chart_seconds(rows)
    validate(rows, events, summary)

    print(f"validated {len(rows)} raw aggregate trades")
    print(f"AXM fixed-$5 events: {len(axm)}")
    print(f"AINETWORK scheduled ~$20 events: {len(ai)}")
    print(f"AINETWORK longest exact 20-minute streak: {longest_exact_20m_streak(ai)} events")


if __name__ == "__main__":
    main()
