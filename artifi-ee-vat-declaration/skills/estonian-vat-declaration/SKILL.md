---
name: Estonian VAT Declaration (KMD)
description: Prepares the monthly Kaibemaksudeklaratsioon (KMD) for EMTA filing, including KMD INF annex and EC Sales List (Form VD)
---

## Trigger

Activate when the user mentions: VAT declaration, KMD, kaibemaksudeklaratsioon, monthly VAT, EMTA filing, VAT return, kaibemaks, or VAT for an Estonian legal entity.

## Prerequisites

Before starting, ask the user for:
1. **Legal entity ID** — which Estonian entity to prepare the declaration for
2. **Period** — month and year (e.g., January 2026)

## Mandatory Checkpoints

Before generating the return you MUST run the **pre-close validation gate** — the seven
checks in **references/validation-checklist.md**, each rated BLOCK or WARN. If any BLOCK
is open, STOP and do not generate. The individual checkpoints below feed that gate:

- **CP1**: All transactions for the period are posted (no drafts) — gate check 2
- **CP2**: All transaction lines have tax codes assigned — gate check 4
- **CP3**: KMD calculations balance and tie to the GL — gate checks 1, 5, 7
- **CP4**: KMD INF totals reconcile and respect the €1,000 threshold — gate check 6
- **CP5**: EC Sales List reconciles with the KMD: VD goods = line 3.1.1, VD services = line 3.1 − 3.1.1 — gate check 7

## Workflow Steps

### Step 1: Discover & Classify Tax Codes

This step is CRITICAL. Do NOT hardcode tax code names. Always discover and classify dynamically.

1. Fetch the entity's active Estonian tax codes:
   ```
   list_entities("tax_code", {"legal_entity_id": ID, "country_code": "EE", "is_active": true})
   ```

2. For each tax code, apply the classification rules from **references/tax-codes-ee.md**:
   - Check `reporting_code_override` first (entity-level override takes priority)
   - Then classify by properties: `default_rate`, `is_reverse_charge`, `is_recoverable`, `tax_type`, `tax_scope`, `metadata`
   - Map each code to a KMD line using the decision tree in **references/kmd-form-structure.md**

3. Present the classification table to the user:
   ```
   | Tax Code | Name | Rate | Reverse Charge | → KMD Line |
   |----------|------|------|----------------|------------|
   | [code]   | [name] | [rate] | [yes/no]   | [line]     |
   ```

4. Ask the user to confirm the classification before proceeding.

### Step 2: Fetch Period Transactions

Fetch all posted transactions for the reporting period:

1. **AR invoices** (sales):
   ```
   list_entities("transaction", {
       "legal_entity_id": ID,
       "transaction_type": "ar_invoice",
       "status": "posted"
   }, date_filters={"transaction_date": {"from": "YYYY-MM-01", "to": "YYYY-MM-DD"}},
   include_lines=true)
   ```

2. **AP invoices** (purchases):
   ```
   list_entities("transaction", {
       "legal_entity_id": ID,
       "transaction_type": "ap_invoice",
       "status": "posted"
   }, date_filters={"transaction_date": {"from": "YYYY-MM-01", "to": "YYYY-MM-DD"}},
   include_lines=true)
   ```

3. **Credit notes** and **journal entries** with VAT impact:
   ```
   list_entities("transaction", {
       "legal_entity_id": ID,
       "status": "posted"
   }, date_filters={"transaction_date": {"from": "YYYY-MM-01", "to": "YYYY-MM-DD"}},
   include_lines=true)
   ```

**CP1 checkpoint**: Check for any draft transactions in the period. If drafts exist, list them and ask the user to post or exclude them.

### Step 3: Verify Tax Code Coverage

Check that all transaction lines have valid tax codes:

1. Scan all fetched transaction lines
2. Flag any lines without a tax code assigned
3. Flag any lines using inactive or unclassified tax codes

**CP2 checkpoint**: If lines are missing tax codes, list them with transaction number, date, and amount. Ask the user to assign tax codes before continuing.

### Step 3.5: Run the pre-close validation gate

Run **every** check in **references/validation-checklist.md** and emit the single
pass/fail report (one row per check, PASS / WARN / BLOCK, with the offending records and
the fix). This catches — before generation — payments without a document (check 2),
cut-off errors (check 3), tax-code/jurisdiction problems (check 4), GL mismatches
(check 5), and INF-threshold inconsistencies (check 6).

- **If any BLOCK is open: STOP. Present the report and do not proceed to Step 4.**
- WARN items are listed for the user to confirm but do not stop the workflow.
- Check 1 (output format) and the arithmetic in check 7 are enforced again by
  `generate_kmd.py` at Step 9, which refuses to write files on any format defect.

### Step 4: Calculate the KMD main form (declarationBody)

Using the tax code classification from Step 1 and transactions from Step 2, compute the
KMD2 `declaration_body` values following **references/kmd-form-structure.md**. These are
taxable **bases** by rate (except the input-VAT lines, which are VAT amounts). Use the
**real KMD2 element names** — NOT Line1_1…Line13.

**Output side — bases by rate:**
- `transactions24` (line 1): base of sales at 24% (standard rate from 07.2025)
- `transactions22` / `transactions20`: legacy standard-rate bases (22% in 2024, 20% ≤2023)
- `transactions9` (line 2): base at 9%; `transactions5` (2¹) at 5%; `transactions13` (2²) at 13%
- `transactionsZeroVat` (line 3): zero-rated total
- `euSupplyInclGoodsAndServicesZeroVat` (3.1) + `euSupplyGoodsZeroVat` (3.1.1): intra-Community supplies
- `exportZeroVat` (3.2): exports to non-EU

**Input side — VAT amounts:**
- `inputVatTotal` (line 5): total recoverable input VAT from purchases
- `importVat` (5.1), `fixedAssetsVat` (5.2), `carsVat`/`carsPartialVat` (5.3/5.4): subsets of line 5

**Reverse charge / acquisitions (bases):**
- `euAcquisitionsGoodsAndServicesTotal` (line 6): goods + services acquired from **EU** suppliers; `euAcquisitionsGoods` (6.1) is the goods subset
- `acquisitionOtherGoodsAndServicesTotal` (line 7): services received from **non-EU** suppliers + domestic reverse charge

**Exempt / adjustments:**
- `supplyExemptFromTax` (line 8)
- `adjustmentsPlus` (line 10) / `adjustmentsMinus` (line 11): non-negative corrections

**Do NOT compute total VAT (line 4), VAT due (line 12) or overpaid (line 13)** — e-MTA
derives them from the bases + `inputVatTotal`, and there are no XSD elements for them.
`generate_kmd.py` computes them for the CSV / summary automatically.

**CP3 checkpoint**: Present the completed main form. Sanity-check that
`Σ(base × rate) − inputVatTotal` gives the expected net VAT (payable if positive,
refundable if negative).

### Step 5: Prepare KMD INF Annex

Following **references/kmd-inf-annex.md**:

1. **Part A (Sales)**: Group AR invoices by customer. For each customer where total > EUR 1,000:
   ```
   aggregate_entities("transaction", ["party_name"], {"amount": "sum", "id": "count"},
       {"legal_entity_id": ID, "transaction_type": "ar_invoice"},
       date_filters={"transaction_date": {"from": "YYYY-MM-01", "to": "YYYY-MM-DD"}})
   ```
   Collect per partner: registration code, name, taxable amount (excl. VAT), tax rate.
   These become `sales_annex.lines` entries (`buyerRegCode`, `buyerName`, `invoiceSum`,
   `taxRate`, `sumForRateInPeriod`).

2. **Part B (Purchases)**: Group AP invoices by vendor. For each vendor where total
   (incl. VAT) > EUR 1,000: collect registration code, name, total incl. VAT, input VAT
   for the period. These become `purchases_annex.lines` entries (`sellerRegCode`,
   `sellerName`, `invoiceSumVat`, `vatInPeriod`).

3. Validate registration codes (8-digit format for Estonian partners).

When no partner reaches the EUR 1,000 threshold, omit the annex — the generator sets
`noSales` / `noPurchases` to `true`.

**CP4 checkpoint**: Verify Part A totals are consistent with KMD output VAT lines. Verify Part B totals are consistent with total AP invoice base.

### Step 6: Prepare EC Sales List (Form VD)

Following **references/ec-sales-list.md**:

1. Identify intra-community supply transactions (zero-rated sales to EU B2B customers)
2. Group by customer VAT number
3. Classify supply type: **G** (goods), **S** (services), or **T** (triangular)
4. Calculate total supply amount per customer per type

**CP5 checkpoint**: Verify Form VD col 3 (goods) total = `euSupplyGoodsZeroVat` (KMD line 3.1.1) and col 5 (services) total = `euSupplyInclGoodsAndServicesZeroVat` − `euSupplyGoodsZeroVat` (line 3.1 − 3.1.1). Triangular resale (col 4) is NOT declared in the KMD. If no IC transactions exist, note that Form VD is not required.

### Step 7: Reconcile VAT GL Accounts

Compare calculated KMD amounts with GL account balances:

```
generate_report("trial_balance", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})
```

1. VAT Output account balance should match the computed total output VAT (line 4)
2. VAT Input account balance should match `inputVatTotal` (line 5)
3. Net VAT payable/receivable should match line 12 or line 13

If there are differences, identify the cause (timing, manual entries, rounding) and present to the user.

### Step 8: Submit Tax Return to ERP

Store the KMD calculation results in the ERP so they are viewable in Admin Dashboard → Tax → Returns and XML can be regenerated on demand:

```
submit("tax_return", "create", {
    "legal_entity_id": <entity_id>,
    "reporting_period_id": <period_id>,
    "tax_authority_id": <EMTA authority id>,
    "return_type": "vat_return",
    "return_data": {
        "form_code": "KMD",
        "year": <YYYY>,
        "month": <MM>,
        "regcode": "<business registry code>",
        "declaration_body": {
            "transactions24": <base>, "transactions22": <base>, "transactions20": <base>,
            "transactions9": <base>, "transactions5": <base>, "transactions13": <base>,
            "transactionsZeroVat": <base>,
            "euSupplyInclGoodsAndServicesZeroVat": <base>, "euSupplyGoodsZeroVat": <base>,
            "exportZeroVat": <base>,
            "inputVatTotal": <vat>, "importVat": <vat>, "fixedAssetsVat": <vat>,
            "euAcquisitionsGoodsAndServicesTotal": <base>, "euAcquisitionsGoods": <base>,
            "acquisitionOtherGoodsAndServicesTotal": <base>,
            "supplyExemptFromTax": <base>,
            "adjustmentsPlus": <amount>, "adjustmentsMinus": <amount>
        },
        "sales_annex": {"sum_per_partner": true, "lines": [{"buyerRegCode": "...", "buyerName": "...", "invoiceSum": <amount>, "taxRate": "24"}, ...]},
        "purchases_annex": {"sum_per_partner": true, "lines": [{"sellerRegCode": "...", "sellerName": "...", "invoiceSumVat": <amount>, "vatInPeriod": <amount>}, ...]},
        "sales_summary": {
            "standard_rate": {"rate": 24, "net_sales": <amount>, "vat_amount": <amount>},
            "reduced_rate": {"rate": 13, "net_sales": <amount>, "vat_amount": <amount>},
            "zero_rated": {"rate": 0, "net_sales": <amount>, "vat_amount": 0},
            "exempt": {"net_sales": <amount>, "vat_amount": 0}
        },
        "purchases_summary": {"total_purchases": <amount>, "input_vat_recoverable": <amount>},
        "vat_calculation": {
            "total_output_vat": <computed total VAT, line 4>,
            "total_input_vat": <inputVatTotal, line 5>,
            "net_vat_due": <line 12 payable, or negative of line 13 overpaid>
        },
        "reverse_charge_transactions": {"count": <n>, "total_value": <amount>, "vat_self_assessed": <amount>},
        "validation_results": {"cp1": true, "cp2": true, "cp3": true, "cp4": true, "cp5": true},
        "filing_instructions": {
            "form": "KMD + KMD INF + Form VD",
            "filing_method": "e-MTA XML upload",
            "portal_url": "https://maasikas.emta.ee",
            "due_date": "<YYYY-MM-20 of following month>",
            "payment_due": "<YYYY-MM-20 of following month>"
        }
    },
    "notes": "<Month Year> KMD - auto-calculated"
})
```

Tell the user: "Tax return saved (ID: {tax_return_id}). You can view it at Admin Dashboard → Tax → Returns."

### Step 9: Post VAT Closing Journal Entry

Post a journal entry to reclassify VAT accounts for the period. VAT Output/Input are already posted per-transaction — this entry moves the net balance to a VAT Payable (or Receivable) account.

**If Line 12 > 0 (net VAT payable):**
```
submit("transaction", "post", {
    "transaction_type_code": "GL_JOURNAL",
    "legal_entity_id": <entity_id>,
    "description": "VAT closing - KMD <YYYY>/<MM>",
    "transaction_date": "<last day of reporting period>",
    "lines": [
        { "account_number": "<VAT Output account>", "debit": <total output VAT, line 4>, "credit": 0 },
        { "account_number": "<VAT Input account>", "debit": 0, "credit": <inputVatTotal, line 5> },
        { "account_number": "<VAT Payable account>", "debit": 0, "credit": <net VAT payable, line 12> }
    ]
})
```

**If Line 13 > 0 (VAT overpaid/refundable):**
```
submit("transaction", "post", {
    "transaction_type_code": "GL_JOURNAL",
    "legal_entity_id": <entity_id>,
    "description": "VAT closing - KMD <YYYY>/<MM> (overpaid)",
    "transaction_date": "<last day of reporting period>",
    "lines": [
        { "account_number": "<VAT Output account>", "debit": <total output VAT, line 4>, "credit": 0 },
        { "account_number": "<VAT Receivable account>", "debit": <net VAT overpaid, line 13>, "credit": 0 },
        { "account_number": "<VAT Input account>", "debit": 0, "credit": <inputVatTotal, line 5> }
    ]
})
```

Tell the user: "VAT closing journal entry posted. Net VAT {payable/overpaid}: EUR {amount}."

> **Note:** Determine the correct VAT Output, Input, Payable, and Receivable account numbers by querying the entity's chart of accounts. Look for accounts with `account_subtype` matching `vat_output`, `vat_input`, or similar naming conventions.

### Step 10: Generate Output

Compile the final declaration package:

1. **KMD Form Summary** — All main-form values in a clear table
2. **KMD INF** — Part A (sales partners) and Part B (purchase partners)
3. **EC Sales List** — Form VD data (if applicable)
4. **Reconciliation** — GL vs KMD comparison
5. **Validation Results** — All checkpoint results from **references/validation-checklist.md**

Provide filing guidance from **references/emta-filing-guide.md**:
- Deadline: 20th of the following month
- Portal: e-MTA (maasikas.emta.ee)
- XML format available for upload (downloadable from Admin Dashboard → Tax → Returns → [this return])
- Digital signature required

After the user files with EMTA and receives confirmation, mark the return as filed
(this also transitions the tax reporting period to `filed`):
```
submit("tax_return", "file", {
    "return_id": <tax_return_id from Step 8>,
    "confirmation_number": "<confirmation from e-MTA>"
})
```

Then offer to **lock the period** so the filed return keeps matching the ledger:
```
submit("tax_period", "lock", {
    "period_id": <reporting_period_id>,
    "reason": "KMD filed — confirmation <number>"
})
```
To amend later: `submit("tax_period", "unlock", …)` → correct → re-file → re-lock.
The Reports → Sales tax reconciliation panel flags any ledger-vs-return drift.

> **Payment note:** Check your e-MTA prepayment account (ettemaksukonto) balance before paying. If payroll taxes or other obligations already created a positive balance, the actual payment may be lower than KMD Line 12. Make a bank transfer to EMTA — the bank statement reconciliation will clear the VAT Payable account.

## Output Format

Present the final output as a structured document with clear sections:
- KMD main-form table (KMD2 element values)
- KMD INF partner tables (Part A and Part B)
- EC Sales List table (if applicable)
- Reconciliation summary
- Validation checklist (pass/fail for each check)
- Tax return ID and link to Admin Dashboard
- Filing instructions and deadline reminder
