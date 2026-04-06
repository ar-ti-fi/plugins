# Opening Balance Preparation Checklist

Step-by-step guide to preparing and uploading opening balances.

## What Are Opening Balances?

Opening balances represent the financial position of the company at the cutoff date — the moment the old system stops and Arfiti takes over. Every balance sheet account (assets, liabilities, equity) gets an opening entry. Income statement accounts (revenue, expense) are NOT included — they start at zero in Arfiti.

## Prerequisites

Before uploading opening balances, ensure:
- [ ] Chart of accounts is imported (Phase 1 complete)
- [ ] Bank accounts are created
- [ ] Vendors and customers are imported (needed for subledger records)
- [ ] Fixed asset categories exist (if importing assets)

## Source Document

The user needs one of these:
- **Trial balance** as of cutoff date (preferred — has all accounts with balances)
- **Balance sheet** as of cutoff date (only balance sheet accounts — no P&L)
- **Closing balance report** from old system
- **Connector sync** (automated for Path A)

## Account Mapping

For each line in the source document:
1. Match to an account in the imported CoA by account number or name
2. Determine if it's a debit or credit balance:
   - Assets (1000-1999): normally debit
   - Liabilities (2000-2999): normally credit
   - Equity (3000-3999): normally credit
   - Revenue (4000-4999): NOT included in opening balance
   - Expenses (5000-9999): NOT included in opening balance
3. Flag any unmatched lines for user clarification

## The Clearing Account Pattern

Opening balances use a clearing account (typically 3300 — Retained Earnings) to ensure the entry balances:

```
Debit:  1000 Cash           10,000
Debit:  1200 Receivables    25,000
Credit: 2100 Payables              15,000
Credit: 2500 Loans                  8,000
Credit: 3300 Ret. Earnings         12,000  ← balancing entry
```

**Why clearing account matters for subledger:**
When AR and AP have individual open items (invoices/bills), the opening balance entry uses clearing account 0000 for the control accounts (1200, 2100). The individual AR_INVOICE and AP_INVOICE transactions post to the actual control accounts. This way:
- The GL control account total is correct (sum of individual items = clearing offset)
- Each individual invoice/bill appears in aging reports
- The clearing account (0000) nets to zero

## Subledger Detection

Scan the balance sheet for accounts that need individual records. See **advisory-intelligence.md** for the full detection rules.

**Critical subledger accounts:**
| Account Type | Range | Individual Records Needed |
|-------------|-------|--------------------------|
| Accounts Receivable | 1200-1299 | Open customer invoices |
| Accounts Payable | 2100-2199 | Open vendor bills |
| Fixed Assets | 1500-1599 (cost), 1600-1699 (depreciation) | Asset register entries |

## Upload Methods

### Basic Opening Balance (no subledger detail)
```
manage_imports(
    action="opening_balances",
    legal_entity_id=ENTITY_ID,
    balances=[
        {"account_number": "1000", "debit": "10000.00", "credit": "0"},
        {"account_number": "1200", "debit": "25000.00", "credit": "0"},
        {"account_number": "2100", "debit": "0", "credit": "15000.00"},
        ...
    ],
    fiscal_period_name="2026-01",
    balancing_account_number="3300"
)
```

### With Subledger Details (recommended)
```
manage_imports(
    action="opening_balances_with_subledger",
    legal_entity_id=ENTITY_ID,
    balances=[...],
    fiscal_period_name="2026-01",
    balancing_account_number="3300",
    open_ar_items=[
        {
            "customer_name": "Acme Corp",
            "reference_number": "INV-2025-089",
            "amount": 5000.00,
            "invoice_date": "2025-10-15",
            "due_date": "2025-11-15"
        }
    ],
    open_ap_items=[
        {
            "vendor_name": "Office Supply Co",
            "reference_number": "BILL-4521",
            "amount": 2500.00,
            "invoice_date": "2025-11-01",
            "due_date": "2025-12-01"
        }
    ],
    fixed_assets_detail=[
        {
            "name": "Dell Server R750",
            "acquisition_date": "2023-06-15",
            "original_cost": 15000.00,
            "accumulated_depreciation": 5000.00,
            "useful_life_months": 60
        }
    ]
)
```

## Verification

After uploading, run these checks:

1. **Trial balance**: `generate_report("trial_balance", {"legal_entity_id": ID, "as_of_date": "CUTOFF_DATE"})`
   - Total debits MUST equal total credits
   - Each account balance should match the source document

2. **If subledger items provided:**
   - AR aging: `generate_report("ar_aging", {"legal_entity_id": ID, "as_of_date": "CUTOFF_DATE"})` — each invoice visible
   - AP aging: `generate_report("ap_aging", {"legal_entity_id": ID, "as_of_date": "CUTOFF_DATE"})` — each bill visible
   - Fixed assets: `list_entities("fixed_asset", {"legal_entity_id": ID})` — each asset visible

3. **Bank balances**: Compare system bank account balance vs actual bank balance at cutoff

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Debits ≠ credits | Missing accounts or wrong amounts | Review mapping, add missing lines |
| Account not found | Account number doesn't exist in CoA | Create the account or fix the number |
| Large retained earnings difference | Prior year P&L not captured | Expected — retained earnings absorbs historical profits |
| Small rounding difference | Currency conversion or decimal rounding | Normal — balancing account handles this (typically < 1.00) |
| Negative bank balance | More outflows than inflows recorded | Check if opening balance is correct |
| Vendor/customer not found | Master data not imported | Import vendors/customers first, then retry |
