#!/usr/bin/env python3
import csv
import json
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

BASE = "https://api.mexc.com/api/v3/aggTrades"
TARGET = "AINETWORKUSDT"
CONTROL = "DADDYUSDT"
WINDOWS = [
    ("2026-09-27", "2026-09-27T00:00:00Z", "2026-09-27T23:59:59.999Z"),
    ("2026-09-28-partial", "2026-09-28T00:00:00Z", "2026-09-28T05:59:59.999Z"),
]

def ms(iso):
    return int(datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp() * 1000)

def fetch(symbol, start_ms, end_ms):
    params = urllib.parse.urlencode({
        "symbol": symbol,
        "startTime": start_ms,
        "endTime": end_ms,
        "limit": 1000,
    })
    req = urllib.request.Request(f"{BASE}?{params}", headers={"User-Agent": "dn-market-health-research/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def fetch_window(symbol, start_iso, end_iso):
    start, end = ms(start_iso), ms(end_iso)
    rows = {}
    step = 60 * 60 * 1000
    cursor = start
    while cursor <= end:
        stop = min(cursor + step - 1, end)
        for x in fetch(symbol, cursor, stop):
            key = (x["T"], x["p"], x["q"], x["m"])
            rows[key] = x
        cursor += step
    return sorted(rows.values(), key=lambda x: x["T"])

def cadence_event(ts):
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return d.second == 49 and d.minute in (7, 27, 47)

def analyse(symbol, period, rows):
    second_counts = [0] * 60
    events = defaultdict(lambda: {"count": 0, "buys": 0, "sells": 0, "qty": 0.0, "notional": 0.0})

    for x in rows:
        d = datetime.fromtimestamp(x["T"] / 1000, tz=timezone.utc)
        second_counts[d.second] += 1
        if cadence_event(x["T"]):
            e = events[x["T"]]
            e["count"] += 1
            if x["m"]:
                e["sells"] += 1
            else:
                e["buys"] += 1
            e["qty"] += float(x["q"])
            e["notional"] += float(x["p"]) * float(x["q"])

    event_rows = []
    for ts, e in sorted(events.items()):
        event_rows.append({
            "period": period,
            "symbol": symbol,
            "time_utc": datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
            "trade_count": e["count"],
            "buy_count": e["buys"],
            "sell_count": e["sells"],
            "total_qty": e["qty"],
            "notional_usdt": e["notional"],
        })

    event_times = [datetime.fromisoformat(x["time_utc"].replace("Z", "+00:00")).timestamp() for x in event_rows]
    intervals = [(event_times[i] - event_times[i-1]) / 60 for i in range(1, len(event_times))]
    near20 = sum(abs(x["notional_usdt"] - 20.0) <= 0.10 for x in event_rows)
    exact20 = sum(abs(x - 20.0) < 1e-9 for x in intervals)

    summary = {
        "period": period,
        "symbol": symbol,
        "trades": len(rows),
        "unique_timestamps": len({x["T"] for x in rows}),
        "cadence_events": len(event_rows),
        "near_20usd_events": near20,
        "exact_20min_intervals": exact20,
        "total_intervals": len(intervals),
        "peak_second": max(range(60), key=lambda s: second_counts[s]) if rows else None,
        "peak_second_share": (max(second_counts) / len(rows)) if rows else 0.0,
    }
    return summary, event_rows, second_counts

def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def main():
    summaries, events, seconds = [], [], []
    for period, start, end in WINDOWS:
        for symbol in (TARGET, CONTROL):
            rows = fetch_window(symbol, start, end)
            summary, event_rows, second_counts = analyse(symbol, period, rows)
            summaries.append(summary)
            events.extend(event_rows)
            for second, count in enumerate(second_counts):
                seconds.append({
                    "period": period,
                    "symbol": symbol,
                    "second": second,
                    "count": count,
                    "share": count / len(rows) if rows else 0.0,
                })

    write_csv("summary.csv", summaries, list(summaries[0].keys()))
    write_csv("cadence_events.csv", events, [
        "period","symbol","time_utc","trade_count","buy_count","sell_count","total_qty","notional_usdt"
    ])
    write_csv("second_of_minute.csv", seconds, ["period","symbol","second","count","share"])

    print(json.dumps(summaries, indent=2))

if __name__ == "__main__":
    main()
