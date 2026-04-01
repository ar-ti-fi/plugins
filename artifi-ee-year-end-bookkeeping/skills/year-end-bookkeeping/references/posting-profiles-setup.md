# Posting Profiles Setup Guide

Posting profiles define which GL accounts are used when recording each type of transaction. This guide helps configure them for a typical Estonian company.

## What Are Posting Profiles?

When you record "payment to vendor", the system needs to know:
- Which account to debit (Accounts Payable)
- Which account to credit (Bank)

Posting profiles store these mappings so you don't have to specify them every time.

## Standard Profile Configuration

### For Every Company

| Transaction Type | Debit Account | Credit Account | Notes |
|---|---|---|---|
| AP_PAYMENT | 2000 Accounts Payable | 1000 Bank | Paying suppliers |
| AR_PAYMENT | 1000 Bank | 1100 Accounts Receivable | Receiving from customers |
| BANK_FEE | 6000 Bank fee expense | 1000 Bank | Bank charges |
| BANK_INTEREST | 1000 Bank | 7000 Interest income | Interest earned |
| BANK_TRANSFER | 1000 Target Bank | 1000 Source Bank | Between own accounts |
| JOURNAL_ENTRY | (varies) | (varies) | Manual entries |

### If Company Has Suppliers / Bills

| Transaction Type | Debit Account | Credit Account | Notes |
|---|---|---|---|
| AP_INVOICE | 5xxx/6xxx Expense | 2000 Accounts Payable | Recording a bill |

The expense account varies by what was purchased (rent → 5300, telecom → 6020, etc.).

### If Company Sells Goods / Services

| Transaction Type | Debit Account | Credit Account | Notes |
|---|---|---|---|
| AR_INVOICE | 1100 Accounts Receivable | 4000 Revenue | Issuing an invoice |

### If Company Has Loans

| Transaction Type | Debit Account | Credit Account | Notes |
|---|---|---|---|
| LOAN_DISBURSEMENT | 1000 Bank | 2500 Long-term loan | Receiving loan |
| LOAN_REPAYMENT | 2500 Loan + 7010 Interest | 1000 Bank | Repaying loan |

### If Company Pays Dividends

| Transaction Type | Debit Account | Credit Account | Notes |
|---|---|---|---|
| OWNER_DISTRIBUTION | 3200 Retained earnings | 1000 Bank | Dividend payment |

### If Owner Contributes Capital

| Transaction Type | Debit Account | Credit Account | Notes |
|---|---|---|---|
| CAPITAL_CONTRIBUTION | 1000 Bank | 3000 Share capital | Capital injection |

## VAT Handling (If VAT Registered)

For VAT-registered companies (most Estonian companies with revenue > EUR 40,000):

| Situation | VAT Account | Direction |
|---|---|---|
| Buying (input VAT) | 2100 VAT Receivable | Debit (you can reclaim this) |
| Selling (output VAT) | 2110 VAT Payable | Credit (you owe this to EMTA) |
| EMTA VAT payment | 2110 VAT Payable | Debit (clearing what you owe) |

Standard Estonian VAT rate: 22% (as of 2025).

## How to Verify Profiles

After configuration, verify each profile works:

1. `batch_lookup([{"entity_type": "account", "filters": {"legal_entity_id": ENTITY_ID, "is_active": true}}])`
2. Check that each account referenced in profiles exists and is active
3. Test with a small transaction if unsure

## Common Estonian Account Assignments

For a typical Estonian OÜ (IT consultancy / freelancer):

```
Bank (LHV):          1000
Bank (Wise):         1001
Accounts Receivable: 1100
Accounts Payable:    2000
VAT Receivable:      2100
VAT Payable:         2110
Social Tax Payable:  2120
Income Tax Payable:  2130
Share Capital:       3000
Retained Earnings:   3200
Service Revenue:     4000
Salary Expense:      5100
Social Tax Expense:  5110
Office Expense:      6000
Software/IT:         6010
Telecom:             6020
Accounting Services: 6030
Travel:              6040
Bank Fees:           6050
Interest Income:     7000
Interest Expense:    7010
Income Tax:          8000
```

Adjust account numbers to match the imported CoA.
