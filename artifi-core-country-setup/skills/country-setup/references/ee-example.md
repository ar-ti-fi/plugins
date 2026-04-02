# Annotated Example: Estonia (ee.json)

This is the complete Estonian template with annotations explaining each field's purpose. Use this as the gold standard when generating templates for other countries.

Source file: `mcp-server/src/data/onboarding/ee.json`

---

## Top-Level

```json
{
  "country_code": "EE",        // ISO 3166-1 alpha-2. Used for filtering throughout the system.
  "country_name": "Estonia",   // English name. Not used programmatically, just for readability.
```

## vat_tax_codes

Estonia uses EU VAT. Note: we include historical rates because companies may need to process older transactions.

```json
  "vat_tax_codes": [
    {
      "tax_code": "EU-EE-STD",           // Convention: EU-{CC}-{tier}
      "tax_name": "Estonian VAT Standard 24%",
      "tax_type": "vat",                  // Could be: vat, gst, sales_tax, hst
      "default_rate": 24.00,              // PERCENTAGE, not decimal
      "country_code": "EE",
      "description": "Estonian standard VAT rate (effective July 2025)"
    },
    // Historical rates (useful for processing past transactions)
    {"tax_code": "EU-EE-STD-22", "default_rate": 22.00, "description": "Historical (Jan 2024 - June 2025)"},
    {"tax_code": "EU-EE-OLD-20", "default_rate": 20.00, "description": "Historical (until Dec 2023)"},

    // Reduced, zero, exempt — every VAT country has these
    {"tax_code": "EU-EE-RED", "default_rate": 9.00, "description": "Reduced: books, medicines, accommodation"},
    {"tax_code": "EU-EE-ZERO", "default_rate": 0.00, "description": "Zero-rated: exports, intra-EU B2B"},
    {"tax_code": "EU-EE-EXEMPT", "default_rate": 0.00, "description": "Exempt: financial services, healthcare"},

    // Special mechanisms
    {"tax_code": "EU-EE-RC", "default_rate": 0.00, "description": "Reverse charge (construction, scrap metal)"},

    // EU-specific: intra-community transactions
    {"tax_code": "EU-EE-IC-ACQ", "default_rate": 24.00, "description": "Intra-EU acquisitions"},
    {"tax_code": "EU-EE-IC-SUPPLY", "default_rate": 0.00, "description": "Intra-EU supplies"}
  ],
```

**Key patterns:**
- Include historical rates if a recent rate change occurred
- EU countries need IC-ACQ and IC-SUPPLY codes
- Exempt and zero-rated are different: exempt = no VAT at all, zero = VAT at 0% (still reported)

## tax_authorities

```json
  "tax_authorities": [
    {
      "code": "EMTA",                           // Short uppercase, used as FK
      "name": "Maksu- ja Tolliamet",             // LOCAL LANGUAGE name
      "jurisdiction_type": "vat_authority",
      "country_code": "EE",
      "authority_type": "vat",
      "filing_frequency": "monthly",
      "website_url": "https://www.emta.ee",
      "metadata": {
        "name_en": "Estonian Tax and Customs Board",  // English name in metadata
        "tax_types": ["vat", "income", "social"]      // What this authority handles
      }
    },
    {
      "code": "EMTA-PAYROLL",                    // Same org, different code for payroll
      "name": "Maksu- ja Tolliamet (Payroll)",
      "jurisdiction_type": "payroll_authority",
      "authority_type": "payroll",
      "filing_frequency": "monthly",
      "metadata": {
        "filing_form": "TSD",                    // Official form name
        "filing_deadline_day": 10,               // Due on 10th of following month
        "payment_deadline_day": 10
      }
    }
  ],
```

**Key patterns:**
- In Estonia, the same authority (EMTA) handles both VAT and payroll — we create two entries with different codes
- Some countries have completely separate authorities for VAT vs payroll vs social security

## tax_jurisdictions

```json
  "tax_jurisdictions": [
    {
      "code": "EE-VAT",
      "name": "Estonian VAT",
      "jurisdiction_type": "country",            // Estonia is small = one national jurisdiction
      "country_code": "EE",
      "authority_code": "EMTA",                  // FK → tax_authorities.code
      "metadata": {
        "filing_frequency": "monthly",
        "form_code": "KMD"                       // The official VAT return form
      }
    }
  ],
```

**Key patterns:**
- `authority_code` MUST match a `code` in `tax_authorities`
- Larger countries may have multiple jurisdictions (e.g., state-level)

## tax_reporting_periods

```json
  "tax_reporting_periods": {
    "frequency": "monthly",         // "monthly" → 12 periods, "quarterly" → 4 periods
    "filing_due_day": 20,           // VAT return due on 20th of following month
    "generate_for_year": true       // Auto-generate periods for current year
  },
```

**Key patterns:**
- Set to `null` for countries without VAT/GST
- The executor generates actual period records from this config

## payroll_tax_jurisdictions

```json
  "payroll_tax_jurisdictions": [
    {
      "tax_type": "income",                   // Short identifier
      "tax_name": "Estonian Income Tax",
      "employee_rate": 0.22,                  // DECIMAL (0.22 = 22%), NOT percentage
      "effective_from": "2025-01-01",
      "metadata": {
        "basic_exemption": 700                // Country-specific details in metadata
      }
    },
    {
      "tax_type": "social",
      "tax_name": "Estonian Social Tax",
      "employer_rate": 0.33,                  // Employer-only tax
      "minimum_wage_base": 886,
      "effective_from": "2025-01-01"
    },
    {
      "tax_type": "unemployment",
      "tax_name": "Unemployment Insurance",
      "employee_rate": 0.016,                 // Split between employee and employer
      "employer_rate": 0.008,
      "effective_from": "2025-01-01"
    },
    {
      "tax_type": "pension_ii_pillar",
      "tax_name": "Pension II Pillar",
      "employee_rate": 0.02,                  // Employee-only
      "effective_from": "2025-01-01",
      "metadata": {"voluntary": true}         // Important context
    }
  ],
```

**Key patterns:**
- Rates are DECIMALS (0.22), not percentages (22)
- Use `null` for rates that don't apply (e.g., employer has no income tax rate)
- Include metadata for country-specific nuances (basic exemptions, brackets, voluntary flags)

## payroll_vendors

```json
  "payroll_vendors": [
    {
      "vendor_key": "emta",                     // Reference key for payroll_vendor_config
      "vendor_name": "Maksu- ja Tolliamet (EMTA)",
      "vendor_type": "government",
      "tax_id": "70000349",                     // Real registration number
      "email": "emta@emta.ee",
      "website": "https://www.emta.ee",
      "currency": "EUR",
      "payment_method": "wire",
      "notes": "Receives all payroll tax payments via single prepayment account.",
      "metadata": {
        "name_en": "Estonian Tax and Customs Board",
        "payment_accounts": [                   // Real bank account details
          {"bank": "SEB Pank", "iban": "EE351010052031000004", "swift": "EEUHEE2X"}
        ],
        "tax_types_handled": ["income_tax", "social_tax", "unemployment", "pension_ii_pillar"],
        "filing_forms": {
          "TSD": "Monthly payroll declaration — due 10th of following month"
        }
      }
    }
    // ... more vendors (Tootukassa, Pensionikeskus)
  ],
```

**Key patterns:**
- Use REAL data: actual tax IDs, actual bank accounts, actual websites
- `vendor_key` is the FK used by `payroll_vendor_config`
- Some countries route all payments through one agency (like Estonia's EMTA)
- Other countries have separate agencies for each tax type

## payroll_vendor_config

```json
  "payroll_vendor_config": [
    {"line_type": "income_tax", "vendor_key": "emta", "expense_account_number": null, "payable_account_number": "2410"},
    {"line_type": "social_tax", "vendor_key": "emta", "expense_account_number": "6100", "payable_account_number": "2420"},
    {"line_type": "unemployment_employee", "vendor_key": "tootukassa", "expense_account_number": null, "payable_account_number": "2440"},
    {"line_type": "unemployment_employer", "vendor_key": "tootukassa", "expense_account_number": "6100", "payable_account_number": "2440"},
    {"line_type": "pension", "vendor_key": "pension_fund", "expense_account_number": null, "payable_account_number": "2430"}
  ],
```

**Key patterns:**
- `expense_account_number` is null for employee-only deductions (income tax, employee unemployment)
- `expense_account_number` is set for employer-side costs (social tax, employer unemployment)
- Split employee/employer for taxes that have both components
- `vendor_key` MUST match a key in `payroll_vendors`

## payroll_gl_accounts

```json
  "payroll_gl_accounts": [
    {"account_number": "2420", "account_name": "Social Tax Payable", "account_type": "liability", "account_subtype": "current_liability", "normal_balance": "credit"},
    {"account_number": "2430", "account_name": "Pension Contributions Payable", "account_type": "liability", "account_subtype": "current_liability", "normal_balance": "credit"},
    {"account_number": "2440", "account_name": "Unemployment Insurance Payable", "account_type": "liability", "account_subtype": "current_liability", "normal_balance": "credit"},
    {"account_number": "6100", "account_name": "Social Security Costs", "account_type": "expense", "account_subtype": "operating_expense", "normal_balance": "debit"}
  ],
```

**Key patterns:**
- Only accounts that the standard COA might NOT have
- Liabilities in 2400-2499 range, expenses in 6000-6199 range
- These get inserted into `master_accounts` during onboarding

## withholding_tax_rates

```json
  "withholding_tax_rates": [
    {"payment_type": "services", "withholding_rate": 20.0, "description": "Non-resident services WHT"},
    {"payment_type": "interest", "withholding_rate": 20.0, "description": "Interest payments to non-residents"},
    {"payment_type": "royalties", "withholding_rate": 10.0, "description": "Royalty payments to non-residents"},
    {"payment_type": "dividends", "withholding_rate": 0.0, "description": "No WHT on dividends (CIT at distribution level)"}
  ],
```

**Key patterns:**
- Rates are PERCENTAGES (20.0 = 20%), not decimals
- Note: this is different from payroll rates which are decimals — be careful!
- Include 0.0 rates to explicitly document that the country doesn't withhold on that type

## vat_declaration

```json
  "vat_declaration": {
    "form_code": "KMD",
    "form_name": "Estonian VAT Return (kaibemaksudeklaratsioon)",
    "boxes": [
      {"box_number": "1", "box_label": "24% taxable supply", "tax_code_pattern": "EU-EE-STD", "transaction_type_filter": "sales", "sign_multiplier": 1},
      {"box_number": "2", "box_label": "9% taxable supply", "tax_code_pattern": "EU-EE-RED", "transaction_type_filter": "sales", "sign_multiplier": 1},
      {"box_number": "5", "box_label": "Input VAT deductible", "tax_code_pattern": "%", "transaction_type_filter": "purchases", "sign_multiplier": -1}
    ]
  }
```

**Key patterns:**
- `tax_code_pattern` uses SQL LIKE: `%` matches anything, `EU-EE-STD` matches exactly
- `sign_multiplier`: 1 for output/sales, -1 for input/purchases (credits reduce the return)
- Box numbers match the official government form
- Set entire `vat_declaration` to `null` for non-VAT countries
