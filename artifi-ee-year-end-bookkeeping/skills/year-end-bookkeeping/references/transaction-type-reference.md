# Transaction Type Reference for Estonian Year-End Bookkeeping

This reference documents all transaction types used when posting bank statement lines and other accounting entries. Each entry shows the required fields and typical GL posting pattern.

## Core Transaction Types

### AP_PAYMENT — Paying a Supplier

**When**: Money goes OUT to a vendor/supplier.
**Plain language**: "You paid someone for goods or services."

```json
{
  "transaction_type_code": "AP_PAYMENT",
  "legal_entity_id": ENTITY_ID,
  "vendor_id": VENDOR_ID,
  "transaction_date": "2025-01-15",
  "bank_account_id": BANK_ACCOUNT_ID,
  "description": "Payment to Telia for January invoice",
  "lines": [
    {"account_id": AP_ACCOUNT_ID, "debit": 120.00, "description": "Clear AP balance"},
    {"account_id": BANK_ACCOUNT_ID_GL, "credit": 120.00, "description": "Bank outflow"}
  ]
}
```

**GL effect**: Debit Accounts Payable (reduces what you owe), Credit Bank (money leaves).

### AR_PAYMENT — Receiving Payment from a Customer

**When**: Money comes IN from a customer.
**Plain language**: "A customer paid you."

```json
{
  "transaction_type_code": "AR_PAYMENT",
  "legal_entity_id": ENTITY_ID,
  "customer_id": CUSTOMER_ID,
  "transaction_date": "2025-01-20",
  "bank_account_id": BANK_ACCOUNT_ID,
  "description": "Payment from Client X for December work",
  "lines": [
    {"account_id": BANK_ACCOUNT_ID_GL, "debit": 5000.00, "description": "Bank inflow"},
    {"account_id": AR_ACCOUNT_ID, "credit": 5000.00, "description": "Clear AR balance"}
  ]
}
```

**GL effect**: Debit Bank (money arrives), Credit Accounts Receivable (reduces what they owe you).

### AP_INVOICE — Recording a Bill from a Supplier

**When**: You receive a bill/invoice from a vendor (even if not yet paid).
**Plain language**: "You got a bill that needs to be recorded."

```json
{
  "transaction_type_code": "AP_INVOICE",
  "legal_entity_id": ENTITY_ID,
  "vendor_id": VENDOR_ID,
  "transaction_date": "2025-01-10",
  "due_date": "2025-02-10",
  "description": "Telia invoice #12345 for telecom services",
  "lines": [
    {"account_id": EXPENSE_ACCOUNT_ID, "debit": 100.00, "description": "Telecom expense"},
    {"account_id": VAT_INPUT_ACCOUNT_ID, "debit": 20.00, "description": "VAT 20%"},
    {"account_id": AP_ACCOUNT_ID, "credit": 120.00, "description": "Amount owed to vendor"}
  ]
}
```

**GL effect**: Debit Expense + VAT, Credit Accounts Payable.

### AR_INVOICE — Recording a Sales Invoice

**When**: You issue an invoice to a customer.
**Plain language**: "You billed a customer for your work or products."

```json
{
  "transaction_type_code": "AR_INVOICE",
  "legal_entity_id": ENTITY_ID,
  "customer_id": CUSTOMER_ID,
  "transaction_date": "2025-01-31",
  "due_date": "2025-02-28",
  "description": "Invoice #001 for consulting services January 2025",
  "lines": [
    {"account_id": AR_ACCOUNT_ID, "debit": 6000.00, "description": "Amount owed by customer"},
    {"account_id": REVENUE_ACCOUNT_ID, "credit": 5000.00, "description": "Consulting revenue"},
    {"account_id": VAT_OUTPUT_ACCOUNT_ID, "credit": 1000.00, "description": "VAT 20%"}
  ]
}
```

**GL effect**: Debit Accounts Receivable, Credit Revenue + VAT Payable.

### BANK_FEE — Bank Service Charge

**When**: The bank charges a fee (monthly maintenance, card fees, etc.).
**Plain language**: "The bank charged you a fee."

```json
{
  "transaction_type_code": "BANK_FEE",
  "legal_entity_id": ENTITY_ID,
  "transaction_date": "2025-01-31",
  "bank_account_id": BANK_ACCOUNT_ID,
  "description": "LHV monthly account maintenance fee",
  "lines": [
    {"account_id": BANK_FEE_EXPENSE_ID, "debit": 5.00, "description": "Bank fee expense"},
    {"account_id": BANK_ACCOUNT_ID_GL, "credit": 5.00, "description": "Bank outflow"}
  ]
}
```

### BANK_INTEREST — Interest Earned

**When**: The bank pays you interest on your balance.
**Plain language**: "The bank paid you interest."

```json
{
  "transaction_type_code": "BANK_INTEREST",
  "legal_entity_id": ENTITY_ID,
  "transaction_date": "2025-01-31",
  "bank_account_id": BANK_ACCOUNT_ID,
  "description": "Interest on LHV savings account",
  "lines": [
    {"account_id": BANK_ACCOUNT_ID_GL, "debit": 12.50, "description": "Bank inflow"},
    {"account_id": INTEREST_INCOME_ID, "credit": 12.50, "description": "Interest income"}
  ]
}
```

### BANK_TRANSFER — Transfer Between Own Accounts

**When**: Moving money between your own bank accounts.
**Plain language**: "You moved money from one bank account to another."

```json
{
  "transaction_type_code": "BANK_TRANSFER",
  "legal_entity_id": ENTITY_ID,
  "transaction_date": "2025-01-15",
  "description": "Transfer from LHV to Wise",
  "lines": [
    {"account_id": TARGET_BANK_GL_ID, "debit": 1000.00, "description": "Money into Wise"},
    {"account_id": SOURCE_BANK_GL_ID, "credit": 1000.00, "description": "Money out of LHV"}
  ]
}
```

**Note**: This creates entries on both bank accounts. You only need to post it once (from the source bank statement). When you process the target bank's statement, mark the corresponding line as already posted (it's the same transfer).

## Loan Transaction Types

### LOAN_DISBURSEMENT — Receiving a Loan

**When**: A bank or lender transfers loan money to your account.
**Plain language**: "You received loan money."

```json
{
  "transaction_type_code": "LOAN_DISBURSEMENT",
  "legal_entity_id": ENTITY_ID,
  "transaction_date": "2025-03-01",
  "description": "SEB business loan disbursement",
  "lines": [
    {"account_id": BANK_ACCOUNT_ID_GL, "debit": 50000.00, "description": "Loan proceeds"},
    {"account_id": LOAN_LIABILITY_ID, "credit": 50000.00, "description": "Loan liability"}
  ]
}
```

### LOAN_REPAYMENT — Repaying a Loan

**When**: You make a loan payment (principal + interest).
**Plain language**: "You made a loan payment."

```json
{
  "transaction_type_code": "LOAN_REPAYMENT",
  "legal_entity_id": ENTITY_ID,
  "transaction_date": "2025-04-01",
  "description": "SEB loan monthly payment",
  "lines": [
    {"account_id": LOAN_LIABILITY_ID, "debit": 800.00, "description": "Principal repayment"},
    {"account_id": INTEREST_EXPENSE_ID, "debit": 200.00, "description": "Interest expense"},
    {"account_id": BANK_ACCOUNT_ID_GL, "credit": 1000.00, "description": "Bank outflow"}
  ]
}
```

**Important**: If you have the loan amortization schedule, split principal and interest correctly. If not, post the full amount and adjust in Phase 4.

## Owner / Equity Transaction Types

### OWNER_DISTRIBUTION — Paying Dividends

**When**: The company pays dividends to shareholders.
**Plain language**: "The company paid profits to the owner(s)."

```json
{
  "transaction_type_code": "OWNER_DISTRIBUTION",
  "legal_entity_id": ENTITY_ID,
  "transaction_date": "2025-06-15",
  "description": "Dividend payment to shareholder",
  "lines": [
    {"account_id": RETAINED_EARNINGS_ID, "debit": 10000.00, "description": "Dividend declared"},
    {"account_id": BANK_ACCOUNT_ID_GL, "credit": 10000.00, "description": "Dividend paid"}
  ]
}
```

**Estonian tax note**: Dividends are subject to 20/80 corporate income tax (the company pays 20% on the gross distribution). The CIT payment to EMTA is a separate JOURNAL_ENTRY.

### CAPITAL_CONTRIBUTION — Owner Investing in Company

**When**: An owner puts money into the company (share capital increase or additional contribution).
**Plain language**: "The owner put money into the company."

```json
{
  "transaction_type_code": "CAPITAL_CONTRIBUTION",
  "legal_entity_id": ENTITY_ID,
  "transaction_date": "2025-01-05",
  "description": "Share capital contribution from founder",
  "lines": [
    {"account_id": BANK_ACCOUNT_ID_GL, "debit": 2500.00, "description": "Capital received"},
    {"account_id": SHARE_CAPITAL_ID, "credit": 2500.00, "description": "Share capital increase"}
  ]
}
```

## General Purpose

### JOURNAL_ENTRY — Manual Adjustment

**When**: Anything that doesn't fit the above types: tax payments, salary, accruals, depreciation, etc.
**Plain language**: "A manual accounting entry for special cases."

```json
{
  "transaction_type_code": "JOURNAL_ENTRY",
  "legal_entity_id": ENTITY_ID,
  "transaction_date": "2025-01-31",
  "description": "Social tax payment to EMTA for January",
  "lines": [
    {"account_id": TAX_LIABILITY_ID, "debit": 1650.00, "description": "Clear social tax liability"},
    {"account_id": BANK_ACCOUNT_ID_GL, "credit": 1650.00, "description": "Bank outflow"}
  ]
}
```

**Common JOURNAL_ENTRY uses in Estonian bookkeeping:**
- EMTA tax payments (social tax, income tax, VAT)
- Salary payments (clearing salary liability)
- Pension fund contributions
- Year-end accruals and adjustments
- Depreciation entries
- FX gains/losses

## Posting Rules

1. **Every transaction must balance**: total debits = total credits
2. **Use the correct transaction_type_code** — this determines GL posting behavior and reporting
3. **Always link vendor_id or customer_id** when the counterparty is known
4. **Post in chronological order** within each month
5. **Include descriptive text** in the description field — this helps during reconciliation and audit
