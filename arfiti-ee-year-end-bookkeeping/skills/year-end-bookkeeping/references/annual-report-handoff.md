# Annual Report Handoff Checklist

Before running the annual report plugin (`/arfiti-ee:prepare-annual-report`), verify all items below. Each maps to a checkpoint in the annual report plugin.

## Pre-Flight Checklist

### 1. All Fiscal Periods Closed (maps to Annual Report CP1)

```
list_entities("fiscal_period", {"legal_entity_id": ENTITY_ID})
```

- All 12 monthly periods (January through December) must have status "closed"
- If any period is still open, close it before proceeding

### 2. Trial Balance Balances (maps to Annual Report CP3)

```
generate_report("trial_balance", {"legal_entity_id": ENTITY_ID, "as_of_date": "YYYY-12-31"})
```

- Total debits MUST equal total credits
- If not balanced, there's an error in the posted transactions — find and fix it

### 3. Balance Sheet Balances (maps to Annual Report CP5)

```
generate_report("balance_sheet", {"legal_entity_id": ENTITY_ID, "as_of_date": "YYYY-12-31"})
```

- Total Assets MUST equal Total Liabilities + Total Equity
- Bank balances should match actual bank closing balances

### 4. Prior Year Comparatives Available (maps to Annual Report CP4)

- If this is NOT the first year: opening balances must be posted (Phase 2 of bookkeeping)
- The annual report plugin will fetch prior year data for comparison columns
- Verify: `generate_report("balance_sheet", {"legal_entity_id": ENTITY_ID, "as_of_date": "YYYY-1-12-31"})` returns data

### 5. Bank Accounts Reconciled

For each bank account:
- Opening balance + all posted transactions = closing bank balance
- No unexplained differences

### 6. Revenue and Expenses Complete

- Income statement should reflect all economic activity for the year
- `generate_report("income_statement", {"legal_entity_id": ENTITY_ID, "start_date": "YYYY-01-01", "end_date": "YYYY-12-31"})`
- Revenue should be reasonable given bank inflows
- Expenses should be reasonable given bank outflows

### 7. Special Items Addressed

- Depreciation recorded (if the company has fixed assets)
- Loan interest properly split between principal and interest
- Year-end accruals posted (expenses incurred but not yet billed)
- Prepayments properly allocated
- If dividends were paid: CIT (20/80) recorded

## How to Run the Annual Report

Once all items above are verified:

1. Run: `/arfiti-ee:prepare-annual-report`
2. The plugin will ask for:
   - Legal entity ID
   - Fiscal year
   - Income statement scheme (Scheme 1 by nature is most common)
3. It will generate all financial statements, notes, and XBRL files

## If the Annual Report Plugin Finds Issues

The annual report plugin has its own checkpoints. If it fails on any:

| Annual Report Checkpoint | Likely Cause | Fix |
|---|---|---|
| CP1: Periods not closed | Forgot to close a period | Close the period |
| CP3: TB unbalanced | Unbalanced journal entry | Find and fix the entry |
| CP4: No prior year data | Opening balances not posted | Go back to Phase 2 |
| CP5: BS doesn't balance | Error in posted transactions | Review and correct |
| CP6: Cash flow doesn't reconcile | Missing bank transactions | Go back to Phase 3 |

## Also Available

- **VAT declarations**: `/arfiti-ee-vat:prepare-vat-declaration` — for monthly/quarterly KMD filing
- **Payroll**: `/arfiti-ee-payroll:calculate-payroll` — for TSD declarations
