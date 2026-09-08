---
name: Close Migration
description: Finalize your ERP migration. Runs final verification, presents a migration summary, and advises on next steps for going live with Arfiti.
---

# Close Migration

Finalize my ERP migration and prepare for go-live:

1. Ask which legal entity we're closing migration for
2. Run the full verification suite (Phase 5 checks)
3. If any checks fail, help fix them before proceeding
4. Present a comprehensive migration summary:
   - Migration path used (connector, CSV, greenfield, hybrid)
   - Cutoff date and gap period (if applicable)
   - Master data imported: vendor count, customer count, item count, employee count
   - Opening balance total
   - Gap period transactions posted
   - Total transactions in system
5. Ask the user to confirm migration is complete
6. Update migration state to completed
7. Advise on next steps:
   - Set up bank feeds for automatic reconciliation
   - Configure agent email addresses for bill processing
   - Set up recurring contracts if applicable
   - Schedule first payroll run if needed
   - Plan first month-end close

Use the Implementation Consultant skill for the full close-migration workflow.


### Bank/card purchase replay controls

Preserve provider event rows and their purchase membership. Replaying a charge and refund must not duplicate cash journals, create a second bill, or restart historical receipt reminders. Use the shared purchase identity decision; conflicting references, incomplete FX basis and disputed evidence require finance review. Keep original checking-account opening/closing balances and include explicitly routed card movements in balance and GL coverage checks before closing a period.

A bank/card reset is a separately authorized operation. Prepare scoped source IDs, transaction deletion dependencies, allocations and reclass/variance journals, retained bills/attachments, queued work and a tested restoration procedure before requesting authorization. Use `transaction.delete` with its dependents policy and internal force voucher when permitted; never improvise cascades. Re-link retained evidence through the supported purchase workflow. The August investigation is not general permission to delete another client's data.

Migration acceptance requires exact source coverage, one financial effect per booked movement, AP/subledger agreement, stable replay and one current documentation obligation per purchase. A balanced adjusting journal cannot explain missing provider movements. Keep purchase matching and reminder delivery disabled until the scoped validation and delivery cutoff are approved.
