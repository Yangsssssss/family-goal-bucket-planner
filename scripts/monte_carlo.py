#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Goal-attainment Monte Carlo for a household portfolio.

Given sleeve weights, starting capital, monthly saving, horizon and target,
estimate the probability of reaching the target and the distribution of
terminal value.

Design notes:
  - The portfolio is assumed rebalanced annually back to target weights, so the
    portfolio's monthly return can be synthesised directly from (w'mu, sqrt(w'Sigma w))
    instead of simulating each sleeve. Faster, and the conclusion is identical.
  - Monthly steps, normal monthly returns, no fat tails. See references/assumptions.md
    for why the left tail is understated and how to read p5 anyway.
  - No unit is assumed: pass every amount in the same currency unit (dollars,
    thousands, lakhs). Ratios and percentages are unit-free.

Examples:
  python3 monte_carlo.py --initial 400 --monthly 1.5 --years 20 --target 1600 \
      --weights us:40,dev:15,em:5,bond:35,gold:5

  python3 monte_carlo.py --initial 400 --monthly 1.5 --years 20 --target 1600 \
      --weights us:40,dev:15,em:5,bond:35,gold:5 --foreign us,dev,em --fx-shock 10 --json
"""

import argparse
import json
import math
import random
import sys

# Long-run nominal assumptions in USD. Must stay in sync with references/assumptions.md.
ASSUMPTIONS = {
    "us":   {"name": "US equity",       "mu": 0.070, "sigma": 0.16},
    "dev":  {"name": "Dev ex-US equity","mu": 0.065, "sigma": 0.17},
    "em":   {"name": "EM equity",       "mu": 0.065, "sigma": 0.23},
    "bond": {"name": "Bonds (IG)",      "mu": 0.040, "sigma": 0.06},
    "gold": {"name": "Gold",            "mu": 0.035, "sigma": 0.16},
    "cash": {"name": "Cash / T-bills",  "mu": 0.025, "sigma": 0.01},
}

CORR = {
    ("us", "us"): 1.00, ("us", "dev"): 0.85, ("us", "em"): 0.70,
    ("us", "bond"): 0.05, ("us", "gold"): 0.05, ("us", "cash"): 0.00,
    ("dev", "dev"): 1.00, ("dev", "em"): 0.75, ("dev", "bond"): 0.05,
    ("dev", "gold"): 0.10, ("dev", "cash"): 0.00,
    ("em", "em"): 1.00, ("em", "bond"): 0.00, ("em", "gold"): 0.15,
    ("em", "cash"): 0.00,
    ("bond", "bond"): 1.00, ("bond", "gold"): 0.20, ("bond", "cash"): 0.15,
    ("gold", "gold"): 1.00, ("gold", "cash"): 0.00,
    ("cash", "cash"): 1.00,
}

EQUITY = {"us", "dev", "em"}
DEFENSIVE = {"bond", "gold", "cash"}


def corr(x, y):
    return CORR.get((x, y), CORR.get((y, x), 0.0))


def parse_weights(raw):
    """'us:40,dev:15' -> {'us': 0.40, 'dev': 0.15}"""
    weights = {}
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise SystemExit(
                f"Bad weight '{part}'. Expected sleeve:pct, e.g. us:40")
        key, val = part.split(":", 1)
        key = key.strip().lower()
        if key not in ASSUMPTIONS:
            raise SystemExit(
                f"Unknown sleeve '{key}'. Available: {', '.join(ASSUMPTIONS)}")
        try:
            weights[key] = float(val) / 100.0
        except ValueError:
            raise SystemExit(f"Weight is not a number: '{val}'")
    total = sum(weights.values())
    if not (0.99 <= total <= 1.01):
        raise SystemExit(f"Weights sum to {total*100:.1f}%, must be 100%")
    return {k: v / total for k, v in weights.items()}


def portfolio_stats(weights):
    mu = sum(w * ASSUMPTIONS[k]["mu"] for k, w in weights.items())
    var = 0.0
    for i, wi in weights.items():
        for j, wj in weights.items():
            var += wi * wj * corr(i, j) * ASSUMPTIONS[i]["sigma"] * ASSUMPTIONS[j]["sigma"]
    return mu, math.sqrt(max(var, 0.0))


def simulate(initial, monthly, years, mu, sigma, paths, seed):
    m_m = mu / 12.0
    s_m = sigma / math.sqrt(12.0)
    months = int(round(years * 12))
    rng = random.Random(seed)
    finals = []
    for _ in range(paths):
        v = initial
        for _ in range(months):
            v = max(v * (1.0 + rng.gauss(m_m, s_m)), 0.0) + monthly
        finals.append(v)
    finals.sort()
    return finals


def pct(sorted_vals, p):
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * p / 100.0
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return sorted_vals[int(k)]
    return sorted_vals[lo] * (hi - k) + sorted_vals[hi] * (k - lo)


def main():
    ap = argparse.ArgumentParser(
        description="Goal-attainment Monte Carlo (all amounts in one consistent unit)")
    ap.add_argument("--initial", type=float, required=True, help="starting capital")
    ap.add_argument("--monthly", type=float, default=0.0, help="monthly contribution, default 0")
    ap.add_argument("--years", type=float, required=True, help="horizon in years")
    ap.add_argument("--target", type=float, required=True, help="target amount")
    ap.add_argument("--weights", required=True,
                    help="sleeve weights summing to 100, e.g. us:40,dev:15,em:5,bond:35,gold:5")
    ap.add_argument("--paths", type=int, default=10000, help="paths, default 10000")
    ap.add_argument("--seed", type=int, default=42, help="seed, default 42 for reproducibility")
    ap.add_argument("--foreign", default="", help="comma-separated sleeves held in foreign currency")
    ap.add_argument("--fx-shock", type=float, default=10.0,
                    help="base-currency appreciation to test, in percent, default 10")
    ap.add_argument("--json", action="store_true", help="machine-readable output only")
    args = ap.parse_args()

    if args.years <= 0:
        raise SystemExit("--years must be positive")
    if args.target <= 0:
        raise SystemExit("--target must be positive")

    weights = parse_weights(args.weights)
    mu, sigma = portfolio_stats(weights)
    finals = simulate(args.initial, args.monthly, args.years,
                      mu, sigma, args.paths, args.seed)

    hit = sum(1 for v in finals if v >= args.target) / len(finals)
    contributed = args.initial + args.monthly * 12 * args.years
    saved = args.monthly * 12 * args.years
    savings_share = saved / args.target if args.target else 0.0

    # Geometric-mean drag: why more equity can lower attainment when saving dominates.
    geo = (1.0 + mu) / math.sqrt(1.0 + (sigma ** 2) / ((1.0 + mu) ** 2)) - 1.0
    drag_pp = (mu - geo) * 100

    # Required return implied by the goal (approximate, contributions mid-period).
    denom = args.initial + 0.5 * saved
    required = ((args.target / denom) ** (1.0 / args.years) - 1.0) if denom > 0 else None

    equity = sum(w for k, w in weights.items() if k in EQUITY)
    largest = max(weights.items(), key=lambda kv: kv[1])

    fx = None
    if args.foreign.strip():
        codes = [c.strip().lower() for c in args.foreign.split(",") if c.strip()]
        unknown = [c for c in codes if c not in ASSUMPTIONS]
        if unknown:
            raise SystemExit(f"Unknown sleeve in --foreign: {', '.join(unknown)}")
        share = sum(w for k, w in weights.items() if k in codes)
        fx = {
            "foreign_sleeves": codes,
            "foreign_share_pct": round(share * 100, 1),
            "base_currency_appreciation_pct": args.fx_shock,
            "portfolio_impact_pp": round(-share * args.fx_shock / 100.0 * 100, 2),
            "note": "Impact in percentage points of portfolio value; liabilities are unchanged.",
        }

    # The downside line is not one number. When saving does most of the work, a
    # bad tail is a choice and the plan should not gamble; when compounding
    # carries the target, some downside is unavoidable and a harsher line would
    # reject every equity-heavy plan. See framework.md 4.4.
    if savings_share > 0.50:
        p5_ratio, p5_basis = 0.85, "savings dominate: a bad tail here is a choice, not a necessity"
    else:
        p5_ratio, p5_basis = 0.65, "compounding carries the target: some downside is unavoidable"
    p5_line = args.target * p5_ratio

    result = {
        "assumptions_note": "Returns and volatilities are long-run assumptions, not forecasts.",
        "portfolio": {
            "exp_return": round(mu * 100, 2),
            "volatility": round(sigma * 100, 2),
            "geometric_return": round(geo * 100, 2),
            "volatility_drag_pp": round(drag_pp, 2),
            "sharpe_like": round((mu - ASSUMPTIONS["cash"]["mu"]) / sigma, 2) if sigma else None,
            "equity_pct": round(equity * 100, 1),
            "defensive_pct": round((1 - equity) * 100, 1),
            "largest_sleeve": largest[0],
            "largest_sleeve_pct": round(largest[1] * 100, 1),
            "concentration_flag": largest[1] > 0.50,
        },
        "inputs": {
            "initial": args.initial, "monthly": args.monthly, "years": args.years,
            "target": args.target, "paths": args.paths, "seed": args.seed,
            "total_contributed": round(contributed, 2),
        },
        "success_rate": round(hit * 100, 1),
        "required_return_pct": round(required * 100, 2) if required is not None else None,
        "p5_veto": {
            "threshold_pct_of_target": round(p5_ratio * 100, 0),
            "basis": p5_basis,
            "line": round(p5_line, 2),
            "p5": round(pct(finals, 5), 2),
            "p5_over_target_pct": round(pct(finals, 5) / args.target * 100, 1),
            "pass": pct(finals, 5) >= p5_line,
            "note": "See framework.md 4.4. Rejection is on the downside line, not on attainment alone.",
        },
        "savings_diagnosis": {
            "saved_total": round(saved, 2),
            "savings_share_of_target_pct": round(savings_share * 100, 1),
            "savings_dominates": savings_share > 0.50,
            "note": ("Savings contribute more than half the target: adding equity lowers "
                     "attainment here. Objective is volatility reduction."
                     if savings_share > 0.50 else
                     "Compounding carries a material share of the target."),
        },
        "final_value": {
            "p5": round(pct(finals, 5), 2),
            "p25": round(pct(finals, 25), 2),
            "p50": round(pct(finals, 50), 2),
            "p75": round(pct(finals, 75), 2),
            "p95": round(pct(finals, 95), 2),
        },
        "shortfall_p5": round(max(args.target - pct(finals, 5), 0.0), 2),
        "currency": fx,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    bar = "=" * 64
    print(bar)
    print("GOAL-ATTAINMENT MONTE CARLO")
    print(bar)
    print("Mix         : " + " / ".join(
        f"{ASSUMPTIONS[k]['name']} {w*100:.0f}%" for k, w in weights.items()))
    print(f"Expected    : {mu*100:.2f}%/yr   Volatility {sigma*100:.2f}%/yr   "
          f"Geometric {geo*100:.2f}%")
    print(f"Drag        : {drag_pp:.2f}pp/yr lost to volatility")
    print(f"Equity      : {equity*100:.0f}%   Defensive {(1-equity)*100:.0f}%   "
          f"Largest sleeve {largest[1]*100:.0f}%")
    if largest[1] > 0.50:
        print("            ! Single sleeve above 50% - the portfolio is that sleeve")
    if fx:
        print(f"FX test     : {fx['foreign_share_pct']:.0f}% in foreign currency, "
              f"base +{args.fx_shock:.0f}% -> {fx['portfolio_impact_pp']:+.2f}pp")
    print(f"Start       : {args.initial:.2f} + {args.monthly:.2f}/mo x {args.years:g}y "
          f"= {contributed:.2f} contributed")
    print(f"Target      : {args.target:.2f}")
    if required is not None:
        gap = required - mu
        flag = "  ! above the mix's expected return" if gap > 0.02 else ""
        print(f"Required    : {required*100:.2f}%/yr to hit target{flag}")
    print("-" * 64)
    print(f"Attainment  : {hit*100:.1f}%   ({args.paths} paths, seed={args.seed})")
    print(f"Terminal    : p5 {pct(finals,5):.1f} / p25 {pct(finals,25):.1f} / "
          f"p50 {pct(finals,50):.1f} / p75 {pct(finals,75):.1f} / p95 {pct(finals,95):.1f}")
    print(f"p5 shortfall: {max(args.target - pct(finals,5), 0):.1f}")
    print(f"p5 vs target: {pct(finals,5)/args.target*100:.0f}%  "
          f"(line {p5_ratio*100:.0f}% - {p5_basis})")
    print(f"Savings     : {savings_share*100:.0f}% of target comes from contributions"
          + ("  (savings dominate)" if savings_share > 0.50 else ""))
    print("-" * 64)

    if pct(finals, 5) < p5_line:
        print(f"! p5 VETO   : p5 {pct(finals,5):.1f} < {p5_ratio*100:.0f}% of target ({p5_line:.1f})")
        print("              This plan trades the floor for the median. Rejected.")
        if savings_share > 0.50:
            print("              Saving already does most of the work; a tail this deep is")
            print("              a choice, not a constraint. De-risk before raising the target.")
        else:
            print("              The bad case loses over a third of the goal. Lengthen the")
            print("              horizon or lower the target rather than relying on the good case.")
        return 0

    if hit < 0.70:
        print("VERDICT: below 70% - not deliverable.")
        print("Order of repair: 1) extend horizon  2) raise monthly saving  "
              "3) lower target. Never raise the assumed return.")
    elif hit < 0.85:
        print("VERDICT: 70-85% - deliverable, but the stress case must be shown explicitly.")
    else:
        print("VERDICT: >=85% and p5 clear - plan is sound.")

    if savings_share > 0.50:
        print("NOTE   : savings dominate, so raising equity would LOWER attainment.")
        print("         State this as a volatility-reduction decision, not a return improvement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
