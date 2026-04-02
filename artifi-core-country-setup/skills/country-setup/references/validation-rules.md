# Validation Rules for Country Templates

Run ALL checks before generating the output file. Present results as a checklist.

---

## Referential Integrity

- [ ] **tax_jurisdictions → tax_authorities**: Every `authority_code` in `tax_jurisdictions` MUST exist as a `code` in `tax_authorities`
- [ ] **payroll_vendor_config → payroll_vendors**: Every `vendor_key` in `payroll_vendor_config` MUST exist as a `vendor_key` in `payroll_vendors`
- [ ] **vat_declaration.boxes → vat_tax_codes**: Every `tax_code_pattern` in `vat_declaration.boxes` MUST match at least one `tax_code` in `vat_tax_codes` (using SQL LIKE matching with %)

---

## Rate Sanity

- [ ] **VAT rates**: All `default_rate` in `vat_tax_codes` must be >= 0 and <= 100. Standard rate should be > 0 (unless the country truly has 0% standard rate).
- [ ] **Payroll rates as decimals**: All `employee_rate` and `employer_rate` in `payroll_tax_jurisdictions` must be between 0.0 and 1.0 (NOT percentages). Example: 22% = 0.22.
- [ ] **WHT rates as percentages**: All `withholding_rate` in `withholding_tax_rates` must be >= 0 and <= 100.
- [ ] **No extreme rates**: Flag any employer social security contribution > 50% as suspicious. Flag any single payroll tax > 40% as suspicious. These may be correct but should be double-checked.
- [ ] **Standard VAT rate plausibility**: Most countries have standard VAT between 5% and 27%. Rates outside this range should be flagged.

---

## Country Code Consistency

- [ ] **Top-level** `country_code` matches every occurrence in nested objects:
  - `vat_tax_codes[].country_code`
  - `tax_authorities[].country_code`
  - `tax_jurisdictions[].country_code`
- [ ] **Currency consistency**: `payroll_vendors[].currency` should all use the country's official currency

---

## GL Account Numbering

- [ ] **Payroll liabilities**: Account numbers in `payroll_gl_accounts` and `payroll_vendor_config.payable_account_number` should be in the 2400-2499 range (current liabilities)
- [ ] **Employer costs**: `payroll_vendor_config.expense_account_number` should be in the 6000-6199 range (operating expenses)
- [ ] **No duplicate account numbers**: Each `account_number` in `payroll_gl_accounts` should be unique

---

## Completeness

- [ ] **VAT/tax codes**: At least 3 entries (standard, zero, exempt) for VAT countries. Can be empty for non-VAT countries.
- [ ] **Tax authorities**: At least 1 entry
- [ ] **Tax jurisdictions**: At least 1 entry
- [ ] **Payroll tax jurisdictions**: At least 2 entries (income tax + social security at minimum)
- [ ] **WHT rates**: At least 4 entries (services, interest, royalties, dividends)
- [ ] **Payroll vendors**: At least 1 entry
- [ ] **Payroll vendor config**: At least as many entries as there are distinct tax types in payroll_tax_jurisdictions

---

## Conditional Rules

- [ ] **Non-VAT countries**: If the country uses sales tax instead of VAT (e.g., US), then `vat_declaration` MUST be `null` and `tax_reporting_periods` MUST be `null`
- [ ] **EU countries**: Should have intra-community acquisition and supply codes in `vat_tax_codes` (IC-ACQ, IC-SUPPLY)
- [ ] **Progressive income tax**: If `employee_rate` is `null` for income tax, the `metadata` field MUST explain the bracket structure

---

## URL Validation

- [ ] **Website URLs**: All `website_url` fields in `tax_authorities` and `website` fields in `payroll_vendors` should start with "https://"
- [ ] **No placeholder URLs**: No "example.com" or clearly fake URLs

---

## Reporting Format

Present results as:

```
Validation Report for {CC} ({Country Name})
============================================

Referential Integrity:    5/5 passed
Rate Sanity:              4/4 passed
Country Code Consistency: 2/2 passed
GL Account Numbering:     3/3 passed
Completeness:             6/6 passed
Conditional Rules:        2/2 passed
URL Validation:           2/2 passed

Total: 24/24 checks passed

Warnings:
- (none)

Low Confidence Items:
- (list any items where web search returned conflicting info)
```
