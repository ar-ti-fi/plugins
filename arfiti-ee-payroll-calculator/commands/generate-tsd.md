---
name: Generate TSD Declaration
command: generate-tsd
description: Generate Estonian TSD (monthly tax declaration) from a calculated or approved payroll run.
---

# /arfiti-ee:generate-tsd

Generate the Estonian monthly TSD declaration for EMTA filing.

## Usage

```
/arfiti-ee:generate-tsd <payroll_run_id>
```

## What This Command Does

1. Loads the payroll run (must be `calculated` or `approved`)
2. Fetches payroll run details and detail lines
3. Fetches employee tax IDs (isikukood) from `employee_tax_settings`
4. Builds TSD Part I summary (aggregate totals)
5. Builds Annex 1 per-employee breakdown
6. Optionally builds Annex 4 (fringe benefits) if applicable
7. Generates XML file for EMTA upload
8. Presents summary for review

## Prerequisites

- Payroll run must be in `calculated` or `approved` status
- All employees must have `tax_id_number` in `employee_tax_settings`
- Entity must have a tax registration code

## TSD Filing Deadline

The TSD must be filed by the **10th of the following month**. Tax payment is also due by the 10th.

## Example Output

```
TSD Declaration - January 2026
Entity: OÜ Example (Reg: 12345678)

Part I Summary:
  Total Gross Payments:     EUR 7,700.00
  Income Tax Withheld:      EUR 1,218.56
  Social Tax:               EUR 2,541.00
  Unemployment (Employer):  EUR 61.60
  Unemployment (Employee):  EUR 123.20
  Funded Pension:           EUR 238.00

Annex 1 - 2 employees:
  Jaan Tamm (39001011234): Gross 3,500.00, Tax 588.28
  Mari Mets (49501052345): Gross 4,200.00, Tax 630.28

XML file generated. Upload to e-MTA portal at https://www.emta.ee
Filing deadline: February 10, 2026
```

## See Also

- **references/tsd-declaration.md** — Full TSD structure and XML format
- **references/estonian-tax-formulas.md** — Tax rate reference
