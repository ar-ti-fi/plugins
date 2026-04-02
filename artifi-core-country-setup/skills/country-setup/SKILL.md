---
name: Country Setup Template Generator
description: Generates country-specific tax and payroll onboarding templates by researching a country's tax system, validating findings against official sources, and producing a structured JSON file for the Artifi ERP onboarding system.
---

## Trigger

Activate when the user mentions: generate country template, country setup, country configuration, set up country, create country template, add country support, new country onboarding, or invokes `/generate-country-template`.

## Before You Start — Gather Information

1. **Which country?** Get the 2-letter ISO 3166-1 alpha-2 country code (e.g., DE, LV, AU, FR). If the user provides a country name, convert it to the code.

2. **Check if template already exists.** Read `mcp-server/src/data/onboarding/` to see if `{cc}.json` already exists. If it does, inform the user and ask if they want to regenerate it.

3. **Read the reference files** before starting:
   - Read `references/template-schema.md` for the exact JSON structure
   - Read `references/ee-example.md` to see a complete working example
   - Read `references/validation-rules.md` for cross-validation rules

## Mandatory Checkpoints

You MUST verify each checkpoint before proceeding. If a checkpoint fails, STOP and help the user fix the issue.

- **CP1**: Tax system research validated — all VAT/tax rates verified against official sources
- **CP2**: Payroll system research validated — all payroll tax rates and vendor details verified
- **CP3**: VAT declaration structure and reporting config confirmed
- **CP4**: Cross-validation passes — all referential integrity checks, rate sanity checks, and consistency checks pass

---

## Phase 1 — Parallel Research

*Goal: Research the country's tax and payroll systems simultaneously using specialized agents.*

### Step 1: Spawn Research Agents

Launch both agents **in parallel**, giving each:
- The country code
- The path to `references/template-schema.md` and `references/ee-example.md`
- Instructions to web-search and verify ALL data against official government sources

**Tax Researcher agent** — research and return:
- `vat_tax_codes` (all VAT/GST rate tiers)
- `tax_authorities` (government tax bodies)
- `tax_jurisdictions` (jurisdiction definitions)
- `withholding_tax_rates` (WHT for non-resident payments)

**Payroll Specialist agent** — research and return:
- `payroll_tax_jurisdictions` (all mandatory payroll taxes with rates)
- `payroll_vendors` (government entities employers pay)
- `payroll_vendor_config` (tax-type-to-vendor-and-GL mappings)
- `payroll_gl_accounts` (required payroll liability/expense accounts)
- `deduction_templates` (common voluntary and mandatory deductions)

### Step 2: Collect and Review Results

Wait for both agents to complete. Review their outputs for:
- Completeness (all sections present)
- Structural correctness (fields match the template schema)
- Obvious errors (rates > 100%, missing required fields)

---

## Phase 2 — User Review

*Goal: Present the research findings to the user for confirmation before proceeding.*

### Step 3: Present Tax System Findings

Present the tax researcher's findings in clear tables:

**VAT/Tax Codes:**

| Code | Name | Rate | Type | Description |
|------|------|------|------|-------------|
| ... | ... | ...% | vat | ... |

**Tax Authorities:**

| Code | Name | Type | Filing | Website |
|------|------|------|--------|---------|
| ... | ... | ... | monthly | ... |

**Withholding Tax Rates:**

| Payment Type | Rate | Description |
|--------------|------|-------------|
| services | ...% | ... |
| interest | ...% | ... |

Include the sources used for verification (URLs from web search).

**CP1 checkpoint**: Ask the user: "Do these tax rates and authorities look correct? Any corrections needed?" Wait for confirmation before proceeding.

### Step 4: Present Payroll Findings

Present the payroll specialist's findings:

**Payroll Tax Jurisdictions:**

| Type | Name | Employee Rate | Employer Rate | Notes |
|------|------|---------------|---------------|-------|
| income | ... | ...% | - | ... |
| social | ... | ...% | ...% | ... |

**Government Payroll Vendors:**

| Key | Name | Tax Types Handled |
|-----|------|-------------------|
| ... | ... | ... |

**Payroll Vendor Config:**

| Line Type | Vendor | Expense Acct | Payable Acct |
|-----------|--------|--------------|--------------|
| income_tax | ... | - | 2410 |

Include the sources used for verification.

**CP2 checkpoint**: Ask the user: "Do these payroll tax rates and vendor details look correct? Any corrections needed?" Wait for confirmation before proceeding.

---

## Phase 3 — Compliance Structure

*Goal: Build the VAT declaration form mapping, reporting config, and finalize deduction templates. You act as a Compliance Specialist in this phase.*

### Step 5: Build VAT Declaration Mapping

Using the confirmed tax codes from Phase 2, research the official VAT return form for this country:

1. **Web search** for the official VAT/GST return form structure (box numbers, labels, what goes where)
2. Map each box to the appropriate tax_code_pattern from the confirmed vat_tax_codes
3. Determine the form_code (official form identifier)

Build the `vat_declaration` section:

```json
{
  "form_code": "UStVA",
  "form_name": "German VAT Pre-Return (Umsatzsteuervoranmeldung)",
  "boxes": [
    {
      "box_number": "81",
      "box_label": "Taxable sales at 19%",
      "tax_code_pattern": "EU-DE-STD",
      "transaction_type_filter": "sales",
      "sign_multiplier": 1,
      "description": "Net amount of sales at standard rate"
    }
  ]
}
```

**Rules:**
- `tax_code_pattern` uses SQL LIKE patterns (% for wildcard) and MUST match actual codes from `vat_tax_codes`
- `transaction_type_filter`: "sales", "purchases", or "all"
- `sign_multiplier`: 1 for additions, -1 for subtractions (input VAT is typically -1)
- If the country does NOT use VAT/GST (e.g., US states with sales tax only), set `vat_declaration` to `null`

### Step 6: Build Tax Reporting Config

Determine the filing frequency and due dates:

```json
{
  "frequency": "monthly",
  "filing_due_day": 10,
  "generate_for_year": true
}
```

**Web search** to verify: How often are VAT returns filed? What day of the following month/quarter is the deadline?

If the country has no VAT/GST, set `tax_reporting_periods` to `null`.

### Step 7: Review Deduction Templates

Review the payroll specialist's deduction templates. Ensure they cover:
- Voluntary pension/retirement schemes
- Supplementary health insurance (if applicable)
- Court-ordered deductions (garnishments, child support)
- Common employer benefits (meals, transport, gym)
- Fringe benefit taxation (if the country taxes benefits-in-kind)

**CP3 checkpoint**: Present the VAT declaration structure, reporting config, and deduction templates. Ask the user: "Does the VAT form structure and reporting setup look correct?" Wait for confirmation.

---

## Phase 4 — Validation and Output

*Goal: Cross-validate ALL data for consistency, verify a final time against web sources, and produce the output file. You act as a Financial Controller in this phase — be skeptical and thorough.*

### Step 8: Cross-Validation Checks

Run every check from `references/validation-rules.md`:

**Referential Integrity:**
- [ ] Every `authority_code` in `tax_jurisdictions` exists in `tax_authorities[].code`
- [ ] Every `vendor_key` in `payroll_vendor_config` exists in `payroll_vendors[].vendor_key`
- [ ] Every `tax_code_pattern` in `vat_declaration.boxes` matches at least one code in `vat_tax_codes`

**Rate Sanity:**
- [ ] All `default_rate` values in `vat_tax_codes` are between 0 and 100
- [ ] All payroll rates (employee_rate, employer_rate) are between 0 and 1 (decimal format)
- [ ] All `withholding_rate` values are between 0 and 100
- [ ] No suspiciously high rates (e.g., social security > 50% employer-side is unusual)

**Consistency:**
- [ ] `country_code` is the same across ALL sections
- [ ] Currency in `payroll_vendors` matches the country's official currency
- [ ] GL account numbers follow the numbering convention (2400-2499 for payroll liabilities, 6000-6199 for employer costs)
- [ ] Every payroll tax type in `payroll_tax_jurisdictions` has a corresponding `payroll_vendor_config` entry

**Completeness:**
- [ ] At least 3 VAT/tax codes (standard, zero, exempt at minimum)
- [ ] At least 1 tax authority
- [ ] At least 1 tax jurisdiction
- [ ] At least 2 payroll tax types
- [ ] WHT rates cover: services, interest, royalties, dividends

### Step 9: Final Web Verification

Pick 3-5 key data points and web-search them ONE MORE TIME to catch any errors:
- The standard VAT rate
- The main employer social security rate
- The tax authority's official website URL
- The WHT rate on dividends
- The VAT filing deadline

### Step 10: Present Validation Report

Present the validation results as a checklist showing pass/fail for each check. Include:
- Total checks run and passed
- Any warnings or low-confidence items
- Sources used for verification

**CP4 checkpoint**: Ask the user: "All validation checks pass. Shall I generate the template file?" Wait for explicit confirmation.

### Step 11: Generate Output File

Assemble the complete JSON template by combining all validated sections:

```json
{
  "country_code": "XX",
  "country_name": "Country Name",
  "vat_tax_codes": [...],
  "tax_authorities": [...],
  "tax_jurisdictions": [...],
  "tax_reporting_periods": {...},
  "payroll_tax_jurisdictions": [...],
  "deduction_templates": [...],
  "payroll_vendors": [...],
  "payroll_vendor_config": [...],
  "payroll_gl_accounts": [...],
  "withholding_tax_rates": [...],
  "vat_declaration": {...}
}
```

Write the file to: `mcp-server/src/data/onboarding/{cc}.json`

Present a summary:
- File path written
- Number of records per section
- Next steps: "The template is ready. To use it, commit the file and onboard a new entity with `country_code='{CC}'`. The onboarding executors will automatically pick up the template."

---

## Error Handling

**Agent returns incomplete data:** Ask the agent to retry the missing sections. If it fails again, research those sections yourself using web search.

**Conflicting rates found:** Present both sources to the user and ask which is correct. Add a note in the metadata about the discrepancy.

**Country has no VAT/GST:** Set `vat_tax_codes` to an empty array, `vat_declaration` to `null`, and `tax_reporting_periods` to `null`. This is valid — the onboarding executors handle null gracefully.

**Country has regional/state-level taxes:** Note the complexity in metadata. For the template, use the most common national-level rates. State/provincial variations should be documented in metadata but don't need separate entries unless the country has no national rate (e.g., US sales tax).
