---
name: cash-flow
description: Generate a Cash Flow Statement using the indirect method, with balance sheet reconciliation and cash quality analysis.
---

# Cash Flow Statement

Generate a cash flow statement for a legal entity using the indirect method.

**How it works:** This command fetches cash flow, balance sheet, and P&L data via MCP tools. The SKILL.md workflow guides the indirect method calculation, and the output follows the format in **references/cash-flow-indirect-method.md**.

## Usage

```
/arfiti-core:cash-flow
```

## Prerequisites

- All transactions for the period must be posted
- Both current and prior period balance sheets must be available (for working capital changes)

## Step 1: Collect Data

Ask for the legal entity and date range, then fetch:

```
# Cash flow report (if available)
generate_report("cash_flow_statement", {"legal_entity_id": ID, "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"})

# Current and prior balance sheets (for working capital changes)
generate_report("balance_sheet", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})
generate_report("balance_sheet", {"legal_entity_id": ID, "as_of_date": "PRIOR-YYYY-MM-DD"})

# Income statement (for net profit starting point)
generate_report("income_statement", {"legal_entity_id": ID, "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"})
```

## Step 2: Build the Cash Flow

Follow the indirect method structure from **references/cash-flow-indirect-method.md**:

**A. Operating Activities:**
- Start with net profit
- Add back depreciation, amortization, impairment
- Remove gains/losses on asset disposal
- Adjust for working capital changes (receivables, inventory, payables)

**B. Investing Activities:**
- PP&E purchases and disposals
- Investment purchases and sales

**C. Financing Activities:**
- Loan proceeds and repayments
- Equity transactions
- Dividends paid

## Step 3: Validate

**Mandatory check:** Net change in cash (A + B + C) must equal closing cash minus opening cash on the balance sheet.

If it doesn't reconcile:
- Check for FX translation differences
- Verify all non-cash items are properly adjusted
- Look for reclassifications between periods

## Step 4: Present Results

Present the cash flow statement in the standard three-section format with:
- Operating, investing, and financing activities with line items
- Net change in cash
- Opening and closing cash reconciliation
- Free cash flow (Operating CF - Capex)
- Commentary on cash generation quality (operating CF vs net income)

## Output Format

```markdown
# Cash Flow Statement
**Acme Corp OÜ** | 2026-01-01 to 2026-03-31 | Currency: EUR

## A. Operating Activities

| | Amount |
|---|--------|
| Net profit | 58,000.00 |
| Depreciation and amortization | 12,000.00 |
| Change in receivables | (13,000.00) |
| Change in inventory | 7,000.00 |
| Change in payables | 8,000.00 |
| **Net cash from operating** | **72,000.00** |

## B. Investing Activities

| | Amount |
|---|--------|
| Purchase of PP&E | (15,000.00) |
| Other investments | (3,000.00) |
| **Net cash from investing** | **(18,000.00)** |

## C. Financing Activities

| | Amount |
|---|--------|
| Loan repayments | (25,000.00) |
| **Net cash from financing** | **(25,000.00)** |

## Summary

| | Amount |
|---|--------|
| Net change in cash | 29,000.00 |
| Opening cash | 96,000.00 |
| **Closing cash** | **125,000.00** |
| Free Cash Flow | 57,000.00 |

Validation: Closing cash matches balance sheet ✓
```
