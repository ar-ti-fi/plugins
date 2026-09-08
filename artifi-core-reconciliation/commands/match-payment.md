---
name: Match Payment
description: Manually match a specific payment to one or more invoices. Supports 1:1, 1:N splits, partial matching, and rounding write-offs.
---

## Card purchase policy

Use the backend purchase workspace and shared matching decision; do not implement a competing card matcher in conversation. Preserve provider rows and show net purchase spend. Reference conflicts and competing candidates require review. A paid/settled item can still lack documentation; attach missing source evidence to the existing bill. Evidence review, waiver and grouping use `card_purchase.manage` with current version, evidence fingerprint and reason. Never infer write-off authority from matching tolerance.

Receipt follow-up belongs to the purchase obligation, with one owner and deduplicated reminder stages. Automation and delivery are report-only until the entity rollout settings are explicitly enabled. Statement coverage and opening/movement/closing balance controls must pass independently of agent match counts. August deletion/replay requires its own reviewed manifest and explicit authorization through transaction.delete; implementation permission does not authorize it.

Legacy payment-pass descriptions below apply to non-card AP/AR behavior. Card rows use the shared purchase policy and cannot use nearest-date refund pairing, fuzzy amount identity or adjusting-journal workarounds.



# Match Payment

Match a payment to invoice(s) directly:

1. Ask which payment to match (transaction ID or search)
2. Show the payment details (amount, date, party)
3. List open invoices for the same party
4. Ask which invoice(s) to apply against and how much
5. Show a preview of the match (amounts, status changes)
6. After I confirm, apply the match
7. Show the result

Use the Payment Reconciliation skill for the full workflow (Mode 2).
