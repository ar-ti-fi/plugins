---
name: credit-read
description: Read a borrower's live general ledger and produce a complete credit memo — DSCR, leverage, working-capital cycle, concentration risk, early warning signals — with citations back to specific GL transactions. The headline command of the credit-intelligence plugin.
---

# Credit Read

Generate a portfolio-monitoring credit memo for a single borrower from the live GL.

**How it works:** This command fetches monthly P&L history, balance sheet, AR/AP aging, and cash flow via MCP report tools, computes credit ratios and trend metrics, scans for the early-warning signals defined in `references/credit-signals.md`, builds a compact JSON, and runs `scripts/format_credit_memo.py` — a Python script that produces a consistently formatted markdown credit memo.

## Usage

```
/artifi-credit:credit-read
```

The skill (`skills/credit-intelligence/SKILL.md`) holds the full workflow. Highlights:

## Prerequisites

- Borrower's books are reasonably current — last month's close completed
- Trial balance ties at the as-of date (the skill validates this)
- Python 3.9+ available (`python3 --version`)

## Step 1: Resolve entity + as-of date

Ask the user for the entity (if not clear from context) and the as-of date (default: today).

## Step 2: Fetch the data lineage

The data pull is one income_statement call per month for the last 13 months, plus balance_sheet, ar_aging, ap_aging, cash_flow_statement at the as-of date.

## Step 3: Compute the metrics

For the EBITDA / DSCR / leverage build, see `skills/credit-intelligence/references/dscr-calculation.md`.
For the aging-bucket interpretation, see `references/aging-interpretation.md`.

## Step 4: Run the formatter

Write the compiled JSON to `/tmp/credit_memo_{ENTITY_ID}_{DATE}.json` per `scripts/input_schema_credit_memo.json`, then:

```bash
python3 scripts/format_credit_memo.py \
  --input /tmp/credit_memo_{ENTITY_ID}_{DATE}.json \
  --output /tmp/credit_memo_{ENTITY_ID}_{DATE}.md
```

## Step 5: Validate before presenting

The skill's checkpoint section requires two validations before showing the memo:
1. Trial balance ties at the as-of date
2. DSCR falls in a sane 0.5x–4x range

If either fails, surface it to the user first.

## Output sections

The formatter produces a 6-section credit memo:

1. **Snapshot** — entity header + headline numbers in a single block
2. **Financial trajectory** — 13-month P&L table with margin trend
3. **Liquidity & working capital** — cash, DSO/DPO/DIO, runway
4. **Capital structure & coverage** — net debt, leverage, DSCR vs. covenants
5. **Concentration & quality** — top-5 customer/vendor share, AR aging
6. **Early warning signals** — bulleted EWS with severity + citations

## Output style

Numbers up front, narrative second. Every flagged signal includes 2-3 source citations. The formatter produces sparkline tables for trends — present them as the script outputs them.
