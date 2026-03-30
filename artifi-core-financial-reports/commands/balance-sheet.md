---
name: balance-sheet
description: Generate a Balance Sheet with classification validation, comparative periods, and key liquidity ratios. Uses format_balance_sheet.py for deterministic output.
---

# Balance Sheet

Generate a classified balance sheet for a legal entity as of a specific date.

**How it works:** This command fetches balance sheet data via the MCP tool, builds a compact JSON, and runs `scripts/format_balance_sheet.py` — a Python script that produces a consistently formatted markdown report with validation, ratios, and comparative analysis.

## Usage

```
/artifi-core:balance-sheet
```

## Prerequisites

- All transactions for the period must be posted
- Python 3.9+ available (`python3 --version`)

## Step 1: Collect Data

Ask for the legal entity and reporting date, then fetch:

```
generate_report("balance_sheet", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})
```

If comparative period requested:
```
generate_report("balance_sheet", {"legal_entity_id": ID, "as_of_date": "PRIOR-YYYY-MM-DD"})
```

## Step 2: Build Input JSON

Classify accounts using `account_type` and `account_category` properties (see **references/balance-sheet-classification.md**). Build the JSON per `scripts/input_schema_balance_sheet.json`.

```json
{
  "entity_name": "Company Name",
  "as_of_date": "YYYY-MM-DD",
  "currency": "EUR",
  "current_assets": [
    {"name": "Cash and cash equivalents", "category": "cash", "amount": 125000.00},
    {"name": "Trade receivables", "category": "receivable", "amount": 85000.00}
  ],
  "noncurrent_assets": [...],
  "current_liabilities": [...],
  "noncurrent_liabilities": [...],
  "equity": [...],
  "prior": { "...same structure..." }
}
```

Write to: `/tmp/balance_sheet_{ENTITY_ID}_{DATE}.json`

## Step 3: Run the Formatter

```bash
python3 format_balance_sheet.py --input /tmp/balance_sheet_{ENTITY_ID}_{DATE}.json --output /tmp/balance_sheet_report.md
```

The script produces a markdown report with:
- **Classified balance sheet**: Current/non-current assets, current/non-current liabilities, equity
- **Validation**: Assets = Liabilities + Equity (PASS/FAIL)
- **Key ratios**: Current ratio, quick ratio, debt-to-equity, equity ratio
- **Comparative analysis** (if prior period provided): absolute and percentage changes, flags items >10%

## Step 4: Present Results

Read and present the generated markdown report. If validation fails, investigate retained earnings and current year P&L.

## Example Output

```markdown
# Balance Sheet
**Acme Corp OÜ** | As of 2026-03-31 | Currency: EUR

## ASSETS

### Current Assets

  Cash and cash equivalents                    125,000.00
  Trade receivables                             85,000.00
  Inventory                                     45,000.00
  ────────────────────────────────────────────────────────
  **Total Current Assets**                   **275,500.00**

## Validation

| Check | Result |
|-------|--------|
| Assets = Liabilities + Equity | **PASS** (660,500.00 = 660,500.00) |

## Key Ratios

| Ratio | Value | Interpretation |
|-------|-------|----------------|
| Current Ratio | 2.21 | Healthy (target: 1.5-3.0) |
| Debt-to-Equity | 1.00 | Moderate |
```
