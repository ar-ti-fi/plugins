---
name: nav-strike
description: Strike NAV for a fund as of a specific date. Revalues holdings, accrues management and performance fees, processes pending subscriptions and redemptions from the queue, recomputes the per-investor cap table, and produces a strike summary.
---

# NAV Strike

The marquee operation of fund servicing. Strike NAV closes the period for valuation, fee accrual, and investor activity.

**How it works:** The skill (`skills/fund-servicing/SKILL.md`) walks through the 9-step workflow. The strike posts a coordinated set of GL entries (holdings revaluation, fee accruals, sub/red processing, period close), then surfaces a compact strike summary table.

## Usage

```
/artifi-fund:nav-strike
```

## Prerequisites

- Fund's COA includes the fund-specific accounts (holdings at fair value, investor capital, fee accruals — see `references/fund-coa-additions.md` if onboarding didn't include them)
- New fair-value marks for the underlying holdings (manual input or pricing feed)
- Pending sub/red queue is current (subscriptions and redemptions for this strike are already on the books with `metadata.status_flag = 'pending_for_strike'`)

## Step 1: Resolve fund + strike date

Ask the user for the fund (if not in context) and confirm the strike date.

## Step 2: Get current state

Pull the trial balance as of the day before the strike date. Extract pre-strike NAV components: holdings at fair value, cash, investor capital, fee payables, pending sub/red.

## Step 3: Collect new fair-value marks

For each underlying holding, ask the user (or pull from a pricing connector) for the new fair value at strike date. Build the delta vs prior period.

## Step 4: Compute strike NAV and NAV per share

```
NAV_strike = new holdings FV + cash − fees payable − redemptions payable
NAV_per_share = NAV_strike / shares_outstanding
```

## Step 5: Post the strike journal entries

A coordinated set of GL entries (one transaction with multiple lines, or several linked transactions):

- **A.** Holdings revaluation (DR/CR Unrealized G/L on investments)
- **B.** Management fee accrual (DR Management fee expense / CR Management fee payable)
- **C.** Performance fee crystallisation (if NAV/share > HWM)
- **D.** Sub processing (per pending subscription: DR Cash / CR Investor capital paid-in)
- **E.** Red processing (per pending redemption: DR Investor capital / CR Redemptions payable)
- **F.** Period close (allocate unrealized to undistributed earnings)

## Step 6: Validate

- BS ties post-strike
- NAV per share is in sane range (e.g. €0.80–€2.00 for €1-face funds)
- Sum of per-investor capital = total Investor Capital balance

## Step 7: Recompute cap table

For each investor: new shares (if sub/red), shares × NAV per share = position. Track cumulative paid-in and cumulative returns.

## Step 8: Output

A strike summary block + per-investor cap-table table.

Example output:

```
NAV strike — March 2026
- Pre-strike NAV: €50,320,741
- Holdings revaluation: +€278,000
- Management fee accrued: €62,901
- Subscriptions processed: €800,000 (2 investors)
- Redemption processed: €200,000 (1 investor)
- Post-strike NAV: €51,123,840
- NAV per share: €1.0028  (+0.28% vs prior)
- Shares outstanding: 51,000,000 (was 50,200,000)
```

## Output style

Bank back-office grade. Investor names spelled correctly, currency consistent to cents, NAV per share to 4 decimals. Read by fund administrators and investors directly.
