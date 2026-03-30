---
name: Calculate Estonian Payroll
command: calculate-payroll
description: Calculate gross-to-net payroll for an Estonian legal entity and submit results to the ERP.
---

# /artifi-ee:calculate-payroll

Calculate Estonian payroll for a draft payroll run.

## Usage

```
/artifi-ee:calculate-payroll <payroll_run_id>
```

## What This Command Does

1. Loads the payroll run and verifies it's in `draft` status
2. Fetches all active employees with compensation, tax settings, and deductions
3. Loads Estonian tax rates from `payroll_tax_jurisdictions`
4. Calculates per-employee:
   - Unemployment insurance (employee 1.6%, employer 0.8%)
   - Funded pension II pillar (2%/4%/6% per employee setting)
   - Pre-tax voluntary deductions
   - Income tax (22% after exemptions)
   - Post-tax deductions
   - Net pay
   - Social tax (33% employer, with minimum base)
5. Submits calculated results via `submit_calculation`
6. Presents summary table

## Prerequisites

- Payroll run must exist in `draft` status
- All employees must have:
  - Active `employee_compensation` record
  - Active `employee_tax_settings` record
- Entity must have `payroll_vendor_config` configured for Estonian taxes
- See **skills/estonian-payroll/SKILL.md** for full checkpoint list

## After Calculation

The payroll run transitions to `calculated` status. Next steps:

```
# Review and approve
submit(object_type="payroll_run", operation="approve", data='{"payroll_run_id": <id>}')

# Process payment (creates GL transaction + payment batch)
submit(object_type="payroll_run", operation="process_payment", data='{"payroll_run_id": <id>, "payment_date": "YYYY-MM-DD", "bank_account_id": <id>}')
```

## Example Output

```
Estonian Payroll Calculation - January 2026
Entity: OÜ Example (ID: 12)
Payroll Run: #42

| Employee       | Gross     | EE Taxes  | Deductions | Net Pay   | ER Cost   |
|----------------|-----------|-----------|------------|-----------|-----------|
| Jaan Tamm      | 3,500.00  | 714.28    | 0.00       | 2,785.72  | 4,683.00  |
| Mari Mets      | 4,200.00  | 884.48    | 200.00     | 3,115.52  | 5,613.60  |
| Totals         | 7,700.00  | 1,598.76  | 200.00     | 5,901.24  | 10,296.60 |

Payroll run #42 is now in 'calculated' status.
Approve with: submit(object_type="payroll_run", operation="approve", ...)
```
