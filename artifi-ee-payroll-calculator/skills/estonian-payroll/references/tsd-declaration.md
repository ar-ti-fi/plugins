# TSD Declaration (Estonian Monthly Tax Return)

## Overview

The TSD (Tulu- ja sotsiaalmaksudeklaratsioon) is the monthly declaration for income and social taxes filed with EMTA (Estonian Tax and Customs Board). It is due by the 10th of the following month.

## TSD Structure

### Part I - Summary Totals

| Line | Description | Source |
|------|-------------|--------|
| 1 | Total gross payments | Sum of all employee gross_pay |
| 2 | Income tax withheld | Sum of all income_tax tax_lines |
| 3 | Social tax | Sum of all social_tax tax_lines |
| 4 | Unemployment insurance (employer) | Sum of all unemployment_employer tax_lines |
| 5 | Unemployment insurance (employee) | Sum of all unemployment_employee tax_lines |
| 6 | Funded pension contributions | Sum of all pension tax_lines |

### Annex 1 - Resident Natural Persons (per employee)

| Field | Description | Source |
|-------|-------------|--------|
| Personal ID | Estonian isikukood | employee_tax_settings.tax_id_number |
| First Name | | master_employees.first_name |
| Last Name | | master_employees.last_name |
| Gross Payment | Total gross for period | payroll_run_details.gross_pay |
| Tax-Free Amount | Basic exemption applied | metadata.basic_exemption_amount |
| Taxable Amount | Gross minus exemptions | metadata.taxable_income |
| Income Tax | Tax withheld | income_tax amount from tax_lines |
| Unemployment (EE) | Employee portion | unemployment_employee from tax_lines |
| Funded Pension | II pillar contribution | pension from tax_lines |

### Annex 4 - Fringe Benefits (employer-level, if applicable)

Only needed in months when fringe benefits are provided.

| Field | Description |
|-------|-------------|
| Benefit type | Type of fringe benefit |
| Taxable value | Total value of benefits provided |
| Income tax | 22/78 gross-up |
| Social tax | 33% on gross-up amount |

### Annex 5 - Gifts, Donations & Entertainment (if applicable)

Only needed in months with such expenses.

## Generating TSD Data from Payroll Run

After a payroll run is in `calculated` or `approved` status, gather TSD data:

```python
# Get payroll run with details
run = get_entity("payroll_run", id=<run_id>)

# Get detail records for each employee
details = list_entities("payroll_run_detail", {
    "payroll_run_id": <run_id>
})

# Get detail lines for tax breakdown
detail_lines = list_entities("payroll_run_detail_line", {
    "payroll_run_id": <run_id>
})

# Get employee tax IDs
for each employee:
    tax_settings = search("employee_tax_settings", "", {
        "employee_id": emp_id,
        "effective_to": null
    })
    personal_id = tax_settings[0]["tax_id_number"]
```

## TSD XML Format

```xml
<?xml version="1.0" encoding="UTF-8"?>
<TSD xmlns="http://emta.ee/tsd">
  <Header>
    <TaxpayerRegCode>12345678</TaxpayerRegCode>
    <Period>
      <Year>2026</Year>
      <Month>01</Month>
    </Period>
  </Header>
  <Summary>
    <TotalGrossPayments>3500.00</TotalGrossPayments>
    <TotalIncomeTax>588.28</TotalIncomeTax>
    <TotalSocialTax>1155.00</TotalSocialTax>
    <TotalUnemploymentEmployer>28.00</TotalUnemploymentEmployer>
    <TotalUnemploymentEmployee>56.00</TotalUnemploymentEmployee>
    <TotalFundedPension>70.00</TotalFundedPension>
  </Summary>
  <Annex1>
    <Person>
      <PersonalId>39001011234</PersonalId>
      <FirstName>Jaan</FirstName>
      <LastName>Tamm</LastName>
      <GrossPayment>3500.00</GrossPayment>
      <TaxFreeAmount>700.00</TaxFreeAmount>
      <TaxableAmount>2674.00</TaxableAmount>
      <IncomeTax>588.28</IncomeTax>
      <UnemploymentEmployee>56.00</UnemploymentEmployee>
      <FundedPension>70.00</FundedPension>
    </Person>
  </Annex1>
</TSD>
```

## Filing Methods

1. **e-MTA Portal** - Manual entry at https://www.emta.ee
2. **XML Upload** - Upload generated XML file
3. **Machine-to-Machine API** - Automated submission (requires EMTA registration)

## Key Deadlines

| Obligation | Deadline |
|------------|----------|
| TSD filing | 10th of following month |
| Tax payment | 10th of following month |
| Employment register | Before first work day |
| INF forms | February 1 (annual) |

## Penalties

- Late filing: Interest at 0.06% per day on unpaid taxes
- Repeated violations: Increased audit scrutiny
