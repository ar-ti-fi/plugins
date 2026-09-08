---
name: Reconcile and Close
description: Phase 5 of year-end bookkeeping. Verify trial balance, balance sheet, reconcile bank accounts, close fiscal periods, and hand off to the annual report plugin.
---

# Reconcile and Close the Year

Guide me through the final verification and year-end close:

1. Ask which legal entity and fiscal year
2. Run the trial balance — verify total debits equal total credits
3. Flag any accounts with unusual balances (negative cash, credit expenses, etc.)
4. Run the balance sheet — verify Assets = Liabilities + Equity
5. For each bank account, verify: opening balance + transactions = closing balance
6. Run the income statement and do a sanity check against bank activity
7. If any issues found, help me fix them before proceeding
8. Close all 12 fiscal periods (January through December)
9. Run the annual report handoff checklist
10. Tell me the results and guide me to the annual report plugin

Use the Year-End Bookkeeping skill for the full Phase 5 workflow.


## Card purchases and close controls

Use backend purchase grouping and shared matching; preserve each source movement. Card source confirmation, bill settlement and receipt evidence are separate checks. A successful agent run or a zero unmatched count cannot prove source completeness. Require original opening/closing balances, explicit account interval/provenance and the routed-card movement bridge before close. Never create an adjusting journal merely to erase an unexplained source gap. Missing source evidence on a paid bill belongs on that existing bill. Historical reset/replay requires its own approved dependency manifest and the transaction.delete workflow; it is not implied by implementation or period-close work.
