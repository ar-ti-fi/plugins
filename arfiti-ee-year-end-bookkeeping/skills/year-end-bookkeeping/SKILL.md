---
name: Estonian Year-End Bookkeeping
description: Builds a full year's accounting from scratch for an Estonian company (OU/AS). Guides through chart of accounts setup, opening balances, bank statement processing, source document posting, reconciliation, and period close — preparing the entity for annual report filing.
---

## Trigger

Activate when the user mentions: year-end bookkeeping, aasta raamatupidamine, build accounting from scratch, process annual data, annual bookkeeping, set up new client, import client data, uue kliendi seadistamine, year-end close, yearly accounting, full year accounting, raamatupidamine algusest, prepare books for annual report, or when the user wants to go from raw bank statements and documents to a complete set of books for an Estonian entity.

## Before You Start — Gather Information

Ask these questions in plain, friendly language:

1. **Which company are we working on?** Ask for the legal entity ID. If the user doesn't know it, help them find it: `list_entities("legal_entity", {})` and pick the right one.

2. **Which fiscal year?** e.g., 2025. This determines the period we're building accounting for.

3. **Is this the company's first year of operations?**
   - If **yes**: we skip opening balances entirely (Phase 2). The company starts from zero.
   - If **no**: we'll need last year's closing numbers to begin.

4. **What documents do you have available?** Guide the user — they may not know what's needed:
   - "Do you have **bank statements** for the full year? You can download these from your bank's website, usually as a CSV or PDF file." Ask which banks the company uses (LHV, SEB, Swedbank, Wise, other).
   - "Do you have **last year's annual report or balance sheet**?" (Only if not first year)
   - "Do you have a **chart of accounts** from a prior accountant or accounting software like Merit Aktiva?" Explain: "This is the list of account categories your prior accountant used — like 'Bank', 'Revenue', 'Rent expense', etc. If you don't have one, that's fine — we'll set up a standard one."
   - "Do you have any **bills, invoices, loan documents, or investment paperwork**?" These help us record the full picture beyond just bank movements.

5. **Which banks does the company use?** LHV, SEB, Swedbank, Wise, or others. We need a bank account for each.

## Mandatory Checkpoints

You MUST verify each checkpoint before proceeding. If a checkpoint fails, STOP and help the user fix it.

- **CP1**: Chart of accounts imported — must have all 5 account types (asset, liability, equity, revenue, expense)
- **CP2**: Bank accounts created for every bank the company uses
- **CP3**: Posting profiles configured for all transaction types the entity needs
- **CP4**: Opening balance posted — total debits equal total credits *(skip if first-year company)*
- **CP5**: Opening balance matches the user's prior year balance sheet *(skip if first-year company)*
- **CP6**: Bank statement lines for month X all classified and posted *(repeated for each bank, each month)*
- **CP7**: Trial balance at year-end balances (total debits = total credits)
- **CP8**: Balance sheet equation holds: Assets = Liabilities + Equity
- **CP9**: All 12 fiscal periods for the year are closed
- **CP10**: Annual report handoff checklist complete — ready for `/arfiti-ee:prepare-annual-report`

---

## Phase 1 — Entity Setup

*Goal: Set up the accounting structure so we can start recording transactions.*

### Step 1: Set Up Chart of Accounts

Explain to the user: "A chart of accounts is the list of categories where we'll organize all your money movements — things like 'Bank account', 'Revenue', 'Rent expense', 'Loans', etc. Every transaction gets recorded to one of these categories."

**If the user has a chart of accounts** (from Merit Aktiva, e-Financials, or another system):
1. Ask them to paste or upload it
2. Review the accounts — use **references/estonian-coa-mapping.md** to understand Estonian CoA conventions
3. Check if the entity already has template accounts: `list_entities("account", {"legal_entity_id": ENTITY_ID})`
4. If template accounts exist, they need to be removed first before importing the client's CoA
5. Map each account to a standard type: asset, liability, equity, revenue, or expense
6. Import: `manage_imports(action="accounts", records=[...], legal_entity_id=ENTITY_ID)`

**If the user does NOT have a chart of accounts** (common for non-accountants):
1. Use the standard Estonian IFRS template: `manage_imports(action="standard_coa", template="ifrs", legal_entity_id=ENTITY_ID, confirmed=true)`
2. Review with the user — ask about their business type (IT consultancy, e-commerce, freelancer, restaurant, etc.)
3. Add any missing accounts specific to their business (e.g., freelancers may need specific expense categories)
4. See **references/estonian-coa-mapping.md** for guidance on customizing by business type

**Verify**: `list_entities("account", {"legal_entity_id": ENTITY_ID})` — confirm accounts exist for all 5 types: asset, liability, equity, revenue, expense.

**CP1 checkpoint**: All account types present.

### Step 2: Create Bank Accounts

Explain: "Now we need to set up your bank accounts in the system. Each bank account (LHV, Swedbank, Wise, etc.) gets its own record so we can track money movements separately."

1. From the chart of accounts, identify bank/cash accounts (typically accounts in the 1000-1099 range in Estonian CoA, or accounts with 'pank'/'bank' in the name)
2. For each bank the user mentioned in prerequisites, ask:
   - Bank name (LHV, SEB, Swedbank, Wise, etc.)
   - IBAN (e.g., EE38 2200 2210 1234 5678)
   - Currency — confirm EUR (standard for Estonia)
3. Create each: `submit('bank_account', 'create', {"legal_entity_id": ENTITY_ID, "bank_name": "...", "account_number": "IBAN", "currency": "EUR", "gl_account_id": ACCOUNT_ID})`
4. If the company has payment card accounts (Wise card, Revolut, etc.), create those too

**CP2 checkpoint**: Bank account exists for every bank the user identified.

### Step 3: Configure Posting Profiles

Explain: "Posting profiles tell the system which accounts to use when recording different types of transactions — like which account for bank fees, which for supplier payments, etc. We'll set these up so everything gets recorded correctly."

1. Determine which transaction types the entity will use, based on the user's business:
   - **All companies**: AP_PAYMENT (paying suppliers), AR_PAYMENT (receiving from customers), BANK_FEE, BANK_INTEREST, BANK_TRANSFER
   - **If they have suppliers/bills**: AP_INVOICE
   - **If they sell goods/services**: AR_INVOICE
   - **If they have loans**: LOAN_DISBURSEMENT, LOAN_REPAYMENT
   - **If they pay dividends**: OWNER_DISTRIBUTION
   - **If there was a capital injection**: CAPITAL_CONTRIBUTION
2. Use **references/posting-profiles-setup.md** to assign the correct GL accounts from the imported CoA
3. Check existing profiles and update where needed

**CP3 checkpoint**: Posting profiles configured for all needed transaction types.

### Step 4: Setup Summary

Present a clear summary:
- "Here's what we've set up:"
- Accounts: X total (Y asset, Z liability, etc.)
- Bank accounts: list each with IBAN
- Posting profiles: list each configured type
- Ask user to confirm everything looks correct before moving on

---

## Phase 2 — Opening Balances

*Goal: Record where the company stood financially at the start of the year. Skip this phase entirely if this is the company's first year of operations.*

### Step 5: Upload Opening Balances

Explain: "Opening balances are the starting point — they tell us how much was in each account on January 1st of the fiscal year. We get this from last year's closing numbers (the balance sheet from December 31st of the prior year)."

1. Ask the user to provide the prior year balance sheet (as of 31.12.YYYY-1) — they can paste it, upload a PDF, or type the numbers
2. Read the document and extract each line item with its balance
3. Map each line to an account in the imported CoA
4. If any lines don't match: flag them and ask the user to clarify which account they belong to
5. Upload: `manage_imports(action="opening_balances", legal_entity_id=ENTITY_ID, balances=[{"account_number": "1000", "debit": 50000, "credit": 0}, ...], fiscal_period_name="YYYY-01", balancing_account_number="3300")`
   - Explain: "The balancing account (3300 = Retained Earnings) absorbs any small rounding differences to keep the books balanced."
6. See **references/opening-balance-guide.md** for common pitfalls

**CP4 checkpoint**: Trial balance from `generate_report("trial_balance", {"legal_entity_id": ENTITY_ID, "as_of_date": "YYYY-01-01"})` shows total debits = total credits.

### Step 6: Verify Opening Balance

1. Run the trial balance: `generate_report("trial_balance", {"legal_entity_id": ENTITY_ID, "as_of_date": "YYYY-01-01"})`
2. Compare each line with the user's prior year balance sheet
3. Flag any discrepancies — ask user to verify
4. Common issues:
   - Retained earnings may differ because it includes prior year net income — this is expected
   - Rounding differences of a few cents are normal (the balancing account handles this)

**CP5 checkpoint**: Opening balance matches the user-provided prior year balance sheet (within rounding tolerance).

---

## Phase 3 — Bank Statement Processing

*Goal: Record every bank transaction for the year. This is the biggest phase — it turns raw bank data into properly categorized accounting entries.*

**This phase runs as a loop: for each bank account, for each month (or the full year at once if the user provides it).**

### Step 7: Read Bank Statement Data

Explain: "Now we'll go through your bank statements and record every transaction. I'll read the data, figure out who each payment was to or from, and categorize it. You just need to review and confirm."

1. Ask the user to paste or upload bank statement data — CSV is easiest, but PDF works too
2. Parse the data directly: extract for each line:
   - Date
   - Amount (positive = money in, negative = money out)
   - Counterparty name (who the money went to or came from)
   - Counterparty IBAN (if available)
   - Description / payment reference
3. If the user provides a full year of data, split it into monthly chunks for manageable processing
4. Present a summary:
   - "I found **X transactions** from **January to December 2025**"
   - "Total money in: EUR X | Total money out: EUR Y"
   - "I'll process these month by month so we can review as we go."

### Step 8: Extract and Create Master Data

Explain: "Before we can record these transactions, I need to set up the people and companies you've been paying or receiving money from. I'll identify them from your bank statements."

1. Extract unique counterparty names from the bank statement
2. Classify each:
   - Money going OUT to this counterparty → likely a **vendor** (supplier)
   - Money coming IN from this counterparty → likely a **customer**
   - Exceptions: tax refunds (EMTA inflow = still a vendor), loan disbursements, transfers between own accounts
3. Check which already exist: `search("vendor", "counterparty_name")`, `search("customer", "counterparty_name")`
4. Present a list of NEW counterparties to the user:
   - "I found these new suppliers/vendors that aren't in the system yet:"
   - Table: Name | Type (Vendor/Customer) | Appears X times | Total amount
   - "Please review — are these correct? Should any names be merged or corrected?"
5. After user confirms, create them:
   - Bulk vendors: `manage_imports(action="vendors", records=[{"vendor_name": "...", "country": "EE"}], legal_entity_id=ENTITY_ID)`
   - Bulk customers: `manage_imports(action="customers", records=[{"customer_name": "...", "country": "EE"}], legal_entity_id=ENTITY_ID)`

### Step 9: Classify Bank Lines

Explain: "Now I'll categorize each bank transaction by its type. For example: paying a supplier is an 'AP Payment', receiving money from a customer is an 'AR Payment', a bank fee is a 'Bank Fee', etc."

Apply the classification rules from **references/bank-statement-classification.md**:

| Pattern | Transaction Type | Explanation |
|---------|-----------------|-------------|
| Outflow to known vendor | AP_PAYMENT | Paying a supplier |
| Inflow from known customer | AR_PAYMENT | Receiving payment from a customer |
| Fee keywords: teenustasu, tasu, commission | BANK_FEE | Bank service charge |
| Interest: intress, interest | BANK_INTEREST | Interest earned or paid |
| Transfer between own accounts | BANK_TRANSFER | Moving money between your own accounts |
| EMTA / Maksu- ja Tolliamet | JOURNAL_ENTRY | Tax payment (income tax, social tax, VAT) |
| Loan: laen, loan | LOAN_DISBURSEMENT or LOAN_REPAYMENT | Loan received or repaid |
| Dividend: dividend, kasumijaotus | OWNER_DISTRIBUTION | Profit distribution to owners |
| Capital: osakapital, sissemakse | CAPITAL_CONTRIBUTION | Owner investing money into company |
| Pension: pensionikeskus, II sammas | JOURNAL_ENTRY | Pension fund contribution |

Present the classification table to the user:
- "Here's how I've categorized this month's transactions. Please review:"
- Table: Date | Amount | Counterparty | Description | → Type | → Vendor/Customer
- "If any classification is wrong, let me know and I'll fix it."

**User confirmation is required before posting.**

### Step 10: Post Bank Transactions

1. After user confirms the classifications, post each line:
   ```
   submit('transaction', 'post', {
     "transaction_type_code": "AP_PAYMENT",
     "legal_entity_id": ENTITY_ID,
     "vendor_id": VENDOR_ID,
     "transaction_date": "2025-01-15",
     "bank_account_id": BANK_ACCOUNT_ID,
     "lines": [{"account_id": ACCOUNT_ID, "amount": 150.00, "description": "Payment to Vendor X"}]
   })
   ```
2. Post in chronological order within each month
3. For each transaction, use the correct `transaction_type_code` as classified in Step 9
4. See **references/transaction-type-reference.md** for the exact payload format for each type
5. Track and report results:
   - "Month complete: **X transactions posted successfully**, Y failed"
   - If any failed, show the error and help fix it

**CP6 checkpoint**: All lines for this month posted successfully.

**Repeat Steps 7-10 for each month and each bank account.** After processing all months for all banks, present a total summary:
- "All bank statements processed!"
- Total transactions posted per bank, per month
- Total inflows and outflows match bank statement totals

---

## Phase 4 — Source Documents and Special Transactions

*Goal: Fill in the gaps — post bills, invoices, and other documents that aren't captured by bank statements alone.*

### Step 11: Identify Gaps

Explain: "Bank statements show the money moving, but sometimes we need the original bills or invoices for proper bookkeeping. Let me check what might be missing."

1. Check for payments without matching source documents:
   - AP payments without bills: `generate_report("ap_aging", {"legal_entity_id": ENTITY_ID, "as_of_date": "YYYY-12-31"})`
   - AR payments without invoices: `generate_report("ar_aging", {"legal_entity_id": ENTITY_ID, "as_of_date": "YYYY-12-31"})`
2. Also look for:
   - Large or unusual transactions that may need supporting docs
   - Recurring payments that might represent subscriptions needing separate bills
3. Present the gap list:
   - "I found **X payments** that don't have matching bills/invoices. Here they are:"
   - Table: Date | Vendor/Customer | Amount | Type | What's needed
   - "For each of these, do you have the original bill or invoice? If not, we can create one based on the payment details."

### Step 12: Request and Post Missing Documents

For each gap identified:

1. Ask the user if they have the source document (bill PDF, invoice, contract)
2. **If they have it**: read the document, extract vendor/customer, amounts, dates, line items, tax
3. **If they don't have it**: create a simplified bill/invoice based on the payment details (amount, date, counterparty)
4. Post the document:
   - Bills: `submit('transaction', 'post', {"transaction_type_code": "AP_INVOICE", "legal_entity_id": ENTITY_ID, "vendor_id": VENDOR_ID, "lines": [...]})`
   - Invoices: `submit('transaction', 'post', {"transaction_type_code": "AR_INVOICE", "legal_entity_id": ENTITY_ID, "customer_id": CUSTOMER_ID, "lines": [...]})`

**Handle special transaction categories:**

- **Loans**: Ask for loan agreement. Calculate interest vs principal split. Post LOAN_DISBURSEMENT for money received, LOAN_REPAYMENT for each installment. If there's an amortization schedule, use it to split principal and interest correctly.
- **Investments / shares**: Ask for share purchase/sale documents. Post as JOURNAL_ENTRY with appropriate accounts (financial investments, gains/losses).
- **Fixed assets**: If the company bought equipment, vehicles, etc. — ask for purchase documents. Create fixed asset records or post JOURNAL_ENTRY to the correct asset account. See if depreciation needs to be calculated.
- **Intercompany / related party**: Transactions with related companies or owners. Ensure they're classified correctly for annual report notes.

### Step 13: Year-End Adjustments

Explain: "Now let's make any final adjustments needed to make the accounts accurate as of year-end."

Common adjustments for Estonian companies:

1. **Accruals**: Expenses incurred but not yet billed (e.g., December rent billed in January)
2. **Prepayments**: Payments made for future periods (e.g., annual insurance paid in advance)
3. **Depreciation**: If the company has fixed assets, calculate and record yearly depreciation
4. **Provisions**: Any known future obligations (e.g., warranty claims, legal disputes)
5. **Tax adjustments**: Estonian CIT is only on distributed profits (20/80 rate), so typically minimal. Check if any dividends were paid during the year.

All adjustments posted via: `submit('transaction', 'post', {"transaction_type_code": "JOURNAL_ENTRY", "legal_entity_id": ENTITY_ID, ...})`

---

## Phase 5 — Reconciliation and Close

*Goal: Verify everything balances, close the year, and hand off to the annual report plugin.*

### Step 14: Trial Balance Verification

Explain: "Let's check that all your accounting entries are balanced — every debit must have an equal credit. This is the fundamental rule of bookkeeping."

1. `generate_report("trial_balance", {"legal_entity_id": ENTITY_ID, "as_of_date": "YYYY-12-31"})`
2. **CP7 checkpoint**: Total debits = total credits
3. Flag any accounts with unexpected balances:
   - Negative cash balances (shouldn't happen unless there's a timing issue)
   - Expense accounts with credit balances (unusual)
   - Revenue accounts with debit balances (unusual)
4. If anything looks wrong, investigate and fix before proceeding

### Step 15: Balance Sheet Verification

1. `generate_report("balance_sheet", {"legal_entity_id": ENTITY_ID, "as_of_date": "YYYY-12-31"})`
2. **CP8 checkpoint**: Assets = Liabilities + Equity
3. Verify bank account balances match the closing balances from bank statements
4. If the balance sheet doesn't balance, check:
   - Were all opening balances entered correctly?
   - Are there any unposted or failed transactions?
   - Were journal entries balanced (equal debits and credits)?

### Step 16: Completeness Check

Run these sanity checks:

1. **Bank reconciliation**: For each bank account:
   - Opening balance (from Phase 2) + all posted transactions = closing balance on bank statement
   - If there's a difference, there are missing or extra transactions
2. **Income statement review**: `generate_report("income_statement", {"legal_entity_id": ENTITY_ID, "start_date": "YYYY-01-01", "end_date": "YYYY-12-31"})`
   - Does the revenue make sense given the bank inflows?
   - Do the expenses make sense given the bank outflows?
3. **Retained earnings check**: Opening retained earnings + net income for the year - dividends paid = closing retained earnings

Present a summary: "Everything checks out!" or "I found some discrepancies we need to resolve."

### Step 17: Period Close and Annual Report Handoff

1. Close all 12 fiscal periods in order (January through December)
2. **CP9 checkpoint**: `list_entities("fiscal_period", {"legal_entity_id": ENTITY_ID})` — all 12 periods status "closed"
3. Run the annual report handoff checklist from **references/annual-report-handoff.md**:
   - All periods closed
   - Trial balance balances
   - Balance sheet balances
   - Prior year comparatives available (for existing companies)
   - Bank accounts reconciled
4. **CP10 checkpoint**: All checklist items pass

Present the final message:
- "Your bookkeeping for fiscal year YYYY is complete!"
- "All 12 months are closed, your books balance, and the entity is ready for annual report preparation."
- "To generate the annual report and XBRL files for filing at ariregister.rik.ee, run: `/arfiti-ee:prepare-annual-report`"
- If they also need VAT declarations: "For VAT declarations, use: `/arfiti-ee-vat:prepare-vat-declaration`"

---

## Error Handling

Common issues and how to resolve them:

| Error | Cause | Resolution |
|-------|-------|------------|
| "Account not found" | CoA import missed an account | Create the missing account, then retry |
| "Vendor not found" | Counterparty wasn't created in Step 8 | Create the vendor/customer, then retry the transaction |
| "Period is closed" | Trying to post to an already-closed period | Reopen the period, post, then re-close |
| "Debits don't equal credits" | Unbalanced journal entry | Check the entry — every debit must have an equal credit |
| "Duplicate transaction" | Same transaction posted twice | Check transaction list, delete the duplicate |
| Opening balance doesn't match | Mapping error during import | Review account mapping, correct and re-import |

## Output Format

At each phase completion, present a clear status table showing:
- What was accomplished
- Key numbers (transaction counts, totals)
- Next steps
- Any issues that need attention
