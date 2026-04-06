---
name: Upload Opening Balance
description: Phase 2 of year-end bookkeeping. Import and verify opening balances from the prior year's balance sheet. Skip this for first-year companies.
---

# Upload Opening Balances

Guide me through importing opening balances for my company:

1. Ask which legal entity and fiscal year
2. Ask if this is the company's first year of operations — if yes, skip this step entirely
3. Ask me to provide last year's balance sheet (December 31st closing numbers)
4. Read the data and map each line to an account in our chart of accounts
5. Flag any lines that don't match and ask me to clarify
6. **Detect subledger accounts** in the mapped balances and ALWAYS ask for details when found:
   - **Accounts Receivable** (1200-range accounts, or names containing "receivable", "ostja", "trade debtor"): "I see accounts receivable of EUR X. For aging reports and collections tracking to work properly, I need the list of unpaid customer invoices that make up this balance. For each invoice, please provide: customer name, invoice number, amount, invoice date, and due date. If you don't have this breakdown, I'll record the total as a lump sum — the GL balance will be correct but aging reports won't show individual invoices."
   - **Accounts Payable** (2110-range accounts, or names containing "payable", "tarnija", "trade creditor"): "I see accounts payable of EUR X. For aging reports and payment scheduling to work, I need the list of unpaid vendor bills. For each bill: vendor name, bill number, amount, bill date, and due date."
   - **Fixed Assets** (1500-1599 cost accounts with corresponding 1600-1699 accumulated depreciation): "I see fixed assets of EUR X with accumulated depreciation of EUR Y. For the asset register and automatic depreciation calculations to work, I need a list of your assets. For each asset: description/name, acquisition date, original cost, accumulated depreciation to date, and estimated useful life (in months or years)."
7. Upload: use `manage_imports(action="opening_balances_with_subledger", ...)` when subledger details are provided, or regular `manage_imports(action="opening_balances", ...)` when not
8. Run a trial balance to verify everything balances (debits = credits)
9. Compare line by line with my provided balance sheet to confirm accuracy

Use the Year-End Bookkeeping skill for the full Phase 2 workflow.
