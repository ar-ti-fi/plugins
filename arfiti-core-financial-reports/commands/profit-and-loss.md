---
name: profit-and-loss
description: Generate a Profit & Loss (Income Statement) with margin analysis and period-over-period comparison. Uses format_income_statement.py for deterministic output.
---

# Profit & Loss

Generate an income statement for a legal entity over a date range.

**How it works:** This command fetches P&L data via the MCP tool, builds a compact JSON, and runs `scripts/format_income_statement.py` — a Python script that produces a consistently formatted markdown report with margins, variance analysis, and EBITDA.

## Usage

```
/arfiti-core:profit-and-loss
```

## Prerequisites

- All transactions for the period must be posted
- Python 3.9+ available (`python3 --version`)

## Step 1: Collect Data

Ask for the legal entity and date range, then fetch:

```
generate_report("income_statement", {"legal_entity_id": ID, "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"})
```

If comparative period requested:
```
generate_report("income_statement", {"legal_entity_id": ID, "start_date": "PRIOR-START", "end_date": "PRIOR-END"})
```

## Step 2: Build Input JSON

Classify revenue and expenses using `account_type` and `account_category` (see **references/income-statement-structure.md**). Build per `scripts/input_schema_income_statement.json`.

```json
{
  "entity_name": "Company Name",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "currency": "EUR",
  "revenue": [{"name": "Product sales", "amount": 380000.00}],
  "cogs": [{"name": "Cost of goods sold", "amount": 220000.00}],
  "expenses": [
    {"name": "Employee costs", "amount": 95000.00},
    {"name": "Depreciation and amortization", "amount": 12000.00}
  ],
  "financial_income": [{"name": "Interest income", "amount": 1200.00}],
  "financial_expenses": [{"name": "Interest expense", "amount": 4800.00}],
  "income_tax": [{"name": "Income tax", "amount": 0.00}],
  "prior": { "...same structure..." }
}
```

Write to: `/tmp/pnl_{ENTITY_ID}_{START}_{END}.json`

## Step 3: Run the Formatter

```bash
python3 format_income_statement.py --input /tmp/pnl_{ENTITY_ID}_{START}_{END}.json --output /tmp/pnl_report.md
```

The script produces:
- **Structured P&L**: Revenue, COGS, gross profit, expenses, operating profit, financial items, tax, net profit
- **Margin analysis**: Gross margin %, operating margin %, net margin %, EBITDA
- **Comparative table** (if prior period): absolute and percentage changes, flags items >15%

## Step 4: Present Results

Read and present the generated markdown report. Verify net profit matches the balance sheet current year result.

## Example Output

```markdown
# Profit & Loss Statement
**Acme Corp OÜ** | 2026-01-01 to 2026-03-31 | Currency: EUR

| | Current | Prior | Change | % |
|---|---------|-------|--------|---|
| **Total Revenue** | **500,000.00** | **405,000.00** | +95,000.00 | +23.5% ⚠️ |
| **Gross Profit** | **280,000.00** | **210,000.00** | +70,000.00 | +33.3% ⚠️ |
| **Net Profit / (Loss)** | **115,800.00** | **72,550.00** | +43,250.00 | +59.6% ⚠️ |

## Margin Analysis

| Metric | Value |
|--------|-------|
| Gross Margin | 56.0% |
| Operating Margin | 24.4% |
| Net Margin | 23.2% |
| EBITDA | 134,000.00 (26.8%) |
```
