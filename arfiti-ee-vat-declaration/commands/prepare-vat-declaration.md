---
name: prepare-vat-declaration
description: Prepare the monthly Estonian VAT declaration (KMD) with KMD INF annex for EMTA filing
---

# Prepare Estonian VAT Declaration (KMD)

Execute the full monthly VAT declaration workflow. This command triggers all 8 steps from the SKILL.md workflow.

## Usage

```
/arfiti-ee:prepare-vat-declaration
```

## What This Does

1. Asks for legal entity ID and reporting period (month/year)
2. Discovers and classifies the entity's tax codes by properties (not hardcoded names)
3. Presents tax code → KMD line mapping for user confirmation
4. Fetches all posted transactions for the period (AR/AP invoices, credit notes, journals)
5. Verifies all transactions have tax codes assigned
6. Calculates KMD Lines 1-13 using property-based classification
7. Prepares KMD INF annex (partners > EUR 1,000)
8. Prepares EC Sales List (Form VD) if intra-community supplies exist
9. Reconciles VAT GL accounts with KMD totals
10. Generates complete filing package with validation results

## Mandatory Checkpoints

The workflow will stop if any checkpoint fails:
- All transactions for the period must be posted (no drafts)
- All transaction lines must have tax codes assigned
- KMD calculations must balance (output - input = net)
- KMD INF totals must reconcile with KMD
- EC Sales List must reconcile with KMD Lines 3.1/3.2

## Output

A comprehensive declaration package including:
- KMD form (Lines 1-13) with calculated amounts
- KMD INF annex (Part A: sales partners, Part B: purchase partners)
- EC Sales List / Form VD (if applicable)
- GL reconciliation summary
- Validation checklist results
- Filing instructions and deadline reminder
