# Estonian Payroll Tax Formulas

## Tax Rates (2025-2026)

### Employee-Withheld Taxes

| Tax | Rate | line_type | category | side | Notes |
|-----|------|-----------|----------|------|-------|
| Income Tax | 22% | `income_tax` | `employee_deduction` | CR | After basic exemption |
| Unemployment Insurance | 1.6% | `unemployment_employee` | `employee_deduction` | CR | Stops at pension age (65) |
| Funded Pension (II Pillar) | 2%, 4%, or 6% | `pension` | `employee_deduction` | CR | Employee's choice |

### Employer Taxes

| Tax | Rate | line_type | category | side | Notes |
|-----|------|-----------|----------|------|-------|
| Social Tax | 33% | `social_tax` | `employer_tax` | BOTH | 20% pension + 13% health |
| Unemployment Insurance | 0.8% | `unemployment_employer` | `employer_tax` | BOTH | |

### Thresholds

| Threshold | 2025 | 2026 |
|-----------|------|------|
| Basic Exemption | EUR 654/month | EUR 700/month |
| Minimum Wage | EUR 886/month | EUR 886/month |
| Social Tax Minimum Base | EUR 820/month | EUR 886/month |
| Social Tax Minimum | EUR 270.60/month | EUR 292.38/month |

## Calculation Order

The order of calculation matters. Follow these steps exactly:

### Step 1: Unemployment Insurance (Employee)
```
unemployment_ee = round(gross * 0.016, 2)
```

### Step 2: Funded Pension (II Pillar)
```
pension_rate = 0.02 | 0.04 | 0.06  (from employee_tax_settings.pension_tier)
pension = round(gross * pension_rate, 2)
```

### Step 3: Pre-Tax Voluntary Deductions
```
pre_tax_deductions = sum of employee_deductions where is_pre_tax = true
```
Examples: III pillar pension, some health insurance plans.

### Step 4: Taxable Income
```
basic_exemption = 700.00 if basic_exemption_applied else 0.00  (2026 rate)
taxable_income = gross - unemployment_ee - pension - pre_tax_deductions - basic_exemption
taxable_income = max(0, taxable_income)  # Cannot be negative
```

### Step 5: Income Tax
```
income_tax = round(taxable_income * 0.22, 2)
```

### Step 6: Post-Tax Voluntary Deductions
```
post_tax_deductions = sum of employee_deductions where is_pre_tax = false
```
Examples: Court enforcement orders, child support, union fees, loan repayments.

### Step 7: Total Employee Taxes
```
total_employee_taxes = unemployment_ee + pension + income_tax
```
Note: Voluntary deductions are NOT included in total_employee_taxes. They go in total_deductions.

### Step 8: Total Deductions (Voluntary)
```
total_deductions = pre_tax_deductions + post_tax_deductions
```

### Step 9: Net Pay
```
net_pay = gross - total_employee_taxes - total_deductions
```
Validation: `net_pay = gross - unemployment_ee - pension - income_tax - pre_tax_deductions - post_tax_deductions`

### Step 10: Social Tax (Employer)
```
social_tax_base = max(gross, social_tax_minimum_base)  # 886 for 2026
social_tax = round(social_tax_base * 0.33, 2)
```
The minimum base ensures a minimum social tax even for part-time/low-salary employees.

### Step 11: Unemployment Insurance (Employer)
```
unemployment_er = round(gross * 0.008, 2)
```

### Step 12: Total Employer Taxes
```
total_employer_taxes = social_tax + unemployment_er
```

### Step 13: Total Employer Cost
```
total_employer_cost = gross + total_employer_taxes
```

## Worked Example

**Input**: Gross EUR 3,500, pension tier 2%, basic exemption applied (2026 rates)

| Step | Calculation | Amount |
|------|-------------|--------|
| Unemployment (EE) | 3500 x 1.6% | EUR 56.00 |
| Pension (II) | 3500 x 2% | EUR 70.00 |
| Pre-tax deductions | (none) | EUR 0.00 |
| Taxable income | 3500 - 56 - 70 - 0 - 700 | EUR 2,674.00 |
| Income tax | 2674 x 22% | EUR 588.28 |
| Post-tax deductions | (none) | EUR 0.00 |
| **Total employee taxes** | 56 + 70 + 588.28 | **EUR 714.28** |
| **Total deductions** | 0 + 0 | **EUR 0.00** |
| **Net pay** | 3500 - 714.28 - 0 | **EUR 2,785.72** |
| Social tax (ER) | 3500 x 33% | EUR 1,155.00 |
| Unemployment (ER) | 3500 x 0.8% | EUR 28.00 |
| **Total employer taxes** | 1155 + 28 | **EUR 1,183.00** |
| **Total employer cost** | 3500 + 1183 | **EUR 4,683.00** |

## Special Cases

### No Basic Exemption
When employee has not applied for basic exemption (e.g., they use it at another employer):
```
taxable_income = gross - unemployment_ee - pension - pre_tax_deductions
# basic_exemption = 0
```

### Pension Age (65+)
Both employee and employer unemployment insurance stop:
```
unemployment_ee = 0
unemployment_er = 0
```

### Part-Time / Low Salary
If gross < social_tax_minimum_base (EUR 886 for 2026):
```
social_tax = round(886 * 0.33, 2)  # EUR 292.38 minimum
# Employer still pays minimum social tax
```

### Mid-Month Start
Pro-rate salary based on working days:
```
working_days_in_month = 22  # typical
days_worked = 12
pro_rata_gross = round(full_monthly_salary * (days_worked / working_days_in_month), 2)
```

### Fringe Benefits (TSD Annex 4)
Fringe benefits are employer-level (not per-employee):
```
gross_up_amount = benefit_value / (1 - 0.22)  # = benefit / 0.78
fringe_income_tax = gross_up_amount - benefit_value
fringe_social_tax = round(gross_up_amount * 0.33, 2)
```
