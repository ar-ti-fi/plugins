# Statement of Changes in Equity (Omakapitali muutuste aruanne)

Required for medium and large companies.

## Format

| Component | Opening Balance | Contributions | Distributions (dividends) | Net Profit/Loss | Transfers | Closing Balance |
|---|---|---|---|---|---|---|
| Share capital (Osakapital) | X | +/- | | | | X |
| Share premium (Ulekurss) | X | +/- | | | | X |
| Statutory reserve (Reservkapital) | X | | | | + from profit | X |
| Other reserves | X | | | | +/- | X |
| Retained earnings | X | | - dividends | | + from profit - to reserve | X |
| Current year profit/loss | 0 | | | Net P&L | - to retained earnings | X |
| **Total equity** | **X** | | | | | **X** |

## MCP Tool Call

```
generate_report("trial_balance", {
    "legal_entity_id": ID,
    "as_of_date": "YYYY-12-31"
})
# Filter equity accounts (5000-5399)

# Prior year for opening balances
generate_report("trial_balance", {
    "legal_entity_id": ID,
    "as_of_date": "YYYY-1-12-31"
})
```

## Notes

- Opening balance of each component = closing balance of prior year
- Current year profit/loss transferred from income statement
- Statutory reserve transfer per profit allocation proposal
- Dividends recorded when declared (distribution date)
