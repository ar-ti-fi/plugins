# KMD Pre-Close Validation Gate

The single gate that runs **before** the KMD is generated or uploaded. Every check has
a severity:

- **BLOCK** — do not generate the return until fixed.
- **WARN** — generate, but surface for the reviewer to confirm.

Run all seven, then emit one pass/fail report (see "Output" below). If any BLOCK is
open, **refuse to generate** and print the list. The `/prepare-vat-declaration` command
runs this gate automatically before the generate step; `/prepare-vat-declaration
validate` runs it standalone and stops.

Each check caused real rework in a prior period; the *Caught* note says what it would
have prevented.

---

## 1. Output-format validation — BLOCK

Enforced mechanically by `scripts/generate_kmd.py` after it builds the files and
**before** it writes them (the script refuses to write on any failure):

- XML validates against the bundled official `vatdeclaration.xsd` (`xmllint --noout --schema`).
- CSV is mechanically well-formed: exactly **31 fields** per row, period-correct
  **version** (KMD6 from 07.2025), **dot** decimals, `TRUE`/`FALSE` flags, **CRLF**
  endings, no BOM, and no total-VAT/payable columns.
- Derived figures recomputed and asserted: `line4 = 24%·line1 + 9%·line2 + …`;
  `line12 = line4 − inputVatTotal + adjustmentsPlus − adjustmentsMinus`; and, when the
  caller passes `expected_vat_payable` / `expected_vat_overpaid`, the computed value
  must match.

*Caught:* all three e-MTA rejections (the fabricated `<KMD>` schema and the
prose-header CSV) and the €20.79 line-5 gross-up error.

## 2. Completeness — payments without a document — BLOCK

Find cash movements in the period with no matching invoice/bill:

```
list_entities("transaction", {"legal_entity_id": ID, "transaction_type": "ar_payment"},
    date_filters={"transaction_date": {"from": "YYYY-MM-01", "to": "YYYY-MM-DD"}})
list_entities("transaction", {"legal_entity_id": ID, "transaction_type": "ap_payment"}, ...)
# plus unmatched bank statement lines for the period
```

Any AR_PAYMENT / AP_PAYMENT with `recon_status` null/unmatched, or any unmatched
`bank_statement_line`, is a **missing invoice/bill** (or a payment that should not be
there). List them and BLOCK until each is resolved.

*Caught:* the €572.88 Telia receipt whose invoice 2077 was never posted; the orphaned
EMTA tax payments.

## 3. Period basis / cut-off — WARN

Build the return strictly from documents **by invoice/document date**, never by payment
date. Flag any document whose invoice date and settlement date fall in different
periods so the reviewer checks the other period.

*Caught:* Nexia (invoice April, paid June) and the DigitalOcean / Supabase / Google May
invoices paid in June — the payment-vs-invoice-date confusion.

## 4. Tax-code coverage & jurisdiction sanity — BLOCK on missing, WARN on mismatch

- **BLOCK**: every taxable transaction line has a tax code (existing CP2), and each code
  resolves to a KMD line (see `references/tax-codes-ee.md`).
- **WARN**: supplier jurisdiction agrees with the code — an Estonian (EE) vendor must
  **not** carry an intra-EU-acquisition code (line 6); a non-EU supplier must map to
  line 7, not line 6. Compare `vendor.country_code` against the code's `tax_scope`.

*Caught:* Nexia / Wise Guys / AWS coded 845 (intra-EU) though domestic; the EU/non-EU
reverse-charge merge. (See `BILL_AGENT_FIX_for_ClaudeCode.md` — this check is the safety
net for that agent bug.)

## 5. GL tie-out — BLOCK on material difference

Reconcile the declaration to the VAT control accounts via
`generate_report("trial_balance", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})`
for the period:

- output VAT (`24%·line1 + reduced rates`) ↔ output-VAT account movement (2300 / 2310);
- input VAT (`inputVatTotal`, line 5) ↔ input-VAT account movement (2300 debit side / 2311);
- net ↔ line 12.

Report any difference above a rounding tolerance (≈ EUR 1) together with the driving
account.

> **Note:** the built-in `vat_report` is currently broken (`relation "tax_transactions"
> does not exist`), so tie out against the **trial balance** until that is fixed.

## 6. INF threshold / annex consistency — BLOCK

Sum sales per partner (excl. VAT) and purchases per partner (incl. VAT) for the period:

```
aggregate_entities("transaction", ["party_name"], {"amount": "sum", "id": "count"},
    {"legal_entity_id": ID, "transaction_type": "ar_invoice"}, date_filters={...})
# and the same for ap_invoice
```

If any partner ≥ EUR 1,000, the corresponding annex (`salesAnnex` / `purchasesAnnex`)
must be present and `noSales` / `noPurchases` = FALSE. Otherwise both must be TRUE and
the annexes omitted. (`generate_kmd.py` derives the flags from the annex lines, so the
gate's job is to confirm the annex lines match the threshold sums.)

*Caught:* confirms Hala's `noSales` / `noPurchases` = TRUE were correct (Telia €910 <
€1,000), and would flag the opposite mistake.

## 7. Arithmetic / form rules — BLOCK

- line 12 and line 13 are mutually exclusive (enforced by the script).
- If an EC Sales List (Form VD) exists: goods total = line 3.1, services total = line 3.2.
- All monetary values have 2 decimals and are non-negative where the XSD requires
  (`adjustmentsPlus` / `adjustmentsMinus`).

---

## Output

Emit a single report — one row per check with **PASS / WARN / BLOCK**, the offending
records, and the fix:

```
KMD Pre-Close Gate — Entity 41, 2026-06
  1. Output format ............ PASS
  2. Payments w/o document .... BLOCK  AP_PAYMENT #518 (€572.88 Telia) unmatched → post invoice 2077
  3. Period cut-off ........... WARN   Nexia inv 2026-04-…, settled 2026-06 → confirm April period
  4. Tax-code jurisdiction .... WARN   Vendor "AWS" (US) coded 845 (intra-EU) → should be line 7
  5. GL tie-out ............... PASS
  6. INF threshold ............ PASS   no partner ≥ €1,000 → noSales/noPurchases=TRUE
  7. Arithmetic / form rules .. PASS

RESULT: 1 BLOCK, 2 WARN → generation refused. Fix BLOCK items and re-run.
```

- **If any BLOCK is open**, refuse to generate the KMD and print the list.
- **WARN items** are listed but do not stop generation — the reviewer confirms them.

## Common issues and resolutions

| Issue | Resolution |
|---|---|
| Payment with no matching document | Post the missing invoice/bill, or reverse the stray payment |
| EE vendor carrying an intra-EU code | Recode to a domestic code; if reverse charge, use line 7 not line 6 |
| Missing tax code on invoice | Assign the correct code (property-based, see tax-codes-ee.md) |
| GL balance ≠ KMD | Unposted entries, manual journals, or a cut-off timing difference |
| KMD INF total ≠ KMD | Partners below threshold, credit notes, exempt transactions |
| EC Sales List ≠ lines 3.1/3.2 | Verify IC classification and customer EU VAT IDs |
