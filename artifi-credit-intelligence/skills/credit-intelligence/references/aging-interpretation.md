# AR/AP aging — the credit-analyst lens

How to read aging output as a credit signal, not just a collections workflow output.

## AR aging shape

A healthy AR aging is **concentrated in the current bucket** with a smooth taper outward. The shape of the taper tells you a lot.

### Headline metrics

For any AR aging report, compute:

- **DSO** (Days Sales Outstanding) = `total_open_AR / revenue_last_90_days × 90`
  - Industry benchmark for B2B SMEs in Italy: 60–75 days
  - Healthy SaaS / consumer: 20–35 days
  - Stressed industrial: 90+ days
- **% in 60+ buckets** = (AR aged 60–90 + 91+) / total open AR
  - Healthy: < 15%
  - Watch: 15–30%
  - Concerning: > 30%
- **Largest single overdue line** as % of total AR
  - If > 10%, name the customer in the output — concentration of bad receivables

### Shape diagnostics

| Shape | Read |
|---|---|
| Most AR in `current` and `1-30`, narrow `31-60`, near-zero `61+` | **Healthy collection rhythm** |
| Steep cliff at one bucket (e.g. lots of stuff at exactly 60-90 days) | **Single large counterparty going slow** — drill into that bucket |
| Long flat tail in `91+` with old aging | **Stale AR** — likely should have been written off or genuinely unrecoverable |
| Recent aging buckets ballooning over time vs. older periods | **DSO drift** — borrower is losing payment cadence (cash strain signal) |

### Top-customer view

Always pull the **top-5 customers by open AR** (not by lifetime revenue). The relevant question for credit risk is: "If our largest receivable goes bad, what's the impact?"

- > 30% single customer share of open AR → **Concentration risk MEDIUM** (or HIGH if also overdue)
- > 50% single customer → **HIGH** regardless of aging
- Top 3 > 60% of AR → **MEDIUM** even if individual concentration is <30%

Cite the actual customer names. The credit team needs them.

## AP aging shape

AP aging tells a different story than AR: it tracks how well **the borrower is paying its own suppliers**. Slow AP isn't always bad (could be deliberate working-capital management), but it has tells.

### Headline metrics

- **DPO** (Days Payable Outstanding) = `total_open_AP / COGS+opex last 90 days × 90`
  - Industry benchmark for Italian SMEs: 30–45 days
  - Stretched / strain: 60+ days
  - Severe strain: 90+ days
- **% in 60+ buckets**
  - Same thresholds as AR
- **In-dispute count** = count of AP invoices with `metadata.status_flag = 'in_dispute'`

### What AP aging tells you

| Pattern | Read |
|---|---|
| DPO stable in 30-45 range, low 60+% | **Borrower paying on time** — healthy supplier relationships |
| DPO rising over 3-6 months | **DPO stretching** — borrower preserving cash. Could be intentional WC management, could be cash strain. Cross-reference with cash position. |
| DPO > 60 with high 60+% | **Strain signal** — borrower paying late, suppliers may put on credit hold |
| In-dispute bills concentrated on one vendor | **Vendor relationship issue** — separate from credit risk but flag it |

### DPO vs DSO together

The single most useful working-capital read is **DSO − DPO** ("net trade days"):

- DSO − DPO < 0: borrower collects from customers BEFORE paying suppliers → financing itself off supplier credit (good)
- DSO − DPO ≈ 0–30 days: balanced
- DSO − DPO > 60 days: borrower needs significant working capital financing
- DSO − DPO trending up: working capital stress building → **flag**

## Inventory aging (DIO)

Less standardized than AR/AP. For manufacturers, DIO matters:

```
DIO = inventory / COGS_last_90_days × 90
```

Build inventory total from all `account_subtype LIKE 'inventory_%'` accounts. Watch for negative balances — they indicate over-consumption (more issued than received), a sign of bookkeeping problems.

## Cash Conversion Cycle (CCC)

```
CCC = DSO + DIO − DPO
```

The full working-capital number. For Italian industrial SMEs, typical CCC is 60–90 days. Above 120 is heavy WC requirement. Below 30 (or negative) is a great cash-flow business.

CCC trending up over 3-6 months → **working-capital deterioration**. Cite it.
