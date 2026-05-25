---
name: cash-runway
description: Compute burn rate and remaining cash runway for a cash-stressed borrower. Reads the last 3 months of operating cash flow, current cash position, and undrawn revolver capacity. Includes ±20% burn sensitivity.
---

# Cash Runway

For borrowers in working-capital strain, surface a clean runway calculation.

## Usage

```
/artifi-credit:cash-runway
```

## When to use this

This is the right command when the borrower's DSCR has tightened, when the EWS flagged "cash runway < 90 days", or when the user is explicitly worried about liquidity. For a healthy borrower, runway is rarely the metric to lead with — `/credit-read` covers liquidity in section 3.

## Workflow

### Step 1: Resolve cash position

Pull the balance sheet at as-of date:
```
generate_report("balance_sheet", {legal_entity_id: ID, as_of_date: <as_of>})
```

Extract:
- Cash and cash equivalents (sum all bank-account GL balances)
- Short-term borrowings (if revolver, find available headroom — needs separate query)
- Available revolver = total committed − drawn (ask the user if not on the books)

### Step 2: Compute monthly burn

Pull cash flow for the last 3 months:
```
generate_report("cash_flow_statement", {
    legal_entity_id: ID,
    start_date: <3mo back>,
    end_date: <as_of>
})
```

Read the **operating cash flow** line. Average it monthly.

- If operating CF is positive: company is **generating cash**. Runway is infinite at current pace; report that and stop.
- If operating CF is negative: that's the **burn**. Continue.

### Step 3: Compute runway

```
runway_months = (cash + available_revolver) / |monthly_burn|
```

### Step 4: Sensitivity

Show the same runway calc at **+20% burn** (faster cash depletion) and **−20% burn** (improvement). This gives the user a band.

## Output

A 3-line headline:

> **Runway: 7.2 months** at current burn (€420k/mo)
> ±20% sensitivity: 6.0–9.0 months
> Cash + undrawn revolver: €3.0M

Then a short table with the cash position breakdown (one row per bank account) and the operating CF trend (last 3 months, line by line). Plus one paragraph of context: what's the biggest driver of burn (typically working-capital build, opex, or interest).

## Output style

Lead with the number. If runway < 90 days, mark it **RED**. If 90–180 days, **AMBER**. If > 180 days, **GREEN**. Three-tier color so the credit team can scan at a glance.
