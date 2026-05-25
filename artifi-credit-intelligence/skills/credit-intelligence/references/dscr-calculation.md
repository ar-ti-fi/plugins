# DSCR & related coverage / leverage ratios

Definitions, formulas, and the GL-account lookups they depend on.

## EBITDA — the foundation

Everything downstream depends on consistently-built EBITDA. Use this build:

```
EBITDA = Revenue
       − Cost of sales
       − Operating expenses (excluding depreciation, amortization, interest, tax)
```

In the standard IFRS chart-of-accounts that comes out of Arfiti onboarding:

| Component | Account-type filter |
|---|---|
| Revenue | `account_type='revenue'` AND `account_subtype LIKE 'operating_revenue%'` (exclude `interest`, `dividend`, `fx_gain`, `other_revenue_gain`) |
| Cost of sales | `account_type='expense'` AND `account_subtype LIKE 'cogs_%'` |
| Operating expenses | `account_type='expense'` AND `account_subtype IN ('operating_expense', 'salaries_expense', 'employee_benefits_expense', 'payroll_withholding')` |
| **EXCLUDE from opex** | `account_subtype IN ('depreciation_expense', 'amortisation_expense', 'interest_expense', 'fx_loss', 'tax_expense_current', 'other_expense')` |

The exclusions are critical — they're the difference between EBITDA and Operating Profit. Forgetting to exclude depreciation gives Operating Profit (OP), not EBITDA.

**Don't hardcode account numbers.** Different orgs and countries have different COA layouts. Filter by `account_type` and `account_subtype`. If you're unsure, dump the COA via `list_entities("account", ...)` and check the subtypes present.

## Trailing-12-month EBITDA

For DSCR and leverage, we use the trailing 12 months of EBITDA. Build it as the sum of EBITDA across the 12 most recent monthly periods ending at as-of date.

If the borrower is less than 12 months old, annualize: `EBITDA_TTM = sum(months_available) × (12 / months_available)`. Flag in the output that this is annualized, not actual TTM.

## Debt service — the denominator of DSCR

```
Annual debt service = Annual interest expense + Scheduled principal repayments
```

**Interest expense** (TTM): sum of expenses where `account_subtype = 'interest_expense'` over last 12 months. In the standard COA this includes `Finance Costs` (~7000) and `Lease Interest` (~7060).

**Scheduled principal repayments** (forward 12 months): this is the harder one. The GL records actual principal *paid*, not scheduled future payments. Two approaches:

1. **Look at last-12-months actual principal paid** as a proxy for next-12-months scheduled. Works if amortization is roughly linear. Compute by finding the trailing-12 decrease in `current_portion_of_long_term_borrowings` (~2610) plus the trailing-12 decrease in `long_term_borrowings` (~2800).
2. **Ask the user** for the loan amortization schedule if it isn't in the books — for a real credit memo, this is more accurate.

Method 1 is fine for the headline `/credit-read`. Method 2 is what `/covenant-monitor` should prefer when projecting forward.

## DSCR

```
DSCR = EBITDA_TTM / annual_debt_service
```

**Interpretation:**

| Range | Read |
|---|---|
| > 2.50x | Comfortable — significant cushion |
| 1.50–2.50x | Healthy |
| 1.20–1.50x | Tight — monitor closely |
| 1.00–1.20x | At the edge — likely near covenant minimum |
| < 1.00x | EBITDA insufficient to service debt — high concern |

A typical Italian SME term-loan covenant is **DSCR ≥ 1.20x**. Mediterranean / SME markets sometimes go as low as 1.10x. Always check the actual loan documentation when available.

## Leverage (Net Debt / EBITDA)

```
Net Debt = Short-term borrowings + Current portion of LT debt + Long-term debt − Cash and equivalents
Leverage = Net Debt / EBITDA_TTM
```

In the standard COA:
- Short-term borrowings: `account_number = '2600'`
- Current portion: `'2610'`
- Long-term debt: `'2800'`
- Lease liabilities: `'2820'` + `'2830'` (include in net debt for full leverage view)
- Cash: all `account_subtype IN ('cash', 'bank')` and not bank_clearing

**Interpretation:**

| Range | Read |
|---|---|
| < 2.00x | Low leverage |
| 2.00–3.00x | Moderate |
| 3.00–4.00x | High |
| > 4.00x | Very high — likely covenant trigger |

Typical SME covenant: **Net Debt / EBITDA ≤ 3.50x**.

## Interest Coverage Ratio (ICR)

```
ICR = EBITDA_TTM / Interest expense TTM
```

A subset of DSCR that strips out principal repayment. Useful when principal schedule isn't reliable in the books.

**Interpretation:**

| Range | Read |
|---|---|
| > 5.00x | Strong |
| 3.00–5.00x | Healthy |
| 2.00–3.00x | Tight |
| < 2.00x | Pressured |

Typical covenant: **ICR ≥ 3.00x**.

## Sanity bands

When computing these ratios, if they fall outside these bands, **investigate before reporting**:

| Ratio | Sane range | If outside, check |
|---|---|---|
| EBITDA / Revenue | -10% to 40% | Expense classification (depreciation buried in opex? interest in opex?) |
| DSCR | 0.5x to 4.0x | Missing principal payments in numerator; or non-operating gains inflating EBITDA |
| Leverage | -1.0x to 6.0x | Negative is fine (more cash than debt); very high or low → look for missing debt accounts |
| Cash days on hand | 5–180 days | Outside this typically means the cash account has uncleared items |

Surface the issue to the user before generating the memo. A 12x DSCR or -3x leverage in a presented memo destroys credibility.
