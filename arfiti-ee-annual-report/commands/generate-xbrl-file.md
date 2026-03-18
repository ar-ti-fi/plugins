---
name: generate-xbrl-file
description: Generate XBRL files (.xbrl + .xsd) for upload to ariregister.rik.ee
---

# Generate XBRL File

Generate a complete XBRL file pair (instance document + companion schema) for the Estonian annual report, ready for upload to the e-Business Register portal at ariregister.rik.ee.

**How it works:** Instead of generating XML by hand (which hits token limits and causes errors), this command builds a structured JSON data file and runs `scripts/generate_xbrl.py` — a Python script that generates both XBRL files with hardcoded correct namespaces and validated element names.

## Usage

```
/arfiti-ee:generate-xbrl-file
```

## Prerequisites

- Annual report data must be prepared (run `/arfiti-ee:prepare-annual-report` first or have financial data available)
- All fiscal periods for the year must be closed
- Python 3.9+ available (`python3 --version`)

## Step 1: Collect Inputs

Ask the user for:

1. **Legal entity ID** — which Estonian entity
2. **Fiscal year** — e.g. 2025
3. **Registry code** (äriregistri kood) — e.g. 12345678
4. **Company size** — Micro, Small, Medium, or Large
5. **Income statement scheme** — Scheme 1 (by nature) or Scheme 2 (by function). Default: Scheme 1
6. **Output directory** — where to write the files. Default: current directory

## Step 2: Fetch Financial Data

Use MCP tools to gather all required data:

```
# Core financial data — current year
generate_report("trial_balance", {"legal_entity_id": ID, "as_of_date": "YYYY-12-31"})
generate_report("balance_sheet", {"legal_entity_id": ID, "as_of_date": "YYYY-12-31"})
generate_report("income_statement", {"legal_entity_id": ID, "start_date": "YYYY-01-01", "end_date": "YYYY-12-31"})

# Prior year comparatives — balance sheet AND income statement
generate_report("balance_sheet", {"legal_entity_id": ID, "as_of_date": "PRIOR-12-31"})
generate_report("income_statement", {"legal_entity_id": ID, "start_date": "PRIOR-01-01", "end_date": "PRIOR-12-31"})

# Note data
generate_report("ar_aging", {"legal_entity_id": ID, "as_of_date": "YYYY-12-31"})
generate_report("ap_aging", {"legal_entity_id": ID, "as_of_date": "YYYY-12-31"})
list_entities("fixed_asset", {"legal_entity_id": ID})
list_entities("bank_account", {"legal_entity_id": ID})
list_entities("employee", {"legal_entity_id": ID})
```

## Step 3: Determine Required Roles

Based on company size and available data, select role codes from **references/xbrl-generation.md** → "Role Catalog for OÜ".

**Minimum roles by size:**
- **Micro**: `["201012", "301011", "702010", "801030", "828000", "843000"]`
- **Small**: `["201012", "301011", "702010", "801000", "804010", "822000", "828000", "832000", "839000", "843000"]`
- **Medium/Large**: `["201010", "301011", "401010", "601010", "702010", "801000", "804010", "816000", "822000", "828000", "832000", "839000", "843000"]`

**Add additional roles if data exists:**
- `"811020"` — when loan receivables exist
- `"818000"` — when intangible assets exist
- `"821000"` — when long-term loan liabilities exist
- `"831010"` — when share capital detail is required
- `"842000"` — when income tax was paid
- `"844000"` — when material post-balance-sheet events exist
- `"702020"` instead of `"702010"` — when there is a net loss

## Step 4: Build XBRL Data JSON

Map financial data to XBRL elements and build the JSON input file. Use the element mapping tables in **references/xbrl-generation.md** and the format shown in **scripts/input_schema.json**.

**CRITICAL element naming rules — use ONLY these exact names:**
- Cash → `CashAndCashEquivalents` (NOT `Cash`, NOT `CashEquivalents`)
- Net profit → `TotalAnnualPeriodProfitLoss` (income statement), `AnnualPeriodProfitLoss` (balance sheet)
- Operating profit → `TotalProfitLoss`
- Revenue → `Revenue`
- Total assets → `Assets`, total liabilities → `Liabilities`, total equity → `Equity`

Full element lists are in **references/xbrl-generation.md** → "Balance Sheet Element Mapping", "Income Statement Element Mapping", etc.

**Validation requirements — verify BEFORE writing the JSON:**
1. `balance_sheet.current.Assets` == `balance_sheet.current.Liabilities` + `balance_sheet.current.Equity`
2. `income_statement.TotalAnnualPeriodProfitLoss` == `balance_sheet.current.AnnualPeriodProfitLoss`
3. `cash_flow.CashAndCashEquivalentsAtEndOfPeriod` == `balance_sheet.current.CashAndCashEquivalents`

**JSON structure** (see `scripts/input_schema.json` for full example):

```json
{
  "regcode": "REGCODE",
  "fiscal_year": YYYY,
  "roles": ["201010", "301011", ...],
  "balance_sheet": {
    "current": { "CashAndCashEquivalents": 50000, "Assets": 210000, ... },
    "prior":   { "CashAndCashEquivalents": 40000, "Assets": 214000, ... }
  },
  "income_statement": { "Revenue": 300000, "TotalAnnualPeriodProfitLoss": 22250, ... },
  "income_statement_prior": { "Revenue": 250000, "TotalAnnualPeriodProfitLoss": 18250, ... },
  "cash_flow": { "CashFlowsFromOperatingActivities": 48000, "CashAndCashEquivalentsAtEndOfPeriod": 50000, ... },
  "cash_flow_prior": { "CashFlowsFromOperatingActivities": 35000, "CashAndCashEquivalentsAtEndOfPeriod": 40000, ... },
  "profit_allocation": { "RetainedEarningsLoss": 80000, "ProposalDividends": -8000, ... },
  "equity_changes": {
    "EquityAtEndOfPreviousPeriodAbstract": { "ChangesInEquityIssuedCapital": 2500, "ChangesInEquity": 70750 },
    "EquityAtEndOfPeriodAbstract": { "ChangesInEquityIssuedCapital": 2500, "ChangesInEquity": 82750 }
  },
  "note_receivables": { "total": { "AccountsReceivables": 20000, "ReceivablesAndPrepayments": 25000 }, ... },
  "note_payables": { "total": { "TradePayablesTotal": 20000, "PayablesAndPrepayments": 30000 }, ... },
  "note_contingent_liabilities": { "DistributableDividends": 94250, "ContingentLiabilitiesTotal": 0 },
  "note_personnel": { "WageAndSalaryExpense": 38000, "LaborExpense": 50000, "AverageNumberOfEmployeesInFullTimeEquivalentUnits": 5 },
  "note_revenue": { "NetSalesByOperatingActivitiesTotal": 300000, "NetSalesByGeographicalLocation": 300000 },
  "note_related_parties": { "Remuneration": 18000 }
}
```

**Prior year comparative data (`income_statement_prior`, `cash_flow_prior`):**
- Include prior year IS/CF data for comparative columns in the BTM portal
- The generator auto-fills `0` for lines that exist in the current year but are missing from the prior year
- Only provide lines that have non-zero values in the prior year

Write this JSON to a temporary file, e.g. `/tmp/xbrl_data_{REGCODE}.json`.

## Step 5: Run the Generator Script

Find the plugin's scripts directory and run the generator:

```bash
# Find the script (it's in the plugin's scripts/ folder)
SCRIPT_DIR="$(dirname "$(which claude)" 2>/dev/null || echo "$HOME/.claude")/plugins/arfiti-ee-annual-report/scripts"

# If the above doesn't work, use the absolute path from the plugin installation
# The script is at: plugins/arfiti-ee-annual-report/scripts/generate_xbrl.py

python3 generate_xbrl.py \
  --input /tmp/xbrl_data_{REGCODE}.json \
  --output {OUTPUT_DIR}
```

The script will:
- Validate balance sheet, net profit, and cash flow consistency (exits with error if any fail)
- Generate `Vormid_{REGCODE}.xsd` with correct linkbase references
- Generate `Aruanne_{REGCODE}.xbrl` with correct namespaces and validated element names
- Print paths of generated files

**If the script is not found**, locate it with:
```bash
find ~ -name "generate_xbrl.py" -path "*/arfiti-ee-annual-report/*" 2>/dev/null
```

## Step 6: Report Results

After the script completes, report to the user:
- Paths of the two generated files
- Any validation errors printed by the script
- Confirmation that files are ready for upload

## Step 7: Filing Instructions

1. Log in to **ariregister.rik.ee** with ID-card or Smart-ID
2. Navigate to "Aruanded" → Create new report for the fiscal year
3. Choose **"Lae XBRL fail"** (Upload XBRL file)
4. Upload both files: `Vormid_{REGCODE}.xsd` and `Aruanne_{REGCODE}.xbrl`
5. The portal will validate — if errors occur, paste them here to debug
6. Review the generated report preview
7. Add signatories and digitally sign
8. Submit

## Output

Two XBRL files ready for upload:
- `Vormid_{REGCODE}.xsd` — companion schema (declares forms/notes)
- `Aruanne_{REGCODE}.xbrl` — instance document (contains financial data)
