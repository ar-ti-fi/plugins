---
name: prepare-vat-declaration
description: Prepare the monthly Estonian VAT declaration (KMD) with KMD INF annex and EC Sales List for EMTA filing, using the generate_kmd.py script for deterministic XML generation.
---

# Prepare Estonian VAT Declaration (KMD)

Execute the full monthly VAT declaration workflow and generate XML files ready for EMTA upload.

**How it works:** Instead of generating XML by hand (which risks namespace errors), this command follows the SKILL.md workflow to calculate KMD lines, then builds a compact JSON and runs `scripts/generate_kmd.py` — a Python script that produces validated KMD, KMD INF, and Form VD XML files.

## Usage

```
/arfiti-ee:prepare-vat-declaration
```

## Prerequisites

- All transactions for the period must be posted (no drafts)
- All transaction lines must have tax codes assigned
- Python 3.9+ available (`python3 --version`)

## Steps 1–7: Follow the SKILL.md Workflow

Follow all steps in **skills/estonian-vat-declaration/SKILL.md** to:
1. Discover and classify tax codes (property-based, NOT hardcoded names)
2. Fetch all posted transactions for the period
3. Verify all lines have tax codes (CP1, CP2)
4. Calculate KMD Lines 1-13
5. Aggregate KMD INF partners (threshold: EUR 1,000)
6. Identify EC Sales List entries (IC supplies)
7. Reconcile VAT GL accounts (CP3, CP4, CP5)

## Step 8: Build KMD Data JSON

After all SKILL.md calculations are complete, build the input JSON for the script.

**JSON structure** (see `scripts/input_schema_kmd.json` for full example):

```json
{
  "regcode": "REGCODE",
  "vat_number": "EEXXXXXXXXXX",
  "year": YYYY,
  "month": MM,
  "kmd_lines": {
    "line1":   100000.00,
    "line1_1":  24000.00,
    "line2":     5000.00,
    "line2_1":    650.00,
    "line3":    10000.00,
    "line3_1":  15000.00,
    "line3_2":   8500.00,
    "line4":    18000.00,
    "line4_1":   5000.00,
    "line5":        0.00,
    "line5_1":      0.00,
    "line6":        0.00,
    "line7":        0.00,
    "line8":        0.00,
    "line10":    6650.00,
    "line11":       0.00,
    "line12":    6650.00,
    "line13":       0.00
  },
  "kmd_inf": {
    "part_a": [
      {"reg_code": "87654321", "name": "Customer OÜ", "invoice_count": 5, "taxable_amount": 5000.00, "vat_amount": 1200.00}
    ],
    "part_b": [
      {"reg_code": "11223344", "name": "Vendor AS", "invoice_count": 3, "taxable_amount": 3000.00, "vat_amount": 720.00}
    ]
  },
  "vd_entries": [
    {"customer_vat_number": "FI12345678", "country_code": "FI", "supply_type": "G", "amount": 15000.00},
    {"customer_vat_number": "DE987654321", "country_code": "DE", "supply_type": "S", "amount": 8500.00}
  ]
}
```

**CRITICAL formulas to verify BEFORE writing JSON:**
- `line10 = (line1_1 + line2_1) - line4 + line8`
- `line12 = max(0, line10 + line11)` — VAT payable
- `line13 = max(0, -(line10 + line11))` — VAT overpaid
- Lines 12 and 13 are mutually exclusive (only one can be non-zero)
- VD goods total (G + T entries) must equal `line3_1`
- VD services total (S entries) must equal `line3_2`
- Omit `vd_entries` key entirely if no intra-community supplies exist

Write this JSON to a temporary file, e.g. `/tmp/kmd_data_{REGCODE}_{YYYYMM}.json`.

## Step 9: Run the Generator Script

Find the plugin's scripts directory and run:

```bash
# The script is at: plugins/arfiti-ee-vat-declaration/scripts/generate_kmd.py
python3 generate_kmd.py \
  --input /tmp/kmd_data_{REGCODE}_{YYYYMM}.json \
  --output {OUTPUT_DIR}
```

The script will:
- Validate Line 10 formula and Lines 12/13 mutual exclusion (exits with error if any fail)
- Validate VD totals reconcile with Lines 3.1/3.2
- Generate `KMD_YYYYMM_{REGCODE}.xml`
- Generate `KMDINF_YYYYMM_{REGCODE}.xml` (if part_a or part_b have entries)
- Generate `VD_YYYYMM_{REGCODE}.xml` (only if vd_entries present)
- Print paths of generated files and a KMD summary

**If the script is not found**, locate it with:
```bash
find ~ -name "generate_kmd.py" -path "*/arfiti-ee-vat-declaration/*" 2>/dev/null
```

## Step 10: Report Results

After the script completes, report to the user:
- Paths of all generated XML files
- KMD summary (output VAT, input VAT, net VAT, payable/overpaid)
- Any validation errors printed by the script
- Confirmation that files are ready for upload

## Step 11: Filing Instructions

1. Log in to **e-MTA** at maasikas.emta.ee with ID-card or Smart-ID
2. Navigate to **Declarations** → **KMD** → Create new for the period
3. Upload `KMD_YYYYMM_{REGCODE}.xml`
4. Upload `KMDINF_YYYYMM_{REGCODE}.xml` as the INF annex
5. If Form VD was generated, upload `VD_YYYYMM_{REGCODE}.xml` separately under EC Sales List
6. The portal will validate — if errors occur, paste them here to debug
7. Sign digitally and submit
8. **Deadline**: 20th of the following month

## Output

Up to three XML files ready for upload:
- `KMD_YYYYMM_{REGCODE}.xml` — Main VAT declaration form (Lines 1-13)
- `KMDINF_YYYYMM_{REGCODE}.xml` — KMD INF annex (Parts A & B, partners > EUR 1,000)
- `VD_YYYYMM_{REGCODE}.xml` — EC Sales List / Form VD (only if IC supplies exist)
