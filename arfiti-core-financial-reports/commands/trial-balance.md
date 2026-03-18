---
name: trial-balance
description: Generate a Trial Balance with debit/credit validation, unusual balance detection, and optional period comparison.
---

# Trial Balance

Generate a trial balance for a legal entity as of a specific date.

**How it works:** This command fetches trial balance data via the MCP tool and presents it in a structured format with validation and anomaly detection.

## Usage

```
/arfiti-core:trial-balance
```

## Step 1: Collect Data

Ask for the legal entity and as-of date, then fetch:

```
generate_report("trial_balance", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})
```

If comparative date requested:
```
generate_report("trial_balance", {"legal_entity_id": ID, "as_of_date": "PRIOR-YYYY-MM-DD"})
```

## Step 2: Validate

1. **Total debits must equal total credits** — if they don't, STOP and investigate
2. Flag unusual balances:
   - Revenue accounts with debit balances
   - Expense accounts with credit balances
   - Accounts with balance sign inconsistent with their type

## Step 3: Present Results

Group accounts by type and present as a clean table:

```markdown
# Trial Balance
**Acme Corp OÜ** | As of 2026-03-31 | Currency: EUR

## Assets

| Account | Name | Debit | Credit |
|---------|------|-------|--------|
| 1000 | Cash - Operating | 125,000.00 | |
| 1200 | Trade Receivables | 85,000.00 | |
| 1500 | Inventory | 45,000.00 | |
| 2200 | Property, Plant & Equipment | 320,000.00 | |
| **Subtotal** | | **575,000.00** | |

## Liabilities

| Account | Name | Debit | Credit |
|---------|------|-------|--------|
| 3100 | Trade Payables | | 62,000.00 |
| 3250 | Tax Payables | | 18,500.00 |
| 3600 | Long-term Bank Loan | | 180,000.00 |
| **Subtotal** | | | **260,500.00** |

## Equity

| Account | Name | Debit | Credit |
|---------|------|-------|--------|
| 5000 | Share Capital | | 25,000.00 |
| 5300 | Retained Earnings | | 245,500.00 |
| **Subtotal** | | | **270,500.00** |

## Revenue & Expense
...

## Validation

| Check | Result |
|-------|--------|
| Debits = Credits | **PASS** (660,500.00 = 660,500.00) |
| Unusual balances | None detected |

## Anomalies (if any)

| Account | Name | Balance | Expected | Issue |
|---------|------|---------|----------|-------|
| 4100 | Service Revenue | 500.00 DR | Credit | Revenue with debit balance — check for reversal |
```
