---
name: aged-payables
description: Generate an AP Aging report with payment scheduling, early payment discount analysis, and cash coverage assessment. Uses format_aging.py for deterministic output.
---

# Aged Payables

Generate an accounts payable aging report with payment scheduling recommendations.

**How it works:** This command fetches AP aging data via the MCP tool, builds a compact JSON, and runs `scripts/format_aging.py --type ap` — a Python script that produces a consistently formatted markdown report with payment priorities, DPO calculation, discount opportunities, and cash coverage analysis.

## Usage

```
/arfiti-core:aged-payables
```

## Prerequisites

- Transactions must be posted for the period
- Python 3.9+ available (`python3 --version`)

## Step 1: Collect Data

Ask for the legal entity and as-of date, then fetch:

```
generate_report("ap_aging", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})

# For DPO calculation
generate_report("income_statement", {"legal_entity_id": ID, "start_date": "YYYY-01-01", "end_date": "YYYY-MM-DD"})

# For cash coverage
generate_report("balance_sheet", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})
```

## Step 2: Build Input JSON

Build the JSON from report data. See `scripts/input_schema_aging.json` for the full schema.

```json
{
  "entity_name": "Company Name",
  "as_of_date": "YYYY-MM-DD",
  "currency": "EUR",
  "annual_cogs": 1200000.00,
  "cash_balance": 125000.00,
  "due_within_7_days": 18500.00,
  "due_within_14_days": 32000.00,
  "due_within_30_days": 62000.00,
  "parties": [
    {
      "name": "Vendor Name",
      "current": 15000.00,
      "days_1_30": 8000.00,
      "days_31_60": 0.00,
      "days_61_90": 0.00,
      "days_90_plus": 0.00
    }
  ],
  "early_payment_discounts": [
    {
      "name": "Vendor Name",
      "discount_percent": 2.0,
      "discount_days": 10,
      "full_days": 30
    }
  ]
}
```

Write to: `/tmp/ap_aging_{ENTITY_ID}_{DATE}.json`

## Step 3: Run the Formatter

```bash
python3 format_aging.py --input /tmp/ap_aging_{ENTITY_ID}_{DATE}.json --output /tmp/ap_aging_report.md --type ap
```

The script produces a markdown report with:
- **Aging matrix** by vendor and bucket, sorted by largest balance
- **Distribution table** with amounts and percentages per bucket
- **Key metrics**: DPO, total outstanding, overdue percentage, upcoming obligations (7/14/30 days)
- **Cash coverage**: whether current cash can cover outstanding payables
- **Payment recommendations**:
  - Overdue — pay immediately (CRITICAL / HIGH / MEDIUM priority)
  - Due within terms — include in next payment batch
- **Early payment discount analysis**: annualized return calculation and take/skip recommendation

## Step 4: Present Results

Read and present the generated markdown report. Add commentary about cash management strategy if relevant.

## Example Output

```markdown
# Aged Payables
**Acme Corp OÜ** | As of 2026-03-31 | Currency: EUR

## Key Metrics

| Metric | Value |
|--------|-------|
| Days Payable Outstanding (DPO) | 27 days |
| Cash Balance | 125,000.00 |
| Cash Coverage | 141.6% — Sufficient |
| Due within 7 days | 18,500.00 |

## Payment Recommendations

### Overdue — Pay Immediately (2 vendors)
| Vendor | Overdue Amount | Total Balance | Priority |
|---|---|---|---|
| Gamma Tech OÜ | 12,300.00 | 12,300.00 | CRITICAL |

### Early Payment Discount Opportunities
| Vendor | Terms | Discount | Annualized Return | Recommendation |
|---|---|---|---|---|
| Alpha Industries | 2.0%/10 NET 30 | 2.0% | 37.2% | Take discount |
```
