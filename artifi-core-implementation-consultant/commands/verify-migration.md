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
7. Check fixed asset register and reconcile to GL: `reconcile_fixed_assets_to_gl(...)`
8. For each bank account, compare system balance vs expected
9. Present a verification dashboard:
   - Trial balance: balanced or not
   - Balance sheet: Assets = Liabilities + Equity?
   - Bank balances: match or variance
   - FA reconciliation: clean or variances
   - Master data counts
   - Any warnings or items needing attention

Use the Implementation Consultant skill for the full Phase 5 verification workflow.
