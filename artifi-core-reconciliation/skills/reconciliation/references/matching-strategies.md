# Matching Strategies Reference

Decision rules for proposing manual matches. Apply strategies in order -- each successive strategy handles more complex cases.

---

## Strategy 1: Exact 1:1 Match

**When:** Payment amount equals one invoice amount exactly (or within 0.01 rounding).

**Logic:**
1. For each unmatched payment, search for an invoice from the same party where `amount_due` equals `abs(payment.amount)`
2. If multiple invoices match, prefer the one closest in date
3. Rounding tolerance: 0.01 (write off automatically, no user confirmation needed)

**Confidence:** Very high. Apply without hesitation.

**Example:**
- Payment: $5,000.00 to Vendor A
- Invoice: $5,000.00 from Vendor A
- Action: Match 1:1, full application

---

## Strategy 2: Partial Match

**When:** Payment amount is less than invoice amount. No combination of invoices matches exactly.

**Logic:**
1. Payment amount < invoice `amount_due`
2. Apply the full payment amount to the invoice
3. Invoice remains open with reduced `amount_due`
4. Payment is fully consumed (`recon_status = 'reconciled'`)

**When to use:**
- Customer made a partial payment (common in B2B)
- Installment payments (first of several)
- Short payment (customer deducted discount, tax, or disputed amount)

**Confidence:** High if the payment amount is a round number or clearly a portion (50%, 25%, etc.). Medium if the amount seems arbitrary -- ask user to confirm.

**Example:**
- Payment: $3,000.00 from Customer B
- Invoice: $5,000.00 to Customer B (no other invoices)
- Action: Apply $3,000 to invoice. Invoice `amount_due` becomes $2,000.

---

## Strategy 3: 1:N Split

**When:** One payment amount equals the sum of multiple invoices from the same party (within rounding tolerance).

**Logic:**
1. For each unmatched payment, find all open invoices for the same party
2. Try combinations of 2, 3, or 4 invoices whose `amount_due` values sum to the payment amount (within tolerance)
3. Start with fewest invoices first (2-invoice combos before 3-invoice combos)
4. Tolerance: 0.05 for exact sums, up to 1.00 with write-off
5. Maximum combination size: 6 invoices (beyond that, it's likely not a real match)

**Combination search approach:**
1. Sort invoices by `amount_due` descending
2. For 2-invoice combos: iterate all pairs
3. For 3-invoice combos: iterate triples (only if no 2-combo found)
4. Stop as soon as a match is found within tolerance

**Confidence:** High if sum matches exactly. Medium if write-off needed. Always show the math to the user.

**Example:**
- Payment: $7,500.00 to Vendor C
- Invoices: $3,000.00 + $4,500.00 = $7,500.00
- Action: Split payment across 2 invoices. Both fully paid.

**Example with rounding:**
- Payment: $7,499.99 to Vendor C
- Invoices: $3,000.00 + $4,500.00 = $7,500.00
- Difference: $0.01
- Action: Split payment, write off $0.01 rounding.

---

## Strategy 4: N:1 Group

**When:** Multiple payments from the same party sum to one invoice amount.

**Logic:**
1. For each open invoice, find all unmatched payments from the same party
2. Try combinations of payments that sum to the invoice `amount_due`
3. Apply each payment to the same invoice (multiple `submit` calls, each for one payment)

**Confidence:** High if amounts sum exactly. Always verify dates are reasonable (payments should be near or after invoice date).

**Example:**
- Payments: $2,000.00 (Jan 15) + $3,000.00 (Feb 1) from Customer D = $5,000.00
- Invoice: $5,000.00 to Customer D
- Action: Apply both payments to the invoice. Invoice fully paid after second application.

---

## Strategy 5: N:N Complex

**When:** Multiple payments map to multiple invoices for the same party. Total payment amount approximately equals total invoice amount.

**Logic:**
1. Sum all unmatched payments for the party
2. Sum all open invoice `amount_due` for the party
3. If totals are within tolerance (max 1.00), this is a valid N:N match
4. Apply payments to invoices in chronological order (oldest invoice first)
5. Each payment fills invoices until exhausted, then moves to next payment

**Application order:**
1. Sort invoices by date ascending (oldest first)
2. Sort payments by date ascending
3. Apply first payment to first invoice:
   - If payment > invoice: fully pay invoice, carry remainder to next invoice
   - If payment < invoice: partially pay invoice, move to next payment
   - If payment = invoice: fully pay both, move to next of each

**Confidence:** Medium. This is the most complex pattern. Always show the full breakdown and ask for confirmation.

**Example:**
- Payments: $14,250.16 (Feb 16) + $1,767.00 (Mar 2) = $16,017.16
- Invoices: $15,903.00 (Feb) + $114.16 (Dec) = $16,017.16
- Difference: $0.00
- Application:
  - PAY1 ($14,250.16) --> INV1 partial ($14,250.16 of $15,903.00)
  - PAY2 ($1,767.00) --> INV1 remainder ($1,652.84) + INV2 full ($114.16) = $1,767.00
- Write-off: $0.00

---

## Strategy 6: Rounding Write-Off

**When:** A match is identified but there's a small difference (less than 1.00).

**Rules:**
| Difference | Action |
|------------|--------|
| <= 0.05 | Write off automatically, mention in notes |
| 0.06 -- 1.00 | Propose write-off, ask user to confirm |
| 1.01 -- 100.00 | Propose write-off, explain clearly, require explicit confirmation |
| > 100.00 | Do NOT write off. Recommend creating an adjusting journal entry instead |

**Write-off direction:**
- Payment > Invoice: DR Rounding Expense / CR AR or AP control
- Payment < Invoice: DR AR or AP control / CR Rounding Income

---

## Cross-Currency Considerations

When payment currency differs from invoice currency:

1. Compare amounts in **functional currency** (the entity's base currency), not document currency
2. FX tolerance: up to 5% difference is acceptable for matching (exchange rates vary)
3. If matched with FX difference:
   - The reconciliation system may auto-post an FX gain/loss journal entry
   - Or flag as `pending_review` for manual variance resolution
4. Always mention the FX difference to the user: "Payment of EUR 450 matches invoice of USD 500 (at current rate, difference is $2.34 FX variance)"

---

## Date Proximity Rules

Payments should be near the invoice date. Use these windows:

| Scenario | Acceptable Window |
|----------|-------------------|
| Normal match | Invoice date to 90 days after |
| Prepayment | Up to 30 days before invoice date |
| Late payment | Up to 180 days after invoice date |
| Suspicious | More than 180 days apart -- flag for review |

---

## Priority Order

When multiple strategies could apply, prefer in this order:
1. Exact 1:1 (highest confidence)
2. 1:N split (clear arithmetic)
3. N:1 group (clear arithmetic)
4. Partial match (leaves invoice open but applies what we have)
5. N:N complex (most complex, needs careful verification)
6. Rounding write-off (add-on to any of the above)
