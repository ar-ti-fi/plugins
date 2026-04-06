# Migration Path Decision Tree

Use this to determine the right migration path during Phase 0 discovery.

## Decision Flow

```
Q: Is the user starting from scratch (no prior system)?
├── Yes → Path C (Greenfield)
└── No → Q: Which accounting system?
    ├── Merit Aktiva → Path A (Connector)
    ├── QuickBooks Online → Path A (Connector)
    ├── SmartAccounts → Path A (Connector)
    ├── Multiple systems → Path D (Hybrid)
    └── Other (Xero, SAP, custom, spreadsheets, etc.) → Path B (CSV/Manual)
```

## Path Comparison

| Aspect | Path A (Connector) | Path B (CSV/Manual) | Path C (Greenfield) | Path D (Hybrid) |
|--------|-------------------|--------------------|--------------------|----------------|
| **Automation** | High — most data synced automatically | Low — user prepares and uploads CSVs | Minimal — interactive creation | Mixed |
| **User effort** | Review and confirm | Prepare exports, map fields, fix errors | Answer questions, create records | Both |
| **Data quality** | Good — connector handles mapping | Varies — depends on export quality | N/A | Varies |
| **Speed** | Fast (hours) | Medium (days) | Fast (minutes) | Medium |
| **Best for** | Users on supported systems | Users on unsupported systems | New companies | Complex migrations |

## Path A — Connector Migration

**Supported connectors:**
- **Merit Aktiva** — Full sync: accounts, customers, vendors, items, dimensions, fixed assets, transactions, opening balances with open items
- **QuickBooks Online** — Full sync: accounts, customers, vendors, items, transactions
- **SmartAccounts** — Full sync: accounts, customers, vendors, transactions

**What the connector handles automatically:**
1. Chart of accounts mapping and import
2. Customer and vendor master data
3. Item/product catalog
4. Dimension types and values
5. Trial balance at cutoff date
6. Open AR invoices (individual records for aging)
7. Open AP bills (individual records for aging)
8. Fixed asset register (with depreciation history)
9. Historical transactions (for gap period)

**What may still need manual setup:**
- Bank accounts (IBANs, GL account links)
- Posting profiles (if not covered by connector)
- Employees and payroll (most connectors don't sync payroll)
- Custom dimensions not in the source system

**How to use:**
1. User sets up connector in admin dashboard (credentials entered securely via UI)
2. Activate: `manage_connectors(action="activate", connector_id=UUID)`
3. Sync master data: `manage_connectors(action="sync_accounting_data", connector_id=UUID, entity_types=[...])`
4. Use migration panel for opening balance with preview and cutoff date selection
5. Sync gap period: `manage_connectors(action="sync_accounting_data", ..., from_date=..., to_date=...)`

## Path B — CSV/Manual Migration

**Import sequence** (order matters — later imports reference earlier ones):
1. Accounts (chart of accounts)
2. Dimension types, then dimension values
3. Customers
4. Vendors
5. Items
6. Employees
7. Fixed assets
8. Opening balances (with or without subledger)
9. Transactions (gap period)

**For each import type, get format guidance:**
```
manage_onboarding(action="get_support", support_type="import_<type>")
```

**Common source formats and how to handle:**
- **Excel/CSV from old system** → Map columns to Arfiti fields, import directly
- **PDF reports** → Extract data (Claude can read PDFs), structure into records
- **Pasted text/tables** → Parse and structure into records
- **Manual entry** → Use `submit()` for individual records or small batches

## Path C — Greenfield

**Minimal setup needed:**
1. Chart of accounts (use IFRS or US GAAP template)
2. Bank accounts
3. A few initial vendors/customers as needed
4. No opening balance (or just initial capital contribution)

**Recommended sequence:**
1. Set up CoA template
2. Create bank accounts
3. Start transacting — create vendors/customers as you go
4. Set up bank feeds for automatic reconciliation

## Path D — Hybrid

**When to use:**
- Connector available for financial data but not for payroll/HR
- Some data in one system, other data in spreadsheets
- Migrating from multiple systems simultaneously

**Approach:**
1. Use connector for what it supports (accounts, vendors, customers, transactions)
2. Manual import for what it doesn't (employees, custom dimensions, etc.)
3. Opening balance from connector, then manually add any missing items
