# Early-warning signals (EWS) — trigger rules

Deterministic signal definitions. Each signal must trigger from specific GL data with at least one cite-able underlying transaction or aggregation.

The credit memo's "Early warning signals" section is a bulleted list of triggered signals, each with severity (LOW / MEDIUM / HIGH) and 2-3 citations.

## Profitability signals

### `GM_COMPRESSION`

**Trigger:** Gross margin (revenue − COGS) / revenue, computed monthly, has declined > 2 percentage points over the trailing 6 months (compare month 1 average to last-3-month average).

**Severity:**
- > 2pp drop: **MEDIUM**
- > 5pp drop: **HIGH**

**Citations:** Month-by-month GM % for the 6-month window. Mention the absolute revenue and COGS for the first and last months.

**Why it matters:** GM compression is the earliest signal of pricing pressure, input cost inflation, or product mix deterioration. By the time it shows up in EBITDA or DSCR, it's already months old. Catch it here.

### `EBITDA_DECLINE`

**Trigger:** Trailing-3-month EBITDA is at least 20% below trailing-12-month average EBITDA, normalized for seasonality.

**Severity:**
- 20–40% drop: **MEDIUM**
- > 40% drop: **HIGH**

**Citations:** The trailing-3 and trailing-12 EBITDA numbers, and which components drove the decline (revenue down? COGS up? opex up?).

## Working capital signals

### `DSO_DRIFT`

**Trigger:** DSO has risen by more than 10 days over the trailing 6 months (compare DSO at month 1 to DSO at as-of date).

**Severity:**
- 10–20 day drift: **MEDIUM**
- > 20 day drift: **HIGH**

**Citations:** DSO at start of window, DSO now, and the top customer whose payment slowdown contributed most (if identifiable).

### `DPO_STRETCH`

**Trigger:** DPO has risen by more than 10 days over the trailing 6 months.

**Severity:**
- 10–20 day stretch: **MEDIUM** (could be deliberate WC management or strain)
- > 20 day stretch: **HIGH** (almost always strain at this magnitude)

**Citations:** DPO at start of window, DPO now, and at least one specific vendor whose payment timing has stretched.

### `AR_AGING_DETERIORATION`

**Trigger:** % of AR in 60+ aging buckets is > 30%, or has risen > 10 percentage points over 3 months.

**Severity:**
- 30–50% in 60+: **MEDIUM**
- > 50% in 60+: **HIGH**

**Citations:** Total AR, breakdown by aging bucket, and the 2-3 largest overdue invoices.

### `WORKING_CAPITAL_GROWTH`

**Trigger:** Cash conversion cycle (DSO + DIO − DPO) has grown > 15 days over the trailing 6 months.

**Severity:**
- 15–30 day growth: **MEDIUM**
- > 30 day growth: **HIGH**

**Citations:** CCC at start vs end of window, decomposed into DSO/DIO/DPO contributions.

## Concentration signals

### `CUSTOMER_CONCENTRATION`

**Trigger:** Largest single customer is > 30% of open AR.

**Severity:**
- 30–50% single customer: **MEDIUM**
- > 50% single customer: **HIGH**

**Citations:** Customer name, their open AR balance, and what % of total AR. Plus their average payment days vs the rest of the book.

### `VENDOR_CONCENTRATION`

**Trigger:** Largest single vendor is > 30% of TTM spend (not open AP — spend).

**Severity:**
- 30–50%: **MEDIUM**
- > 50%: **HIGH**

**Citations:** Vendor name, TTM spend, % of total. Plus the implication (operational dependency on this vendor).

## Coverage / leverage signals

### `DSCR_APPROACHING_COVENANT`

**Trigger:** DSCR is within 0.15x of the covenant minimum (default 1.20x → trigger at 1.35x or below).

**Severity:**
- 1.20x − 1.35x: **MEDIUM**
- ≤ covenant + 0.05x (e.g. ≤ 1.25x against 1.20x covenant): **HIGH**
- Below covenant: **CRITICAL** (out of scope for EWS — this is a breach, not a warning)

**Citations:** Current DSCR, the EBITDA and debt service that compute it, and the trend (compare to DSCR 3 and 6 months ago).

### `LEVERAGE_RISING`

**Trigger:** Leverage (Net Debt / EBITDA) > 3.0x **and** has increased > 0.5x over the trailing 6 months.

**Severity:**
- 3.0–3.5x with rising trend: **MEDIUM**
- > 3.5x with rising trend: **HIGH**

**Citations:** Net debt now vs 6 months ago, EBITDA TTM now vs 6 months ago.

### `INTEREST_BURDEN_GROWING`

**Trigger:** Interest expense as a share of EBITDA has grown > 5 percentage points over the trailing 6 months. (e.g. Interest was 10% of EBITDA, now 18%.)

**Severity:**
- 5–10pp: **MEDIUM**
- > 10pp: **HIGH**

**Citations:** Interest/EBITDA ratio at start vs end of window. If the rate environment changed (e.g. Euribor reset), call it out.

## Liquidity signals

### `CASH_RUNWAY_SHORT`

**Trigger:** Cash + available revolver < 90 days of trailing operating cash burn.

**Severity:**
- 60–90 day runway: **MEDIUM**
- < 60 day runway: **HIGH**

**Citations:** Cash position, revolver headroom, monthly burn.

(Only triggers if monthly operating CF is negative. Positive-CF borrowers don't have a runway problem in this sense.)

### `BANK_BALANCE_VOLATILITY`

**Trigger:** Cash position has swung more than 50% in either direction over the trailing 3 months. Could indicate large transfers, draws on revolver, or unusual operational events.

**Severity:** Always **LOW** — informational, may not be a credit issue.

**Citations:** Cash position at start of window, end, and the single largest cash movement (typically a large transaction in/out).

## Operational / discipline signals

### `VENDOR_DISPUTES_OPEN`

**Trigger:** Any AP_INVOICE has `metadata.status_flag = 'in_dispute'` and is > 30 days old.

**Severity:** **LOW** (informational). Becomes **MEDIUM** if dispute amount > €100k or > 5% of TTM opex.

**Citations:** The disputed invoice number, vendor, amount, and the dispute reason from metadata.

### `BOOKKEEPING_HEALTH`

**Trigger:** Trial balance doesn't tie, OR opening balance contains material plug entries, OR negative inventory balances, OR cash account in a different sign than expected.

**Severity:** Variable. Surface as **LOW** for one issue, **MEDIUM** for multiple.

**Citations:** The specific anomaly (account number, balance, expected sign).

This signal is important even if not strictly credit-risk: bad books = bad numbers in all the other signals. **Always run the bookkeeping checks before relying on the other signals.**

## Composite risk score (for `/borrower-watchlist`)

Sum the severity-weighted points:

| Severity | Points |
|---|---|
| HIGH | 10 |
| MEDIUM | 5 |
| LOW | 1 |

Plus the structural metrics from the watchlist command:

| Metric | Points |
|---|---|
| DSCR < 1.20x | 30 |
| DSCR 1.20–1.40x | 15 |
| Leverage > 3.50x | 25 |
| Leverage 2.50–3.50x | 10 |
| > 30% AR in 60+ buckets | 20 |
| 15–30% AR in 60+ buckets | 10 |
| Top customer > 30% AR | 15 |
| Top customer 20–30% AR | 5 |

A composite score of:
- **> 60** → urgent — recommend full `/credit-read` and a relationship-manager review this week
- **40–60** → watch — `/credit-read` next month
- **< 40** → no action this cycle

The scoring is intentionally simple and deterministic. Sophisticated lenders should replace this with their own credit policy weights once the demo's done.
