# Long-run assumptions

> **These are assumptions, not forecasts.** They are rounded long-run historical figures with a downward bias applied to equity returns, expressed in nominal USD. Monte-Carlo output inherits every error in this table. Never present a result computed from these numbers as a prediction.

---

## 1. Sleeve assumptions

| Code | Sleeve | Expected return | Volatility | Worst 12m (historical) | Notes |
|---|---|---|---|---|---|
| `us` | US equity (total market) | 7.0% | 16% | −37% | Valuation-dependent; current CAPE above median means the realised 10y figure may be lower |
| `dev` | Developed ex-US equity | 6.5% | 17% | −42% | Currency adds an unhedged return component |
| `em` | Emerging market equity | 6.5% | 23% | −53% | Governance and currency risk dominate in stress |
| `bond` | Investment-grade bonds (intermediate) | 4.0% | 6% | −15% | **Most sensitive assumption** — see §4 |
| `gold` | Gold | 3.5% | 16% | −41% | No cash flow; a hedge and a currency substitute, not an income asset |
| `cash` | Cash / T-bills / money market | 2.5% | 1% | 0% | Assumed to track the policy rate |

All figures are nominal. For a real-return view, subtract expected inflation (~2.5%) from each — but keep the whole analysis in one convention; mixing nominal and real is a common and invisible error.

## 2. Correlation matrix

| | us | dev | em | bond | gold | cash |
|---|---|---|---|---|---|---|
| **us** | 1.00 | 0.85 | 0.70 | 0.05 | 0.05 | 0.00 |
| **dev** | 0.85 | 1.00 | 0.75 | 0.05 | 0.10 | 0.00 |
| **em** | 0.70 | 0.75 | 1.00 | 0.00 | 0.15 | 0.00 |
| **bond** | 0.05 | 0.05 | 0.00 | 1.00 | 0.20 | 0.15 |
| **gold** | 0.05 | 0.10 | 0.15 | 0.20 | 1.00 | 0.00 |
| **cash** | 0.00 | 0.00 | 0.00 | 0.15 | 0.00 | 1.00 |

**Correlations are not stable.** Equity-sleeve correlations converge toward 1 in a crisis, which is precisely when the diversification is supposed to work. The matrix above describes ordinary periods. A stress test should assume equity correlations of 0.9+ and a bond-equity correlation that can turn positive when inflation is the shock.

## 3. What the assumptions imply

At these figures, a 60/40 portfolio has an expected return near 5.6% and volatility near 10%. The equity risk premium over cash is roughly 4.5pp — reasonable historically, thin relative to the last decade's realised outcome, and the number most likely to disappoint.

## 4. Failure conditions — when to stop and re-derive

Re-derive the table, do not patch it, if any of the following holds:

- **Policy rate or 10-year yield moves more than 150bp** from the level used here → `bond` and `cash` are invalid, and every conclusion about the bond/equity trade-off changes.
- **Sustained inflation above 4%** → nominal assumptions overstate real outcomes; convert the whole analysis to real terms.
- **Base currency is not USD** → see §5.
- **A single-sleeve allocation above 50%** → the portfolio's behaviour is that sleeve's behaviour; the correlation matrix is no longer doing useful work.

## 5. Using a different base currency

The script's defaults are USD. For another base currency, adjust only `bond` and `cash`, and leave the equity sleeves alone:

```
bond_return  ≈ local 10y government yield − expected default/liquidity spread
cash_return  ≈ local policy rate − 0.5%
```

Sleeves `dev` and `em` then become foreign-currency exposure for that household. Quantify it rather than mentioning it qualitatively:

```
FX impact on portfolio ≈ foreign_currency_share × appreciation of the base currency
```

Example: 55% in `us + dev + em`, base currency appreciates 10% → the portfolio loses 5.5pp, roughly a year of expected return, while the household's future liabilities are unchanged.

To apply this in the script, keep the same sleeve codes and edit the `ASSUMPTIONS` dict at the top of `scripts/monte_carlo.py`. **Update this file in the same commit** — a script that disagrees with its documentation is worse than either alone.

## 6. What is deliberately absent

- **No tactical or valuation signal.** This is a strategic allocation tool. Market timing belongs in a separate decision with its own evidence standard.
- **No individual securities.** Sleeve level only. Naming funds would make the output jurisdiction-specific and is not what this skill is for.
- **No tax modelling.** Account location and tax drag are material and entirely jurisdiction-dependent; state the omission in the output rather than approximating it.
