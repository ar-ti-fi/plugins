# Balance Sheet Classification Guide

How to classify accounts into balance sheet sections using dynamic account properties. NEVER hardcode account numbers — use `account_type` and `account_category` to map accounts.

## Account Discovery

```
list_entities("account", {
    "legal_entity_id": ID,
    "is_active": true
})
```

## Classification by Account Properties

### ASSETS

#### Current Assets

| Section | account_type | account_category | Description |
|---------|-------------|-----------------|-------------|
| Cash and cash equivalents | asset | cash | Bank accounts, petty cash, money market |
| Short-term investments | asset | short_term_investment | Marketable securities, term deposits < 12 months |
| Trade receivables | asset | receivable | Customer invoices outstanding |
| Other receivables | asset | other_receivable | Employee advances, insurance claims, deposits |
| Tax receivables | asset | tax_receivable | VAT refunds, prepaid income tax |
| Prepayments | asset | prepayment | Prepaid rent, insurance, subscriptions |
| Inventory | asset | inventory | Raw materials, WIP, finished goods |

**Total Current Assets** = Sum of all `account_type = 'asset'` where category indicates current (cash, receivable, inventory, prepayment, short_term_investment, other_receivable, tax_receivable)

#### Non-Current Assets

| Section | account_type | account_category | Description |
|---------|-------------|-----------------|-------------|
| Long-term investments | asset | long_term_investment | Subsidiaries, associates, long-term securities |
| Property, plant & equipment | asset | fixed_asset | Land, buildings, machinery, vehicles, furniture |
| Intangible assets | asset | intangible_asset | Software, patents, trademarks, goodwill |
| Right-of-use assets | asset | right_of_use_asset | Leased assets under IFRS 16 / ASC 842 |
| Other non-current assets | asset | other_noncurrent_asset | Long-term deposits, deferred charges |

**Total Non-Current Assets** = Sum of all `account_type = 'asset'` where category indicates non-current

### LIABILITIES

#### Current Liabilities

| Section | account_type | account_category | Description |
|---------|-------------|-----------------|-------------|
| Trade payables | liability | payable | Vendor invoices outstanding |
| Accrued expenses | liability | accrued_expense | Wages payable, accrued interest, utilities |
| Tax payables | liability | tax_payable | VAT payable, income tax payable, payroll taxes |
| Short-term loans | liability | short_term_loan | Bank overdrafts, current portion of long-term debt |
| Deferred revenue | liability | deferred_revenue | Prepayments from customers, unearned revenue |
| Other current liabilities | liability | other_current_liability | Customer deposits, warranty provisions |

#### Non-Current Liabilities

| Section | account_type | account_category | Description |
|---------|-------------|-----------------|-------------|
| Long-term loans | liability | long_term_loan | Bank loans, bonds payable, notes payable |
| Lease liabilities | liability | lease_liability | Long-term lease obligations |
| Provisions | liability | provision | Legal claims, restructuring, environmental |
| Deferred tax liabilities | liability | deferred_tax | Temporary differences |
| Other non-current liabilities | liability | other_noncurrent_liability | Pension obligations, long-term deposits |

### EQUITY

| Section | account_type | account_category | Description |
|---------|-------------|-----------------|-------------|
| Share capital / Issued capital | equity | share_capital | Par value of issued shares |
| Share premium | equity | share_premium | Amount received above par value |
| Treasury shares | equity | treasury_shares | Buyback shares (negative balance) |
| Reserves | equity | reserve | Statutory reserves, revaluation reserves |
| Retained earnings | equity | retained_earnings | Accumulated prior year profits/losses |
| Current year profit/loss | equity | current_year_result | Calculated from income statement |

## Presentation Format

```
ASSETS
  Current Assets
    Cash and cash equivalents          XXX,XXX.XX
    Trade receivables                  XXX,XXX.XX
    Prepayments                         XX,XXX.XX
    Inventory                          XXX,XXX.XX
  Total Current Assets                              X,XXX,XXX.XX

  Non-Current Assets
    Property, plant & equipment        XXX,XXX.XX
    Intangible assets                   XX,XXX.XX
  Total Non-Current Assets                            XXX,XXX.XX

TOTAL ASSETS                                       X,XXX,XXX.XX

LIABILITIES
  Current Liabilities
    Trade payables                     XXX,XXX.XX
    Tax payables                        XX,XXX.XX
    Short-term loans                   XXX,XXX.XX
  Total Current Liabilities                           XXX,XXX.XX

  Non-Current Liabilities
    Long-term loans                    XXX,XXX.XX
  Total Non-Current Liabilities                       XXX,XXX.XX

TOTAL LIABILITIES                                    XXX,XXX.XX

EQUITY
    Share capital                      XXX,XXX.XX
    Retained earnings                  XXX,XXX.XX
    Current year profit/loss            XX,XXX.XX
TOTAL EQUITY                                         XXX,XXX.XX

TOTAL LIABILITIES AND EQUITY                       X,XXX,XXX.XX
```

## Validation Rules

1. **Balance check**: Total Assets = Total Liabilities + Total Equity (mandatory)
2. **Sign check**: Assets should have debit (positive) balances. Liabilities and equity should have credit balances. Flag any exceptions.
3. **Completeness**: All active accounts should appear somewhere. Flag unclassified accounts.
4. **Current year result**: Must match net profit/loss from the income statement for the same period.
