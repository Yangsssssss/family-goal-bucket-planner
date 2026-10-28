# family-goal-bucket-planner

**Plan a household portfolio by goal buckets, not by expected return.**

Most allocation tools answer "what mix maximises return for a given risk?" That is the wrong question for a household. This one answers: *how much belongs in each of four purpose buckets, what does each bucket hold, what is the probability the plan reaches its targets — and what happens in the bad one-in-twenty case.*

Zero dependencies. Python standard library only. Runs anywhere.

## Install

```bash
npx skills add https://github.com/yangsssssss/family-goal-bucket-planner
```

Or copy the folder into your agent's skills directory. Any agent that reads `SKILL.md` can use it.

## Use

Ask in plain language:

- "I have $400k and can save $2,000 a month. How should I split it?"
- "Will I reach $1.2M in 20 years?"
- "How much should I keep in cash?"
- "Is this portfolio too aggressive for me?"
- "How much do I need to save each month to hit my number?"

No arguments to memorise. The skill runs a health check, sets a risk level, splits the money into buckets, and tests the plan.

## What makes it different

**1. It tells you when more equity would *lower* your odds.**

When contributions do more than half the funding, the target is reached by saving rather than compounding. At that point the extra expected return is small in absolute terms while the volatility drag and the fatter left tail are not. Measured on a high-saving 20-year case, attainment moved **97.0% → 95.2% → 93.6%** as equity went 35% → 50% → 65% — monotonically down.

So the output says "we are reducing volatility", not "we are improving returns". Dressing up a de-risking decision as a return decision is the most common way these plans get sold badly.

**2. The downside veto is two-tier, because one line does not fit both cases.**

A flat "bad case must reach 85% of target" rule sounds prudent and fails in practice: it rejects every equity-heavy plan, including ones that are entirely reasonable, so the tool ends up capable of only one answer. The line scales with what funds the plan:

| Savings contribution | p5 line | Reasoning |
|---|---|---|
| > 50% | 85% of target | Saving does the work — a deep tail is a choice, not a constraint |
| ≤ 50% | 65% of target | Returns carry the target — some downside is unavoidable |

Both numbers are stated in the output, with the basis, so you can see which rule was applied rather than trusting a black box.

**3. It refuses to invent weights that do not add up.**

Because every sleeve allocation sums to 100%, some requested combinations are arithmetically impossible — "equity above 70%" and "defensive at least 30%" cannot both hold. Rather than quietly averaging the conflict away, the skill writes out the identity, shows which constraint has to yield, and prices each branch. If you ask for something that cannot exist, you get the arithmetic instead of a plausible-looking table.

**4. Bucket ordering is enforced.**

The committed-spending bucket must be fully funded before long-term money receives anything. Households routinely invert this — investing for retirement while a three-year down payment sits in equities — and it is the single most common structural error this framework catches.

**5. Risk level is the lower of capacity and willingness.**

Not the average. A household that can afford risk but cannot tolerate it sells in the drawdown; one that tolerates risk but cannot afford it has no recovery path if the drawdown coincides with a job loss. Both failure modes are one-sided.

## Example

```
$ python3 scripts/monte_carlo.py --initial 400 --monthly 2.0 --years 20 \
      --target 1200 --weights us:40,dev:15,em:5,bond:35,gold:5

Mix         : US equity 40% / Dev ex-US equity 15% / EM equity 5% / Bonds (IG) 35% / Gold 5%
Expected    : 5.67%/yr   Volatility 10.00%/yr   Geometric 5.20%
Drag        : 0.47pp/yr lost to volatility
Equity      : 60%   Defensive 40%   Largest sleeve 40%
Start       : 400.00 + 2.00/mo x 20y = 880.00 contributed
Target      : 1200.00
Required    : 3.19%/yr to hit target
----------------------------------------------------------------
Attainment  : 91.8%   (20000 paths, seed=42)
Terminal    : p5 1097.1 / p25 1536.1 / p50 1963.4 / p75 2542.1 / p95 3665.4
p5 shortfall: 102.9
p5 vs target: 91%  (line 65% - compounding carries the target: some downside is unavoidable)
Savings     : 40% of target comes from contributions
----------------------------------------------------------------
VERDICT: >=85% and p5 clear - plan is sound.
```

Same inputs, target raised to 2200 and the mix pushed to all-equity: attainment 45.2%, p5 at 41% of target, and the tool returns `p5 VETO` with a reason — rather than a table of weights that would have looked fine.

## Files

```
SKILL.md                          workflow and hard rules
references/framework.md           thresholds, scoring, bucket sizing, the four gates
references/risk-profile.md        8-question willingness questionnaire
references/assumptions.md         return / volatility / correlation table, failure conditions
scripts/monte_carlo.py            attainment, terminal percentiles, p5 veto, FX test
scripts/rebalance.py              size-scaled rebalance bands and trade sizing
assets/plan_template.md           one-page output format
```

## Limits — read these

- **Returns, volatilities and correlations are long-run assumptions, not forecasts.** Everything downstream inherits their error. Assumptions are in `references/assumptions.md` and in the `ASSUMPTIONS` dict of the script; if your base currency is not USD, adjust the bond and cash figures to your local risk-free rate before using it.
- **Normal monthly returns, no fat tails.** Real markets have fatter tails, so the true p5 is somewhat worse than reported. Do not read a passing p5 as a guarantee.
- **Strategic allocation only.** No tactical signal, no market timing, no individual securities, no tax modelling.
- **Not investment, tax, or legal advice.** No securities are recommended and no return is promised. Educational planning tool.

## Licence

MIT.
