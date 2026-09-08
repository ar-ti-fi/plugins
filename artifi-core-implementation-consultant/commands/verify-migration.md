---
name: Verify Migration
description: Run the full verification suite to confirm your migration is correct. Checks trial balance, balance sheet, aging reports, bank balances, and fixed asset reconciliation.
---

# Verify Migration

Run comprehensive verification checks on my migration:

1. Ask which legal entity to verify
2. Run trial balance: `generate_report("trial_balance", ...)`
3. Run balance sheet: `generate_report("balance_sheet", ...)`
4. Run income statement for the gap period (if applicable): `generate_report("income_statement", ...)`
5. Run AP aging: `generate_report("ap_aging", ...)`
6. Run AR aging: `generate_report("ar_aging", ...)`
7. Check fixed asset register and reconcile to GL: `generate_report("fa_gl_reconciliation", {...})`
8. For each bank account, compare system balance vs expected
9. Present a verification dashboard:
   - Trial balance: balanced or not
   - Balance sheet: Assets = Liabilities + Equity?
   - Bank balances: match or variance
   - FA reconciliation: clean or variances
   - Master data counts
   - Any warnings or items needing attention

Use the Implementation Consultant skill for the full Phase 5 verification workflow.


### Bank/card purchase replay controls

Preserve provider event rows and their purchase membership. Replaying a charge and refund must not duplicate cash journals, create a second bill, or restart historical receipt reminders. Use the shared purchase identity decision; conflicting references, incomplete FX basis and disputed evidence require finance review. Keep original checking-account opening/closing balances and include explicitly routed card movements in balance and GL coverage checks before closing a period.

A bank/card reset is a separately authorized operation. Prepare scoped source IDs, transaction deletion dependencies, allocations and reclass/variance journals, retained bills/attachments, queued work and a tested restoration procedure before requesting authorization. Use `transaction.delete` with its dependents policy and internal force voucher when permitted; never improvise cascades. Re-link retained evidence through the supported purchase workflow. The August investigation is not general permission to delete another client's data.

Migration acceptance requires exact source coverage, one financial effect per booked movement, AP/subledger agreement, stable replay and one current documentation obligation per purchase. A balanced adjusting journal cannot explain missing provider movements. Keep purchase matching and reminder delivery disabled until the scoped validation and delivery cutoff are approved.
