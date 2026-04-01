---
name: prepare-ec-sales-list
description: Prepare the EC Sales List (Form VD) for intra-community B2B supplies
---

# Prepare EC Sales List (Form VD)

Generate the EC Sales List for reporting intra-community B2B supplies to VAT-registered customers in other EU member states.

## Usage

```
/artifi-ee:prepare-ec-sales-list
```

## What This Does

1. Asks for legal entity ID and reporting period
2. Discovers tax codes that indicate intra-community supply (zero-rated, EU B2B)
3. Fetches AR invoices for the period with those tax codes
4. Groups by customer VAT number and classifies supply type (Goods / Services / Triangular)
5. Validates customer EU VAT numbers
6. Reconciles totals with KMD Lines 3.1 and 3.2
7. Generates Form VD data ready for EMTA submission

## When to Use

- Monthly alongside KMD preparation (if IC supplies exist)
- When needing to file Form VD separately
- To verify IC transaction classification

## Prerequisites

- Intra-community supplies must exist in the period
- Customer records must have valid EU VAT numbers
- Tax codes must be properly classified (zero-rated IC supply)

## Output

- Form VD data table (customer VAT number, country, supply type, amount)
- Reconciliation with KMD Lines 3.1/3.2
- List of VAT numbers requiring VIES verification
- XML-ready data for EMTA upload
