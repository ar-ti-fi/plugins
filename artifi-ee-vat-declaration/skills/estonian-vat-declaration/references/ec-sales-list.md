# EC Sales List (Form VD / VDP / VDA)

The report on intra-Community supply (Form VD — ühendusesisese käibe aruanne, VAT Act
§ 28) reports intra-Community B2B supplies to VAT-registered persons in other EU
member states. Amendments to prior periods go on **Form VDP**; call-off stock changes
on **VDA**.

Content below follows the official EMTA completion procedure (form valid from
01.02.2021).

## Filing Requirements

| Attribute | Detail |
|---|---|
| **Form** | VD (report) / VDP (amendment of prior periods) / VDA (call-off stock changes) |
| **Frequency** | Monthly, submitted together with the KMD |
| **Deadline** | 20th of the following month |
| **Amounts** | **Full euros** (no cents) |
| **Authority** | EMTA — file at <https://maasikas.emta.ee/decl-list-client/vd> |
| **Required when** | Intra-Community supply of goods, § 10 (4) 9) services to EU taxable persons, triangular resale, or call-off stock transport occurred |
| **Not required when** | None of the above occurred in the period — do not submit an empty VD |

## The Form's Columns (official layout)

One row **per purchaser VAT number** — goods and services for the same purchaser go
in **one row**; a VAT number must not recur.

| Col | Content | Notes |
|---|---|---|
| **1** | Country code of the purchaser | ISO code; **EL** for Greece, **XI** for Northern Ireland |
| **2** | Purchaser's VAT identification number | No punctuation/spaces; verify via VIES before invoicing |
| **3** | Taxable value of **goods** (intra-Community supply) | Empty for pure call-off stock transport |
| **4** | **Triangular transaction** value (as reseller) | Resale in a triangle is NOT intra-Community supply — not in the KMD at all |
| **5** | Taxable value of **services** (§ 10 (4) 9), taxed in recipient's state) | Services to **Northern Ireland (XI) are NOT declared** |
| **6** | VAT number of the **call-off stock** acquirer | Cols 2–3 stay empty for the transport itself |

**Credit notes / cancelled invoices:** reduce the value in the period the credit
invoice was issued (negative values allowed, minus sign). Other corrections of past
periods → Form VDP.

## Reconciliation with the KMD (KMD2 element names)

| VD column | Reconciles with |
|---|---|
| Col 3 (goods) total | `euSupplyGoodsZeroVat` — KMD line **3.1.1** |
| Col 5 (services) total | `euSupplyInclGoodsAndServicesZeroVat` − `euSupplyGoodsZeroVat` — KMD line **3.1 − 3.1.1** |
| Col 4 (triangular) | **Nothing** — the reseller's triangular resale is not declared in the KMD |

> Small legitimate differences on the goods line can arise (e.g. new means of
> transport sold to non-VAT-registered persons, customs-agency representation per
> § 17 (2¹)) — flag but don't hard-block on them; everything else must tie out.

⚠️ Older versions of this plugin reconciled "goods = 3.1, services = 3.2" — that was
**wrong**: 3.1 is the goods+services total and 3.2 is *export of goods* (non-EU),
which never appears on the VD.

## How to Identify IC Transactions

Use tax code properties — never hardcoded names (see `tax-codes-ee.md`):

1. AR invoices for the period where `default_rate = 0` and the customer is an
   EU (non-EE) business with a VAT ID.
2. Classify: **goods** (col 3) vs **§ 10 (4) 9) services** (col 5) vs **triangular
   resale** (col 4) vs **call-off stock** (col 6).
3. Group by purchaser VAT number — one row per purchaser, goods and services summed
   into the same row. Amounts in full euros.
4. Exclude services provided to Northern Ireland (XI) customers.

## VAT Number Verification

Verify every purchaser's VAT number via VIES
(<https://ec.europa.eu/taxation_customs/vies/>) — EMTA itself recommends checking
before invoicing. If a number is invalid, the supply **cannot be zero-rated**
(standard rate applies) and the row does not belong on the VD.

## Filing

The VD is a **separate** e-MTA declaration from the KMD — it is **not** part of the
KMD2 dataset and is not produced by `generate_kmd.py`. Do **not** reuse the KMD
`vatDeclaration` schema or any `http://emta.ee/schemas/vat` namespace for it (that
namespace does not exist at e-MTA).

**File via the e-MTA portal**: enter the per-purchaser rows at
<https://maasikas.emta.ee/decl-list-client/vd>. Unlike the KMD, e-MTA publishes **no
public XSD or machine CSV specification for the VD** on its
technical-information-services page (checked 2026-07-10) — the deliverable of
`/prepare-ec-sales-list` is therefore a validated, reconciled data table for portal
entry, not an upload file. If EMTA later publishes a machine format, mirror the KMD2
approach: bundle the official schema and validate before writing files.

**Authoritative sources:**
- Completion procedure (columns, reconciliation): <https://www.emta.ee/sites/default/files/documents/2021-08/vorm_vd_juhend_eng_2020.pdf>
- VD/VDP forms & procedure: <https://www.emta.ee/en/business-client/taxes-and-payment/tax-returns-exchange-information/vat-return-forms-vd-and-vdp>
- e-MTA VD submission: <https://maasikas.emta.ee/decl-list-client/vd>
