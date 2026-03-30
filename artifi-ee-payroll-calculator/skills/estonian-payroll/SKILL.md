---
name: Estonian Payroll Calculator
description: Calculates Estonian payroll (gross-to-net) with income tax, social tax, unemployment insurance, funded pension, and voluntary deductions. Submits results to the ERP via submit_calculation.
---

## Trigger

Activate when the user mentions: calculate payroll, process payroll, run payroll, palgaarvestus, or palga arvestamine for an Estonian legal entity.

## Prerequisites

Before starting, confirm with the user:
1. **Legal entity ID** — which Estonian entity to run payroll for
2. **Payroll run ID** — the draft payroll run to calculate (or offer to create one)
3. **Pay period** — e.g. January 2026

## Mandatory Checkpoints

You MUST verify each checkpoint before proceeding. If a checkpoint fails, STOP and inform the user.

- **CP1**: Payroll run exists and is in `draft` status
- **CP2**: All employees in the run have active compensation records
- **CP3**: All employees have tax settings (pension tier, basic exemption)
- **CP4**: Tax rates loaded from `payroll_tax_jurisdictions` (country_code = "EE")
- **CP5**: For each employee: `net_pay = gross_pay - total_employee_taxes - total_deductions` (within 0.02 tolerance)
- **CP6**: Submission via `submit_calculation` succeeds

## Workflow Steps

### Step 1: Load Payroll Run & Verify Status

```python
run = get_entity("payroll_run", id=<run_id>)
```

Verify:
- `status` is `draft` (or `calculated` for recalculation)
- `legal_entity_id` matches the target entity
- Note the `payroll_period_id` for date range

**CP1 checkpoint**: Confirm run is in draft status.

### Step 2: Load Employee Data

Fetch all employees included in this payroll run:

```python
# Get employees for this entity
employees = list_entities("employee", {
    "legal_entity_id": <entity_id>,
    "status": "active"
})
```

For each employee, fetch:

```python
# Compensation (salary amount)
comp = search("employee_compensation", "", {
    "employee_id": <emp_id>,
    "effective_to": null
})

# Tax settings (pension tier, basic exemption)
tax = search("employee_tax_settings", "", {
    "employee_id": <emp_id>,
    "effective_to": null
})

# Voluntary deductions (III pillar, court orders, etc.)
deductions = search("employee_deduction", "", {
    "employee_id": <emp_id>,
    "is_active": true
})
```

**CP2 checkpoint**: Every employee has a compensation record.
**CP3 checkpoint**: Every employee has tax settings.

### Step 3: Load Tax Rates

```python
jurisdictions = list_entities("payroll_tax_jurisdiction", {
    "country_code": "EE",
    "is_active": true
})
```

Use the rates from **references/estonian-tax-formulas.md** as fallback if jurisdictions are not configured.

**CP4 checkpoint**: Tax rates available.

### Step 4: Calculate Per Employee

For each employee, apply the Estonian payroll formulas from **references/estonian-tax-formulas.md**:

1. **Gross pay** = compensation base_amount (pro-rate if mid-month start)
2. **Unemployment insurance (employee)** = gross x 1.6%
3. **Funded pension (II pillar)** = gross x pension_tier%
4. **Pre-tax deductions** = sum of voluntary deductions where `is_pre_tax = true`
5. **Taxable income** = gross - unemployment_ee - pension - pre_tax_deductions - basic_exemption (if applied)
6. **Income tax** = max(0, taxable_income x 22%)
7. **Post-tax deductions** = sum of voluntary deductions where `is_pre_tax = false`
8. **Net pay** = gross - unemployment_ee - pension - income_tax - pre_tax_deductions - post_tax_deductions
9. **Social tax (employer)** = max(gross, social_tax_minimum_base) x 33%
10. **Unemployment insurance (employer)** = gross x 0.8%

Build `tax_lines` array per employee with entries for each tax/deduction. See **references/submission-format.md** for exact structure.

**CP5 checkpoint**: Verify net_pay = gross - total_employee_taxes - total_deductions for each employee.

### Step 5: Submit Calculation

Build the payload per **references/submission-format.md** and submit:

```python
submit(
    object_type="payroll_run",
    operation="submit_calculation",
    data=json.dumps({
        "payroll_run_id": <run_id>,
        "employees": [
            {
                "employee_id": emp_id,
                "gross_pay": gross,
                "regular_pay": gross,
                "total_employee_taxes": total_ee_taxes,
                "total_employer_taxes": total_er_taxes,
                "total_deductions": total_deductions,
                "net_pay": net,
                "tax_lines": [...],
                "deduction_details": [...],
                "metadata": {"country": "EE", "basic_exemption_applied": true}
            }
            for each employee
        ]
    })
)
```

**CP6 checkpoint**: Submission succeeds without validation errors.

### Step 6: Summarize Results

Present a summary table to the user:

| Employee | Gross | Employee Taxes | Deductions | Net Pay | Employer Cost |
|----------|-------|---------------|------------|---------|---------------|
| Name 1   | ...   | ...           | ...        | ...     | ...           |
| Totals   | ...   | ...           | ...        | ...     | ...           |

Inform the user that the payroll run is now in `calculated` status and can be approved via:
```python
submit(object_type="payroll_run", operation="approve", data='{"payroll_run_id": <run_id>}')
```

## Error Handling

- **Missing compensation**: List employees without records, ask user to create them
- **Missing tax settings**: List employees, suggest creating with default EE settings
- **Validation failure on submit**: Show the exact error, fix calculation, retry
- **Social tax minimum**: If gross < minimum base, use minimum base for social tax calculation
- **Pension age employees**: Skip unemployment insurance for employees aged 65+
