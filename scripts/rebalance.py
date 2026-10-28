#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rebalancing drift check and trade sizing.

Rules (see references/framework.md 5):
  - Bands scale with sleeve size, because a flat 5pp band never fires on a
    small sleeve: target >=25% -> 5pp, 10-25% -> 3pp, <10% -> 2pp.
  - A sleeve triggers when its absolute deviation exceeds its band, measured in
    percentage points of the portfolio.
  - Fund underweight sleeves with new money first, then income, then sells.

Examples:
  python3 rebalance.py --target "us:40,dev:15,em:5,bond:35,gold:5" \
      --current "us:46,dev:14,em:6,bond:29,gold:5" --total 400 --cash-in 2
"""

import argparse
import json
import sys


def parse(raw, allow_partial=True):
    out = {}
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise SystemExit(f"Bad entry '{part}'. Expected sleeve:pct, e.g. us:40")
        key, val = part.split(":", 1)
        key = key.strip().lower()
        try:
            out[key] = float(val)
        except ValueError:
            raise SystemExit(f"Value is not a number: '{val}'")
    if not allow_partial:
        total = sum(out.values())
        if not (99.0 <= total <= 101.0):
            raise SystemExit(f"Target weights sum to {total:.1f}%, must be 100%")
    return out


def band_for(target_pct):
    """Absolute band in percentage points, scaled by sleeve size."""
    if target_pct >= 25.0:
        return 5.0
    if target_pct >= 10.0:
        return 3.0
    return 2.0


def main():
    ap = argparse.ArgumentParser(description="Rebalancing drift and trade sizing")
    ap.add_argument("--target", required=True, help="target weights, e.g. us:40,dev:15,em:5,bond:35,gold:5")
    ap.add_argument("--current", required=True, help="current weights, same sleeve codes")
    ap.add_argument("--total", type=float, required=True, help="current portfolio value")
    ap.add_argument("--cash-in", type=float, default=0.0, help="new contribution available, default 0")
    ap.add_argument("--fixed-abs", type=float, default=None,
                    help="use one flat absolute band instead of the size-scaled bands")
    ap.add_argument("--json", action="store_true", help="machine-readable output only")
    args = ap.parse_args()

    target = parse(args.target, allow_partial=False)
    current = parse(args.current, allow_partial=True)
    for k in current:
        if k not in target:
            raise SystemExit(f"Sleeve '{k}' in --current has no target weight")

    keys = list(target)
    for k in keys:
        current.setdefault(k, 0.0)

    cur_total = sum(current.values())
    if abs(cur_total - 100.0) > 1.5:
        print(f"Warning: current weights sum to {cur_total:.1f}%, not 100%. "
              f"They will be used as given.", file=sys.stderr)

    total_after = args.total + args.cash_in
    rows, triggered = [], []
    for k in keys:
        dev = current[k] - target[k]
        band = args.fixed_abs if args.fixed_abs is not None else band_for(target[k])
        fired = abs(dev) >= band - 1e-9
        if fired:
            triggered.append(k)
        cur_amt = args.total * current[k] / 100.0
        tgt_amt = total_after * target[k] / 100.0
        rows.append({
            "sleeve": k,
            "target_pct": round(target[k], 1),
            "current_pct": round(current[k], 1),
            "deviation_pp": round(dev, 1),
            "band_pp": round(band, 1),
            "triggered": fired,
            "current_amount": round(cur_amt, 2),
            "target_amount": round(tgt_amt, 2),
            "trade": round(tgt_amt - cur_amt, 2),
        })

    buys = [r for r in rows if r["trade"] > 0]
    sells = [r for r in rows if r["trade"] < 0]
    buy_total = sum(r["trade"] for r in buys)
    sell_total = -sum(r["trade"] for r in sells)

    result = {
        "rule": ("flat %.1fpp band" % args.fixed_abs) if args.fixed_abs is not None
                else "size-scaled bands: >=25% -> 5pp, 10-25% -> 3pp, <10% -> 2pp",
        "total_before": args.total,
        "cash_in": args.cash_in,
        "total_after": round(total_after, 2),
        "triggered": triggered,
        "sleeves": rows,
        "summary": {
            "buy_total": round(buy_total, 2),
            "sell_total": round(sell_total, 2),
            "funded_by_new_money": round(min(args.cash_in, buy_total), 2),
            "sells_required": round(max(sell_total - args.cash_in, 0.0), 2),
        },
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    hdr = (f"{'Sleeve':<8}{'Target%':>9}{'Now%':>8}{'Dev pp':>9}"
           f"{'Band':>7}{'Now':>12}{'Target':>12}{'Trade':>12}")
    print("=" * len(hdr))
    print("REBALANCE CHECK")
    print("=" * len(hdr))
    print(hdr)
    for r in rows:
        flag = "  <- FIRE" if r["triggered"] else ""
        print(f"{r['sleeve']:<8}{r['target_pct']:>9.1f}{r['current_pct']:>8.1f}"
              f"{r['deviation_pp']:>9.1f}{r['band_pp']:>7.1f}"
              f"{r['current_amount']:>12.2f}{r['target_amount']:>12.2f}"
              f"{r['trade']:>+12.2f}{flag}")
    print("-" * len(hdr))
    print(f"Buy {buy_total:.2f} / Sell {sell_total:.2f}   "
          f"new money {args.cash_in:.2f} covers {min(args.cash_in, buy_total):.2f}")

    if not triggered:
        print("\nNo sleeve outside its band. Do nothing - a calendar check is unnecessary.")
        return 0

    print(f"\nTriggered: {', '.join(triggered)}")
    print("Execution order: new contributions -> income and dividends -> sell overweight")
    print("-> adjust within a sleeve. Never sell a position just to match a number.")
    if args.cash_in >= buy_total:
        print("New money covers the whole buy side; no sales needed.")
    else:
        print(f"New money covers {args.cash_in:.2f} of {buy_total:.2f}; "
              f"the balance needs sales of at least {max(sell_total - args.cash_in, 0):.2f}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
