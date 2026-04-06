# Opening Balance Guide

This guide explains how to extract, prepare, and upload opening balances for an existing company.

## What Are Opening Balances?

Opening balances are the starting point for the new fiscal year. They represent the financial position of the company on January 1st — essentially, last year's closing numbers become this year's opening numbers.

**If this is the company's first year of operations, skip this entirely.** The only opening entry might be the initial share capital contribution.

## Where to Get Opening Balances

The best source is the **prior year balance sheet** (as of December 31st of the previous year). This can come from:

1. **Prior year annual report** (majandusaasta aruanne) — the balance sheet section
2. **Trial balance from prior accountant** — ask the accountant for the closing trial balance
3. **Merit Aktiva / e-Financials export** — the prior accounting software can export this
4. **Tax return or regulatory filing** — EMTA or ariregister.rik.ee may have the filed report

## What to Include

Opening balances include **only balance sheet accounts** (not revenue or expenses):

| Include (Balance Sheet) | Do NOT Include (P&L) |
|---|---|
| Bank accounts (cash) | Revenue |
| Accounts receivable | Expenses |
| Inventory | Cost of goods sold |
| Fixed assets | Depreciation expense |
| Accounts payable | |
| Loans | |
| Tax liabilities | |
| Share capital | |
| Retained earnings | |

**Why no revenue/expenses?** Because revenue and expenses reset to zero at the start of each year. Last year's net profit/loss gets rolled into Retained Earnings.

## Preparing the Data

### Step 1: Extract from Balance Sheet

For each line in the prior year balance sheet, identify:
- Account number (from the imported CoA)
- Debit or credit amount

**Rule of thumb:**
- Assets with positive balances → **debit**
- Liabilities with positive balances → **credit**
- Equity with positive balances → **credit**
- Accumulated depreciation (negative asset) → **credit**

### Step 2: Handle Retained Earnings

This is the trickiest part. Retained earnings in the opening balance should include:
- Prior year's retained earnings (from the balance sheet)
- PLUS prior year's net income (profit or loss)
- MINUS any dividends paid during the prior year

In the prior year balance sheet, this is usually already combined. But if you're given separate figures:

```
Opening Retained Earnings = Prior Year Retained Earnings + Prior Year Net Income - Prior Year Dividends
```

### Step 3: Verify the Balance

Before uploading, check:
- Total debits = Total credits
- If they don't balance, there's a mapping error — review each line

## Upload Format

Use `manage_imports` with the opening_balances action:

```
manage_imports(
    action="opening_balances",
    legal_entity_id=ENTITY_ID,
    balances=[
        {"account_number": "1000", "debit": 15000.00, "credit": 0},
        {"account_number": "1100", "debit": 8000.00, "credit": 0},
        {"account_number": "1500", "debit": 25000.00, "credit": 0},
        {"account_number": "1600", "debit": 0, "credit": 10000.00},
        {"account_number": "2000", "debit": 0, "credit": 5000.00},
        {"account_number": "2500", "debit": 0, "credit": 20000.00},
        {"account_number": "3000", "debit": 0, "credit": 2500.00},
        {"account_number": "3200", "debit": 0, "credit": 10500.00}
    ],
    fiscal_period_name="2025-01",
    balancing_account_number="3300"
)
```

### The Balancing Account

The `balancing_account_number` (typically 3300 = Current Year Result or 3200 = Retained Earnings) absorbs any small rounding difference to ensure the entry balances. If your data is correct, the balancing amount should be zero or at most a few cents.

If the balancing amount is large (more than EUR 1), something is wrong — review the data.

## Subledger Details (Open AP, Open AR, Fixed Assets)

### What Are Subledger Details and Why They Matter

When the balance sheet shows "Accounts Receivable: 25,000 EUR", that is the total. But that total is made up of individual unpaid customer invoices — for example, Invoice #001 for 10,000 from Customer A and Invoice #002 for 15,000 from Customer B. The same applies to accounts payable (individual unpaid vendor bills) and fixed assets (individual assets with their own depreciation schedules).

Without these details, the GL balance is correct, but:
- **AR aging reports** show one lump sum instead of individual invoices with due dates
- **AP aging reports** cannot show which bills are overdue or coming due
- **Fixed asset register** is empty, so automatic depreciation cannot run
- **Collections and payment scheduling** have no individual items to track

With the details, the system creates proper subledger records: each open invoice becomes an AR transaction, each unpaid bill becomes an AP transaction, and each asset gets its own depreciation schedule.

### How It Works: The Clearing Account Approach

When subledger details are provided, the system uses a migration clearing account (account 0000 or a designated clearing account) to keep the GL balanced:

1. The **opening balance entry** posts the clearing account instead of the AR/AP control account. For example, instead of debiting "1200 Accounts Receivable" for 25,000, it debits "0000 Migration Clearing" for 25,000.
2. Each **open AR invoice** is posted as a proper AR_INVOICE transaction: debit 1200 Accounts Receivable, credit 0000 Migration Clearing.
3. The clearing account nets to zero (25,000 debit from opening entry, 25,000 credit from the individual invoices).

The same approach applies to AP and fixed assets. The end result: the GL balances are identical, but the subledger now has individual trackable items.

### What to Provide for Each Category

**Open AR (unpaid customer invoices):**
- Customer name
- Invoice number
- Amount (outstanding balance)
- Invoice date
- Due date

**Open AP (unpaid vendor bills):**
- Vendor name
- Bill number
- Amount (outstanding balance)
- Bill date
- Due date

**Fixed assets:**
- Asset name/description
- Acquisition date
- Original cost
- Accumulated depreciation to date
- Estimated useful life (in months or years)

### Example Format

**Open AR items:**

| Customer | Invoice # | Amount | Invoice Date | Due Date |
|----------|-----------|--------|--------------|----------|
| Acme OÜ | INV-2024-089 | 10,000.00 | 2024-10-15 | 2024-11-15 |
| Baltic Tech AS | INV-2024-102 | 15,000.00 | 2024-11-20 | 2024-12-20 |
| **Total** | | **25,000.00** | | |

**Open AP items:**

| Vendor | Bill # | Amount | Bill Date | Due Date |
|--------|--------|--------|-----------|----------|
| Office Supplies OÜ | BILL-4521 | 3,200.00 | 2024-11-01 | 2024-12-01 |
| Cloud Hosting AS | BILL-8834 | 1,800.00 | 2024-12-01 | 2025-01-01 |
| **Total** | | **5,000.00** | | |

**Fixed assets:**

| Asset | Acquisition Date | Original Cost | Accum. Depreciation | Useful Life |
|-------|-----------------|---------------|---------------------|-------------|
| MacBook Pro (x3) | 2023-03-15 | 6,000.00 | 2,000.00 | 36 months |
| Office Furniture | 2022-06-01 | 4,000.00 | 1,600.00 | 60 months |
| Server Equipment | 2024-01-10 | 15,000.00 | 6,400.00 | 48 months |
| **Total** | | **25,000.00** | **10,000.00** | |

The totals must match the corresponding balance sheet lines (AR total = receivable balance, AP total = payable balance, asset cost total = fixed asset account, depreciation total = accumulated depreciation account).

### If You Don't Have the Details

It is OK to proceed without subledger details. The GL balances will be correct and the trial balance will match the prior year balance sheet. You can add individual items later by manually creating invoices, bills, or fixed asset records. But it is better to do it during migration if you have the data — retrofitting later requires more work.

## Common Pitfalls

1. **Forgetting accumulated depreciation**: Fixed assets are recorded at cost (debit 1500), but accumulated depreciation is a separate credit entry (credit 1600). The net book value = 1500 - 1600.

2. **Double-counting net income**: If the prior year balance sheet already includes the year's net income in retained earnings, don't add it again.

3. **VAT balances**: If the company had a VAT receivable or payable at year-end, include it. Check the prior year's final KMD declaration.

4. **Loan balances**: Split between short-term (due within 12 months → 2000-2099) and long-term (due after 12 months → 2500-2599).

5. **Prepayments**: Annual insurance or rent paid in advance — these are assets (prepaid expenses, account 1300).

## Verification

After uploading, run:
```
generate_report("trial_balance", {"legal_entity_id": ENTITY_ID, "as_of_date": "YYYY-01-01"})
```

Check:
- Total debits = Total credits
- Each line matches the prior year balance sheet
- Retained earnings makes sense (prior year RE + prior year net income)
