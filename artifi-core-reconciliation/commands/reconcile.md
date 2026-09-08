---
name: Reconcile Payments
description: Run full payment-to-invoice reconciliation. Starts automated matching, then guides manual matching for complex cases (N:N splits, partial payments, rounding write-offs).
---

## Card purchase policy

Use the backend purchase workspace and shared matching decision; do not implement a competing card matcher in conversation. Preserve provider rows and show net purchase spend. Reference conflicts and competing candidates require review. A paid/settled item can still lack documentation; attach missing source evidence to the existing bill. Evidence review, waiver and grouping use `card_purchase.manage` with current version, evidence fingerprint and reason. Never infer write-off authority from matching tolerance.

Receipt follow-up belongs to the purchase obligation, with one owner and deduplicated reminder stages. Automation and delivery are report-only until the entity rollout settings are explicitly enabled. Statement coverage and opening/movement/closing balance controls must pass independently of agent match counts. August deletion/replay requires its own reviewed manifest and explicit authorization through transaction.delete; implementation permission does not authorize it.

Legacy payment-pass descriptions below apply to non-card AP/AR behavior. Card rows use the shared purchase policy and cannot use nearest-date refund pairing, fuzzy amount identity or adjusting-journal workarounds.



# Reconcile Payments

Guide me through reconciling payments to invoices:

1. Ask which legal entity and scope (AR, AP, or both)
2. Show current reconciliation state (how many unmatched payments and open invoices)
3. Run the automated reconciliation agent (6-pass matching algorithm)
4. Show what the agent matched and what remains
5. For each party with unmatched payments, analyze and propose manual matches
6. Show match proposals with amounts and explain the logic
7. After I confirm, apply the matches
8. Categorize unresolvable items (missing bills, unknown parties, etc.)
9. Show before/after summary with match rate

Use the Payment Reconciliation skill for the full workflow (Mode 1).
