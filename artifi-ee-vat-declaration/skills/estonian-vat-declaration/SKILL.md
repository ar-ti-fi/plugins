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

You MUST verify each checkpoint before proceeding. If a checkpoint fails, STOP and inform the user.

- **CP1**: All transactions for the period are posted (no drafts)
- **CP2**: All transaction lines have tax codes assigned
- **CP3**: KMD calculations balance (output VAT - input VAT = net VAT)
- **CP4**: KMD INF totals reconcile with KMD
- **CP5**: EC Sales List reconciles with KMD Lines 3.1 and 3.2

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

### Step 4: Calculate KMD Lines 1-13

Using the tax code classification from Step 1 and transactions from Step 2, calculate each KMD line following the formulas in **references/kmd-form-structure.md**:

**Output VAT (Sales side):**
- Line 1: Sum taxable base of sales with 24% rate codes
- Line 1.1: Sum VAT amount from those transactions (or Line 1 x 0.24)
- Line 2: Sum taxable base of sales with 13%/9% rate codes
- Line 2.1: Sum VAT amount from reduced-rate transactions
- Line 3: Sum of zero-rated exports (non-EU customers)
- Line 3.1: Sum of intra-community goods supplies
- Line 3.2: Sum of intra-community services supplies

**Input VAT (Purchase side):**
- Line 4: Sum of recoverable input VAT from all purchases
- Line 4.1: Subset of Line 4 posted to fixed asset accounts (1500-1599)

**Reverse charge / IC acquisitions:**
- Line 5: IC acquisition of goods (taxable base)
- Line 5.1: IC acquisition of services (taxable base)
- Line 6: Domestic reverse charge — goods
- Line 7: Domestic reverse charge — real estate / scrap metal

**Adjustments and totals:**
- Line 8: Credit notes, corrections, bad debt relief (net adjustment)
- Line 10: (Line 1.1 + Line 2.1) - Line 4 + Line 8
- Line 11: Import VAT (from customs declarations)
- Line 12: VAT payable = max(0, Line 10 + Line 11)
- Line 13: VAT overpaid = max(0, -(Line 10 + Line 11))

**CP3 checkpoint**: Verify Line 12 and Line 13 are mutually exclusive. Verify Line 10 formula is correct.

Present the completed KMD form to the user in a table.

### Step 5: Prepare KMD INF Annex

Following **references/kmd-inf-annex.md**:

1. **Part A (Sales)**: Group AR invoices by customer. For each customer where total > EUR 1,000:
   ```
   aggregate_entities("transaction", ["party_name"], {"amount": "sum", "id": "count"},
       {"legal_entity_id": ID, "transaction_type": "ar_invoice"},
       date_filters={"transaction_date": {"from": "YYYY-MM-01", "to": "YYYY-MM-DD"}})
   ```
   Collect: partner registration code, name, invoice count, taxable amount, VAT amount.

2. **Part B (Purchases)**: Group AP invoices by vendor. For each vendor where total > EUR 1,000:
   Same approach, filtering for `transaction_type = "ap_invoice"`.

3. Validate registration codes (8-digit format for Estonian partners).

**CP4 checkpoint**: Verify Part A totals are consistent with KMD output VAT lines. Verify Part B totals are consistent with total AP invoice base.

### Step 6: Prepare EC Sales List (Form VD)

Following **references/ec-sales-list.md**:

1. Identify intra-community supply transactions (zero-rated sales to EU B2B customers)
2. Group by customer VAT number
3. Classify supply type: **G** (goods), **S** (services), or **T** (triangular)
4. Calculate total supply amount per customer per type

**CP5 checkpoint**: Verify Form VD goods total = KMD Line 3.1, services total = KMD Line 3.2. If no IC transactions exist, note that Form VD is not required.

### Step 7: Reconcile VAT GL Accounts

Compare calculated KMD amounts with GL account balances:

```
generate_report("trial_balance", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})
```

1. VAT Output account balance should match total output VAT (Lines 1.1 + 2.1)
2. VAT Input account balance should match Line 4
3. Net VAT payable/receivable should match Line 12 or Line 13

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
        "kmd_lines": {
            "line_1": <Line 1>, "line_1_1": <Line 1.1>,
            "line_2": <Line 2>, "line_2_1": <Line 2.1>,
            "line_3": <Line 3>, "line_3_1": <Line 3.1>, "line_3_2": <Line 3.2>,
            "line_4": <Line 4>, "line_4_1": <Line 4.1>,
            "line_5": <Line 5>, "line_5_1": <Line 5.1>,
            "line_6": <Line 6>, "line_7": <Line 7>, "line_8": <Line 8>,
            "line_10": <Line 10>, "line_11": <Line 11>,
            "line_12": <Line 12>, "line_13": <Line 13>
        },
        "kmd_inf": {
            "part_a": [{"reg_code": "...", "name": "...", "invoices": <amount>, "vat": <amount>}, ...],
            "part_b": [{"reg_code": "...", "name": "...", "invoices": <amount>, "vat": <amount>}, ...]
        },
        "vd_entries": [{"vat_number": "...", "name": "...", "goods": <amount>, "services": <amount>, "triangular": <amount>}, ...],
        "sales_summary": {
            "standard_rate": {"rate": 24, "net_sales": <amount>, "vat_amount": <amount>},
            "reduced_rate": {"rate": 13, "net_sales": <amount>, "vat_amount": <amount>},
            "zero_rated": {"rate": 0, "net_sales": <amount>, "vat_amount": 0},
            "exempt": {"net_sales": <amount>, "vat_amount": 0}
        },
        "purchases_summary": {"total_purchases": <amount>, "input_vat_recoverable": <amount>},
        "vat_calculation": {
            "total_output_vat": <Line 1.1 + Line 2.1>,
            "total_input_vat": <Line 4>,
            "net_vat_due": <Line 12 or negative of Line 13>
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
        { "account_number": "<VAT Output account>", "debit": <Line 1.1 + Line 2.1>, "credit": 0 },
        { "account_number": "<VAT Input account>", "debit": 0, "credit": <Line 4> },
        { "account_number": "<VAT Payable account>", "debit": 0, "credit": <Line 12> }
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
        { "account_number": "<VAT Output account>", "debit": <Line 1.1 + Line 2.1>, "credit": 0 },
        { "account_number": "<VAT Receivable account>", "debit": <Line 13>, "credit": 0 },
        { "account_number": "<VAT Input account>", "debit": 0, "credit": <Line 4> }
    ]
})
```

Tell the user: "VAT closing journal entry posted. Net VAT {payable/overpaid}: EUR {amount}."

> **Note:** Determine the correct VAT Output, Input, Payable, and Receivable account numbers by querying the entity's chart of accounts. Look for accounts with `account_subtype` matching `vat_output`, `vat_input`, or similar naming conventions.

### Step 10: Generate Output

Compile the final declaration package:

1. **KMD Form Summary** — All lines 1-13 in a clear table
2. **KMD INF** — Part A (sales partners) and Part B (purchase partners)
3. **EC Sales List** — Form VD data (if applicable)
4. **Reconciliation** — GL vs KMD comparison
5. **Validation Results** — All checkpoint results from **references/validation-checklist.md**

Provide filing guidance from **references/emta-filing-guide.md**:
- Deadline: 20th of the following month
- Portal: e-MTA (maasikas.emta.ee)
- XML format available for upload (downloadable from Admin Dashboard → Tax → Returns → [this return])
- Digital signature required

After the user files with EMTA and receives confirmation, mark the return as filed:
```
submit("tax_return", "file", {
    "return_id": <tax_return_id from Step 8>,
    "confirmation_number": "<confirmation from e-MTA>"
})
```

> **Payment note:** Check your e-MTA prepayment account (ettemaksukonto) balance before paying. If payroll taxes or other obligations already created a positive balance, the actual payment may be lower than KMD Line 12. Make a bank transfer to EMTA — the bank statement reconciliation will clear the VAT Payable account.

## Output Format

Present the final output as a structured document with clear sections:
- KMD form table (Lines 1-13 with amounts)
- KMD INF partner tables (Part A and Part B)
- EC Sales List table (if applicable)
- Reconciliation summary
- Validation checklist (pass/fail for each check)
- Tax return ID and link to Admin Dashboard
- Filing instructions and deadline reminder
