---
name: aged-receivables
description: Generate an AR Aging report with collection priority recommendations, DSO calculation, and concentration risk analysis. Uses format_aging.py for deterministic output.
---

# Aged Receivables

Generate an accounts receivable aging report with actionable collection recommendations.

**How it works:** This command fetches AR aging data via the MCP tool, builds a compact JSON, and runs `scripts/format_aging.py --type ar` — a Python script that produces a consistently formatted markdown report with collection priorities, DSO calculation, and concentration analysis.

## Usage

```
/artifi-core:aged-receivables
```

## Prerequisites

- Transactions must be posted for the period
- Python 3.9+ available (`python3 --version`)

## Step 1: Collect Data

Ask for the legal entity and as-of date, then fetch:

```
generate_report("ar_aging", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})
```

Also fetch annual revenue for DSO calculation:

```
generate_report("income_statement", {"legal_entity_id": ID, "start_date": "YYYY-01-01", "end_date": "YYYY-MM-DD"})
```

## Step 2: Build Input JSON

Build the JSON from the report data. See `scripts/input_schema_aging.json` for the full schema.

```json
{
  "entity_name": "Company Name",
  "as_of_date": "YYYY-MM-DD",
  "currency": "EUR",
  "annual_revenue": 2000000.00,
  "parties": [
    {
      "name": "Customer Name",
      "current": 15000.00,
      "days_1_30": 8000.00,
      "days_31_60": 0.00,
      "days_61_90": 0.00,
      "days_90_plus": 0.00
    }
  ]
}
```

Write to a temporary file: `/tmp/ar_aging_{ENTITY_ID}_{DATE}.json`

## Step 3: Run the Formatter

```bash
python3 format_aging.py --input /tmp/ar_aging_{ENTITY_ID}_{DATE}.json --output /tmp/ar_aging_report.md --type ar
```

The script produces a markdown report with:
- **Aging matrix** by customer and bucket, sorted by largest balance
- **Distribution table** showing amounts and percentages per bucket
- **Key metrics**: DSO, total outstanding, overdue percentage, top 5 concentration
- **Collection priorities** categorized as:
  - Urgent (90+ days) — phone call + formal demand letter
  - Action needed (61-90 days) — written reminder + follow-up
  - Monitor (31-60 days) — email reminder
  - Current — no action needed

## Step 4: Present Results

Read and present the generated markdown report to the user. Add any additional commentary about trends or specific customers if relevant.

## Example Output

```markdown
# Aged Receivables
**Acme Corp OÜ** | As of 2026-03-31 | Currency: EUR

## Aging Summary

| Customer | Current | 1-30 days | 31-60 days | 61-90 days | 90+ days | **Total** |
|---|---------|-----------|------------|------------|----------|-----------|
| Alpha Industries | 15,000.00 | 8,000.00 | — | — | — | **23,000.00** |
| Delta Corp | 22,000.00 | — | — | — | — | **22,000.00** |
| Gamma Tech OÜ | — | — | — | 4,500.00 | 7,800.00 | **12,300.00** |
| **TOTAL** | **50,500.00** | **13,500.00** | **12,000.00** | **4,500.00** | **7,800.00** | **88,300.00** |

## Key Metrics

| Metric | Value |
|--------|-------|
| Days Sales Outstanding (DSO) | 16 days |
| Total Outstanding | 88,300.00 |
| Overdue Amount | 37,800.00 (42.8%) |

## Collection Priorities

### Urgent — 90+ Days (1 customer)
| Customer | 90+ Amount | Total Balance | Action |
|---|---|---|---|
| Gamma Tech OÜ | 7,800.00 | 12,300.00 | Phone call + formal demand letter |
```
