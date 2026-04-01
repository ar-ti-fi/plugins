# Budget Building Methods Reference

## 1. Flat/Even Distribution

Divide an annual target evenly across all periods.

**When to use**: Stable, predictable costs (rent, insurance, subscriptions).

**Formula**: `monthly_amount = annual_target / 12`

```
Annual rent: 60,000
Monthly budget: 60,000 / 12 = 5,000 per month
```

**Rounding**: Round to 2 decimal places. Assign any rounding remainder to the last period.

---

## 2. Growth-Based

Apply a growth rate to prior year actuals.

**When to use**: Revenue projections, cost inflation adjustments.

**Formula**: `new_amount = prior_actual x (1 + growth_rate)`

```
2025 actual revenue (Jan): 42,000
Growth rate: 8%
2026 budget (Jan): 42,000 x 1.08 = 45,360
```

**Variants**:
- **Uniform growth**: Same rate for all accounts and periods
- **Per-account growth**: Revenue +10%, Salaries +3%, Rent +0%
- **Stepped growth**: 5% for H1, 8% for H2 (accelerating growth)

---

## 3. Seasonal Patterns

Apply monthly weight factors to distribute an annual target unevenly.

**When to use**: Businesses with seasonal revenue (retail, tourism, agriculture).

**Formula**: `month_amount = annual_target x weight_factor[month]`

**Example — Retail pattern** (December spike):

| Month | Weight | Budget (Annual: 600K) |
|-------|--------|-----------------------|
| Jan | 6% | 36,000 |
| Feb | 6% | 36,000 |
| Mar | 7% | 42,000 |
| Apr | 7% | 42,000 |
| May | 8% | 48,000 |
| Jun | 8% | 48,000 |
| Jul | 8% | 48,000 |
| Aug | 8% | 48,000 |
| Sep | 9% | 54,000 |
| Oct | 9% | 54,000 |
| Nov | 10% | 60,000 |
| Dec | 14% | 84,000 |
| **Total** | **100%** | **600,000** |

**Validation**: Weights must sum to 100%. After rounding, adjust the largest month to absorb any difference.

**Deriving weights from actuals**: Calculate each month's share of the annual total from prior year actuals, then apply those percentages to the new annual target.

---

## 4. Step Function

Different amounts before and after a known event (new hire, contract start, price change).

**When to use**: Mid-year changes with known dates.

**Example**: New employee starts April 1:
```
Jan-Mar: 0 (no employee yet)
Apr-Dec: 4,500/month (salary + burden)
Annual total: 40,500
```

**Example**: Price increase from July:
```
Jan-Jun: 100/unit x 500 units = 50,000/month
Jul-Dec: 110/unit x 500 units = 55,000/month
Annual total: 630,000
```

---

## 5. Driver-Based

Budget = driver_quantity x cost_per_unit.

**When to use**: Costs that scale with measurable drivers (headcount, units, square footage).

**Common drivers**:

| Driver | Cost Item | Formula |
|--------|-----------|---------|
| Headcount | Office supplies | employees x 50/month |
| Headcount | Software licenses | seats x 25/month |
| Revenue | Sales commissions | revenue x 5% |
| Square meters | Rent | sqm x 15/month |
| Transactions | Payment processing | transactions x 0.30 |

**Example**:
```
Current headcount: 25
Planned Q3 hire: +3
Software license: 25/seat/month

Jan-Jun: 25 x 25 = 625/month
Jul-Dec: 28 x 25 = 700/month
Annual: 7,950
```

---

## 6. Zero-Based

Build from zero — every line item must be justified. No automatic carry-forward.

**When to use**: Cost reduction exercises, new departments, startup budgets.

**Process**:
1. List every expected cost category
2. For each: justify the need and estimate the amount
3. Sum to get the total budget
4. No line exists unless explicitly added

**Difference from growth-based**: Growth-based starts from last year and adjusts. Zero-based starts from scratch — nothing is assumed.

---

## 7. Top-Down vs Bottom-Up

**Top-Down**: Executive sets total targets → allocate to departments/accounts.
```
CFO target: Total OPEX must be < 70% of revenue
Revenue budget: 1,000,000
OPEX cap: 700,000
Allocate: Sales 250K, Engineering 300K, G&A 150K
```

**Bottom-Up**: Departments build their own budgets → roll up to total.
```
Sales requests: 280K
Engineering requests: 320K
G&A requests: 160K
Total: 760K → exceeds 700K cap → negotiate cuts
```

**Hybrid** (recommended): Set top-down targets, let departments build bottom-up within those targets.

---

## Rounding Rules

When calculations produce fractional cents:

1. Calculate each period's amount and round to 2 decimal places
2. Sum all rounded amounts
3. Compare to the target total
4. If difference exists, adjust the **largest period** to absorb the remainder
5. This ensures the annual total matches exactly

**Example**:
```
Annual target: 100,000
Monthly (even): 100,000 / 12 = 8,333.333...
Rounded: 8,333.33 x 12 = 99,999.96
Difference: 0.04

Fix: Set December to 8,333.37 (absorbs the 0.04)
Verify: 11 x 8,333.33 + 8,333.37 = 100,000.00 ✓
```

---

## Combining Methods

Real budgets often combine multiple methods:

- **Revenue**: Seasonal pattern (derived from prior year) x growth rate
- **Salaries**: Driver-based (headcount x rate) + step function (planned hires)
- **Rent**: Flat distribution (known annual amount / 12)
- **Marketing**: Zero-based (campaign-by-campaign justification)
- **Commissions**: Driver-based (budgeted revenue x commission rate)
