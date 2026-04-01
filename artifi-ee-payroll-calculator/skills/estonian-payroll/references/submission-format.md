# submit_calculation Payload Format

## Overview

After calculating payroll for all employees, submit the results to the ERP backend via the `submit` MCP tool. The backend validates the calculations and stores them in the payroll run.

## MCP Tool Call

```python
submit(
    object_type="payroll_run",
    operation="submit_calculation",
    data=json.dumps(payload)
)
```

## Payload Structure

```json
{
    "payroll_run_id": 42,
    "employees": [
        {
            "employee_id": 50,
            "gross_pay": "3500.00",
            "regular_pay": "3500.00",
            "total_employee_taxes": "714.28",
            "total_employer_taxes": "1183.00",
            "total_deductions": "0.00",
            "net_pay": "2785.72",
            "tax_lines": [
                {
                    "line_type": "income_tax",
                    "category": "employee_deduction",
                    "amount": "588.28",
                    "side": "CR",
                    "description": "Income tax (tulumaks) 22%"
                },
                {
                    "line_type": "unemployment_employee",
                    "category": "employee_deduction",
                    "amount": "56.00",
                    "side": "CR",
                    "description": "Unemployment insurance (employee) 1.6%"
                },
                {
                    "line_type": "pension",
                    "category": "employee_deduction",
                    "amount": "70.00",
                    "side": "CR",
                    "description": "Funded pension II pillar 2%"
                },
                {
                    "line_type": "social_tax",
                    "category": "employer_tax",
                    "amount": "1155.00",
                    "side": "BOTH",
                    "description": "Social tax (sotsiaalmaks) 33%"
                },
                {
                    "line_type": "unemployment_employer",
                    "category": "employer_tax",
                    "amount": "28.00",
                    "side": "BOTH",
                    "description": "Unemployment insurance (employer) 0.8%"
                }
            ],
            "deduction_details": [],
            "metadata": {
                "country": "EE",
                "basic_exemption_applied": true,
                "basic_exemption_amount": "700.00",
                "pension_tier": "2%",
                "taxable_income": "2674.00"
            }
        }
    ]
}
```

## Field Reference

### Top Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `payroll_run_id` | int | Yes | ID of the payroll run (must be in `draft` or `calculated` status) |
| `employees` | array | Yes | List of per-employee calculation results (min 1) |

### Employee Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `employee_id` | int | Yes | Employee ID (must be active in the entity) |
| `gross_pay` | decimal | Yes | Total gross pay for the period |
| `regular_pay` | decimal | Yes | Regular pay component (usually = gross_pay) |
| `total_employee_taxes` | decimal | Yes | Sum of all employee-withheld taxes |
| `total_employer_taxes` | decimal | Yes | Sum of all employer taxes |
| `total_deductions` | decimal | Yes | Sum of all voluntary deductions (default: 0) |
| `net_pay` | decimal | Yes | Net pay after all taxes and deductions |
| `ytd_gross` | decimal | No | Year-to-date gross (for reporting) |
| `tax_lines` | array | Yes | Individual tax line items (min 1) |
| `deduction_details` | array | No | Voluntary deduction details |
| `metadata` | object | No | Country-specific metadata |

### Tax Line Object

| Field | Type | Required | Values | Description |
|-------|------|----------|--------|-------------|
| `line_type` | string | Yes | `income_tax`, `social_tax`, `unemployment_employee`, `unemployment_employer`, `pension` | Must match `payroll_vendor_config` line_type |
| `category` | string | Yes | `employee_deduction`, `employer_tax` | Determines GL posting pattern |
| `amount` | decimal | Yes | >= 0 | Tax amount |
| `side` | string | Yes | `CR`, `BOTH` | CR = employee-withheld (credit only), BOTH = employer (debit expense + credit payable) |
| `description` | string | Yes | max 200 chars | Human-readable description |

### Deduction Detail Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `deduction_type` | string | Yes | From employee_deductions taxonomy (e.g., `pension_iii`, `court_enforcement`) |
| `deduction_name` | string | Yes | Human-readable name |
| `amount` | decimal | Yes | Deduction amount (>= 0) |
| `is_pre_tax` | bool | No | Whether deducted before income tax calculation |
| `master_vendor_id` | int | No | Vendor to pay (overrides payroll_vendor_config) |
| `payable_account_number` | string | No | GL account for liability |
| `expense_account_number` | string | No | GL account for employer expense |

## Validation Rules

The backend validates the following before accepting:

1. **Net pay formula**: `|net_pay - (gross_pay - total_employee_taxes - total_deductions)| <= 0.02`
2. **Employee tax sum**: `|sum(tax_lines where category=employee_deduction) - total_employee_taxes| <= 0.02`
3. **Employer tax sum**: `|sum(tax_lines where category=employer_tax) - total_employer_taxes| <= 0.02`
4. **Employee exists**: Each `employee_id` must be an active employee in the entity
5. **Run status**: Payroll run must be `draft` or `calculated`

## Example with Voluntary Deductions

Employee with III pillar pension (pre-tax) and court enforcement (post-tax):

Calculation:
- Gross: EUR 4,000.00
- Unemployment EE: 4000 x 1.6% = EUR 64.00
- Pension II: 4000 x 4% = EUR 120.00
- Pre-tax deductions: EUR 200.00 (III pillar pension)
- Taxable: 4000 - 64 - 120 - 200 - 700 = EUR 2,916.00
- Income tax: 2916 x 22% = EUR 641.52
- Post-tax deductions: EUR 500.00 (court enforcement)
- Total employee taxes: 64 + 120 + 641.52 = EUR 825.52
- Total deductions: 200 + 500 = EUR 700.00
- Net pay: 4000 - 825.52 - 700 = EUR 2,474.48
- Social tax: 4000 x 33% = EUR 1,320.00
- Unemployment ER: 4000 x 0.8% = EUR 32.00
- Total employer taxes: 1320 + 32 = EUR 1,352.00

```json
{
    "employee_id": 51,
    "gross_pay": "4000.00",
    "regular_pay": "4000.00",
    "total_employee_taxes": "825.52",
    "total_employer_taxes": "1352.00",
    "total_deductions": "700.00",
    "net_pay": "2474.48",
    "tax_lines": [
        {"line_type": "income_tax", "category": "employee_deduction", "amount": "641.52", "side": "CR", "description": "Income tax 22%"},
        {"line_type": "unemployment_employee", "category": "employee_deduction", "amount": "64.00", "side": "CR", "description": "Unemployment 1.6%"},
        {"line_type": "pension", "category": "employee_deduction", "amount": "120.00", "side": "CR", "description": "Pension II pillar 4%"},
        {"line_type": "social_tax", "category": "employer_tax", "amount": "1320.00", "side": "BOTH", "description": "Social tax 33%"},
        {"line_type": "unemployment_employer", "category": "employer_tax", "amount": "32.00", "side": "BOTH", "description": "Unemployment 0.8%"}
    ],
    "deduction_details": [
        {
            "deduction_type": "pension_iii",
            "deduction_name": "III Pillar Pension (LHV)",
            "amount": "200.00",
            "is_pre_tax": true,
            "master_vendor_id": 47,
            "payable_account_number": "2250"
        },
        {
            "deduction_type": "court_enforcement",
            "deduction_name": "Court order #2026-1234",
            "amount": "500.00",
            "is_pre_tax": false,
            "payable_account_number": "2710"
        }
    ],
    "metadata": {
        "country": "EE",
        "basic_exemption_applied": true,
        "basic_exemption_amount": "700.00",
        "pension_tier": "4%",
        "taxable_income": "2916.00"
    }
}
```

## After Submission

Once `submit_calculation` succeeds:
1. Run status changes to `calculated`
2. `payroll_run_details` populated with per-employee data
3. `payroll_run_detail_lines` populated with vendor-linked GL lines

Next steps:
- **Approve**: `submit(object_type="payroll_run", operation="approve", data='{"payroll_run_id": <id>}')`
- **Process payment**: `submit(object_type="payroll_run", operation="process_payment", data='{"payroll_run_id": <id>, "payment_date": "YYYY-MM-DD", "bank_account_id": <id>}')`
