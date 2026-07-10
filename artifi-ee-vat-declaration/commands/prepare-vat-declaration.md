---
name: prepare-vat-declaration
description: Prepare and validate the monthly Estonian VAT return (KMD) for e-MTA — runs the pre-close validation gate, then generates the KMD2 machine CSV + XSD-validated XML and the KMD INF annex. Hands off the EC Sales List to /prepare-ec-sales-list when intra-EU supplies exist. Run with `validate` to check only.
---

# Estonian VAT Return (KMD)

The **single** command for the monthly VAT close. It runs the pre-close validation gate,
and only if nothing is blocking does it generate the filing. Everything — the KMD main
form, KMD INF A/B, and the EC Sales List (Form VD) — happens here.

## Usage

```
/artifi-ee:prepare-vat-declaration            # full run: gate → generate → file
/artifi-ee:prepare-vat-declaration validate   # run the gate only, then stop
```

`validate` runs Phases 1–3 (the gate) and stops with the pass/fail report — nothing is
generated. Use it to check early, or to re-check after corrections.

## Prerequisites

- All transactions for the period posted (no drafts); all lines have tax codes.
- Python 3.9+ available (`python3 --version`).

---

## Phase 1 — Gather (SKILL steps 1–3)

Follow **skills/estonian-vat-declaration/SKILL.md**:
1. Discover & classify tax codes (property-based — never hardcode names).
2. Fetch all posted transactions for the period (AR/AP invoices, credit notes, journals).
3. Verify every line has a valid tax code.

## Phase 2 — Pre-close validation gate (BLOCK / WARN)

Run **every** check in **skills/estonian-vat-declaration/references/validation-checklist.md**
and emit the single pass/fail report:

1. Output-format validation — enforced by `generate_kmd.py` in Phase 5 (listed here for completeness)
2. Completeness — payments without a document — **BLOCK**
3. Period basis / cut-off — **WARN**
4. Tax-code coverage & jurisdiction sanity — **BLOCK** on missing, **WARN** on mismatch
5. GL tie-out vs. the trial balance — **BLOCK** on material difference
6. INF threshold / annex consistency — **BLOCK**
7. Arithmetic / form rules — **BLOCK**

**If any BLOCK is open: STOP. Print the report and the fix list. Do not generate.**
WARN items are listed for the reviewer to confirm but do not stop the run.

> **If invoked as `validate`: stop here** and present the report. Do not proceed.

## Phase 3 — Build the KMD data (SKILL steps 4–5)

Once the gate is green (no open BLOCK):

- Compute `declaration_body` with **real KMD2 element names** (bases by rate +
  `inputVatTotal` + reverse-charge lines 6/7). Do **not** supply total VAT / line 12 /
  line 13 — e-MTA computes them.
- Aggregate KMD INF partners (threshold EUR 1,000) into `sales_annex` / `purchases_annex`.

Build the input JSON (see `scripts/input_schema_kmd.json` for the full example):

```json
{
  "regcode": "REGCODE",
  "submitter_person_code": null,
  "year": YYYY, "month": MM, "declaration_type": 1,
  "input_vat_full_deduction": true,
  "expected_vat_payable": 138.07,
  "declaration_body": {
    "transactions24": 910.00, "inputVatTotal": 80.33,
    "euAcquisitionsGoodsAndServicesTotal": 36.64,
    "acquisitionOtherGoodsAndServicesTotal": 50.00
  },
  "sales_annex": {"sum_per_partner": false, "lines": [ ... ]},
  "purchases_annex": {"sum_per_partner": false, "lines": [ ... ]}
}
```

- Pass `expected_vat_payable` (or `expected_vat_overpaid`) — the figure you derived from
  the GL tie-out — so the generator asserts its computation matches (check 1).
- Set `input_vat_full_deduction: false` if the taxpayer's input VAT is only partly
  deductible; the generator then warns that the reverse charge does not net out.
- Omit an annex entirely when no partner reaches EUR 1,000 (the generator sets
  `noSales` / `noPurchases` = true).

## Phase 4 — EC Sales List (Form VD) hand-off, only if intra-EU B2B supplies exist

Check whether the period has zero-rated supplies to EU VAT-registered customers
(KMD lines 3.1 / 3.2 non-zero). If so, the **EC Sales List (Form VD)** is due — a
**separate** e-MTA declaration with its own format. Tell the user to run
**`/artifi-ee:prepare-ec-sales-list`** for it (it reconciles goods total = line 3.1,
services total = line 3.2). If there are no IC supplies, state that Form VD is not
required. Form VD is intentionally its own command because it is a distinct filing, not
part of the KMD2 dataset.

## Phase 5 — Generate

```bash
# scripts/generate_kmd.py  (find with: find ~ -name generate_kmd.py -path "*/artifi-ee-vat-declaration/*")
python3 generate_kmd.py --input /tmp/kmd_data_{REGCODE}_{YYYYMM}.json --output {OUTPUT_DIR}
```

The script re-runs the **output-format gate** (check 1) on its own output and **refuses
to write files** on any failure: it validates the XML against the bundled
`vatdeclaration.xsd`, mechanically checks the CSV (31 fields/row, correct version, dot
decimals, TRUE/FALSE, CRLF), and asserts the derived figures (incl. any `expected_*`).
On success it writes:

- `KMD_YYYYMM_{REGCODE}.csv` — KMD2 machine CSV (fixed 31-field rows), **primary**.
- `vatDeclaration_YYYYMM_{REGCODE}.xml` — full KMD2 XML (main form + INF A/B), secondary.

## Phase 6 — Record & post to the ERP (SKILL steps 8–9)

- `submit("tax_return", "create", …)` with `return_data.declaration_body` (+ annexes,
  summaries). Report the `tax_return_id`.
- Post the VAT closing journal entry (net to VAT Payable / Receivable).

## Phase 7 — File & confirm

1. Log in to **e-MTA** (maasikas.emta.ee), Declarations → KMD, select the period.
2. "Laadi fail" → upload `KMD_YYYYMM_{REGCODE}.csv` (or the XML — both carry the main
   form and the INF partners). If Form VD applies, file it separately.
3. Portal validates → sign digitally → submit. **Deadline: 20th of the following month.**
4. After filing: `submit("tax_return", "file", {"return_id": …, "confirmation_number": …})` —
   this also transitions the tax reporting period to `filed`.
5. **Lock the period** so the filed return keeps matching the ledger:
   `submit("tax_period", "lock", {"period_id": <reporting_period_id>, "reason": "KMD filed — conf# …"})`.
   Ask the user first; to amend later, `submit("tax_period", "unlock", …)`, correct, re-file, re-lock.
   The Reports → Sales tax reconciliation panel flags any ledger-vs-return drift either way.

> **Payment note:** check the e-MTA prepayment account (ettemaksukonto) first — a
> positive balance from payroll taxes may reduce the actual transfer below KMD line 12.

## Output

- Pre-close gate report (Phase 2) with PASS / WARN / BLOCK per check.
- `KMD_YYYYMM_{REGCODE}.csv` (primary) + `vatDeclaration_YYYYMM_{REGCODE}.xml` (secondary).
- A hand-off to `/prepare-ec-sales-list` when IC supplies exist (Form VD is filed separately).
- Tax return record + VAT closing journal entry, with the `tax_return_id`.
