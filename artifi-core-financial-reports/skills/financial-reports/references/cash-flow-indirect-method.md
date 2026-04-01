# Cash Flow Statement — Indirect Method

## Structure

The cash flow statement explains the change in cash between two dates by categorizing all cash movements into three activities.

### A. Cash Flows from Operating Activities

Start with net profit and adjust for non-cash items and working capital changes.

| Adjustment | Source | Direction |
|-----------|--------|-----------|
| **Net profit / (loss)** | Income statement | Starting point |
| + Depreciation and amortization | Fixed asset register / GL | Add back (non-cash expense) |
| + Impairment losses | GL detail | Add back (non-cash) |
| +/- Gain/loss on disposal of assets | GL detail | Remove (investing activity) |
| +/- Unrealized FX gains/losses | GL detail | Remove (non-cash) |
| +/- Changes in provisions | Balance sheet comparison | Non-cash |
| **Working capital changes:** | | |
| - (Increase) / + Decrease in receivables | BS comparison | Cash tied up / released |
| - (Increase) / + Decrease in inventory | BS comparison | Cash tied up / released |
| + Increase / - (Decrease) in payables | BS comparison | Cash received / paid |
| + Increase / - (Decrease) in deferred revenue | BS comparison | Cash received / returned |
| +/- Change in other operating assets/liabilities | BS comparison | Net movement |
| **= Net cash from operating activities** | | |

### B. Cash Flows from Investing Activities

| Item | Source | Direction |
|------|--------|-----------|
| - Purchase of PP&E | Fixed asset acquisitions | Cash outflow |
| + Proceeds from sale of PP&E | Asset disposal records | Cash inflow |
| - Purchase of intangible assets | Asset acquisitions | Cash outflow |
| - Purchase of investments | GL detail | Cash outflow |
| + Proceeds from sale of investments | GL detail | Cash inflow |
| + Interest received | GL detail | Cash inflow (if classified here) |
| + Dividends received | GL detail | Cash inflow |
| **= Net cash from investing activities** | | |

### C. Cash Flows from Financing Activities

| Item | Source | Direction |
|------|--------|-----------|
| + Proceeds from issuing shares | Equity accounts | Cash inflow |
| - Treasury share purchases | Equity accounts | Cash outflow |
| + Proceeds from loans / borrowings | Loan accounts | Cash inflow |
| - Repayment of loans / borrowings | Loan accounts | Cash outflow |
| - Lease payments (principal portion) | Lease liability accounts | Cash outflow |
| - Dividends paid | Equity / GL detail | Cash outflow |
| - Interest paid | GL detail | Cash outflow (if classified here) |
| **= Net cash from financing activities** | | |

### Summary

```
Net cash from operating activities       XXX,XXX.XX
Net cash from investing activities       (XX,XXX.XX)
Net cash from financing activities       (XX,XXX.XX)
                                        ───────────
Net increase / (decrease) in cash        XXX,XXX.XX
Cash at beginning of period              XXX,XXX.XX
FX effect on cash (if multi-currency)      X,XXX.XX
                                        ───────────
Cash at end of period                    XXX,XXX.XX
```

## Data Collection

```
# Current period balance sheet
generate_report("balance_sheet", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})

# Prior period balance sheet (for working capital changes)
generate_report("balance_sheet", {"legal_entity_id": ID, "as_of_date": "PRIOR-YYYY-MM-DD"})

# Income statement (for net profit starting point)
generate_report("income_statement", {"legal_entity_id": ID, "start_date": "...", "end_date": "..."})

# Cash flow report (if available as a built-in report)
generate_report("cash_flow_statement", {"legal_entity_id": ID, "start_date": "...", "end_date": "..."})
```

## Validation

1. **Cash reconciliation** (mandatory): Net change in cash = Closing cash balance - Opening cash balance on the balance sheet
2. **Operating cash vs net income**: If significantly different, explain the main non-cash adjustments
3. **Free cash flow**: Operating cash flow - Capital expenditures. Positive = company generates cash after maintaining assets

## Analysis Points

- **Operating CF > Net Income**: Healthy — company converts profits to cash
- **Operating CF < Net Income**: Investigate — may indicate aggressive revenue recognition, growing receivables, or declining collections
- **Negative investing CF**: Normal for growing companies (buying assets)
- **Positive investing CF**: May indicate asset sales / downsizing — investigate
- **Negative financing CF**: Paying down debt or returning capital — generally healthy
- **Positive financing CF**: Taking on debt or raising equity — check why
