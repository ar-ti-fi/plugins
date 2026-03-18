---
name: Estonian Annual Report Preparation
description: Prepares the majandusaasta aruanne (annual report) for Estonian Business Register filing via ariregister.rik.ee
---

## Trigger

Activate when the user mentions: annual report, majandusaasta aruanne, year-end report, aastaaruanne, or filing for an Estonian legal entity.

## Prerequisites

Before starting, ask the user for:
1. **Legal entity ID** — which Estonian entity to prepare the report for
2. **Fiscal year** — e.g. 2025
3. **Income statement scheme** — Scheme 1 (by nature, most common) or Scheme 2 (by function)

## Mandatory Checkpoints

You MUST verify each checkpoint before proceeding to the next step. If a checkpoint fails, STOP and inform the user.

- **CP1**: All 12 fiscal periods for the year must be closed
- **CP2**: Company size category must be determined (affects which statements are required)
- **CP3**: Trial balance must balance (total debits = total credits)
- **CP4**: Prior year comparatives must be fetched and verified
- **CP5**: Balance sheet must balance (Total Assets = Total Liabilities + Total Equity)
- **CP6**: Cash flow net change must equal closing cash minus opening cash

## Workflow Steps

### Step 1: Check Prerequisites & Determine Company Category

1. Verify year-end close: `list_entities("fiscal_period", {"legal_entity_id": ID})` — all 12 periods must be status "closed"
2. Fetch balance sheet: `generate_report("balance_sheet", {"legal_entity_id": ID, "as_of_date": "YYYY-12-31"})` — get total assets
3. Fetch income statement: `generate_report("income_statement", {"legal_entity_id": ID, "start_date": "YYYY-01-01", "end_date": "YYYY-12-31"})` — get total revenue
4. Count employees: `list_entities("employee", {"legal_entity_id": ID})` — count active employees

Apply size thresholds (2 of 3 criteria) from **references/rtj-standards.md** to determine: Micro, Small, Medium, or Large.

Assess audit requirement using thresholds from **references/rtj-standards.md**.

**CP1 checkpoint**: Confirm all periods closed. **CP2 checkpoint**: Confirm size category.

### Step 2: Fetch Financial Data

Fetch all data needed for the report:

1. **Trial balance** (current + prior year): `generate_report("trial_balance", ...)` — **CP3 checkpoint**: verify it balances
2. **Balance sheet** (current + prior year): `generate_report("balance_sheet", ...)`
3. **Income statement** (current + prior year): `generate_report("income_statement", ...)`
4. **AR aging**: `generate_report("ar_aging", ...)` — for receivables note
5. **AP aging**: `generate_report("ap_aging", ...)` — for payables note
6. **Fixed assets**: `list_entities("fixed_asset", ...)` — for PP&E note and depreciation
7. **Bank accounts**: `list_entities("bank_account", ...)` — for cash note
8. **Employee list**: already fetched in Step 1

**CP4 checkpoint**: Confirm prior year data available and matches previously filed report.

### Step 3: Balance Sheet (Bilanss)

Map trial balance accounts to the statutory line items from **references/balance-sheet-format.md**.

Follow the Annex 1 format: Current Assets (A) + Non-Current Assets (B) = Total Assets. Current Liabilities (C) + Non-Current Liabilities (D) + Equity (E) = Total Liabilities & Equity.

**CP5 checkpoint**: Total Assets MUST equal Total Liabilities + Total Equity.

### Step 4: Income Statement (Kasumiaruanne)

Map trial balance to income statement lines from **references/income-statement-format.md**.

Use the scheme selected by the user (Scheme 1 by nature or Scheme 2 by function). Note the Estonian CIT system: tax only on distributed profits (20/80 rate).

### Step 5: Cash Flow Statement (Rahavoogude aruanne)

Required for Medium and Large companies. Use the indirect method template from **references/cash-flow-format.md**.

Calculate: Operating activities + Investing activities + Financing activities = Net change in cash.

**CP6 checkpoint**: Net change must equal closing cash minus opening cash.

### Step 6: Statement of Changes in Equity (Omakapitali muutuste aruanne)

Required for Medium and Large companies. Use the template from **references/equity-changes-format.md**.

Show movements for: Share capital, Share premium, Statutory reserve, Other reserves, Retained earnings, Current year profit/loss.

### Step 7: Notes to Financial Statements (Lisad)

Number of notes depends on company size. Use the templates and data sources from **references/notes-templates.md**.

- Micro: up to 3 notes (accounting policies, contingent liabilities, related parties)
- Small: up to 9 notes (add cash, receivables, PP&E, intangibles, loans, payables)
- Medium/Large: ~15 notes (add revenue breakdown, personnel, financial income/expenses, income tax, equity details, post-BS events)

### Step 8: Management Report (Tegevusaruanne)

Required for all except micro-entities. Use the template from **references/management-report.md**.

Calculate KPIs from the financial data: revenue growth, net profit margin, current ratio, quick ratio, debt-to-equity, ROE, ROA, personnel expense ratio.

### Step 9: Profit Allocation Proposal

Calculate statutory reserve requirement and draft the proposal using **references/profit-allocation.md**.

Statutory reserve must reach 10% of share capital; minimum 5% of net profit transferred annually until met.

### Step 10: Compile Output

Generate a comprehensive summary document with:
- Cover page (company name, registry code, period, board members)
- All financial statements with current year and prior year columns
- All notes
- Management report with KPIs
- Profit allocation proposal
- Validation checklist results

### Step 11: Generate XBRL Files

Generate the XBRL files for upload to ariregister.rik.ee using **references/xbrl-generation.md** as the complete reference.

**CRITICAL before generating — read the "CRITICAL RULES" section at the top of xbrl-generation.md:**
- Taxonomy namespace is EXACTLY `http://xbrl.eesti.ee/taxonomy/et-gaap_2026-01-01/` (trailing slash required)
- Entity identifier scheme is EXACTLY `http://xbrl.eesti.ee/estonian_commercial_register`
- Use ONLY element names from the mapping tables — never invent names (e.g., `Cash` is WRONG, use `CashAndCashEquivalents`)
- Declare ONLY the `iso4217:EUR` unit — never declare `xbrli:pure`
- No XML comments in the output files
- No other taxonomy namespaces (`dei`, `us-gaap`, etc.)

Steps:
1. **Determine required roles** based on company size and available data (see Role Catalog in xbrl-generation.md)
2. **Generate companion XSD** (`Vormid_{REGCODE}.xsd`) with linkbase references for each selected role
3. **Build context definitions** — instant (I1, I2), duration (D21), and dimensional contexts for notes
4. **Map all financial values to XBRL elements** using the element mapping tables in xbrl-generation.md
5. **Generate instance document** (`Aruanne_{REGCODE}.xbrl`) with all contexts, unit, and fact values
6. **Validate** — BS balances, net profit consistency, cash flow reconciliation, context references, XSD completeness

Write both files to the user's specified output directory. These two files are all that's needed for XBRL upload.

Alternatively, the user can run `/arfiti-ee:generate-xbrl-file` as a standalone command.

### Step 12: Filing Guidance

Provide the user with filing instructions from **references/e-business-register.md**.

**Primary method: XBRL file upload** — upload the generated `.xsd` and `.xbrl` files directly to the portal. This is faster and less error-prone than manual form entry.

**Fallback method: Manual portal entry** — use the XBRL mapping table from **references/xbrl-mapping.md** to fill in portal forms.

Remind: filing deadline is 6 months after fiscal year end (typically June 30). The report must be digitally signed by board members.

## Output Format

Present the final report in a structured format with clear sections, using tables for financial data. Include the validation checklist showing pass/fail for each checkpoint.
