# EMTA Filing Guide

## Overview

The Estonian Tax and Customs Board (EMTA — Maksu- ja Tolliamet) accepts VAT returns
through the e-MTA portal. Three forms are filed together monthly:

1. **KMD** — Main VAT declaration (Lines 1-13)
2. **KMD INF** — Transaction partner annex (Part A: Sales, Part B: Purchases)
3. **Form VD** — EC Sales List (if intra-community supplies exist)

## Filing Requirements

| Requirement | Details |
|---|---|
| **Filing Deadline** | 20th of the following month |
| **Filing Frequency** | Monthly |
| **Submission Method** | e-MTA portal (manual entry or XML upload) |
| **Currency** | EUR (rounded to 2 decimal places) |
| **Language** | Estonian (form labels are bilingual on portal) |

## e-MTA Portal

URL: [https://maasikas.emta.ee](https://maasikas.emta.ee)

### Manual Entry
1. Log in with ID-card, Mobile-ID, or Smart-ID
2. Navigate to: Deklaratsioonid > Kaibemaks > KMD
3. Select reporting period (month/year)
4. Enter values for Lines 1-13
5. Navigate to KMD INF tab for partner reporting
6. Submit and digitally sign

### XML Upload
1. Log in to e-MTA
2. Navigate to: Deklaratsioonid > Kaibemaks > KMD
3. Select "Laadi fail" (Upload file)
4. Upload KMD XML file
5. Upload KMD INF XML file separately
6. Upload Form VD XML file (if applicable)
7. Review imported values
8. Submit and digitally sign

## XML Specifications

### KMD Main Form

```xml
<?xml version="1.0" encoding="UTF-8"?>
<KMD xmlns="http://emta.ee/schemas/vat">
  <Period>
    <Year>2025</Year>
    <Month>01</Month>
  </Period>
  <TaxpayerRegCode>12345678</TaxpayerRegCode>
  <Line1>10000.00</Line1>
  <Line1_1>2400.00</Line1_1>
  <Line2>5000.00</Line2>
  <Line2_1>650.00</Line2_1>
  <Line3>0.00</Line3>
  <Line3_1>15000.00</Line3_1>
  <Line3_2>8000.00</Line3_2>
  <Line4>1800.00</Line4>
  <Line4_1>500.00</Line4_1>
  <Line5>3000.00</Line5>
  <Line5_1>2000.00</Line5_1>
  <Line6>0.00</Line6>
  <Line7>0.00</Line7>
  <Line8>0.00</Line8>
  <Line10>1250.00</Line10>
  <Line11>0.00</Line11>
  <Line12>1250.00</Line12>
  <Line13>0.00</Line13>
</KMD>
```

### Encoding and Format Rules

- XML must be UTF-8 encoded
- Amounts: 2 decimal places, no thousands separator
- Period: 4-digit year, 2-digit month (zero-padded)
- Registration code: 8 digits (Estonian business registry)
- All amount fields must be present (use 0.00 if no value)

## Penalties

| Violation | Penalty |
|---|---|
| Late filing | Up to EUR 3,200 per occurrence |
| Incorrect declaration | Interest on underpaid tax (0.06% per day) |
| Failure to file | Up to EUR 3,200 + enforcement proceedings |
| KMD INF omissions | Separate penalty up to EUR 3,200 |

Filing within 3 months of the deadline with voluntary correction generally avoids penalties.

## Amendment Process

To amend a previously filed declaration:
1. File a new KMD for the same period (replaces the previous one)
2. For KMD INF: file corrected annex
3. For Form VD: file Form VDP (amendment form) specifying the original period

## Calendar Reminders

| Month Activity | Deadline |
|---|---|
| January KMD | February 20 |
| February KMD | March 20 |
| March KMD | April 20 |
| ... | 20th of following month |
| December KMD | January 20 (next year) |
