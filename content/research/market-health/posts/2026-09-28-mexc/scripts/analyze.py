#!/usr/bin/env python3
"""Reproduce the AXM/USDT fixed-notional analysis from committed MEXC rows."""
from __future__ import annotations
import csv
from pathlib import Path
from datetime import datetime, timezone

POST_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = POST_DIR / "data"
RAW = DATA_DIR / "raw_aggtrades.csv"
TARGET = 5.00
TOLERANCE = 0.01
SYMBOLS = ("AXMUSDT", "XL1USDT")
PERIODS = ("2026-09-27", "2026-09-28-partial")

def read_raw():
    rows = []
    with RAW.open(newline="", encoding="utf-8") as f:
        for source_line, r in enumerate(csv.DictReader(f), start=2):
            if r["symbol"] not in SYMBOLS:
                raise RuntimeError("unexpected symbol: " + r["symbol"])
            rows.append({
                "source_line": source_line,
                "period": r["period"],
                "symbol": r["symbol"],
                "price": float(r["price"]),
                "qty": float(r["qty"]),
                "timestamp_ms": int(r["timestamp_ms"]),
                "buyer_is_maker": r["buyer_is_maker"].lower() == "true",
                "best_price_match": r["best_price_match"].lower() == "true",
            })
    return rows

def build_events(rows):
    # The committed capture has blank aggregate/order IDs, so do not infer
    # identity from timestamps. Each supplied aggregate-trade row is one
    # observation/event, even when multiple rows share the same millisecond.
    return [{
        "source_line": r["source_line"],
        "period": r["period"],
        "symbol": r["symbol"],
        "timestamp_ms": r["timestamp_ms"],
        "trade_count": 1,
        "buy_count": 0 if r["buyer_is_maker"] else 1,
        "sell_count": 1 if r["buyer_is_maker"] else 0,
        "qty": r["qty"],
        "notional": r["price"] * r["qty"],
    } for r in rows]

def side(e):
    return "SELL" if e["sell_count"] else "BUY"

def is_target(e):
    return abs(e["notional"] - TARGET) <= TOLERANCE

def compute_summary(rows, events):
    out = []
    for period in PERIODS:
        for symbol in SYMBOLS:
            rr = [r for r in rows if r["period"] == period and r["symbol"] == symbol]
            ee = [e for e in events if e["period"] == period and e["symbol"] == symbol]
            target = [e for e in ee if is_target(e)]
            buys = [e for e in target if side(e) == "BUY"]
            sells = [e for e in target if side(e) == "SELL"]
            total = sum(r["price"] * r["qty"] for r in rr)
            tn = sum(e["notional"] for e in target)
            bn = sum(e["notional"] for e in buys)
            sn = sum(e["notional"] for e in sells)
            out.append({
                "period": period, "symbol": symbol,
                "metric": "fixed_notional" if symbol == "AXMUSDT" else "control_fixed_notional",
                "target_label": "5.00 USDT +/- 0.01",
                "trades": len(rr), "events": len(ee), "total_notional": total,
                "target_events": len(target), "target_event_share": len(target)/len(ee) if ee else 0.0,
                "target_notional": tn, "target_notional_share": tn/total if total else 0.0,
                "target_buy_events": len(buys), "target_sell_events": len(sells),
                "target_mixed_events": 0, "target_buy_notional": bn,
                "target_sell_notional": sn,
                "net_to_gross": abs(bn-sn)/(bn+sn) if (bn+sn) else 0.0,
            })
    return out

def check(ok, message):
    if not ok:
        raise RuntimeError(message)

def validate_raw(rows):
    check(len(rows) == 1584, "raw row count changed")
    keys = [(r["period"],r["symbol"],r["price"],r["qty"],r["timestamp_ms"],r["buyer_is_maker"],r["best_price_match"]) for r in rows]
    check(len(keys) == len(set(keys)), "exact duplicate raw rows found")

def validate(summary, events):
    sm = {(r["period"],r["symbol"]):r for r in summary}
    a27,x27 = sm[("2026-09-27","AXMUSDT")],sm[("2026-09-27","XL1USDT")]
    a28,x28 = sm[("2026-09-28-partial","AXMUSDT")],sm[("2026-09-28-partial","XL1USDT")]
    check(a27["target_events"] == 368 and a27["target_buy_events"] == 185 and a27["target_sell_events"] == 183, "AXM Sep-27 headline changed")
    check(a28["target_events"] == 128 and a28["target_buy_events"] == 65 and a28["target_sell_events"] == 63, "AXM Sep-28 headline changed")
    check(abs(a27["target_event_share"]-0.63339071) < 1e-8, "AXM Sep-27 event share changed")
    check(abs(a27["target_notional_share"]-0.39629711) < 1e-8, "AXM Sep-27 notional share changed")
    check(abs(a28["target_event_share"]-0.57918552) < 1e-8, "AXM Sep-28 event share changed")
    check(abs(a28["target_notional_share"]-0.44026359) < 1e-8, "AXM Sep-28 notional share changed")
    check(x27["target_events"] == 0 and x28["target_events"] == 0, "XL1 control now has ~$5 rows")
    axm = [e for e in events if e["symbol"] == "AXMUSDT" and is_target(e)]
    check(len(axm) == 496, "combined AXM target count changed")
    check(sum(side(e)=="BUY" for e in axm)==250 and sum(side(e)=="SELL" for e in axm)==246, "combined AXM side counts changed")

def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

def write_summary(path, rows, fields):
    float_fields = {
        "total_notional", "target_event_share", "target_notional",
        "target_notional_share", "target_buy_notional",
        "target_sell_notional", "net_to_gross",
    }
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(fields)
        for row in rows:
            w.writerow([
                f"{float(row[field]):.8f}" if field in float_fields else row[field]
                for field in fields
            ])

def export_events(events):
    out=[]
    for e in events:
        if e["symbol"]!="AXMUSDT" or not is_target(e):
            continue
        dt=datetime.fromtimestamp(e["timestamp_ms"]/1000,tz=timezone.utc)
        out.append({
            "raw_row_number": e["source_line"],
            "period":e["period"],
            "time_utc":dt.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "trade_count":1,
            "buy_count":e["buy_count"],
            "sell_count":e["sell_count"],
            "total_qty":f'{e["qty"]:.8f}',
            "notional_usdt":f'{e["notional"]:.6f}',
        })
    return out

def svg_concentration(summary):
    sm={(r["period"],r["symbol"]):r for r in summary}
    a27,x27=sm[("2026-09-27","AXMUSDT")],sm[("2026-09-27","XL1USDT")]
    a28,x28=sm[("2026-09-28-partial","AXMUSDT")],sm[("2026-09-28-partial","XL1USDT")]
    def y(v): return 390-v*450
    def h(v): return v*450
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="470" viewBox="0 0 900 470">
<rect width="100%" height="100%" fill="white"/>
<text x="450" y="30" text-anchor="middle" font-family="sans-serif" font-size="19">Share of aggregate-trade rows within $5.00 +/- $0.01</text>
<line x1="70" y1="390" x2="850" y2="390" stroke="black"/>
<line x1="70" y1="60" x2="70" y2="390" stroke="black"/>
<rect x="150" y="{y(a27['target_event_share']):.1f}" width="80" height="{h(a27['target_event_share']):.1f}" fill="none" stroke="black" stroke-width="2"/>
<text x="190" y="{378-a27['target_event_share']*450:.1f}" text-anchor="middle" font-family="sans-serif" font-size="12">{a27['target_event_share']*100:.1f}%</text>
<text x="300" y="378" text-anchor="middle" font-family="sans-serif" font-size="12">{x27['target_event_share']*100:.1f}%</text>
<rect x="510" y="{y(a28['target_event_share']):.1f}" width="80" height="{h(a28['target_event_share']):.1f}" fill="none" stroke="black" stroke-width="2"/>
<text x="550" y="{378-a28['target_event_share']*450:.1f}" text-anchor="middle" font-family="sans-serif" font-size="12">{a28['target_event_share']*100:.1f}%</text>
<text x="660" y="378" text-anchor="middle" font-family="sans-serif" font-size="12">{x28['target_event_share']*100:.1f}%</text>
<text x="225" y="425" text-anchor="middle" font-family="sans-serif" font-size="12">2026-09-27 captured rows: AXM / XL1</text>
<text x="585" y="425" text-anchor="middle" font-family="sans-serif" font-size="12">2026-09-28 partial: AXM / XL1</text>
<text x="450" y="452" text-anchor="middle" font-family="sans-serif" font-size="11">Same row-level fixed-notional rule applied to both markets</text>
</svg>
"""

def svg_balance(events):
    a=[e for e in events if e["symbol"]=="AXMUSDT" and is_target(e)]
    buys=sum(side(e)=="BUY" for e in a); sells=sum(side(e)=="SELL" for e in a)
    bn=sum(e["notional"] for e in a if side(e)=="BUY"); sn=sum(e["notional"] for e in a if side(e)=="SELL")
    imb=abs(bn-sn)/(bn+sn)*100
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="760" height="430" viewBox="0 0 760 430">
<rect width="100%" height="100%" fill="white"/>
<text x="380" y="30" text-anchor="middle" font-family="sans-serif" font-size="19">AXM ~$5 aggregate trades: taker-side balance</text>
<line x1="80" y1="350" x2="700" y2="350" stroke="black"/>
<rect x="180" y="{350-buys:.1f}" width="110" height="{buys:.1f}" fill="none" stroke="black" stroke-width="2"/>
<text x="235" y="{338-buys:.1f}" text-anchor="middle" font-family="sans-serif" font-size="14">{buys}</text>
<text x="235" y="380" text-anchor="middle" font-family="sans-serif" font-size="13">taker-buy rows</text>
<rect x="470" y="{350-sells:.1f}" width="110" height="{sells:.1f}" fill="none" stroke="black" stroke-width="2"/>
<text x="525" y="{338-sells:.1f}" text-anchor="middle" font-family="sans-serif" font-size="14">{sells}</text>
<text x="525" y="380" text-anchor="middle" font-family="sans-serif" font-size="13">taker-sell rows</text>
<text x="380" y="408" text-anchor="middle" font-family="sans-serif" font-size="11">absolute buy/sell notional imbalance: {imb:.2f}% of gross selected turnover</text>
</svg>
"""

def main():
    rows=read_raw()
    validate_raw(rows)
    events=build_events(rows)
    summary=compute_summary(rows,events)
    validate(summary,events)

    fields=["period","symbol","metric","target_label","trades","events","total_notional","target_events","target_event_share","target_notional","target_notional_share","target_buy_events","target_sell_events","target_mixed_events","target_buy_notional","target_sell_notional","net_to_gross"]
    write_summary(DATA_DIR/"summary.csv",summary,fields)
    write_csv(DATA_DIR/"axm_fixed_notional_events.csv",export_events(events),["raw_row_number","period","time_utc","trade_count","buy_count","sell_count","total_qty","notional_usdt"])
    (POST_DIR/"axm-fixed-notional.svg").write_text(svg_concentration(summary),encoding="utf-8")
    (POST_DIR/"axm-side-balance.svg").write_text(svg_balance(events),encoding="utf-8")
    print("validated 1584 committed raw rows; AXM target=496, XL1 same-rule target=0")

if __name__=="__main__":
    main()
