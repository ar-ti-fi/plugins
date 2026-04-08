---
name: Reconcile Payments
description: Run full payment-to-invoice reconciliation. Starts automated matching, then guides manual matching for complex cases (N:N splits, partial payments, rounding write-offs).
---

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
