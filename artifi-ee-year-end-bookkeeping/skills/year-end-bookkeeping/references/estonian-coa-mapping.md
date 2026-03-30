# Estonian Chart of Accounts Mapping Guide

This reference helps set up a chart of accounts for Estonian companies, whether importing from a prior system or starting fresh.

## Standard Estonian Account Number Ranges

Estonian companies typically use this numbering convention (based on the Estonian Accounting Standards / RTJ):

| Range | Account Type | Category | Examples |
|-------|-------------|----------|----------|
| 1000-1099 | Asset | Cash & Bank | Kassas (cash), LHV arvelduskonto, Swedbank |
| 1100-1199 | Asset | Short-term receivables | Ostjate noudeid (AR), Ettemaksed tarnijatele |
| 1200-1299 | Asset | Inventories | Kaubad, Tooraine, Valmistoodang |
| 1300-1399 | Asset | Other current assets | Viitlaekumised, Ettemakstud kulud |
| 1500-1599 | Asset | Fixed assets (PP&E) | Arvutid, Mööbel, Autod, Hooned |
| 1600-1699 | Asset | Accumulated depreciation | Akumuleeritud kulum (negative) |
| 1700-1799 | Asset | Intangible assets | Tarkvara, Litsentsid, Firmavaartus |
| 1800-1899 | Asset | Financial investments | Aktsiad, Osalused, Laenud antud |
| 2000-2099 | Liability | Short-term payables | Hankijate volad (AP), Maksud |
| 2100-2199 | Liability | Tax liabilities | Kaibemaks, Tulumaks, Sotsiaalmaks |
| 2200-2299 | Liability | Employee liabilities | Palgavolad, Puhkusereserv |
| 2300-2399 | Liability | Other current liabilities | Ettemaksed klientidelt, Viitlaekumised |
| 2500-2599 | Liability | Long-term loans | Pangalaenud, Liisingukohustused |
| 2600-2699 | Liability | Other long-term liabilities | Pikaajaline volgnevus |
| 3000-3099 | Equity | Share capital | Osakapital, Aktsiakapital |
| 3100-3199 | Equity | Reserves | Kohustuslik reservkapital |
| 3200-3299 | Equity | Retained earnings | Eelmiste perioodide jaotamata kasum |
| 3300-3399 | Equity | Current year result | Aruandeaasta kasum/kahjum |
| 4000-4099 | Revenue | Sales revenue | Müügitulu, Teenuse tulu |
| 4100-4199 | Revenue | Other revenue | Muu aritulu, Toetused |
| 5000-5099 | Expense | Cost of goods sold | Kaubad, Materjalid, Alltöövõtt |
| 5100-5199 | Expense | Personnel expenses | Palgakulu, Sotsiaalmaks, Tööjõumaksud |
| 5200-5299 | Expense | Depreciation | Põhivara kulum |
| 5300-5399 | Expense | Other operating expenses | Rent, Kommunaalid, Transport |
| 6000-6099 | Expense | Administrative expenses | Kontor, IT, Raamatupidamine |
| 6100-6199 | Expense | Marketing expenses | Reklaam, Turundus |
| 7000-7099 | Revenue/Expense | Financial income/expense | Intressitulu, Intressikulu |
| 8000-8099 | Expense | Income tax | Tulumaks dividendidelt |

## Importing from Common Estonian Systems

### Merit Aktiva

Merit Aktiva is the most common Estonian accounting software. Their CoA export typically includes:
- Account number (4-digit)
- Account name (in Estonian)
- Account type (Varad, Kohustused, Omakapital, Tulud, Kulud)

**Mapping Merit types to Artifi:**
| Merit Type | Artifi account_type | Artifi normal_balance |
|---|---|---|
| Varad (Assets) | asset | debit |
| Kohustused (Liabilities) | liability | credit |
| Omakapital (Equity) | equity | credit |
| Tulud (Revenue) | revenue | credit |
| Kulud (Expenses) | expense | debit |

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
2xxx → liability
3xxx → equity
4xxx → revenue
5xxx-6xxx → expense
7xxx → revenue (if interest income) or expense (if interest expense)
8xxx → expense (tax)
```

## Import Format

When using `manage_imports(action="accounts")`, each record needs:

```json
{
  "account_number": "1000",
  "account_name": "LHV arvelduskonto",
  "account_type": "asset",
  "normal_balance": "debit",
  "is_active": true
}
```

The `normal_balance` follows from `account_type`:
- asset → debit
- expense → debit
- liability → credit
- equity → credit
- revenue → credit
