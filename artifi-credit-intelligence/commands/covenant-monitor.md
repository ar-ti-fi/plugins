---
name: covenant-monitor
description: Track financial covenants forward in time. Pulls current DSCR, leverage, and interest coverage from the live GL, projects the trend 90 days forward based on trailing-3-month slope, and flags any covenant that's likely to breach.
---

# Covenant Monitor

For an existing credit facility, surface the covenant ratios as of today and project them forward 90 days based on the trailing trend.

## Usage

```
/artifi-credit:covenant-monitor
```

## Prerequisites

- Borrower's books current through last month-end
- Known covenant package (minimum DSCR, maximum leverage, etc.) — the skill will ask if not provided

## What it does

For each covenant in scope:
1. Compute the **current** ratio from the live GL
2. Compute the **trailing-3-month** trend (slope per month)
3. Project the ratio at **+30d, +60d, +90d**
4. Compute **headroom**: (current − covenant minimum) for each projection point
5. Flag breach probability: NONE / LOW / MEDIUM / HIGH

## Standard covenant set

If the user doesn't specify covenants, default to the typical Italian SME term-loan set:

| Covenant | Standard minimum | Standard maximum |
|---|---|---|
| DSCR | **≥ 1.20x** | — |
| Leverage (Net Debt / EBITDA) | — | **≤ 3.50x** |
| Interest Coverage (EBITDA / Interest) | **≥ 3.00x** | — |
| Tangible Net Worth | **≥ €500k** | — |

Ask the user to override these if the facility has different terms.

## Workflow

### Step 1: Fetch the trailing data

Same data pull as `/credit-read`:
```
generate_report("income_statement", {legal_entity_id: ID, start_date: <13mo back>, end_date: <as_of>})
generate_report("balance_sheet", {legal_entity_id: ID, as_of_date: <as_of>})
```

Plus 3 monthly P&Ls for the last 3 months to compute the slope.

### Step 2: Compute current ratios

See `skills/credit-intelligence/references/dscr-calculation.md` for the ratio definitions and EBITDA build.

### Step 3: Compute the slope per ratio

For each covenant ratio (e.g., DSCR), build the last 3 monthly trailing-12 readings and compute the linear slope:

```
slope = (ratio_now - ratio_3mo_ago) / 3
```

### Step 4: Project forward

```
projection_30d = current + slope × 1
projection_60d = current + slope × 2
projection_90d = current + slope × 3
```

### Step 5: Flag breach probability

For each projection point:
- **NONE**: headroom > 0.20 across all projection horizons
- **LOW**: headroom > 0.10 but trend deteriorating
- **MEDIUM**: headroom < 0.10 at 90d, or any projection point below covenant
- **HIGH**: current already at headroom < 0.05, or 30d projection below covenant

## Output

A single table per covenant with current / 30d / 60d / 90d projections, headroom at each point, and the breach flag. Compact, decision-ready.

Plus a 2-3 sentence narrative summarizing which covenant is the most likely to breach and what the underlying driver is (e.g., "EBITDA deterioration of 8%/month over the last 3 months pushes DSCR from 1.27x → 1.15x by 90 days, below the 1.20x minimum").

## Output style

Bank-relationship-manager grade output. Numbers in tables. Drivers in plain text. No filler.
