# EMTA Filing Guide (KMD2)

## Overview

The Estonian Tax and Customs Board (EMTA — Maksu- ja Tolliamet) accepts the monthly
VAT return through the e-MTA portal. The return is the **KMD2** dataset, which bundles
three parts into a single submission:

1. **KMD** — the main VAT return form (`declarationBody`)
2. **KMD INF A** — sales-partner annex (`salesAnnex`)
3. **KMD INF B** — purchase-partner annex (`purchasesAnnex`)

The **EC Sales List (Form VD)** for intra-Community B2B supplies is a **separate**
declaration with its own format — see the `/prepare-ec-sales-list` command
(and `references/ec-sales-list.md`). It is not part of the KMD2 dataset and is not
produced by `generate_kmd.py`.

## Filing requirements

| Requirement | Details |
|---|---|
| **Deadline** | 20th of the following month |
| **Frequency** | Monthly |
| **Submission** | e-MTA portal — CSV upload, XML upload, or manual entry |
| **Currency** | EUR, 2 decimal places |
| **Reg code** | Estonian business registry code |

## Two file formats — CSV (primary) and XML

`scripts/generate_kmd.py` emits both:

- **`KMD_YYYYMM_{regcode}.csv`** — the KMD2 **machine CSV** (e-MTA's fixed-column
  upload format). **Primary artifact.**
- **`vatDeclaration_YYYYMM_{regcode}.xml`** — the full KMD2 XML (main form + KMD INF
  A/B annexes), validated against the bundled `vatdeclaration.xsd`. **Secondary.**

Both files carry the KMD INF A/B partners (the CSV as `A`/`B` rows).

### CSV layout (KMD2 machine format)

This is a **fixed-column** file — **not** the English prose-header human export, which
e-MTA rejects ("Only xml, csv and zip files corresponding to the specification are
allowed"). Every row has exactly **31 semicolon-separated fields**; unused trailing
fields are left empty. Rules: **dot** decimals (2 places), flags `TRUE`/`FALSE`,
**CRLF** line endings, no BOM, invoice dates `DD.MM.YYYY`.

```
header;14276473;;2026;6;1;;;;…                       ← general part (reg;submitter;year;month;type)
KMD6;TRUE;TRUE;FALSE;FALSE;910.00;;…;80.33;;…        ← version;noSales;noPurchases;sumSales;sumPurch;<26 body values>
A;2345678;Nimi;887766385;10.07.2025;1000.00;24;1000.00;1000.00;;… ← salesAnnex saleLine (KMD INF A)
B;3456789;Nimi;448826649;07.07.2025;1220.00;220.00;110.00;12;;…   ← purchasesAnnex purchaseLine (KMD INF B)
```

The 26 body values are the `declarationBody` elements in XSD sequence order (omitting the
obsolete `selfSupply20`/`selfSupply9`): transactions24, transactions22, transactions20,
transactions9, transactions5, transactions13, transactionsZeroVat,
euSupplyInclGoodsAndServicesZeroVat, euSupplyGoodsZeroVat, exportZeroVat,
salePassengersWithReturnVat, inputVatTotal, importVat, fixedAssetsVat, carsVat,
numberOfCars, carsPartialVat, numberOfCarsPartial, euAcquisitionsGoodsAndServicesTotal,
euAcquisitionsGoods, acquisitionOtherGoodsAndServicesTotal,
acquisitionImmovablesAndScrapMetalAndGold, supplyExemptFromTax, supplySpecialArrangements,
adjustmentsPlus, adjustmentsMinus.

There are **no** columns for total VAT (line 4) or amount payable (line 12) — e-MTA
computes them from the bases + `inputVatTotal` + lines 6/7.

### XML upload — official format

Per e-MTA's format description, the XML document is the general part
(`taxPayerRegCode`, `submitterPersonCode`, `year`, `month`, `declarationType`,
`version`) plus any of the three data parts. You may send one, two, or all three
parts; the general part is always mandatory. Files may be sent raw or zipped (one
file per upload, max 10 MB).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<vatDeclaration>
  <taxPayerRegCode>14276473</taxPayerRegCode>
  <year>2026</year>
  <month>6</month>
  <declarationType>1</declarationType>
  <version>KMD6</version>
  <declarationBody>
    <noSales>true</noSales>
    <noPurchases>true</noPurchases>
    <sumPerPartnerSales>false</sumPerPartnerSales>
    <sumPerPartnerPurchases>false</sumPerPartnerPurchases>
    <transactions24>736.10</transactions24>
    <inputVatTotal>71.25</inputVatTotal>
    <euAcquisitionsGoodsAndServicesTotal>155.10</euAcquisitionsGoodsAndServicesTotal>
  </declarationBody>
</vatDeclaration>
```

**Format rules** (enforced by the XSD):

- Root `vatDeclaration`, **no XML namespace**.
- Amounts: `xs:decimal`, 2 fraction digits, **dot** separator, no thousands separator.
- `version` is period-dependent: **KMD4** (01.2024–12.2024), **KMD5**
  (01.2025–06.2025), **KMD6** (from 07.2025). `generate_kmd.py` sets it automatically.
- When a period has no partner exceeding the KMD INF threshold, set `noSales` /
  `noPurchases` to `true` and **omit** the corresponding annex.
- Do **not** emit total VAT (line 4), VAT due (line 12) or overpaid (line 13) —
  there are no elements/columns for them; e-MTA computes them.

### Source of truth

- Technical info: <https://www.emta.ee/en/business-client/e-services-training-courses/how-use-e-services/technical-information-services>
- XSD (07.2025+, has the 24% rate): <https://ncfailid.emta.ee/s/W5ncAiYRyye2of3/download/vatdeclaration.xsd>
- Format description: <https://www.emta.ee/media/1096/download>

The bundled `scripts/vatdeclaration.xsd` is a copy of the XSD above; `generate_kmd.py`
validates every XML against it (via `xmllint --schema`) and refuses to write files on
a schema violation.

## e-MTA portal

URL: <https://maasikas.emta.ee>. Log in with ID-card, Mobile-ID, or Smart-ID.

1. Navigate to: Deklaratsioonid → Käibemaks → KMD, select the period.
2. **CSV/XML upload**: choose "Laadi fail" (Upload file) and upload
   `KMD_YYYYMM_{regcode}.csv` (or the XML). Review the imported values.
3. **Manual entry**: enter the main-form values and, if applicable, the KMD INF
   partners.
4. Review, sign digitally, and submit.

## Penalties

| Violation | Penalty |
|---|---|
| Late filing | Up to EUR 3,200 per occurrence |
| Incorrect declaration | Interest on underpaid tax (0.06% per day) |
| Failure to file | Up to EUR 3,200 + enforcement proceedings |
| KMD INF omissions | Separate penalty up to EUR 3,200 |

Filing within 3 months of the deadline with a voluntary correction generally avoids
penalties.

## Amendment process

To amend a filed return, file a new KMD2 submission for the same period — it replaces
the previous one. For the EC Sales List, file the VD amendment separately (via the
`/prepare-ec-sales-list` command).

## Calendar reminders

| Period | Deadline |
|---|---|
| January KMD | February 20 |
| February KMD | March 20 |
| … | 20th of the following month |
| December KMD | January 20 (next year) |
