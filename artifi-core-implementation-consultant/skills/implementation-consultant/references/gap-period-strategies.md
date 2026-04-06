# Gap Period Strategies

When the cutoff date is in the past, there is a gap between the cutoff date and today. This gap needs to be filled with transactions so the system reflects reality.

## When Does a Gap Exist?

```
Cutoff date: 2025-12-31
Today:       2026-04-06
Gap:         2026-01-01 to 2026-04-06 (4 months)
```

If the gap is 0 (cutoff = today or in the future), skip Phase 4 entirely.

## Strategy Selection Matrix

| Factor | Strategy A (Full Import) | Strategy B (Bank Statements) | Strategy C (Bulk Upload) |
|--------|------------------------|-----------------------------|-----------------------|
| **Best when** | Transaction export available from old system or connector | Only bank statements available, no structured export | Large volume (>500 transactions) |
| **Gap length** | Any | Any | Any (but especially >3 months) |
| **Data source** | CSV export from old system, or connector sync | Bank statement CSV/PDF | CSV in Arfiti import format |
| **User effort** | Low (export + review) | Medium (review classifications monthly) | Medium (prepare CSV in format) |
| **Speed** | Fast (bulk import) | Slow (month-by-month) | Medium (upload + async processing) |
| **Completeness** | High — includes non-bank transactions | Medium — only bank transactions | High — whatever is in the CSV |
| **Missing items** | Accruals, adjustments not in export | Accruals, prepayments, depreciation, non-bank transactions | Depends on CSV completeness |

## Recommendation Logic

```
If Path A (connector):
    → Strategy A (connector can sync gap period automatically)

If Path B (CSV) AND user can export transactions:
    → Strategy A (CSV import)

If Path B (CSV) AND user CANNOT export transactions:
    If estimated transactions < 200/month:
        → Strategy B (bank statements)
    Else:
        → Strategy C (admin bulk upload)

If Path C (greenfield):
    → No gap period (cutoff = today)

If Path D (hybrid):
    → Strategy A for connector data + Strategy B for manual data
```

## Strategy A — Full Transaction Import

### Via Connector
```
manage_connectors(action="sync_accounting_data", connector_id=CONNECTOR_ID,
    entity_types=["invoices", "bills", "payments", "journal_entries"],
    from_date="GAP_START", to_date="GAP_END")
```

The connector pulls all transaction types in dependency order and posts them to Arfiti.

### Via CSV Import
1. Get format guidance: `manage_onboarding(action="get_support", support_type="import_transactions")`
2. User exports transactions from old system
3. Map columns to Arfiti transaction format
4. Validate: `manage_imports(action="transactions", records=[...], validate_only=true)`
5. Import: `manage_imports(action="transactions", records=[...], legal_entity_id=ENTITY_ID)`
6. For >50 records, monitor: `get_import_status(import_id=...)`

### What to watch for:
- **Duplicate prevention**: Use `on_duplicate="skip"` to avoid duplicating transactions that may have been included in the opening balance
- **Sequence**: Import in chronological order when possible
- **Missing master data**: If transactions reference vendors/customers not yet imported, import master data first
- **Payment matching**: Imported payments may need to be matched to imported invoices/bills

## Strategy B — Bank Statement Processing

Process month by month to keep it manageable and allow user review.

### Monthly Loop:
For each month in the gap period:

1. **Upload statement**: Ask user for bank statement (CSV preferred, PDF acceptable)
2. **Parse lines**: Extract date, amount, counterparty, description
3. **Identify new counterparties**: Check against existing vendors/customers via `search()`
4. **Create master data**: New vendors/customers after user confirmation
5. **Classify**: Apply transaction type rules:
   | Pattern | Type |
   |---------|------|
   | Outflow to vendor | AP_PAYMENT |
   | Inflow from customer | AR_PAYMENT |
   | Fee/commission keywords | BANK_FEE |
   | Interest keywords | BANK_INTEREST |
   | Own account transfer | BANK_TRANSFER |
   | Tax authority payments | JOURNAL_ENTRY |
   | Loan keywords | LOAN_REPAYMENT |
   | Dividend/distribution | OWNER_DISTRIBUTION |
   | Capital contribution | CAPITAL_CONTRIBUTION |
6. **Review**: Present classification table to user for confirmation
7. **Post**: Submit each confirmed transaction
8. **Verify**: Check monthly totals match bank statement

### After all months processed:
- Check for missing source documents (bills for AP payments, invoices for AR payments)
- Post year-end adjustments if needed (accruals, depreciation, prepayment amortization)

### Limitations of Strategy B:
- **Non-bank transactions are missed**: Accruals, depreciation, inventory adjustments
- **Bills and invoices**: Only payments show in bank data — user should provide bills/invoices separately for proper AP/AR tracking
- **Payroll**: Salary payments appear in bank but without line-item detail — suggest importing payroll records separately

## Strategy C — Admin Portal Bulk Upload

For large datasets (>500 transactions), the admin dashboard provides a more efficient upload experience.

### Steps:
1. Provide the CSV template format: `manage_onboarding(action="get_support", support_type="import_transactions")`
2. Guide user on preparing the CSV:
   - Required columns: transaction_type, reference_number, transaction_date, amount, account_number
   - Optional: vendor_name, customer_name, description, currency
3. User uploads via admin dashboard (Settings → Data Import)
4. Monitor progress: `get_import_status(import_id=...)`
5. Review results: imported count, skipped count, error details

### When to combine strategies:
- Use Strategy C for the bulk of transactions, then Strategy B for a final month that's still in progress
- Use Strategy A (connector) for most data, then Strategy B for transactions not covered by the connector

## Post-Gap Verification

After any strategy, run these checks:

1. **Trial balance at today**: `generate_report("trial_balance", {"legal_entity_id": ID, "as_of_date": "TODAY"})` — must balance
2. **Bank balance check**: System balance for each bank account should match actual bank balance
3. **Income statement**: `generate_report("income_statement", {"legal_entity_id": ID, "start_date": "GAP_START", "end_date": "TODAY"})` — does revenue/expense make sense?
4. **Missing transactions**: If bank balance doesn't match, there are missing or extra transactions — investigate
