---
name: prepare-annual-report
description: Prepare the full Estonian annual report (majandusaasta aruanne) for a legal entity
---

# Prepare Estonian Annual Report

Execute the full annual report preparation workflow. This command triggers all 11 steps from the SKILL.md workflow.

## Usage

```
/artifi-ee:prepare-annual-report
```

## What This Does

1. Asks for legal entity ID, fiscal year, and income statement scheme
2. Verifies year-end close is complete
3. Determines company size category (Micro/Small/Medium/Large)
4. Fetches all financial data (trial balance, BS, IS, aging, fixed assets)
5. Compiles balance sheet following Annex 1 format
6. Compiles income statement (Scheme 1 or 2)
7. Compiles cash flow statement (if Medium/Large)
8. Compiles equity changes statement (if Medium/Large)
9. Compiles all required notes
10. Drafts management report with KPIs
11. Calculates profit allocation proposal
12. Generates XBRL mapping for portal entry
13. Provides filing guidance

## Mandatory Checkpoints

The workflow will stop if any checkpoint fails:
- All fiscal periods must be closed
- Trial balance must balance
- Balance sheet must balance
- Cash flow must reconcile

## Output

A comprehensive report document with all financial statements, notes, management report, and filing instructions.
