---
name: Generate TSD Declaration
command: generate-tsd
description: Generate the real Estonian e-MTA TSD XML (income + social tax monthly declaration) from a calculated/approved payroll run. Output is validated against the official XSD and ready for upload to https://maasikas.emta.ee.
---

# /artifi-ee:generate-tsd

Generate the Estonian monthly TSD declaration as e-MTA-compatible XML.

**How it works:** the command fetches payroll data + universal tax-filing metadata from the ERP, builds a compact JSON payload, and runs `scripts/generate_tsd.py` — a Python generator that produces the **real e-MTA format** (root `<tsd_vorm>`, no namespace, `c{NNN}_*` element naming, mandatory `<vorm>TSD</vorm>`, BOM-prefixed UTF-8). Output is validated against the official XSD before being written.

This command is the **reference implementation** of the universal country-plugin contract documented in [`docs/GUIDES/GUIDE_TAX_FILING_PLUGINS.md`](../../../docs/GUIDES/GUIDE_TAX_FILING_PLUGINS.md). All country-specific data is read via universal MCP tools — no hard-coded country logic in the calling skill.

## Usage

```
/artifi-ee:generate-tsd <payroll_run_id>
```

Optional: `--month YYYY-MM` if the payroll run spans multiple TSD periods (rare).

## Prerequisites

1. Payroll run is in `calculated` or `approved` status.
2. The org has been onboarded for Estonia — `tax_filing_forms` and `payment_classifications` are seeded for `country_code = "EE"`.
3. Each `master_employees` row in the run has `metadata.tax_filing.*` populated (residency, basic_exemption_code, pension_fund_id, is_pensioner). If missing, the skill falls back to defaults (`residency=resident`, `basic_exemption_code=610`, `is_pensioner=false`).
4. Each `employee_compensation` row has `payment_classification_slug` set (e.g. `salary_wage`, `board_fee`). Falls back to `salary_wage` if missing.
5. Python 3.9+ available locally for running `generate_tsd.py`.

## Step 1 — Confirm form is registered for Estonia

```python
forms = query("tax_filing_form", filters={"country_code": "EE", "form_code": "TSD"})
```

Expect 1 row. If 0, the org hasn't run the EE onboarding seeders yet — escalate (run `setup_tax_filing_forms` for this org).

## Step 2 — Fetch payroll data

```python
# Run header → legal_entity_id, period_id
run = get_entity("payroll_run", id=<run_id>)

# Period → year, month for c108/c109
period = get_entity("payroll_period", id=run["payroll_period_id"])
```

`payroll_run_details` (per-employee breakdown) and `payroll_run_detail_lines`
(tax line breakdown: income_tax, social_tax, unemployment_employee,
unemployment_employer, pension) exist in the schema but have no registered
`query()` entity type -- they cannot be fetched through the MCP query tool
today. Until that gap is closed, reconstruct each employee's per-line amounts
from `employee_compensation` + `employee_tax_settings` + the current
`payroll_tax_jurisdiction` rates, using the same formulas the calculator
applies (income tax 22% of taxable base, social tax 33% of gross with the
EUR 886/month minimum base, unemployment 1.6%/0.8%, funded pension by tier --
see `references/tsd-codes.md`), and validate the totals against
`payroll_run`'s aggregate fields (`total_gross_pay`, `total_employee_taxes`,
`total_employer_taxes`, `total_deductions`, `total_net_pay`).

```python
details = query("employee_compensation", filters={"legal_entity_id": run["legal_entity_id"], "is_active": True})
```

## Step 3 — Fetch universal tax-filing metadata (no per-country branching)

```python
# Slug → c1020/c1150/c2020/c3010 external code map
classifications = query("payment_classification", filters={"country_code": "EE"})
slug_to_code = {c["slug"]: c["external_code"] for c in classifications["results"]}

# Legal entity (regKood)
entity = get_entity("legal_entity", id=run["legal_entity_id"])
regcode = entity["registry_code"] or entity["tax_id"]
```

## Step 4 — Fetch per-employee filing attributes

For each `employee_id` in `details`:

```python
emp = get_entity("employee", id=<employee_id>)
tax_filing = (emp.get("metadata") or {}).get("tax_filing") or {}

# Defaults — used when metadata is incomplete
residency = tax_filing.get("residency", "resident")
is_pensioner = tax_filing.get("is_pensioner", False)
basic_exemption_code = tax_filing.get("basic_exemption_code", "610")
basic_exemption_amount = tax_filing.get("basic_exemption_amount", 700.00)
```

For each employee's active compensation:

```python
comps = query("employee_compensation", filters={"employee_id": <employee_id>, "is_active": True})
classification_slug = comps["results"][0].get("payment_classification_slug", "salary_wage")
payment_type_code = slug_to_code.get(classification_slug)  # e.g. "10" for salary, "21" for board fee
```

If any employee has `residency != "resident"`, route them through Annex 2 (currently a future release — emit a warning and skip them, or escalate to user).

## Step 4b — Fetch Annex 4 (fringe benefits) data — optional

Annex 4 captures employer-provided fringe benefits (company vehicle, accommodation, etc.) — see `references/tsd-codes.md` for the full c4xxx field list. Skip this step if there are no fringe benefits this month.

```python
# Source 1 (when wired up — future release): expense_reports tagged with item_id whose
# global_item_id starts with 'FRG-' (e.g. FRG-CAR, FRG-MEALS).
# Source 2 (interim): manual entries by the bookkeeper.
# Source 3 (when wired up): a dedicated FRINGE_BENEFIT_RUN transaction type.

# For now, build the annex_4 dict by category from whichever source you have.
# The generator validates and emits only the keys you populate.
annex_4 = {
    "company_vehicle": <sum>,            # c4040_Ts
    "representation_amount": <sum>,      # c4140_EsSumma — total taxable amount
    "special_income_tax": <taxable × 22/78>,    # c4170_TmEj — caller computes
    "social_tax_base": <taxable + special_income_tax>,
    "social_tax": <base × 33%>          # c4180_Sm
    # ... see references/tsd-codes.md for all c4xxx keys
}
```

## Step 4c — Fetch Annex 5 (gifts/donations/entertainment) — optional

Annex 5 is **CoA-driven**: scan transaction lines posting to accounts whose `metadata.filing_categories[]` includes `{form: TSD, annex: 5, code: ...}`. EE seed tags accounts:
- `6850` Business Entertainment → `c5100_KyKuluKuu`
- `6860` Gifts and Hospitality (Non-Employee) → `c5000_Ki`
- `6870` Charitable Donations and Sponsorship → `c5010_IKiKuu`

```python
# Find tagged accounts for the EE entity
accounts = query("account", filters={"legal_entity_id": run["legal_entity_id"]})
annex5_buckets = {}  # c-code → [account_numbers]
for a in accounts["results"]:
    cats = (a.get("metadata") or {}).get("filing_categories") or []
    for cat in cats:
        if cat.get("form") == "TSD" and cat.get("annex") == "5":
            annex5_buckets.setdefault(cat["code"], []).append(a["account_number"])

# Aggregate transaction-line debits on those accounts for the period
totals_by_code = {}  # c-code → Decimal
for code, account_numbers in annex5_buckets.items():
    agg = query(
        "transaction_line",
        group_by=["account_number"],
        aggregates={"debit": "sum"},
        filters={
            "legal_entity_id": run["legal_entity_id"],
            "account_number": {"in": account_numbers},
            "transaction_date": {"between": [period["period_start"], period["period_end"]]},
        },
    )
    totals_by_code[code] = sum(D(r["debit_sum"]) for r in agg["results"])

# Map c-codes to the input-key names used by generate_tsd.py
CODE_TO_KEY = {
    "5000": "general_gifts",
    "5010": "listed_charity_month",
    "5100": "entertainment_month",
    # ... see references/tsd-codes.md for full mapping
}
annex_5 = {CODE_TO_KEY[code]: float(amt) for code, amt in totals_by_code.items() if code in CODE_TO_KEY}

# Compute tax fields (caller's responsibility — see tsd-codes.md formulas)
# Common case: special_income_tax_payable = (entertainment_month - threshold) × 22/78
```

## Step 4d — Split residents / non-residents (Annex 1 vs Annex 2)

For each `details` row from Step 2, route the employee based on `master_employees.metadata.tax_filing.residency`:

```python
resident_persons = []      # → Annex 1
non_resident_persons = []  # → Annex 2

for detail in details["results"]:
    emp = get_entity("employee", id=detail["employee_id"])
    tax_filing = (emp.get("metadata") or {}).get("tax_filing") or {}
    residency = tax_filing.get("residency", "resident")

    person_block = {
        "personal_id": <from employee_tax_settings.tax_id_number>,
        "full_name": <FIRST LAST in uppercase>,
        "payments": [...]    # built from the recomputed per-employee figures (Step 2)
    }

    if residency == "non_resident":
        # Annex 2 needs country_of_residence + income_tax_rate per payment
        for payment in person_block["payments"]:
            payment["country_of_residence"] = tax_filing.get("country_of_residence")
            payment["income_tax_rate"] = tax_filing.get("treaty_rate_override", 22.00)
            payment["payment_type_code"] = "120"  # or 122 for royalty, etc. — use slug→external_code map
        non_resident_persons.append(person_block)
    else:
        resident_persons.append(person_block)
```

The generator emits `<tsd_L1_0>` only when `resident_persons` is non-empty, and `<tsd_L2_0>` only when `non_resident_persons` is non-empty. Both can coexist for orgs with mixed payrolls.

## Step 4e — Fetch Annex 7 (dividends) + INF1 — optional, December only or as-declared

Annex 7 is populated by querying `DIVIDEND_PAYMENT` transactions for the period:

```python
divs = query("transaction", filters={
    "legal_entity_id": run["legal_entity_id"],
    "transaction_type_code": "DIVIDEND_PAYMENT",
    "transaction_date": {"between": [period["period_start"], period["period_end"]]},
})

if divs["results"]:
    total_dividends = sum(D(t["total_amount"]) for t in divs["results"])
    # Income tax computation (EE: 22% standard; 14% reduced for repeated distributions)
    # Caller computes the tax math — generator just emits.
    annex_7 = {
        "dividends_total": float(total_dividends),                    # c7008_DivKokku
        "equity_social_tax_corrected": float(total_dividends * 0.33), # c7050_OmakapSmKorrig (rolls into header c115_Sm)
        "payable_income_tax": float(total_dividends * 22 / 78),       # c7200_TasutavTm (rolls into header c110_Tm)
    }
```

INF1 is built from the same `DIVIDEND_PAYMENT` transactions (typically only filed in December alongside the year-end TSD). Each transaction's party becomes one INF1 recipient:

```python
if period["period_end"].month == 12 and divs["results"]:
    recipients = []
    for tx in divs["results"]:
        # Party can be vendor (corporate shareholder) or employee (individual shareholder)
        if tx.get("vendor_id"):
            party = get_entity("vendor", id=tx["vendor_id"])
            tax_filing = (party.get("metadata") or {}).get("tax_filing") or {}
            recipients.append({
                "estonian_registry_code": party.get("registry_code"),
                "name": party["vendor_name"],
                "distribution_type_code": "DK",                # see references/tsd-codes.md for full list
                "distribution_amount": float(tx["total_amount"]),
                "tax_rate": 22.00,
                "withheld_tax": float(D(tx["total_amount"]) * Decimal("22") / Decimal("78")),
            })
        elif tx.get("employee_id"):
            emp = get_entity("employee", id=tx["employee_id"])
            recipients.append({
                "estonian_registry_code": <employee_tax_settings.tax_id_number>,
                "name": f"{emp['first_name']} {emp['last_name']}".upper(),
                "distribution_type_code": "DK",
                "distribution_amount": float(tx["total_amount"]),
                # ...
            })

    inf1 = {
        "withheld_tax_total": sum(D(r["withheld_tax"]) for r in recipients if "withheld_tax" in r),
        "taxed_proportion": 1.000000000,  # caller computes — proportion of taxed equity vs total
        "recipients": recipients,
    }
```

## Step 5 — Build the TSD JSON input

For each resident employee with payments in this period, build one entry in `persons[]`:

```jsonc
{
  "regcode": "<regcode>",
  "year": <YYYY>,
  "month": <MM>,
  "load_mode": "P",                         // "L" for first submission of period; "P" to amend in-progress (default)
  "persons": [
    {
      "personal_id": "<from employee_tax_settings.tax_id_number>",
      "full_name": "<FIRST LAST in uppercase>",
      "payments": [
        {
          "payment_type_code": "<payment_type_code from Step 4>",
          "gross": <employee's gross pay, recomputed per Step 2>,
          "social_tax_base": <usually = gross; differs for partial-month / minimum-base scenarios>,
          "social_tax": <employee's social tax, recomputed per Step 2>,
          "combined_kp": <pension + unemployment_employee>,
          "unemployment_employee": <if non-zero>,
          "unemployment_employer": <if non-zero>,
          "income_tax": <employee's income tax, recomputed per Step 2>,
          "tax_free_items": [
            {"code": "<basic_exemption_code>", "amount": <basic_exemption_amount>}
          ]
        }
      ]
    }
  ],
  "non_resident_persons": <from Step 4d — omit the whole key if no non-residents>,
  "annex_4": <from Step 4b — omit the whole key if no fringe benefits>,
  "annex_5": <from Step 4c — omit the whole key if no gifts/donations/entertainment>,
  "annex_7": <from Step 4e — omit the whole key if no dividends declared this period>,
  "inf1":    <from Step 4e — typically only December; omit otherwise>
}
```

Write this JSON to `/tmp/tsd_data_{regcode}_{YYYYMM}.json`.

## Step 6 — Run the generator

```bash
python3 plugins/artifi-ee-payroll-calculator/scripts/generate_tsd.py \
  --input /tmp/tsd_data_{regcode}_{YYYYMM}.json \
  --output {OUTPUT_DIR}
```

The generator:
- Validates per-row identities (social_tax = base × 33%, income_tax = (gross − Kp − exemptions) × 22%) within ±0.02 tolerance.
- Computes header c110-c119 and Annex 1 c1200-c1250 roll-ups automatically.
- Writes `TSD_YYYYMM_{regcode}.xml` with BOM-prefixed UTF-8.

If validation fails, re-check: did `payroll_run.process_payment` post correctly? Are any `gross` values negative? Did the calculation step round in the wrong direction?

## Step 7 — Persist the return

```python
authority = query("tax_authority", filters={"country_code": "EE", "code": "EMTA-PAYROLL"})

submit("tax_return", "create", json.dumps({
    "legal_entity_id": run["legal_entity_id"],
    "return_type": "TSD",
    "tax_authority_id": authority["results"][0]["id"],
    "reporting_period_id": <if period exists in tax_reporting_periods>,
    "return_data": {
        # Save the generated XML's path AND the JSON input for audit trail
        "filing_xml_path": "<output path>",
        "filing_json_input": <the JSON we built in Step 5>,
        "header_totals": {
            "c110_Tm": <income_tax_total>,
            "c115_Sm": <social_tax_total>,
            "c116_Tk": <unemployment_total>,
            "c117_Kp": <pension_total>,
            "c118_KohustKokku": <total_obligation>
        },
        "person_count": <len(persons)>,
        "payment_row_count": <total payments across persons>
    }
}))
```

## Step 7b — Post the settlement bill (the payable the payment chain settles)

The declaration is the moment the collectible total is known — so the filing
itself posts one AP bill per authority vendor. From here on, everything is the
ordinary AP chain: payment proposals pick the bill up, the batch transmits, the
bank-statement confirmation applies the payment, `bills_collector` chases a
real due date. Do **not** pay the authority outside this bill — entities using
this flow have the authority vendor listed in `payroll.tax_bill_vendor_ids`,
which removes it from payroll payment batches and makes the bank processor
refuse unapplied payments to it.

```python
# 1. Per-entity mapping: line_type → (vendor, payable account). NEVER hardcode
#    accounts or vendor ids — this is entity configuration.
cfg = query("payroll_vendor_config",
            filters={"legal_entity_id": run["legal_entity_id"], "is_active": True})
by_line_type = {r["line_type"]: r for r in cfg["results"]}

# 2. Map the declared header totals onto payable accounts.
#    Every euro of c118_KohustKokku must land on exactly one bill line:
components = [
    ("income_tax",            income_tax_total),      # c110_Tm
    ("social_tax",            social_tax_total),      # c115_Sm
    ("unemployment_employee", unemployment_total),    # c116_Tk (employee+employer share the payable account)
    ("pension",               pension_total),         # c117_Kp
]
lines_by_vendor = {}   # master_vendor_id → {account_number → amount}
for line_type, amount in components:
    if amount == 0:
        continue
    r = by_line_type[line_type]   # KeyError = config gap → STOP, fix payroll_vendor_config
    lines_by_vendor.setdefault(r["master_vendor_id"], {})
    acct = lines_by_vendor[r["master_vendor_id"]]
    acct[r["payable_account_number"]] = acct.get(r["payable_account_number"], 0) + amount

# 3. Anything else inside c118 (Annex 7 dividend CIT, Annex 4/5 special income
#    tax) gets its own line on the account its accrual journal credited —
#    e.g. the corporate income tax payable account credited by the 22/78
#    dividend gross-up JE. Then HARD-STOP unless everything reconciles:
assert sum(sum(a.values()) for a in lines_by_vendor.values()) == total_obligation, \
    "bill lines must sum to c118_KohustKokku — find the unmapped component before posting"

# 4. One bill per authority vendor (EE: all line types map to the single EMTA
#    vendor → exactly one bill). Discover org-required fields FIRST — several
#    orgs require header dimensions on postings:
workflow(action="schema", object_type="transaction", operation="post")

period_str = f"{year}-{month:02d}"
due = <10th of the month AFTER the declared period>   # July TSD → due 10 August
settlement_bill_ids = []
for vendor_id, accounts in lines_by_vendor.items():
    result = submit("transaction", "post", json.dumps({
        "transaction_type_code": "AP_INVOICE",
        "legal_entity_id": run["legal_entity_id"],
        "vendor_id": vendor_id,
        "invoice_date": "<today, the TSD generation date>",
        "due_date": due,
        "reference_number": f"TSD-{run['legal_entity_id']}-{period_str}",
        "description": f"TSD settlement {period_str}",
        "lines": [
            {"account_number": acct, "amount": amt,
             "description": f"TSD {period_str} — {acct}"}
            for acct, amt in accounts.items()
        ],
        # plus dimensions/fields the schema call above marked required
        "metadata": {"source": "payroll_tax_settlement",
                     "tax_return_id": <id from Step 7>,
                     "tsd_period": period_str},
    }))
    settlement_bill_ids.append(result["transaction_id"])

# Idempotency: the AP_INVOICE executor rejects a duplicate (vendor +
# reference_number) that is already posted. On a re-run, treat that rejection
# as "already done" — look the bill up by reference and reuse its id. Never
# post a second bill for the same period.

# 5. Link return ↔ bill both ways:
submit("tax_return", "update", json.dumps({
    "return_id": <id from Step 7>,
    "return_data": {**return_data, "settlement_bill_ids": settlement_bill_ids},
}))
```

A correction TSD for an already-billed period posts a **supplemental** bill for
the positive delta with reference `TSD-{le}-{period}-K1` (a negative delta is a
vendor credit) — the base reference stays unique, so idempotency holds.

## Step 8 — Filing instructions to user

After successful generation, show:

1. Path of the generated XML file: `TSD_YYYYMM_{regcode}.xml`
2. Header totals summary (income tax, social tax, unemployment, pension, total obligation)
3. Filing steps:
   - Log in to **e-MTA** at https://maasikas.emta.ee with ID-card or Smart-ID
   - Navigate to **Declarations → TSD → Create** for the period (or **Amend** if `load_mode = P` and a draft already exists)
   - Choose **Upload XML** and select the generated file
   - Review the parsed declaration on screen
   - Sign digitally and submit
4. Deadline: **10th of the following month** (same day as tax payment)
5. After upload, ask user for the e-MTA confirmation number, then call:
   ```python
   submit("tax_return", "file", json.dumps({
       "return_id": <id from Step 7>,
       "confirmation_number": "<from portal>",
       "filing_date": "<YYYY-MM-DD>"
   }))
   ```

6. Payment: the Step 7b settlement bill is already in the AP queue — the payment
   proposal pays it by the same 10th-of-month deadline. Do not instruct the user
   to pay the authority manually outside that bill.

## Output

- `TSD_YYYYMM_{regcode}.xml` — the e-MTA-compatible XML
- `tax_return` row in the ERP linking the XML, JSON input, and header totals
- AP bill(s) `TSD-{legal_entity_id}-{YYYY-MM}` to the authority vendor(s) (Step 7b) — the payable the payment chain settles; ids stored in `return_data.settlement_bill_ids`

## Validation

The generator validates against the e-MTA XSD (`tsd_schema_eng_01.01.2023.xsd`) before writing. To re-validate manually:

```bash
xmllint --noout --schema /path/to/tsd_schema_eng_01.01.2023.xsd /path/to/TSD_YYYYMM_REGCODE.xml
# Output: ".../TSD_YYYYMM_REGCODE.xml validates"
```

Also verify the settlement bill: `get_entity("transaction", <settlement_bill_id>)` —
posted, vendor = the authority, lines sum to `c118_KohustKokku`, due the 10th of the
following month, and `tax_return.return_data.settlement_bill_ids` points back at it.

## See also

- `references/tsd-format.md` — full XSD structure and emit rules
- `references/tsd-codes.md` — `c1020_ValiKood`, `c1150_TuliKood`, `c3010_TuliKood` lookup tables
- `scripts/generate_tsd.py` — the generator
- `scripts/test_tsd_round_trip.py` — golden-master test against `Downloads/TSD 2026 4.xml`
- [`docs/GUIDES/GUIDE_TAX_FILING_PLUGINS.md`](../../../docs/GUIDES/GUIDE_TAX_FILING_PLUGINS.md) — the universal country-plugin contract
