---
name: Check Progress
description: Check the overall progress of year-end bookkeeping across all 5 phases. Shows what's done, what's next, and any issues.
---

# Check Year-End Bookkeeping Progress

Show me the current status of year-end bookkeeping for my company:

1. Ask which legal entity and fiscal year
2. **Phase 1 — Entity Setup**: Check if accounts exist (`query("account")`), bank accounts created (`query("bank_account")`), posting profiles configured
3. **Phase 2 — Opening Balances**: Check if opening balance entry exists (look for OPENING_ENTRY transactions), verify trial balance at year start
4. **Phase 3 — Bank Statements**: For each bank account and each month, check if transactions exist. Show a grid: months (Jan-Dec) vs banks, with checkmarks for months that have transactions posted
5. **Phase 4 — Source Documents**: Check AP/AR aging for unlinked payments (payments without matching invoices/bills)
6. **Phase 5 — Reconciliation**: Check if trial balance balances, balance sheet balances, and if periods are closed

Present a clear dashboard:
- Phase completion percentages
- Next recommended action
- Any issues or blockers found

Use the Year-End Bookkeeping skill for reference on what each phase requires.


## Card purchases and close controls

Use backend purchase grouping and shared matching; preserve each source movement. Card source confirmation, bill settlement and receipt evidence are separate checks. A successful agent run or a zero unmatched count cannot prove source completeness. Require original opening/closing balances, explicit account interval/provenance and the routed-card movement bridge before close. Never create an adjusting journal merely to erase an unexplained source gap. Missing source evidence on a paid bill belongs on that existing bill. Historical reset/replay requires its own approved dependency manifest and the transaction.delete workflow; it is not implied by implementation or period-close work.
