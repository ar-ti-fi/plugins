---
name: Fund Servicing
description: Strike NAV, accrue management and performance fees, process subscriptions and redemptions, maintain the per-investor cap table, and produce investor statements — all on an AI-native general ledger. The accounting and servicing layer behind tokenized funds, FoFs, and private-market vehicles.
---

## Trigger

Activate when the user mentions: NAV, NAV strike, NAV per share, fund valuation, management fee accrual, performance fee, high-water mark, subscriptions, redemptions, sub/red queue, investor capital, cap table, investor statement, fund administration, fund servicing, sub-fund, or specific fund product references (UCITS, SICAV, FCI, ELTIF, AIF).

## Core concept

A fund vehicle is structurally different from an operating company:

- **NAV (Net Asset Value)** = Assets − Liabilities = Investor equity at fair value
- **NAV per share** = NAV / shares outstanding
- Investor "balance" is shares × NAV per share, not a fixed amount
- Inflows are **subscriptions** (priced at the NAV per share at the strike), outflows are **redemptions** (same)
- Fund earnings are **management fees** (to the SGR/manager) and **performance fees** (crystallised above hurdle / high-water mark)
- The fund's "P&L" is unrealized + realized gains on holdings minus fees and expenses

The general ledger captures all of this, but you have to model it with care — investor capital sits in equity-section accounts, holdings sit in asset-section accounts marked to fair value, and the periodic "NAV strike" is the workflow that connects them.

## Prerequisites

Before any operation, determine:
1. **Fund legal entity ID** — which sub-fund to act on
2. **Strike date** — the date as of which NAV is being calculated
3. **Share class** — for multi-class funds, which class is being struck

The fund's COA needs the additions documented in `references/fund-coa-additions.md`: holdings at fair value, unrealized gains, investor capital paid-in, undistributed earnings, redemptions payable, management fee accruals, etc.

## Available commands

### 1. `/nav-strike` — the headline operation

Strike NAV for a given fund and date. This is the demo's marquee command and the most complex operation in fund servicing.

**Workflow:**

#### Step 1: Resolve fund + strike date

```
list_entities("legal_entity", {})
```

Pick the fund entity. Confirm strike date (typically last business day of the period).

#### Step 2: Pull current state of the fund

```
generate_report("trial_balance", {"legal_entity_id": ID, "as_of_date": <strike_date - 1 day>})
```

You need the pre-strike state to know:
- Holdings at fair value (account `1820` or equivalent)
- Cash position
- Investor capital — paid in (`3100`)
- Undistributed earnings (`3110`)
- Pending subscriptions receivable (`1830`)
- Pending redemptions payable (`2400`)
- Management fee payable (`2410`)

#### Step 3: Get new fair-value marks for holdings

This is the bit that has to come from outside the GL. Options:

- **Pricing feed** — if the fund has an external pricing connector, pull via that (out of scope for v0.1)
- **Manual input** — ask the user for new prices per holding (one row per ISIN)
- **Carry forward** — for illiquid holdings, mark unchanged (and note that in the strike journal)

Build a per-holding table: ISIN, name, prior fair value, new fair value, delta.

#### Step 4: Compute the strike NAV

```
NAV_strike = sum(new fair values) + cash − fees payable − redemptions payable
```

Note: subscriptions receivable count toward NAV (they're investor capital pledged), and management fee accrued in this period is a liability that reduces NAV.

#### Step 5: Compute NAV per share

```
NAV_per_share = NAV_strike / shares_outstanding_before_strike
```

`shares_outstanding_before_strike` = total Class A shares already on the cap table, before processing this strike's subs/red.

For the demo / simple case: assume **one share class** and **shares = paid-in capital at €1.0 face** as a starting convention. For real funds with multiple classes and per-class NAV, see `references/multi-class-funds.md` (advanced — out of v0.1 scope).

#### Step 6: Build the strike journal entries

A single NAV-strike workflow posts a series of GL entries:

**A. Holdings revaluation:**
```
DR 1825 (Unrealized gain on investments)        Δ fair value
CR 4720 (Unrealized gain/(loss) income)        Δ fair value
```
(Or the reverse if Δ is negative)

**B. Management fee accrual:**
```
DR 5500 (Management fee expense)               fee_amount
CR 2410 (Management fee payable to SGR)        fee_amount
```
Where `fee_amount = NAV_strike × (annual_fee_rate / 12)` for monthly accrual.

**C. Performance fee crystallisation** (if applicable):
```
DR 5505 (Performance fee expense)              perf_fee
CR 2420 (Performance fee accrued)              perf_fee
```
Only if NAV per share > high-water mark. Compute as % of excess. See `references/performance-fees.md`.

**D. Sub/red processing**: see `references/sub-red-processing.md`. Each pending subscription becomes:
```
DR 1001 (Cash, when received) or maintain 1830 → settle later
CR 3100 (Investor capital — paid in)
```
Each pending redemption:
```
DR 3100 (Investor capital — paid in) for the redeemed amount
CR 2400 (Redemptions payable)
```
Plus a per-investor cap table update (see Step 8).

**E. Period close** (allocate undistributed earnings):
```
DR 4720 (Unrealized gain) — close to undistributed
CR 3110 (Investor capital — undistributed earnings)
```

#### Step 7: Validate

- BS balances after all entries
- NAV per share is in a sane range (e.g. €0.80–€2.00 for funds priced at €1 face) — outside that, investigate
- Sum of per-investor capital ties to total `3100 + 3110` balance

#### Step 8: Recompute the cap table

For each investor, compute their share of NAV after the strike:
```
investor_shares × NAV_per_share = investor_position_post_strike
```

Track separately:
- Shares held (before / after strike)
- NAV per share at strike
- Position value
- Cumulative paid-in
- Cumulative returns (position − paid-in)

#### Step 9: Surface the strike summary

Present a compact result:

```
NAV strike — March 2026
- Pre-strike NAV: €50,320,741
- Holdings revaluation: +€278,000 (six holdings up, two flat)
- Management fee accrued: €62,901 (1.5% p.a. monthly)
- Custodian/admin paid: €12,000
- Subscriptions processed: €800,000 (Banca Mediolanum €500k, Family Office Bertarelli €300k)
- Redemption processed: €200,000 (Marco Esposito)
- Post-strike NAV: €51,123,840
- NAV per share: €1.0028  (+0.28% vs prior strike)
- Shares outstanding: 51,000,000 (was 50,200,000)
```

### 2. `/investor-statement` — per-investor view

For a single investor, produce a statement showing:
- Investor identity (name, tax ID, share class)
- Subscription history (date, amount, NAV per share at sub, shares issued)
- Redemption history (date, amount, NAV per share at red, shares redeemed)
- Current shares held
- Current position value at latest NAV per share
- Cumulative paid-in, cumulative returns, IRR
- Distributions received (if any)

**Workflow:**
1. Resolve investor (customer by name)
2. List all transactions where this investor was a counterparty
3. List the strike-date NAV per share history
4. Build the per-investor table

For a clean output, present this as a markdown table with columns: Date, Type, Amount EUR, NAV/share, Shares, Cumulative shares. Plus a header block with the investor identity and totals.

### 3. `/cap-table` — current cap table snapshot

Snapshot of all investors as of the last NAV strike.

For each investor:
- Name + tier (institutional / mid / HNW)
- Shares held
- Position EUR (shares × latest NAV per share)
- % ownership of fund

Sorted by position descending. Includes total checks: sum of positions should equal NAV, sum of shares should equal shares outstanding.

## Output style

This is bank-back-office output. Investor names spelled correctly, currency consistent, precision to the cent on amounts and to 4 decimal places on NAV per share. Investor statements typically end up emailed or as PDFs — assume the demo audience is reading them as a fund administrator would.

## What this plugin does NOT do (v0.1)

- **External pricing feeds.** New fair-value marks need to be input manually or via a separate connector.
- **Performance fee with crystallisation logic.** Only the simple high-water-mark math; equalisation, side pockets, and stepped performance hurdles are out of scope.
- **Multi-class waterfall.** Single share class only in v0.1.
- **Distribution accounting beyond accrual.** When dividends/distributions are declared, you'd need a separate workflow to compute per-investor allocation — not in v0.1.
- **DLT / token settlement.** The accounting layer assumes a separate token-side or registry-side process handles the on-chain settlement; this plugin records the books.

These exclusions are deliberate scoping for v0.1. Each is straightforward to add in a future version once the core NAV-strike + sub/red flow is validated.
