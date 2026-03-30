# Cash Flow Statement (Rahavoogude aruanne)

Required for medium and large companies. Optional for small. Uses the indirect method.

## Structure (Indirect Method)

| Section | Line Items | Data Source |
|---|---|---|
| **A. Operating activities** | | |
| Net profit/loss | From income statement | Income statement |
| Depreciation and amortization | Add back non-cash | Fixed asset register |
| Change in receivables | (Increase)/decrease | BS comparison |
| Change in inventories | (Increase)/decrease | BS comparison |
| Change in payables | Increase/(decrease) | BS comparison |
| Other non-cash items | Provisions, impairments | GL detail |
| **Net cash from operating activities** | | Calculated |
| **B. Investing activities** | | |
| Purchase of PP&E | Cash paid for assets | Fixed asset acquisitions |
| Sale of PP&E | Cash received | Fixed asset disposals |
| Purchase of investments | | GL detail |
| **Net cash from investing activities** | | Calculated |
| **C. Financing activities** | | |
| Proceeds from loans | | GL detail (loan accounts) |
| Repayment of loans | | GL detail (loan accounts) |
| Dividends paid | | GL detail (equity accounts) |
| Share capital contributions | | GL detail (equity accounts) |
| **Net cash from financing activities** | | Calculated |
| **Net change in cash** | A + B + C | Calculated |
| Cash at beginning of year | | Prior year BS |
| **Cash at end of year** | | Current year BS |

## MCP Tool Calls

```
# Cash account movements
generate_report("trial_balance", {"legal_entity_id": ID, "as_of_date": "YYYY-12-31"})
generate_report("trial_balance", {"legal_entity_id": ID, "as_of_date": "YYYY-1-12-31"})

# Fixed asset movements for investing activities
list_entities("fixed_asset", {"legal_entity_id": ID})
```

## Validation

**Net change in cash MUST equal closing cash minus opening cash on the balance sheet.**

If it does not reconcile:
- Compare cash GL detail to BS cash lines
- Check for FX translation differences
- Verify all non-cash items are properly adjusted
