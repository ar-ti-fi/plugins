# Notes to Financial Statements (Lisad)

The number and detail of notes depends on company size category.

## Micro-Entity Notes (up to 3)

| Note | Topic | Content | MCP Data Source |
|---|---|---|---|
| 1 | Accounting policies | Basis of preparation, measurement bases | Standard text |
| 2 | Contingent liabilities | Guarantees, legal claims | Manual input |
| 3 | Related party transactions | Board/shareholder transactions | `search("vendor", {"query": "<name>"})` |

## Small Company Notes (up to 9)

| Note | Topic | Content | MCP Data Source |
|---|---|---|---|
| 1 | Accounting policies | Summary of significant policies | Standard text template |
| 2 | Cash and cash equivalents | Bank balances, restricted cash | `list_entities("bank_account", {"legal_entity_id": ID})` |
| 3 | Receivables and prepayments | Trade receivables, tax receivables, prepaid | `generate_report("ar_aging", {"legal_entity_id": ID, "as_of_date": "YYYY-12-31"})` |
| 4 | Property, plant and equipment | Cost, depreciation, NBV, movements | `list_entities("fixed_asset", {"legal_entity_id": ID})` |
| 5 | Intangible assets | Goodwill, licenses, development costs | `list_entities("fixed_asset", {"legal_entity_id": ID})` filtered by type |
| 6 | Loans and borrowings | Terms, maturity, interest rates | GL detail for accounts 3000-3099, 3600-3699 |
| 7 | Trade and other payables | Vendor balances, tax, accruals | `generate_report("ap_aging", {"legal_entity_id": ID, "as_of_date": "YYYY-12-31"})` |
| 8 | Related party transactions | Shareholders, board, key management | Query by dimension or vendor name |
| 9 | Contingent liabilities | Guarantees, legal claims, other | Manual input |

## Medium/Large Company Notes (~15)

All of the above, plus:

| Note | Topic | Content | MCP Data Source |
|---|---|---|---|
| 10 | Revenue breakdown | Revenue by EMTAK activity code | `aggregate_entities("transaction", ["party_name"], {"amount": "sum"}, {"transaction_type": "ar_invoice"})` |
| 11 | Personnel expenses | Wages, social tax, pension, avg employees | GL detail for accounts 5300-5399 |
| 12 | Financial income/expenses | Interest, FX gains/losses | GL detail for accounts 6000-6999 |
| 13 | Income tax | CIT on distributions, deferred tax | GL detail for account 7000 |
| 14 | Equity details | Share capital structure, changes | Equity statement data |
| 15 | Events after balance sheet date | Material post-period events | Manual input |

## Note 4 Detail: PP&E Roll-Forward

| Category | Opening Cost | Additions | Disposals | Closing Cost | Opening Depr | Depr Charge | Disposals | Closing Depr | NBV |
|---|---|---|---|---|---|---|---|---|---|
| Land | X | +/- | +/- | X | - | - | - | - | X |
| Buildings | X | +/- | +/- | X | X | X | +/- | X | X |
| Machinery | X | +/- | +/- | X | X | X | +/- | X | X |
| Other | X | +/- | +/- | X | X | X | +/- | X | X |
| Under construction | X | +/- | +/- | X | - | - | - | - | X |
| **Total** | **X** | | | **X** | **X** | **X** | | **X** | **X** |

Group `list_entities("fixed_asset", ...)` results by `asset_category`:
- Opening cost = acquisition_cost for assets acquired before period start
- Additions = assets with acquisition_date within period
- Disposals = assets with disposal_date within period
- Depreciation charge = sum of period depreciation

## Note 8 Detail: Related Party Transactions

Required disclosure for transactions with:
- Shareholders (direct and indirect)
- Board members (juhatuse liikmed) and supervisory board (noukogu liikmed)
- Key management personnel
- Entities controlled by the above

Disclose: nature of relationship, transaction type, amount, outstanding balances.
