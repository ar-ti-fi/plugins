---
name: prepare-ec-sales-list
description: Prepare the EC Sales List (Form VD) for intra-Community B2B supplies — a validated, KMD-reconciled data table for e-MTA portal entry
---

# Prepare EC Sales List (Form VD)

Prepare the report on intra-Community supply (Form VD, VAT Act § 28) for
VAT-registered B2B customers in other EU member states. Follows the official EMTA
completion procedure — see **skills/estonian-vat-declaration/references/ec-sales-list.md**
for the authoritative column semantics.

## Usage

```
/artifi-ee:prepare-ec-sales-list
```

## What This Does

1. Asks for legal entity ID and reporting period
2. Discovers tax codes that indicate intra-Community supply (property-based: zero-rated, EU B2B)
3. Fetches AR invoices for the period with those codes
4. Classifies per the form's columns: **goods** (col 3), **§ 10 (4) 9) services**
   (col 5), **triangular resale** (col 4), **call-off stock** (col 6)
5. Groups by purchaser VAT number — **one row per purchaser** (goods + services in the
   same row; a VAT number must not recur); amounts in **full euros**; credit notes as
   negative values in the period of the credit invoice
6. Excludes services to Northern Ireland (XI) customers
7. Validates purchaser VAT numbers (VIES) and flags unverified ones
8. Reconciles with the KMD: **col 3 total = `euSupplyGoodsZeroVat` (line 3.1.1)**;
   **col 5 total = `euSupplyInclGoodsAndServicesZeroVat` − `euSupplyGoodsZeroVat`
   (line 3.1 − 3.1.1)**; triangular (col 4) is NOT in the KMD

## When to Use

- Monthly alongside `/prepare-vat-declaration` when IC supplies exist (same deadline,
  20th of the following month)
- Skip entirely when the period has no IC supplies — an empty VD is not submitted
- Prior-period corrections go on **Form VDP**, call-off stock changes on **VDA**

## Prerequisites

- Customer records must carry valid EU VAT numbers (verify via VIES)
- Tax codes properly classified (zero-rated IC supply, property-based)

## Output

A portal-entry-ready table (one row per purchaser):

| Country (1) | VAT number (2) | Goods € (3) | Triangular € (4) | Services € (5) | Call-off acquirer (6) |
|---|---|---|---|---|---|

plus the KMD reconciliation (col 3 ↔ line 3.1.1, col 5 ↔ line 3.1 − 3.1.1) and a list
of VAT numbers still needing VIES verification.

**Filing**: enter the rows at <https://maasikas.emta.ee/decl-list-client/vd> and sign.
e-MTA publishes no public machine format (XSD/CSV) for the VD — unlike the KMD — so
portal entry is the supported path; do not generate XML for it.
