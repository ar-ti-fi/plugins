---
name: investor-statement
description: Generate a per-investor statement for a fund — subscription/redemption history, current shares held, position value at latest NAV per share, cumulative paid-in, cumulative returns, IRR. Statement-grade output suitable for emailing or PDF export.
---

# Investor Statement

Produce a complete per-investor statement showing their journey in the fund.

## Usage

```
/artifi-fund:investor-statement
```

## Prerequisites

- Fund has had at least one NAV strike (so there's NAV-per-share history to reference)
- Investor is in the cap table (subscribed at some point)

## Workflow

### Step 1: Resolve investor

Ask the user for the investor name. Look them up:
```
search("customer", "<investor name>")
```

Confirm the right investor by name + tax ID. Capture share class.

### Step 2: Pull transaction history

```
list_entities("transaction", {
    "legal_entity_id": FUND_ID,
    "customer_id": INVESTOR_ID
}, include_lines=True)
```

Filter to subscription / redemption / distribution transactions. Sort chronologically.

### Step 3: Pull NAV-per-share history

For each NAV strike (look for `transaction_type = JOURNAL_ENTRY` with `description LIKE 'NAV strike — %'`), capture the strike date and resulting NAV per share. Build a time series.

### Step 4: Compute investor's per-event positions

For each subscription/redemption:
- Subscription at strike date X: `shares_issued = amount / NAV_per_share_at_X`
- Redemption at strike date Y: `shares_redeemed = amount / NAV_per_share_at_Y`

Track cumulative shares held.

### Step 5: Compute current position

`current_position = shares_held × latest_NAV_per_share`

### Step 6: Compute returns

```
cumulative_returns = current_position - cumulative_paid_in + cumulative_distributions
total_return_pct = cumulative_returns / cumulative_paid_in
```

For an IRR calculation, treat each subscription as a negative cash flow at the subscription date, each redemption/distribution as positive at that date, and the current position as a final positive flow at the as-of date. Compute IRR with standard methods.

## Output

A markdown statement with:

### Header block

```
**Investor:** Banca Mediolanum SpA
**Tax ID:** IT11851040159
**Share class:** Class A
**Statement date:** 2026-05-31
**Status:** Active
```

### Position summary

```
| | EUR |
|---|---:|
| Cumulative paid-in | 5,500,000 |
| Cumulative redemptions | 0 |
| Cumulative distributions | 0 |
| Current shares held | 5,484,632 |
| NAV per share | 1.0028 |
| Current position | 5,500,016 |
| Cumulative returns | +16 |
| Total return | +0.0003% |
| Annualized IRR | 0.07% |
```

### Transaction history

```
| Date | Type | Amount EUR | NAV/share | Shares | Cumulative shares |
|---|---|---:|---:|---:|---:|
| 2026-01-01 | Initial subscription | 5,500,000 | 1.0000 | 5,500,000 | 5,500,000 |
| 2026-03-15 | Subscription | 500,000 | 1.0021 | 498,952 | 5,998,952 |
| 2026-04-30 | Redemption | 514,320 | 1.0028 | (513,000) | 5,485,952 |
```

## Output style

Investor-statement formatting: clean, no clutter, every number labelled, currency consistent. Should be read at face value with no need for explanation. Plus a 1-sentence footer with the run timestamp and the fund's contact info for queries.
