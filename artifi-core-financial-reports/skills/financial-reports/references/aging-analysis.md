# Aging Analysis — Receivables & Payables

Reference guide for the `/aged-receivables` and `/aged-payables` commands.

## Standard Aging Buckets

| Bucket | Days Past Due | Severity |
|--------|--------------|----------|
| Current | Not yet due | Normal |
| 1-30 days | 1 to 30 days past due | Monitor |
| 31-60 days | 31 to 60 days past due | Action needed |
| 61-90 days | 61 to 90 days past due | Escalate |
| 90+ days | Over 90 days past due | Urgent |

## AR Aging: Collection Priority Framework

### Priority 1 — Urgent (90+ days overdue)

**Action:** Immediate personal contact, escalation to management, consider collection agency or legal action.

**Indicators:**
- Outstanding > 90 days
- Large balance (top 20% by amount)
- No recent payment activity
- No documented dispute

**Recommended steps:**
1. Verify invoice was received and is not disputed
2. Direct phone call to customer's AP contact
3. Send formal demand letter with payment deadline
4. Escalate internally — involve sales relationship owner
5. If no response within 14 days, evaluate collection agency or write-off

### Priority 2 — Action Needed (61-90 days overdue)

**Action:** Formal written reminder, phone follow-up.

**Recommended steps:**
1. Send second reminder with invoice copies attached
2. Phone call to confirm receipt
3. Request specific payment date commitment
4. Flag in CRM / note customer file

### Priority 3 — Monitor (31-60 days overdue)

**Action:** Automated or soft reminder.

**Recommended steps:**
1. Send friendly payment reminder email
2. Check if invoice is in customer's payment queue
3. Verify no disputes pending

### Priority 4 — Current (not yet due)

**Action:** No immediate action. Monitor for approaching due dates.

## AP Aging: Payment Scheduling Framework

### Overdue Items

**Action:** Pay immediately unless there is a documented dispute.

**Considerations:**
- Late payment may trigger late fees
- Vendor relationship damage
- Credit terms may be revoked
- Supply disruption risk

### Due Within 7 Days

**Action:** Include in next payment run.

### Due Within 30 Days

**Action:** Schedule for standard payment cycle.

**Optimization:**
- Check for early payment discounts (e.g., 2/10 NET 30 — 2% discount if paid in 10 days)
- Calculate annualized return of early payment: `Discount% / (1 - Discount%) × 365 / (Full Terms - Discount Days)`
- Example: 2/10 NET 30 = 2/98 × 365/20 = **37.2% annualized return** — almost always worth taking

### Not Yet Due (>30 days)

**Action:** No immediate action. Monitor cash forecast.

## Key Metrics

### AR Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| DSO (Days Sales Outstanding) | (AR Balance / Annual Revenue) × 365 | < Payment terms average |
| Overdue % | Overdue AR / Total AR × 100 | < 20% |
| Concentration Risk | Top 5 customers AR / Total AR × 100 | < 40% |
| Collection Effectiveness Index | (Beginning AR + Revenue - Ending AR) / (Beginning AR + Revenue) × 100 | > 80% |

### AP Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| DPO (Days Payable Outstanding) | (AP Balance / Annual COGS) × 365 | Within payment terms |
| Overdue % | Overdue AP / Total AP × 100 | < 5% |
| Cash Coverage | Cash Balance / Total AP × 100 | > 100% |
| Upcoming 7-day obligations | Sum of AP due within 7 days | Compare to available cash |

## Presentation Format

### AR Aging Table

```
AGED RECEIVABLES as of YYYY-MM-DD
═══════════════════════════════════════════════════════════════════
Customer          Current   1-30d    31-60d   61-90d    90+d     Total
───────────────────────────────────────────────────────────────────
Acme Corp          5,000    2,500     —        —         —       7,500
Beta Inc           3,200      —      1,800     —         —       5,000
Gamma Ltd            —        —        —      2,100    4,500     6,600
...
───────────────────────────────────────────────────────────────────
TOTAL             45,200   12,800    8,300    4,200    6,500    77,000

DSO: 38 days | Overdue: 41.3% | Top 5 concentration: 62%
```

### Collection Priority Summary

```
COLLECTION PRIORITIES
  🔴 Urgent (90+ days):     3 customers, 6,500 total — immediate action
  🟠 Action needed (61-90): 2 customers, 4,200 total — formal reminder
  🟡 Monitor (31-60):       4 customers, 8,300 total — soft follow-up
  🟢 Current:              15 customers, 58,000 total — no action needed
```

## Trend Analysis

When comparative data is available, highlight:
- **Deteriorating DSO** — collection slowing, investigate causes
- **Growing 90+ bucket** — potential bad debts, review provisioning policy
- **Single customer concentration** — diversification risk
- **Seasonal patterns** — compare same period prior year, not just prior month
