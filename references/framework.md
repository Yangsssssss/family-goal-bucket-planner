# Framework — rules and thresholds

Every threshold here is a decision rule, not a suggestion. Where a number is arbitrary, it says so.

---

## 1. M1 — Financial health check

Compute all six. A failing ratio is a fact about the household, not an opinion, and it constrains M4.

| # | Ratio | Formula | Healthy | Action if breached |
|---|---|---|---|---|
| 1 | Savings rate | (net income − total spending) ÷ net income | **≥ 25%** | Below 15%: the plan is a spending problem, not an allocation problem. Say so before proposing weights. |
| 2 | Debt-to-asset | total debt ÷ total assets | **≤ 50%** | Above 50%: pay down debt before adding equity risk. Deleveraging is a guaranteed return. |
| 3 | Debt service | annual debt payments ÷ net income | **≤ 35%** | Above 35%: cut equity ceiling by one risk level (M2). |
| 4 | Liquidity months | liquid assets ÷ monthly essential spending | **≥ 6** | Below 3: this is the first thing to fix. Allocation advice is meaningless while a job loss forces selling. |
| 5 | Investable multiple | investable assets ÷ annual essential spending | **≥ 5×** | Below 5×: retirement is not the current question; savings capacity is. |
| 6 | Insurance cover | life = 10× income + outstanding debt; critical illness = 3–5× income | as stated | Shortfall: quantify it in currency. Do not sell investment risk before transferring mortality and health risk. |

**Essential spending** excludes discretionary items. If the user only knows total spending, estimate essentials at 70% of total and label the estimate.

---

## 2. M2 — Risk level

Two independent scores. **The level is the lower of them.**

### 2.1 Capacity (objective) — 0–3 per item, 5 items, max 15

| Item | 3 | 2 | 1 | 0 |
|---|---|---|---|---|
| Income stability | tenured / public sector, dual income | stable salaried, single income | variable or commission-based | unemployed, in transition, or single-breadwinner startup |
| Debt service ratio | < 10% | 10–20% | 20–35% | > 35% |
| Horizon (years to first major draw) | > 20 | 10–20 | 5–10 | < 5 |
| Dependants funded | none | one, plus adequate cover | two or more, partial cover | dependants with no cover |
| Investable multiple | > 10× | 5–10× | 2–5× | < 2× |

Mapping to level: **≥12 → 5 · 9–11 → 4 · 6–8 → 3 · 3–5 → 2 · ≤2 → 1**

### 2.2 Willingness (subjective) — questionnaire in `references/risk-profile.md`

8 questions, 0–3 each, max 24. Mapping: **≥19 → 5 · 15–18 → 4 · 11–14 → 3 · 7–10 → 2 · ≤6 → 1**

### 2.3 Combine

```
level = min(capacity_level, willingness_level)
```

**Why the lower, and not the average.** A household that can afford risk but cannot tolerate it will sell in the drawdown, realising the loss the model assumed it would ride out. A household that tolerates risk but cannot afford it has no recovery path if the drawdown coincides with a job loss. Both failure modes are one-sided, so the conservative side wins.

One adjustment is allowed: **if the household is in an income gap (unemployment, career transition, business wind-down), drop one further level.** This is not a judgement about them; it reflects that the emergency bucket is being drawn, not funded.

---

## 3. M3 — Bucket by purpose

| Bucket | Purpose | Size rule | Permitted sleeves |
|---|---|---|---|
| 1 Emergency | job loss, medical, urgent repair | monthly essential spending × months (6 stable dual income; **12–18** if single income, variable income, or in transition) | cash, T-bills, money market |
| 2 Committed ≤3y | down payment, car, tuition, wedding | sum of known outlays, inflated | cash, short-duration bonds, CDs. **No equity — ever.** |
| 3 Goals 5–10y | education, home upgrade | present value of the target at the bucket's expected return | sleeves one to two levels more defensive than the household's level |
| 4 Long money 15y+ | retirement | everything remaining | the household's level mix (§4.1) |

**Ordering is mandatory.** Bucket 2 fully funded before bucket 4 gets a dollar. Households routinely invert this — investing for retirement while carrying a 3-year down-payment in equities is the single most common structural error this framework catches.

---

## 4. M4 — Sizing and gates

### 4.1 Sleeve mix by level, for bucket 4

| Level | US eq | Dev ex-US eq | EM eq | Bonds | Gold | Cash | Expected return | Volatility |
|---|---|---|---|---|---|---|---|---|
| 1 Very Conservative | 10 | 5 | 0 | 70 | 10 | 5 | ~3.8% | ~5% |
| 2 Conservative | 25 | 10 | 3 | 50 | 9 | 3 | ~4.8% | ~8% |
| 3 Balanced | 40 | 15 | 5 | 35 | 5 | 0 | ~5.7% | ~11% |
| 4 Growth | 50 | 18 | 7 | 20 | 5 | 0 | ~6.1% | ~13% |
| 5 Aggressive | 58 | 20 | 10 | 7 | 5 | 0 | ~6.4% | ~15% |

These are starting points with long-run assumptions from `references/assumptions.md`. Verify each with the script rather than trusting the table — the table assumes the default inputs.

### 4.2 Constraint arithmetic — do this before proposing anything

The sleeves sum to 100%. That identity makes some requests arithmetically impossible, and the arithmetic should be shown, not hidden:

```
bond + cash = 100% − equity − gold
```

So "equity ≥ 70%" and "defensive ≥ 30%" cannot both hold. Likewise "bonds ≤ 15%" and "equity ≤ 60%" and "gold ≤ 5%" forces cash = 20%, which may contradict a separate "cash ≤ 10%" preference.

When a user's constraints conflict:
1. Write the identity out with their numbers.
2. Show which constraint must yield, and what each branch costs (in attainment and in p5).
3. Let them choose. Do not average the conflict away.

Also check the **required return** implied by the goal before allocating:

```
required_return ≈ (target ÷ (initial + 0.5 × total_contributions))^(1/years) − 1
```

If required return exceeds the level's expected return by more than 2 percentage points, the goal is not an allocation problem. The fix is a longer horizon, higher saving, or a lower target — in that order.

### 4.3 Attainment gate

| Attainment probability | Verdict |
|---|---|
| ≥ 85% | Deliverable |
| 70–85% | Deliverable, but the stress case must be shown explicitly |
| < 70% | **Not deliverable.** Fix horizon → saving → target. Never raise the assumed return. |

### 4.4 p5 veto — the rule that overrides the attainment gate

**If p5 (the 5th percentile terminal value, i.e. the bad 1-in-20 outcome) falls below the downside line, the plan is rejected even when attainment is high.** The line moves with what is doing the funding, measured by §4.5's savings contribution:

| Savings contribution | p5 line | Why |
|---|---|---|
| > 50% (savings dominate) | **85% of target** | The target is reached mainly by contributions, so a deep bad tail is a *choice*, not a constraint. There is no reason to gamble when saving already does the work. |
| ≤ 50% (compounding carries it) | **65% of target** | Some downside is mathematically unavoidable when returns carry the target. A harsher line would reject every equity-heavy plan and the tool would only ever output one answer. |

A single flat line was tried first and failed calibration: at 85% it rejected a 75/25 growth plan with 80% attainment *and* rejected every 10-year equity plan, which is not a useful verdict. At 65% it would let a savings-dominated household gamble with money it does not need to risk. The split follows the same variable that drives §4.5.

Why a floor at all, rather than reporting p5 and letting the user decide: p5 is not a disaster scenario, it is a plausible one — one bad stretch in twenty. A plan whose bad case lands near the target can be closed with a few extra years of saving, which the household controls. A plan whose bad case lands far short requires the good case to happen, which it does not. The gate is there so that the output cannot quietly become "this works if markets cooperate".

Diagnose it directly — the script prints the applicable line and the ratio:

```bash
python3 scripts/monte_carlo.py ... # prints "p5 VETO" and the basis when violated
```

### 4.5 Savings-contribution diagnosis

```
savings_contribution = (monthly × 12 × years) ÷ target
```

**If savings contribution > 50%, raising equity lowers the attainment probability.** This is counter-intuitive and worth stating in the output.

Mechanism: the geometric return is roughly `μ − σ²/2`. When the plan is mostly funded by contributions, the target is reached through saving, not compounding; the extra `μ` from more equity is small in absolute terms, while the `σ²/2` drag and the fatter left tail are not. Measured on a 20-year, high-saving case, attainment moved 97.0% → 95.2% → 93.6% as equity went 35% → 50% → 65%. It fell monotonically.

So: when savings dominate, the objective is **volatility reduction**, and the report must say "we are damping volatility" rather than "we are improving returns". Never dress up a de-risking decision as a return-enhancing one.

### 4.6 Report attainment and median together

Cutting bonds typically raises the median and lowers p5. Reporting only one of them hides which trade is being made.

| Bonds | 44% | 42% | 40% | 38% | 36% | 32% |
|---|---|---|---|---|---|---|
| Attainment | 90.5% | 90.5% | 90.1% | 89.6% | 89.6% | 89.0% |
| p50 | 686 | 694 | 698 | 704 | 709 | 719 |
| p5 | 461 | 459 | 456 | 451 | 449 | 443 |

*(Illustrative, in the currency's thousands, from a 20-year high-saving case. Each 4pp of bonds traded away buys roughly +10 of median and costs roughly −5 of p5.)*

---

## 5. M5 — Rebalancing

See `references/rebalance_rules` behaviour in `scripts/rebalance.py`. Thresholds scale with position size, because a flat 5pp band never triggers on a 10% sleeve:

| Target weight | Absolute band |
|---|---|
| ≥ 25% | 5pp |
| 10–25% | 3pp |
| < 10% | 2pp |

Rebalance with new contributions first, then income and dividends, then sell overweight positions. A calendar review annually is a backstop, not the primary trigger.

---

## 6. Default assumptions when the user supplies nothing

Fill these, print them on the first screen, and mark what changes if wrong:

| Assumption | Default | If wrong, re-run |
|---|---|---|
| Base currency | USD | bonds and cash assumptions (§`assumptions.md` 5) |
| Mortgage / other debt | none | M1 ratios 2 & 3, M2 capacity, equity ceiling |
| Household | married, no dependants | emergency months, life cover, M2 dependants item |
| Insurance | statutory only | M1 ratio 6 shortfall |
| Monthly essential spending | provided, else 70% of total spending | emergency bucket, liquidity months |
| Income after any transition | user's stated figure | M2 income stability, capacity level |

Assume, label, and proceed. Ask at most one round of questions — a report with a visible assumption list is more useful than an interrogation that never ends.
