---
name: dimension-analysis
description: Generate a P&L breakdown by dimension (department, project, cost center) with profitability ranking. Uses format_dimension_analysis.py for deterministic output.
---

# Dimension Analysis

Analyze profitability by department, project, cost center, or any custom dimension.

**How it works:** This command fetches dimension-level P&L data via the MCP tool, builds a compact JSON, and runs `scripts/format_dimension_analysis.py` — a Python script that produces a consistently formatted P&L matrix with profitability ranking, budget variance, and recommendations.

## Usage

```
/arfiti-core:dimension-analysis
```

## Prerequisites

- Transactions must have dimension tags for meaningful analysis
- Python 3.9+ available (`python3 --version`)

## Step 1: Discover Dimensions

Ask for the legal entity and date range, then discover available dimensions:

```
list_entities("dimension_value", {"legal_entity_id": ID})
```

Present options and let the user choose which dimension to analyze.

## Step 2: Collect Data

```
generate_report("dimension_analysis", {
    "legal_entity_id": ID,
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "dimension_type": "department"
})
```

If budget data exists:
```
generate_report("variance_summary", {"legal_entity_id": ID, "start_date": "...", "end_date": "..."})
```

## Step 3: Build Input JSON

See `scripts/input_schema_dimension.json` for the full schema.

```json
{
  "entity_name": "Company Name",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "currency": "EUR",
  "dimension_type": "Department",
  "unallocated_amount": 12500.00,
  "dimensions": [
    {
      "name": "Sales",
      "revenue": 380000.00,
      "direct_costs": 95000.00,
      "operating_expenses": 38000.00,
      "prior": {"contribution": 198000.00},
      "budget": {"contribution": 230000.00}
    }
  ]
}
```

Write to: `/tmp/dimension_{ENTITY_ID}_{TYPE}_{DATE}.json`

## Step 4: Run the Formatter

```bash
python3 format_dimension_analysis.py --input /tmp/dimension_{ENTITY_ID}_{TYPE}_{DATE}.json --output /tmp/dimension_report.md
```

The script produces:
- **P&L matrix**: Revenue, direct costs, gross profit, operating expenses, contribution per dimension
- **Margin percentages**: Gross margin and contribution margin per dimension
- **Profitability ranking**: Dimensions ranked by contribution with health status
- **Unallocated warning**: Flags if >20% of transactions lack dimension tags
- **Period comparison** (if prior data): changes with variance flags
- **Budget variance** (if budget data): actual vs budget with favorable/unfavorable status
- **Recommendations**: Actionable items for underperforming dimensions

## Step 5: Present Results

Read and present the generated markdown report.

## Example Output

```markdown
# Dimension Analysis
**Acme Corp OÜ** | 2026-01-01 to 2026-03-31 | By: Department | Currency: EUR

## P&L by Department

| | Sales | Marketing | Engineering | Operations | **Total** |
|---|---|---|---|---|---|
| Revenue | 380,000.00 | 50,000.00 | — | 20,000.00 | **450,000.00** |
| Direct costs | (95,000.00) | (15,000.00) | — | (45,000.00) | **(155,000.00)** |
| **Contribution** | 247,000.00 | -7,000.00 | -120,000.00 | -57,000.00 | **63,000.00** |

## Profitability Ranking

| Rank | Department | Contribution | Margin | Status |
|------|---|---|---|---|
| 1 | Sales | 247,000.00 | 65.0% | Healthy |
| 2 | Marketing | -7,000.00 | -14.0% | Below breakeven |

## Recommendations

- **Marketing**: Negative contribution (-7,000.00). Review pricing or cost structure.
- **Unallocated**: 12,500.00 untagged. Assign department tags for accuracy.
```
