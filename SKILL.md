---
name: family-goal-bucket-planner
version: 1.0.0
description: 'Plans a household portfolio by goal buckets instead of by expected return. Given investable assets, monthly saving, and target amounts, it runs a financial health check, assigns a risk level from both capacity and willingness (taking the lower), splits money into four purpose buckets, and sizes each bucket with a Monte-Carlo goal-attainment probability plus a two-tier downside p5 veto. Use when someone asks "how should I split my savings", "will I hit my retirement number", "how much should I keep in cash", "is this portfolio too aggressive", or "how much do I need to save each month". Zero dependencies — Python standard library only. Planning aid, not investment advice.'
license: MIT
author: yangsssssss
category: finance
tags:
  - asset-allocation
  - financial-planning
  - monte-carlo
  - goal-based-investing
  - retirement
  - risk-profiling
disclaimer: 'All returns, volatilities, and correlations are long-run assumptions, not forecasts. Monte-Carlo output is a function of those assumptions. This skill does not recommend securities, does not promise returns, and is not investment, tax, or legal advice.'
---

# Family Goal-Bucket Planner

Allocate by **purpose**, not by expected return. The deliverable is a one-page plan stating: how much sits in each of four buckets, what each bucket is invested in at the sleeve level, what probability the plan reaches its targets, and what happens in the bad 5% of cases.

## When to use

Trigger when the user wants to split investable money across goals rather than pick securities: "I have $X, how should I allocate it", "will I reach $Y by age Z", "how much emergency cash do I need", "can I afford to take more risk", "how much must I save monthly".

Do **not** use for single-security research, options strategies, or institutional portfolio management.

## Workflow

Execute in order. Do not skip M1 to get to the allocation — the buckets depend on the balance sheet.

**M1 — Financial health check.** Compute six ratios from `references/framework.md` §1: savings rate, debt-to-asset, debt-service-to-income, liquidity months, investable-to-annual-expense multiple, insurance coverage. Flag every ratio outside its band. A failed liquidity or debt-service check overrides any risk appetite the user claims.

**M2 — Risk level.** Score objective **capacity** (income stability, debt load, age, dependants, horizon) and subjective **willingness** (questionnaire in `references/risk-profile.md`). **Take the lower of the two** — this is a hard rule, not a tiebreak. Output level 1–5 (Very Conservative / Conservative / Balanced / Growth / Aggressive).

**M3 — Bucket by purpose.** Split the money into four buckets, sized by use and deadline, never by expected return:
1. Emergency reserve — months of essential spending (6 if stable dual income; 12–18 if single income, variable income, or mid-career transition)
2. Committed spending within 3 years (down payment, car, tuition, wedding) — principal-protection instruments only, never equity
3. Goals 5–10 years out (education, home upgrade)
4. Long money 15 years+ (retirement)

Bucket 2 must be fully funded before bucket 4 receives anything.

**M4 — Size each bucket and test it.** For buckets 3 and 4, choose a sleeve mix from `references/assumptions.md`, then run the attainment test:

```bash
python3 scripts/monte_carlo.py --initial 400 --monthly 1.5 --years 20 \
    --target 1600 --weights "us:40,dev:15,em:5,bond:35,gold:5"
```

Report **both** the attainment probability and the p5 outcome. Apply the three gates from `references/framework.md` §4:
- attainment < 70% → plan not deliverable; fix by extending the horizon, raising the monthly saving, or lowering the target — never by raising the assumed return
- p5 below 85% of target → plan rejected regardless of attainment (see §4.4)
- savings contribution > 50% → say so explicitly: at that point more equity *lowers* attainment, and the goal is to damp volatility, not chase return

**Output.** One page using `assets/plan_template.md`: the four buckets with amounts, the sleeve mix per bucket, attainment probability with p5, and the assumption list. State assumptions up front and label them as assumptions. If the user cannot supply a figure, use the defaults in `references/framework.md` §6 and list them on the first screen — do not interrogate them item by item.

## Hard rules

1. **Take the lower of capacity and willingness.** A household that scores high on willingness but low on capacity sells at the bottom in a drawdown.
2. **Never fund bucket 4 before bucket 2 is complete.**
3. **p5 veto is absolute.** A plan that clears the attainment threshold but breaks the downside line is a plan that trades the floor for the median. Reject it and say why.
4. **Do not reconcile contradictory instructions silently.** Because the sleeves must sum to 100%, constraints can be mutually exclusive (e.g. "keep bonds under 15%" plus "cap foreign currency at 20%" plus "keep equity above 70%" has no solution). Show the arithmetic, show the cost of each branch, and let the user choose. Fabricating weights that do not add up is the one failure this skill must not commit.
5. **Assumptions are editable, forecasts are not.** If the user's base currency is not USD, adjust the bond and cash assumptions to their local risk-free rate before running anything — see `references/assumptions.md` §5.

## Files

- `references/framework.md` — thresholds, scoring rules, bucket sizing, the four gates, constraint arithmetic
- `references/risk-profile.md` — 8-question willingness questionnaire, 0–3 scoring
- `references/assumptions.md` — sleeve return/volatility/correlation table, failure conditions, override guide
- `scripts/monte_carlo.py` — attainment probability, terminal percentiles, p5 veto
- `scripts/rebalance.py` — banded rebalancing thresholds and trade sizing
- `assets/plan_template.md` — the one-page output format
