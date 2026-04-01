---
name: financial-summary
description: Generate an executive financial summary combining BS, P&L, Cash Flow, and ratios. Uses format_financial_summary.py for deterministic output.
---

# Financial Summary

Generate a comprehensive executive summary combining all key financial data.

**How it works:** This command fetches balance sheet, P&L, and cash flow data via MCP tools, builds a compact JSON, and runs `scripts/format_financial_summary.py` — a Python script that produces a single-page executive overview with ratios and key takeaways.

## Usage

```
/artifi-core:financial-summary
```

## Prerequisites

- All transactions for the period must be posted
- Python 3.9+ available (`python3 --version`)

## Step 1: Collect Data

Ask for the legal entity and reporting period, then fetch all three reports:

```
generate_report("balance_sheet", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})
generate_report("income_statement", {"legal_entity_id": ID, "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"})
generate_report("cash_flow_statement", {"legal_entity_id": ID, "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"})
```

If comparative period requested, also fetch prior period data.

## Step 2: Build Input JSON

Combine data from all reports. See `scripts/input_schema_financial_summary.json` for the full schema.

```json
{
  "entity_name": "Company Name",
  "period_start": "YYYY-MM-DD",
  "period_end": "YYYY-MM-DD",
  "currency": "EUR",
  "pnl": {
    "revenue": 500000.00,
    "cogs": 220000.00,
    "operating_expenses": 160000.00,
    "depreciation": 12000.00,
    "interest_expense": 5400.00,
    "net_profit": 58000.00
  },
  "balance_sheet": {
    "cash": 125000.00,
    "receivables": 85000.00,
    "inventory": 45000.00,
    "current_assets": 275500.00,
    "total_assets": 660500.00,
    "payables": 62000.00,
    "current_liabilities": 124500.00,
    "total_liabilities": 329500.00,
    "total_equity": 331000.00
  },
  "cash_flow": {
    "operating": 72000.00,
    "investing": -18000.00,
    "financing": -25000.00,
    "capex": -15000.00
  }
}
```

Write to: `/tmp/financial_summary_{ENTITY_ID}_{DATE}.json`

## Step 3: Run the Formatter

```bash
python3 format_financial_summary.py --input /tmp/financial_summary_{ENTITY_ID}_{DATE}.json --output /tmp/summary_report.md
```

The script produces:
- **P&L snapshot**: Revenue, gross profit, operating profit, EBITDA, net profit with margins
- **Balance sheet snapshot**: Cash, assets, liabilities, equity
- **Cash flow snapshot**: Operating, investing, financing, free cash flow
- **Ratio dashboard**: Liquidity, profitability, leverage, efficiency ratios with assessments
- **Key takeaways**: 3-5 bullet points highlighting the most important findings

## Step 4: Present Results

Read and present the generated markdown report.

## Example Output

```markdown
# Financial Summary
**Acme Corp OÜ** | Period: 2026-01-01 to 2026-03-31 | Currency: EUR

## Profit & Loss

| | Amount | % of Revenue |
|---|--------|-------------|
| Revenue | 500,000.00 | 100.0% |
| Gross Profit | 280,000.00 | 56.0% |
| **Net Profit** | **58,000.00** | **11.6%** |

## Financial Ratios

| Category | Ratio | Value | Assessment |
|----------|-------|-------|------------|
| Liquidity | Current Ratio | 2.21 | Healthy |
| Profitability | Net Margin | 11.6% | |
| Leverage | Debt-to-Equity | 1.00 | Moderate |
| Efficiency | DSO | 62 days | |

## Key Takeaways

- Net profit of 58,000.00 (11.6% margin)
- Strong cash generation: operating CF (72,000.00) exceeds net profit
- Revenue grew 23.5% vs prior period
```
