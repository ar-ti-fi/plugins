# Advisory Intelligence — Balance Sheet Analysis Rules

When a user provides their balance sheet or trial balance for opening balance import, scan each account line to detect what additional data is needed. Present findings conversationally, grouped by priority tier.

## Detection Rules

### Tier 1 — Required for Migration

These affect core ERP features. Without this data, subledger features (aging, depreciation, payment scheduling) won't work properly. **Always ask for these.**

#### Accounts Receivable
**Detection:** Account number in 1200-1299 range, OR account name contains: "receivable", "trade debtor", "debtor", "ostjad" (Estonian), "forderungen" (German), "creances" (French)
**Condition:** Balance > 0
**Question:** "I see [AMOUNT] in accounts receivable ([ACCOUNT_NAME]). For aging reports and collections tracking to work, I need the list of unpaid customer invoices that make up this balance. For each invoice, please provide: customer name, invoice number, amount, invoice date, and due date. If you don't have this breakdown, I'll record the total as a lump sum — the GL balance will be correct but aging reports won't show individual invoices."
**Tool:** `open_ar_items` parameter in `manage_imports(action="opening_balances_with_subledger")`

#### Accounts Payable
**Detection:** Account number in 2100-2199 range, OR account name contains: "payable", "trade creditor", "creditor", "tarnijad" (Estonian), "verbindlichkeiten" (German), "fournisseurs" (French)
**Condition:** Balance > 0 (credit side)
**Question:** "I see [AMOUNT] in accounts payable ([ACCOUNT_NAME]). For payment scheduling and vendor aging to work, I need the list of unpaid vendor bills. For each: vendor name, bill number, amount, bill date, and due date."
**Tool:** `open_ap_items` parameter in `manage_imports(action="opening_balances_with_subledger")`

#### Fixed Assets
**Detection:** Account numbers in 1500-1599 (asset cost) WITH corresponding accounts in 1600-1699 (accumulated depreciation), OR account names containing: "fixed asset", "equipment", "machinery", "vehicle", "furniture", "property", "pohivara" (Estonian), "anlagevermoegen" (German)
**Condition:** Cost account balance > 0
**Question:** "I see fixed assets of [COST_AMOUNT] with accumulated depreciation of [DEPR_AMOUNT] (net book value: [NBV]). For the asset register and automatic depreciation to work, I need a list of your assets. For each: description/name, acquisition date, original cost, accumulated depreciation to date, useful life in months, and asset category (equipment, vehicles, furniture, etc.)."
**Tool:** `fixed_assets_detail` parameter in `manage_imports(action="opening_balances_with_subledger")`

### Tier 2 — Recommended

These improve accuracy and enable advanced features. Ask about them, but accept if user doesn't have the details.

#### Long-term Loans / Borrowings
**Detection:** Account number in 2500-2599 range, OR account name contains: "loan", "borrowing", "long-term debt", "mortgage", "laen" (Estonian), "darlehen" (German)
**Condition:** Balance > 0 (credit side)
**Question:** "I see loan balances of [AMOUNT]. Do you have the loan agreements? With the terms (interest rate, repayment schedule, maturity date), I can set up proper repayment tracking and interest accrual. Without them, the balance is still correct but you'll need to manually track repayments."
**Action:** If provided, create loan details as notes or set up recurring journal entries for interest accrual.

#### Prepaid Expenses
**Detection:** Account number in 1300-1399 range, OR account name contains: "prepaid", "prepayment", "advance payment", "ettemaks" (Estonian), "vorauszahlung" (German)
**Condition:** Balance > 0
**Question:** "I see [AMOUNT] in prepaid expenses. What are these for? (Annual insurance, prepaid rent, software licenses, etc.) Knowing the details helps me set up proper amortization — expensing a portion each month — instead of leaving it as a lump sum."
**Action:** If details provided, suggest monthly amortization journal entries.

#### Tax Liabilities
**Detection:** Account number in 2200-2299 range, OR account name contains: "tax payable", "VAT payable", "income tax", "social tax", "maksuvõlg" (Estonian)
**Condition:** Balance > 0 (credit side)
**Question:** "I see [AMOUNT] in tax liabilities. What taxes are outstanding? (VAT, income tax, social tax, payroll taxes?) This is important because it affects your first tax filing period in Arfiti — we need to know what's already been declared vs. what's new."
**Action:** Note tax obligations for first filing period.

#### Short-term Loans / Credit Lines
**Detection:** Account number in 2300-2399 range, OR account name contains: "short-term loan", "credit line", "overdraft", "revolving"
**Condition:** Balance > 0
**Question:** "I see short-term borrowings of [AMOUNT]. Is this a credit line, overdraft, or short-term loan? Knowing the terms helps with cash flow tracking."

### Tier 3 — Suggested

Nice to have. Mention briefly but don't pressure.

#### Investment Accounts
**Detection:** Account number in 1700-1799 range, OR account name contains: "investment", "financial asset", "securities", "shares", "bonds"
**Condition:** Balance > 0
**Question:** "I see [AMOUNT] in investment accounts. If you have documentation (statements, purchase confirmations), I can set up proper tracking. This is optional — the balance is correct either way."

#### Payroll Liabilities
**Detection:** Account number in 2400-2499 range, OR account name contains: "salary payable", "wages payable", "pension liability", "palgavõlg" (Estonian)
**Condition:** Balance > 0
**Question:** "I see [AMOUNT] in payroll liabilities. Are there unpaid salary or pension obligations? This is relevant if you're setting up payroll in Arfiti."

#### Inventory
**Detection:** Account number in 1400-1499 range, OR account name contains: "inventory", "stock", "goods", "varud" (Estonian), "vorraete" (German)
**Condition:** Balance > 0
**Question:** "I see [AMOUNT] in inventory. Do you track inventory by item? If so, we can import your item catalog with quantities and costs for proper inventory management."

#### Multiple Bank Accounts
**Detection:** Multiple accounts in 1000-1099 range with balances > 0
**Condition:** 2+ bank accounts
**Suggestion:** "I see [N] bank accounts. After migration, you might want to set up bank feeds (we support Wise, LHV, Swedbank, SEB, and 3000+ banks via Salt Edge) for automatic transaction import and reconciliation."

#### Revenue Patterns
**Detection:** Multiple revenue accounts (4000-4999 range) with different names suggesting product/service lines
**Condition:** 3+ distinct revenue accounts
**Suggestion:** "You have several revenue streams. Do you use recurring contracts or subscriptions? Arfiti can automate recurring invoicing if you set up contracts."

## Presentation Guidelines

1. **Group by tier** — present Tier 1 first, then Tier 2, then Tier 3
2. **Be conversational** — "Based on your balance sheet, I have a few questions..." not "The following items require attention:"
3. **Explain the tradeoff** — always tell the user what happens WITH and WITHOUT the additional data
4. **Accept "I don't have this"** — provide the fallback path (basic opening balance) gracefully
5. **Don't overwhelm** — if there are many Tier 3 items, mention them briefly: "I also noticed investment accounts and inventory — we can set those up in detail later if needed."
6. **Track what was provided** — note which Tier 1 items got detail data vs. lump sum, so verification (Phase 5) can flag limitations
