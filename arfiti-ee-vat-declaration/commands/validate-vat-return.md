---
name: validate-vat-return
description: Run pre-submission validation checks on a prepared VAT declaration
---

# Validate VAT Return

Run the full validation checklist against a prepared or in-progress VAT declaration without generating the complete filing package.

## Usage

```
/arfiti-ee:validate-vat-return
```

## What This Does

1. Asks for legal entity ID and reporting period
2. Checks transaction completeness (no drafts, all tax codes assigned)
3. Verifies KMD calculation integrity (line formulas, mutually exclusive 12/13)
4. Validates KMD INF partner data (registration codes, threshold compliance)
5. Checks EC Sales List reconciliation with KMD Lines 3.1/3.2
6. Reconciles VAT GL account balances against KMD totals
7. Reports all issues by severity (Blocker / Warning / Info)

## When to Use

- Before filing to catch errors early
- After making corrections to re-validate
- Monthly as part of close process
- When investigating GL vs. KMD discrepancies

## Output

A validation report with:
- Pass/fail status for each check
- Issues grouped by severity (Blockers must be fixed before filing)
- Specific transaction references for any failed checks
- Suggested resolutions for common issues
