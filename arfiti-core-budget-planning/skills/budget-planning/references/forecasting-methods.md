# Forecasting Methods Reference

Use these methods when creating a mid-year forecast (Mode 3). The goal is to blend YTD actuals with projected amounts for remaining months to produce a full-year outlook.

## Setup

Before applying any method, gather:
- **YTD Actuals**: Actual GL amounts for completed months (from `generate_report`)
- **Original Budget**: Approved budget line amounts for all 12 months
- **Prior Year Actuals**: Same period last year (optional, for seasonal methods)
- **Current Month**: The dividing line between actuals and projections

## 1. Run Rate

Extrapolate from YTD performance assuming the current pace continues.

**Formula**: `forecast_remaining = (ytd_actual / months_elapsed) x months_remaining`

**Example** (through June, forecasting Jul-Dec):
```
YTD Revenue (Jan-Jun): 285,000
Monthly run rate: 285,000 / 6 = 47,500
Forecast (Jul-Dec): 47,500 x 6 = 285,000
Full-year forecast: 285,000 + 285,000 = 570,000
Original budget: 540,000
Variance: +30,000 (5.6% favorable)
```

**Best for**: Stable businesses with even monthly patterns.
**Weakness**: Ignores seasonality — will over/underestimate if H2 is naturally different from H1.

---

## 2. Linear Trend

Fit a line to the YTD monthly data points and extrapolate forward.

**Formula**: Use least-squares regression on monthly actuals to find slope and intercept, then project.

**Example**:
```
Month:   Jan    Feb    Mar    Apr    May    Jun
Actual:  42K    44K    45K    47K    48K    49K

Trend line: y = 41,333 + 1,400 x month_number
July forecast: 41,333 + 1,400 x 7 = 51,133
August forecast: 41,333 + 1,400 x 8 = 52,533
... and so on
```

**Best for**: Growing or declining businesses with a clear trend.
**Weakness**: Assumes linear growth continues — can be unrealistic for long projections.

---

## 3. Seasonal Adjusted

Apply the prior year's seasonal pattern to the current year's run rate.

**Formula**:
1. Calculate prior year monthly weights: `weight[m] = prior_year_month[m] / prior_year_total`
2. Calculate current annual run rate: `run_rate = ytd_actual / sum(weights for elapsed months)`
3. Project remaining months: `forecast[m] = run_rate x weight[m]`

**Example** (using prior year seasonal pattern):
```
Prior year (2025):
  Jan: 40K (7%), Feb: 38K (7%), Mar: 42K (7%), Apr: 45K (8%), May: 48K (8%), Jun: 50K (9%)
  Jul: 52K (9%), Aug: 50K (9%), Sep: 55K (10%), Oct: 58K (10%), Nov: 60K (10%), Dec: 62K (11%)
  Total: 600K

2026 YTD actual (Jan-Jun): 285K
2025 H1 weight: 7+7+7+8+8+9 = 46%
Implied annual run rate: 285K / 0.46 = 619.6K

July forecast: 619.6K x 9% = 55.8K
August forecast: 619.6K x 9% = 55.8K
... apply each month's weight
```

**Best for**: Seasonal businesses (retail, tourism, agriculture, B2B with fiscal year-end spikes).
**Weakness**: Assumes the seasonal pattern is stable year-over-year.

---

## 4. Three-Month Moving Average

Use the average of the last 3 completed months as the forecast for each remaining month.

**Formula**: `forecast[m] = (actual[m-1] + actual[m-2] + actual[m-3]) / 3`

As each month completes, the window slides forward (but for forecasting all at once, use the most recent 3 months for all remaining months).

**Example** (through June):
```
April actual: 47K, May actual: 48K, June actual: 49K
Moving average: (47 + 48 + 49) / 3 = 48K

Jul-Dec forecast: 48K each = 288K
Full year: 285K (YTD) + 288K = 573K
```

**Best for**: Smoothing out volatile months. Good default when no strong trend or seasonality.
**Weakness**: Assumes recent performance is representative of the future.

---

## 5. Budget-to-Actual Blending

Adjust the remaining budget months by the YTD variance trend.

**Formula**:
1. Calculate YTD variance %: `(ytd_actual - ytd_budget) / ytd_budget`
2. Apply adjustment to remaining budget months: `forecast[m] = budget[m] x (1 + variance_trend)`

**Example**:
```
YTD budget: 270K, YTD actual: 285K
Variance: +5.6%

Remaining budget months (Jul-Dec): 270K total
Adjusted forecast: 270K x 1.056 = 285,120
Full-year forecast: 285K + 285.1K = 570.1K
```

**Variants**:
- **Uniform adjustment**: Apply same % to all remaining months
- **Converging**: Gradually reduce the adjustment (assume performance normalizes)
- **Per-account**: Calculate variance % per account and apply individually

**Best for**: When the budget was reasonably accurate but actual performance is slightly above/below.
**Weakness**: Assumes the variance trend continues unchanged.

---

## 6. What-If Scenarios

Create multiple forecast versions to model different outcomes.

**Scenarios**:
- **Base case**: Most likely outcome (use any method above)
- **Optimistic**: Best case (e.g., +10% on base)
- **Pessimistic**: Worst case (e.g., -15% on base)

**Implementation**:
```python
# Create base forecast
submit("budget_version", "create", {..., "scenario": "forecast", "version_name": "FY2026 Forecast - Base"})

# Create stretch (optimistic)
submit("budget_version", "create", {..., "scenario": "stretch", "version_name": "FY2026 Forecast - Optimistic"})
```

Use `scenario` field to distinguish:
- `budget` = original annual budget
- `forecast` = revised projection (base case)
- `stretch` = aspirational / optimistic target

---

## Choosing a Method

| Situation | Recommended Method |
|-----------|-------------------|
| Stable business, even months | Run Rate |
| Clear growth/decline trend | Linear Trend |
| Strong seasonal pattern | Seasonal Adjusted |
| Volatile month-to-month | Moving Average |
| Budget was close to actuals | Budget-to-Actual Blending |
| Multiple possible outcomes | What-If Scenarios |

**Default recommendation**: Start with Run Rate for simplicity. If the user mentions seasonality, switch to Seasonal Adjusted. If they want to compare scenarios, use What-If.

---

## Presentation Format

Always show the forecast in a clear table with:
- (A) markers for actual months
- (F) markers for forecast months
- Original budget comparison
- Variance column

```
| Account | Jan (A) | Feb (A) | ... | Jun (A) | Jul (F) | ... | Dec (F) | FY Total | vs Budget |
```
