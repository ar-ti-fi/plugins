---
name: Reconciliation Status
description: Check current reconciliation health. Shows matched, unmatched, and partial counts for AP and AR payments with recommendations.
---

## Card purchase policy

Use the backend purchase workspace and shared matching decision; do not implement a competing card matcher in conversation. Preserve provider rows and show net purchase spend. Reference conflicts and competing candidates require review. A paid/settled item can still lack documentation; attach missing source evidence to the existing bill. Evidence review, waiver and grouping use `card_purchase.manage` with current version, evidence fingerprint and reason. Never infer write-off authority from matching tolerance.

Receipt follow-up belongs to the purchase obligation, with one owner and deduplicated reminder stages. Automation and delivery are report-only until the entity rollout settings are explicitly enabled. Statement coverage and opening/movement/closing balance controls must pass independently of agent match counts. August deletion/replay requires its own reviewed manifest and explicit authorization through transaction.delete; implementation permission does not authorize it.

Legacy payment-pass descriptions below apply to non-card AP/AR behavior. Card rows use the shared purchase policy and cannot use nearest-date refund pairing, fuzzy amount identity or adjusting-journal workarounds.



# Reconciliation Status

Show me the current reconciliation health:

1. Ask which legal entity
2. Show payment reconciliation breakdown (matched, partial, unmatched) for AP and AR
3. Show open invoice counts and amounts
4. Show aging of unmatched payments (how old are the oldest unmatched items)
5. Recommend next action (run full reconciliation, investigate specific parties, etc.)

Use the Payment Reconciliation skill for the full workflow (Mode 3).
