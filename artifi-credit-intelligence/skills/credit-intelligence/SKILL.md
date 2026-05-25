---
name: Credit Intelligence
description: Read a borrower's live general ledger and produce a credit memo with DSCR, leverage, working-capital cycle, concentration risk, early-warning signals, and citations. Designed for portfolio credit monitoring — not for one-off underwriting from PDFs. Works against any chart of accounts through dynamic discovery.
---

## Trigger

Activate when the user mentions: credit memo, credit read, credit analysis, DSCR, covenant, covenant monitor, borrower review, portfolio credit, watchlist, cash runway, early warning, EWS, AR aging risk, vendor concentration, customer concentration, or "is this borrower healthy".

## Core principle

A credit memo is only as good as its data lineage. **Every metric in the output must trace back to a specific GL account or transaction.** When you cite a number, name the source (account code, transaction reference, or aggregation period). When you flag a signal, show two or three of the underlying rows so a credit analyst can drill in.

The borrower is "alive" — their books move daily. Re-running this command an hour after the last run can produce a different DSCR if a payment posted in between. Treat the read as a point-in-time snapshot and **always include the timestamp** of the run in the output.

## Prerequisites

Before starting, determine:
1. **Legal entity ID** — which borrower to analyze
2. **As-of date** — typically today; for back-testing or covenant review, the last period close
3. **Reporting currency** — derive from the entity's functional currency

## What "the credit memo" contains

A complete `/credit-read` produces a 5-section markdown report:

1. **Snapshot** — entity, as-of date, key headline numbers (NAV-equivalent: equity, total assets, net debt, cash; revenue and EBITDA trailing-12; DSCR; concentration)
2. **Financial trajectory** — 12-month monthly history of revenue, GP, opex, EBITDA, and the DSCR line. Includes margin trend ("GM compressing 3.5pp over 6 months") with citations.
3. **Liquidity & working capital** — cash position, DSO / DPO / DIO trends, cash conversion cycle, runway calc.
4. **Capital structure & coverage** — net debt, leverage (Net Debt / EBITDA), interest coverage (EBITDA / interest), DSCR (EBITDA / total debt service). Each metric vs. its covenant if known.
5. **Concentration & quality** — top-5 customer share of AR + revenue, top-5 vendor share of AP + spend, AR aging buckets, any in-dispute flags, large unreconciled items.
6. **Early warning signals (EWS)** — bullet list of detected red flags, each with citation. See `references/credit-signals.md` for the trigger rules.

## Available commands

### 1. `/credit-read <entity>` — the headline command

**Workflow:**

#### Step 1: Resolve the entity

```
list_entities("legal_entity", {})
```

Pick the entity by name or ID. Read `functional_currency` and `country_code` for reporting context.

#### Step 2: Pull the financial trajectory

Get **monthly P&L** for the last 13 months (12 prior + current partial):

```
generate_report("income_statement", {
    "legal_entity_id": ID,
    "start_date": "YYYY-MM-01",   # 13 months back
    "end_date": "<as_of>"
})
```

For each month in scope, also pull a separate income_statement for just that month so you can build the **monthly trend table**. Compute:
- Revenue per month
- Gross profit (revenue − cogs)
- Gross margin %
- Operating expenses
- EBITDA = Revenue − COGS − OpEx (excl. depreciation, interest, tax)
- Trailing-12 EBITDA (sum)

See `references/dscr-calculation.md` for the EBITDA build and DSCR formula.

#### Step 3: Pull the balance sheet snapshot

```
generate_report("balance_sheet", {
    "legal_entity_id": ID,
    "as_of_date": "<as_of>"
})
```

Extract:
- Cash and cash equivalents
- Trade receivables (gross)
- Inventory total
- Trade payables
- Short-term debt + current portion of long-term debt
- Long-term debt
- Total equity

Compute:
- Net debt = (short-term debt + LT debt) − cash
- Net debt / trailing-12 EBITDA → **leverage**
- Quick liquidity = (cash + AR) / current liabilities

#### Step 4: Pull AR and AP aging

```
generate_report("ar_aging", {"legal_entity_id": ID, "as_of_date": "<as_of>"})
generate_report("ap_aging", {"legal_entity_id": ID, "as_of_date": "<as_of>"})
```

Compute:
- Total open AR, % by aging bucket (current / 1-30 / 31-60 / 61-90 / 91+)
- Top-5 customer concentration: each customer's open AR as % of total
- DSO = (open AR / revenue last 90 days) × 90
- Same for AP and DPO

See `references/aging-interpretation.md` for the credit-analyst lens on aging shape.

#### Step 5: Detect signals

Run through the EWS rules in `references/credit-signals.md`. For each signal triggered, capture:
- Signal name (e.g., "GM compression > 2pp over 6 months")
- The two or three GL data points that triggered it (so the user can drill in)
- Severity (LOW / MEDIUM / HIGH)

Common signals to scan for:
- Gross margin trend (compression > 2pp over 6 months → MEDIUM, > 5pp → HIGH)
- DSO drift (rising > 10 days over 6 months → MEDIUM)
- DPO stretching (rising > 10 days over 6 months → MEDIUM — sign of cash strain)
- Customer concentration > 30% on one customer → MEDIUM
- DSCR approaching covenant (< 1.5x → MEDIUM, < covenant + 0.1x → HIGH)
- Cash runway < 90 days at current burn → HIGH
- Vendor invoices flagged in_dispute or unmatched in AP aging → LOW (informational)

#### Step 6: Build the input JSON and run the formatter

Compile a single JSON document per `scripts/input_schema_credit_memo.json` shape, write to `/tmp/credit_memo_{ENTITY_ID}_{DATE}.json`, then:

```bash
python3 scripts/format_credit_memo.py \
  --input /tmp/credit_memo_{ENTITY_ID}_{DATE}.json \
  --output /tmp/credit_memo_{ENTITY_ID}_{DATE}.md
```

Read the output and present it to the user. **Don't paraphrase** — the script's output is the deliverable. If the formatter errors, fix the input JSON and re-run; don't try to assemble the memo by hand.

### 2. `/covenant-monitor <facility>` — track covenant ratios forward

For a known credit facility, project DSCR and leverage forward 90 days based on the trailing trend and scheduled debt service. Flag if any projection breaches the covenant.

Pull the same data as `/credit-read`, then for each covenant:
1. Compute the current ratio
2. Compute the trailing-3-month trend (slope)
3. Project forward 90 days
4. Flag breach probability: NONE / LOW / MEDIUM / HIGH

Output as a single table per covenant with current / 30-day / 60-day / 90-day projections and the breach flag.

### 3. `/cash-runway <entity>` — burn rate + runway

For a cash-stressed borrower:
1. Operating cash flow from `cash_flow_statement` report, last 3 months
2. Compute average monthly burn (or generation)
3. Current cash position + any undrawn revolver capacity
4. Runway = (cash + undrawn revolver) / monthly burn — only meaningful if burn > 0
5. Sensitivity: same calculation at +/- 20% burn

Output is a compact paragraph with the headline number and 3-month sensitivity.

### 4. `/borrower-watchlist` — multi-borrower comparison

When the user is monitoring multiple borrowers as a portfolio. For each entity in scope:
- Run a lightweight version of `/credit-read` (key metrics only — DSCR, leverage, AR concentration, signal count)
- Compile into one comparison table
- Rank by composite risk score (described in `references/credit-signals.md`)

This is for **portfolio review** — for any individual borrower the user wants to drill into, switch to `/credit-read <entity>` for the full memo.

## Output style

Credit memos are **read by people who need to make a decision fast**. The output style:

- **Numbers up front, narrative second.** Headlines as tables and bullets. Reserve commentary for the EWS section.
- **Always cite.** Never write "DSCR is 1.27x" without "EBITDA €780k / debt service €615k (trailing 12 months)". Never flag a signal without 2-3 underlying rows.
- **Show the trend.** A single point-in-time metric is much less useful than the 6-month trajectory. The formatter produces sparkline tables — don't try to summarize them as narrative.
- **Be specific about confidence.** If a number depends on a posting that hasn't happened yet (e.g., end-of-month accrual not yet posted), say so. Don't pretend it's clean if it isn't.

## Checkpoint: validate before presenting

Before showing the memo to the user, run two sanity checks:

1. **Trial balance ties.** Pull `trial_balance` at the as-of date and confirm total debits = total credits. If they don't, STOP and flag — the underlying ledger is mid-posting and any derived metric will be off.
2. **DSCR sanity range.** A real-world DSCR is typically 0.5x–4x. If your computed DSCR is outside this range, investigate before presenting — it's almost always a sign that either EBITDA includes non-operational items, or debt service is missing principal repayments.

If either check fails, surface the issue to the user and ask before continuing. Better a delayed memo than a wrong one.

## What this skill does NOT do

- **Underwrite a new credit.** This is portfolio monitoring, not initial underwriting. New-borrower memos need diligence inputs (corporate structure, management background, market analysis) that aren't in the ledger.
- **Make recommendations.** Output is observations and signals. The credit committee decides what to do.
- **Project default probability.** No PD model is fitted here. Signals are deterministic, not statistical.

These are deliberate design choices — `/credit-read` produces input *for* a credit decision, not the decision itself.
