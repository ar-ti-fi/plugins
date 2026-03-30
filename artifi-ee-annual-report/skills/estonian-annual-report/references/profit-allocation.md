# Profit Allocation Proposal (Kasumi jaotamise ettepanek)

Required for all companies.

## Statutory Reserve Calculation

Estonian Commercial Code requires:
- **Statutory reserve** must reach at least **1/10 (10%) of share capital**
- Each year, at least **1/20 (5%) of net profit** must be transferred to statutory reserve until the minimum is met

## Calculation Logic

```
Share capital:                          EUR [X]
Required statutory reserve (10%):       EUR [X * 0.10]
Current statutory reserve:              EUR [Y]
Shortfall:                              EUR [X * 0.10 - Y]

Net profit for the year:                EUR [Z]
Minimum transfer to reserve (5%):       EUR [Z * 0.05]
Actual transfer (min of shortfall, 5%): EUR [min(shortfall, Z * 0.05)]

Available for distribution:             EUR [Z - actual_transfer]
```

## MCP Tool Call

```
generate_report("trial_balance", {
    "legal_entity_id": ID,
    "as_of_date": "YYYY-12-31"
})
```

Extract:
- Share capital (accounts 5000-5049)
- Current statutory reserve (accounts 5150-5199)
- Net profit for the year (calculated from income statement)

## Template

```
KASUMI JAOTAMISE ETTEPANEK / PROFIT ALLOCATION PROPOSAL

Net profit for the financial year YYYY:              EUR [amount]

The Management Board proposes to allocate the net profit as follows:

1. Transfer to statutory reserve (reservkapital):    EUR [amount]
   (5% of net profit / amount needed to reach 10% of share capital)

2. Dividend distribution to shareholders:            EUR [amount]
   (Note: Subject to 20/80 income tax on distribution)

3. Carry forward to retained earnings:               EUR [amount]

Total:                                               EUR [net_profit]
```

## Estonian CIT on Dividends

When dividends are distributed, the company pays CIT at the rate of 20/80 on the net dividend amount. For example, a EUR 8,000 net dividend results in EUR 2,000 CIT (8,000 * 20/80), with the gross distribution being EUR 10,000.
