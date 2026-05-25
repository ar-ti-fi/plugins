---
name: cap-table
description: Snapshot of the fund's investor cap table as of the latest NAV strike. Lists all active investors with shares held, position value, and % ownership. Sorted by position descending.
---

# Cap Table

The current snapshot of who owns what share of the fund.

## Usage

```
/artifi-fund:cap-table
```

## Prerequisites

- Fund has had at least one NAV strike

## Workflow

### Step 1: Resolve fund + latest strike

Pick the fund entity. Find the most recent NAV strike (`description LIKE 'NAV strike — %'`) and capture:
- Strike date
- NAV per share at strike
- Total shares outstanding

### Step 2: For each active investor, compute position

For each customer that has had a subscription:
1. Net shares held = sum(subscription_shares) − sum(redemption_shares)
2. If net shares ≤ 0, investor is no longer in the fund — skip
3. Position EUR = net_shares × NAV_per_share
4. % ownership = net_shares / total_shares_outstanding

Track investor tier (institutional / mid / HNW) from `customer.metadata.investor_tier` if available.

### Step 3: Sort and present

Sort by position descending.

## Output

```
# Cap table — Multimanager Test SGR — Sub-fund A — Class A
**As of strike:** 2026-03-31  |  **NAV per share:** €1.0028  |  **Total shares:** 51,000,000  |  **NAV:** €51,123,840

| # | Investor | Tier | Shares | Position EUR | % of NAV |
|---|---|---|---:|---:|---:|
| 1 | Generali Italia Vita SpA | INST | 9,000,000 | €9,025,200 | 17.7% |
| 2 | Allianz SpA | INST | 7,500,000 | €7,521,000 | 14.7% |
| ... | ... | ... | ... | ... | ... |

## Concentration

- Top 5 investors: **49.0%** of NAV
- Top 10 investors: **76.4%** of NAV
- Institutional: 65.3% / Mid: 28.9% / HNW: 5.8%
```

### Validation

- Sum of positions = NAV (within €0.01 rounding) — CHECK
- Sum of shares = total shares outstanding — CHECK

If either check fails, surface the discrepancy with the size of the gap before presenting.

## Output style

Cap table style. Investors with consistent name spelling. Numbers right-aligned, comma-separated. Top 3 highlighted in bold. Tier tags as short codes. Plus a concentration summary block at the bottom.
