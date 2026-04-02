# Country Onboarding Template Schema

This document defines the exact JSON structure for country onboarding templates stored in `mcp-server/src/data/onboarding/{cc}.json`. Every field, its type, and whether it's required are specified below.

The template is consumed by `mcp-server/src/tools/onboarding/task_executors.py` during entity onboarding. The loader is `mcp-server/src/tools/onboarding/country_templates.py`.

---

## Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `country_code` | string | Yes | ISO 3166-1 alpha-2 code (e.g., "DE", "LV", "AU") |
| `country_name` | string | Yes | English country name (e.g., "Germany") |

---

## `vat_tax_codes` (array, required)

Each entry represents one tax rate tier. Inserted into `master_tax_codes`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tax_code` | string | Yes | Unique code (e.g., "EU-DE-STD"). Convention: `{system}-{CC}-{tier}` |
| `tax_name` | string | Yes | Display name (e.g., "German VAT Standard 19%") |
| `tax_type` | string | Yes | One of: "vat", "gst", "sales_tax", "hst" |
| `default_rate` | number | Yes | Percentage rate (e.g., 19.00 for 19%) |
| `country_code` | string | Yes | Must match top-level country_code |
| `description` | string | No | What this rate applies to |

**Minimum entries:** Standard rate, zero rate, exempt. Include reduced rate(s) and reverse charge where applicable.

---

## `tax_authorities` (array, required)

Each entry represents a government tax body. Inserted into `master_tax_authorities`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | Yes | Short uppercase code (e.g., "BZSt", "HMRC", "ATO"). Used as FK reference. |
| `name` | string | Yes | Official local-language name |
| `jurisdiction_type` | string | Yes | One of: "vat_authority", "payroll_authority", "income_tax_authority", "sales_tax_authority" |
| `country_code` | string | Yes | Must match top-level country_code |
| `authority_type` | string | Yes | One of: "vat", "payroll", "income", "customs", "sales_tax" |
| `filing_frequency` | string | No | "monthly", "quarterly", or "annually" |
| `website_url` | string | No | Official website URL |
| `metadata` | object | No | Additional info: `name_en`, `tax_types`, `filing_form`, `filing_deadline_day` |

---

## `tax_jurisdictions` (array, required)

Each entry defines a tax jurisdiction. Inserted into `tax_jurisdictions`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | Yes | Short code (e.g., "DE-VAT", "AU-GST") |
| `name` | string | Yes | Display name |
| `jurisdiction_type` | string | Yes | "country", "state", "province", "canton", "federal" |
| `country_code` | string | Yes | Must match top-level country_code |
| `authority_code` | string | Yes | **Must reference a code from `tax_authorities`** |
| `metadata` | object | No | Filing frequency, form codes, etc. |

---

## `tax_reporting_periods` (object or null)

Configuration for generating filing periods. Set to `null` if country has no VAT/GST.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `frequency` | string | Yes | "monthly" or "quarterly" |
| `filing_due_day` | integer | Yes | Day of the following period when return is due (1-28) |
| `generate_for_year` | boolean | No | Whether to auto-generate periods for current year (default true) |

---

## `payroll_tax_jurisdictions` (array, required)

Each entry represents a mandatory payroll tax. Inserted into `payroll_tax_jurisdictions`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tax_type` | string | Yes | Short identifier: "income", "social", "unemployment", "pension", "health_insurance", "medicare", "social_security" |
| `tax_name` | string | Yes | Display name, ideally with local-language name |
| `employee_rate` | number or null | Conditional | Decimal rate (0.22 = 22%). Null if not applicable or progressive. |
| `employer_rate` | number or null | Conditional | Decimal rate. Null if not applicable. |
| `effective_from` | string | No | ISO date "YYYY-MM-DD". Default: "2025-01-01" |
| `wage_base_limit` | number or null | No | Maximum wage base for this tax |
| `minimum_wage_base` | number or null | No | Minimum wage base |
| `metadata` | object | No | Filing frequency, forms, authority, brackets, basic exemption, etc. |

**Note:** At least one of `employee_rate` or `employer_rate` must be non-null. If the rate is progressive (brackets), set the rate to null and describe brackets in metadata.

---

## `payroll_vendors` (array)

Government entities that receive payroll tax payments. Inserted into `master_vendors`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `vendor_key` | string | Yes | Unique key for referencing in config (e.g., "emta", "finanzamt") |
| `vendor_name` | string | Yes | Official name in local language |
| `vendor_type` | string | Yes | "government" |
| `tax_id` | string | No | Official registration number |
| `email` | string | No | Official contact email |
| `phone` | string | No | Official phone with country code |
| `website` | string | No | Official website URL |
| `currency` | string | Yes | ISO 4217 currency code (e.g., "EUR", "AUD") |
| `payment_method` | string | No | "wire" (default) |
| `notes` | string | No | Description of what this vendor handles |
| `metadata` | object | No | `name_en`, `registry_code`, `address`, `payment_accounts`, `filing_forms`, etc. |

---

## `payroll_vendor_config` (array)

Maps payroll tax types to vendors and GL accounts. Inserted into `payroll_vendor_config`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `line_type` | string | Yes | Tax type identifier (e.g., "income_tax", "social_tax", "unemployment_employee") |
| `vendor_key` | string | Yes | **Must reference a vendor_key from `payroll_vendors`** |
| `expense_account_number` | string or null | No | GL account for employer-side costs (e.g., "6100"). Null for employee-only deductions. |
| `payable_account_number` | string | Yes | GL liability account (e.g., "2410") |

---

## `payroll_gl_accounts` (array)

Additional GL accounts needed for payroll that may not exist in the standard COA.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account_number` | string | Yes | Account number (e.g., "2420") |
| `account_name` | string | Yes | Display name |
| `account_type` | string | Yes | "liability" or "expense" |
| `account_subtype` | string | Yes | "current_liability" or "operating_expense" |
| `normal_balance` | string | Yes | "credit" for liabilities, "debit" for expenses |

---

## `withholding_tax_rates` (array)

WHT rates for non-resident payments. Inserted into `withholding_tax_rates`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `payment_type` | string | Yes | One of: "services", "interest", "royalties", "dividends", "rent", "management_fees" |
| `withholding_rate` | number | Yes | Percentage rate (e.g., 15.0 for 15%). Use 0.0 if no WHT. |
| `description` | string | No | Description of what triggers this rate |

---

## `vat_declaration` (object or null)

VAT return form structure. Set to `null` if country doesn't use VAT/GST. Inserted into `vat_declaration_mapping`.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `form_code` | string | Yes | Official form identifier (e.g., "KMD", "UStVA", "BAS") |
| `form_name` | string | Yes | Full form name with local-language name |
| `boxes` | array | Yes | Array of box definitions (see below) |

### Box definition:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `box_number` | string | Yes | Box/line number on the form |
| `box_label` | string | Yes | Label text |
| `tax_code_pattern` | string | No | SQL LIKE pattern matching `vat_tax_codes[].tax_code` (use % wildcard) |
| `transaction_type_filter` | string | No | "sales", "purchases", or "all" |
| `sign_multiplier` | integer | No | 1 (addition) or -1 (subtraction). Default: 1 |
| `description` | string | No | Additional explanation |

---

## `deduction_templates` (array)

Common payroll deductions for the country. Not inserted during onboarding currently but stored for reference and future use.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `deduction_type` | string | Yes | Unique identifier (e.g., "voluntary_pension", "health_insurance") |
| `deduction_name` | string | Yes | Display name with local-language name where relevant |
| `deduction_category` | string | Yes | "voluntary_benefit", "court_order", or "employer_cost" |
| `is_mandatory` | boolean | Yes | True for court orders, false for voluntary |
| `calculation_method` | string | Yes | "percentage", "fixed", or "none" |
| `default_percentage` | number | No | Default rate if calculation_method is "percentage" |
| `is_pre_tax` | boolean | No | Whether deducted before income tax calculation |
| `payable_account_number` | string | No | GL account for the liability |
| `expense_account_number` | string | No | GL account for employer-side cost |
| `description` | string | No | Description with country-specific context |
