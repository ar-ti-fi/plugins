---
name: Generate TSD Declaration
command: generate-tsd
description: Generate Estonian TSD (monthly tax declaration) XML from a calculated or approved payroll run, ready for upload to e-MTA.
---

# /artifi-ee:generate-tsd

Generate the Estonian monthly TSD declaration XML for EMTA filing.

**How it works:** Instead of generating XML by hand (which risks namespace errors), this command fetches payroll data from the ERP, builds a compact JSON, and runs `scripts/generate_tsd.py` — a Python script that produces a validated TSD XML with the correct namespace `http://emta.ee/tsd`.

## Usage

```
/artifi-ee:generate-tsd <payroll_run_id>
```

## Prerequisites

- Payroll run must be in `calculated` or `approved` status
- All employees must have `tax_id_number` (isikukood) in `employee_tax_settings`
- Python 3.9+ available (`python3 --version`)

## Step 1: Collect Inputs

Ask the user for:

1. **Payroll run ID** — the calculated/approved run to declare
2. **Output directory** — where to write the XML file. Default: current directory

## Step 2: Fetch Payroll Data

Use MCP tools to gather all required data:

```
# Payroll run header (contains legal_entity_id, period dates)
get_entity("payroll_run", id=<run_id>)

# Per-employee detail records (gross_pay, net_pay, total_deductions, metadata)
list_entities("payroll_run_detail", {"payroll_run_id": <run_id>})

# Tax line breakdown per employee (income_tax, social_tax, unemployment, pension amounts)
list_entities("payroll_run_detail_line", {"payroll_run_id": <run_id>})

# Employee personal data and isikukood
for each employee_id in detail records:
    get_entity("employee", id=<employee_id>)
    search("employee_tax_settings", "", {"employee_id": <employee_id>, "effective_to": null})
```

## Step 3: Build TSD Data JSON

Map the fetched data to the input schema. See `scripts/input_schema_tsd.json` for a full example.

**Per-employee field mapping:**

| JSON field | Source |
|---|---|
| `personal_id` | `employee_tax_settings.tax_id_number` |
| `first_name` | `master_employees.first_name` |
| `last_name` | `master_employees.last_name` |
| `gross_pay` | `payroll_run_details.gross_pay` |
| `basic_exemption_applied` | `payroll_run_details.metadata.basic_exemption_applied` |
| `basic_exemption_amount` | `payroll_run_details.metadata.basic_exemption_amount` |
| `taxable_amount` | `payroll_run_details.metadata.taxable_income` |
| `income_tax` | detail line where `line_type = "income_tax"` → amount |
| `unemployment_employee` | detail line where `line_type = "unemployment_employee"` → amount |
| `funded_pension` | detail line where `line_type = "pension"` → amount |
| `social_tax` | detail line where `line_type = "social_tax"` → amount |
| `unemployment_employer` | detail line where `line_type = "unemployment_employer"` → amount |
| `total_deductions` | `payroll_run_details.total_deductions` |
| `net_pay` | `payroll_run_details.net_pay` |

**JSON structure:**

```json
{
  "regcode": "REGCODE",
  "year": YYYY,
  "month": MM,
  "employees": [
    {
      "personal_id": "39001011234",
      "first_name": "Jaan",
      "last_name": "Tamm",
      "gross_pay": 3500.00,
      "basic_exemption_applied": true,
      "basic_exemption_amount": 700.00,
      "taxable_amount": 2674.00,
      "income_tax": 588.28,
      "unemployment_employee": 56.00,
      "funded_pension": 70.00,
      "social_tax": 1155.00,
      "unemployment_employer": 28.00,
      "total_deductions": 0.00,
      "net_pay": 2785.72
    }
  ]
}
```

Write this JSON to a temporary file, e.g. `/tmp/tsd_data_{REGCODE}_{YYYYMM}.json`.

## Step 4: Run the Generator Script

Find the plugin's scripts directory and run:

```bash
# The script is at: plugins/artifi-ee-payroll-calculator/scripts/generate_tsd.py
python3 generate_tsd.py \
  --input /tmp/tsd_data_{REGCODE}_{YYYYMM}.json \
  --output {OUTPUT_DIR}
```

The script will:
- Validate net pay formula for each employee (exits with error if any fail)
- Generate `TSD_YYYYMM_{REGCODE}.xml` with correct namespace `http://emta.ee/tsd`
- Print path of generated file and summary totals

**If the script is not found**, locate it with:
```bash
find ~ -name "generate_tsd.py" -path "*/artifi-ee-payroll-calculator/*" 2>/dev/null
```

## Step 5: Report Results

After the script completes, report to the user:
- Path of the generated XML file
- Summary totals (gross, income tax, social tax, unemployment, pension)
- Any validation errors printed by the script

## Step 6: Filing Instructions

1. Log in to **e-MTA** at maasikas.emta.ee with ID-card or Smart-ID
2. Navigate to **Declarations** → **TSD** → Create new for the period
3. Choose **Upload XML** and upload `TSD_YYYYMM_{REGCODE}.xml`
4. The portal will validate — if errors occur, paste them here to debug
5. Review the generated declaration
6. Sign digitally and submit
7. **Deadline**: 10th of the following month (same day as tax payment)

## Output

One XML file ready for upload:
- `TSD_YYYYMM_{REGCODE}.xml` — TSD declaration with Header, Summary, and Annex 1 per-employee data

## See Also

- **references/tsd-declaration.md** — Full TSD structure and field reference
- **references/estonian-tax-formulas.md** — Tax rate reference and worked examples
