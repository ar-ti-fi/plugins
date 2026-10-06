# Estonian Chart of Accounts Mapping Guide

This reference helps set up a chart of accounts for Estonian companies, whether importing from a prior system or starting fresh.

## The Merit Aktiva default chart (what Artifi imports)

Merit's default Estonian chart (RTJ-based) is classified account by account in Artifi's
`mcp-server/src/data/templates/ee_standard_subtypes.json`. Its structure:

| Range | Account type | Contents (examples) |
|-------|--------------|---------------------|
| 1000-1099 | asset | Cash and bank (arvelduskonto), term deposits, cash in transit |
| 1200-1299 | asset | Trade receivables, doubtful receivables (contra), loans issued, prepayments |
| 1300-1399 | asset | Inventories, prepayments to suppliers |
| 1800-1899 | asset | Tangible fixed assets and their accumulated depreciation (odd numbers) |
| 1900-1999 | asset | Goodwill, development costs, software, licences and their accumulated amortisation |
| 2000-2099 | liability | Bank loans, overdraft, owner loans, current portion of loans and finance leases |
| 2100-2199 | liability | Trade payables |
| 2200-2299 | liability | Payroll withholdings, vacation pay liability |
| 2300-2499 | liability | VAT (output and input, net), payroll taxes, income tax, interest payable |
| 2800-2899 | liability | Long-term liabilities, provisions, target financing |
| 2900-2999 | equity | Share capital, share premium, own shares, reserves, retained earnings, profit for the year |
| 3000-3499 | revenue | Sales revenue |
| 3500-3599 | revenue | Other operating income: disposal of fixed assets, realised FX gain, grants |
| 4000-4099 | cogs | Materials, goods and services bought for resale, subcontracting |
| 4100-4699 | expense | Rent, utilities, IT, bank charges, bad debts, vehicles, travel, fringe benefits |
| 4700-4799 | expense | Personnel: salaries, social tax, vacation accrual |
| 4800-4899 | expense | Depreciation and amortisation |
| 4900-4999 | expense | Other operating expenses: loss on disposal, tax interest, realised FX loss |
| 6000-6099 | expense | Financial expenses (interest) |

## Importing from Common Estonian Systems

### Merit Aktiva

Merit Aktiva is the most common Estonian accounting software. Their CoA export typically includes:
- Account number (4-digit)
- Account name (in Estonian)
- Account type (Varad, Kohustused, Omakapital, Tulud, Kulud)

The Merit connector classifies each account by number from that table (account_type, account_subtype and normal_balance), so no manual mapping is needed; an account outside the table falls back to its number range.

### e-Financials

e-Financials exports use similar numbering but may have 5-6 digit account numbers. Map similarly based on the first digits.

### No Prior System — Standard Template

If the user has no prior CoA, use `manage_imports(action="standard_coa", template="ifrs")` and then customize based on business type.

## Customizing for Business Types

After importing the standard IFRS template, add or rename accounts based on the company's business:

### IT Consultancy / Freelancer (most common Estonian OU)
Typically needs:
- 1000 Bank account (one per bank)
- 1100 Accounts receivable
- 2000 Accounts payable
- 2100 Tax liabilities (VAT, income tax, social tax)
- 3000 Share capital (usually EUR 2,500 minimum)
- 3200 Retained earnings
- 4000 Consulting revenue / Service revenue
- 5100 Salary expense (if they have employees)
- 5110 Social tax expense
- 6000 Office expenses
- 6010 Software subscriptions
- 6020 Internet & phone
- 6030 Accounting services
- 6040 Travel expenses
- 7000 Interest income (from bank)
- 7010 Interest expense (if loans)

### E-commerce
Add to the above:
- 1200 Inventory
- 4010 Product sales revenue
- 5000 Cost of goods sold
- 5010 Shipping expenses
- 6100 Marketing / advertising

### Restaurant / Food Service
Add:
- 1200 Food & beverage inventory
- 5000 Food cost
- 5010 Beverage cost
- 5300 Rent expense
- 5310 Utilities (electricity, water, gas)
- 5320 Equipment maintenance

## Account Type Detection

When importing a CoA without explicit types, determine the type from the account number:

```
1xxx → asset
20xx–28xx → liability
29xx → equity
3xxx → revenue
40xx → cogs
41xx–49xx → expense
60xx → expense (financial)
```

## Import Format

When using `manage_imports(action="accounts")`, each record needs:

```json
{
  "account_number": "1000",
  "account_name": "LHV arvelduskonto",
  "account_type": "asset",
  "account_subtype": "bank",
  "normal_balance": "debit",
  "is_active": true
}
```

The `normal_balance` follows from `account_type`:
- asset → debit
- cogs → debit
- expense → debit
- liability → credit
- equity → credit
- revenue → credit

Contra accounts take the opposite side, as the Merit default chart table states per account: accumulated
depreciation and amortisation (18xx/19xx contra rows) and the doubtful-receivables allowance (1208) are
credit-normal assets, own shares (2940, 2942) and unpaid share capital (2962) are debit-normal equity, and the disposed
assets' carrying amount and disposal loss (3512, 3514) are debit-normal revenue. Send the table's `normal_balance`
for those rows rather than the type's.
