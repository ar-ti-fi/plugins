---
name: borrower-watchlist
description: Portfolio view across multiple borrower entities. Computes a lightweight credit snapshot for each (DSCR, leverage, AR concentration, signal count) and ranks by composite risk score so the credit team can spot which borrowers need attention.
---

# Borrower Watchlist

When you're monitoring a portfolio of borrowers — typical for bank relationship managers, PE credit teams, alternative lenders.

## Usage

```
/artifi-credit:borrower-watchlist
```

## Prerequisites

- Multiple legal entities visible (either via consolidated org access or multi-org connection)
- Books reasonably current on each — entities mid-close will show stale numbers

## Workflow

### Step 1: Enumerate entities in scope

```
list_entities("legal_entity", {is_active: true})
```

If the user has narrowed the watchlist (e.g., "just the manufacturing portfolio"), filter accordingly. Otherwise default to all active entities the connection has read access to.

### Step 2: For each entity, pull the lightweight metric set

For each entity, run a **lightweight** version of `/credit-read` — just enough to populate the comparison table. Skip the full memo formatter. Per entity, pull:

```
generate_report("balance_sheet", {legal_entity_id: ID, as_of_date: <as_of>})
generate_report("income_statement", {legal_entity_id: ID, start_date: <12mo back>, end_date: <as_of>})
generate_report("ar_aging", {legal_entity_id: ID, as_of_date: <as_of>})
```

Compute:
- Trailing-12 EBITDA
- Net debt
- Leverage (ND / EBITDA)
- DSCR (using best-effort debt service from balance-sheet debt accounts)
- Top customer concentration (largest customer's % of open AR)
- AR aging shape — % of AR in 60+ buckets
- Signal count (run the EWS rules from `references/credit-signals.md`, count triggers)

### Step 3: Compute composite risk score

A simple 0-100 score (higher = riskier), combining:
- DSCR signal: 30 pts if < 1.20x covenant, 15 pts if 1.20-1.40x, 0 pts if > 1.40x
- Leverage signal: 25 pts if > 3.50x, 10 pts if 2.50-3.50x, 0 pts otherwise
- AR aging signal: 20 pts if > 30% of AR in 60+ buckets, 10 if 15-30%, 0 if < 15%
- Concentration signal: 15 pts if top customer > 30% of AR, 5 if 20-30%, 0 if < 20%
- EWS count: 2 pts per signal (capped at 10)

### Step 4: Rank and present

Build one comparison table sorted by risk score descending:

| Entity | TTM Rev | EBITDA | DSCR | Leverage | Top Cust % | Risk Score | Flags |
|---|---:|---:|---:|---:|---:|---:|---|
| Lombardia Manifattura SRL | €12.0M | €0.8M | 1.27x | 2.50x | 28% | **62** | GM↓, DSO↑ |
| ... | ... | ... | ... | ... | ... | ... | ... |

For any borrower scoring **>50**, recommend follow-up with `/credit-read <entity>` for the full memo. For **<30**, no action.

## Output style

This is a **scan view**. One table, max 20 rows. Highlight (color or `**bold**`) the top 3 by risk score. Keep flags concise — 2-3 character codes (GM↓ = gross margin compression, DSO↑ = DSO rising, COV⚠ = approaching covenant, AGE⚠ = AR aging deteriorating, DISP = vendor disputes present).

Below the table, a 2-sentence narrative: "Of N borrowers, X are above the action threshold. Top concern: <entity> — <one-line driver>."
