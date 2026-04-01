---
name: Financial Reports
description: Prepare and present standard financial reports — Balance Sheet, Profit & Loss, Cash Flow Statement, Trial Balance, Aging Analysis, and Dimension Analysis. Works with any chart of accounts.
---

## Trigger

Activate when the user mentions: balance sheet, profit and loss, P&L, income statement, cash flow, trial balance, financial statements, financial summary, aged receivables, aged payables, aging report, AR aging, AP aging, dimension analysis, department P&L, project profitability, or cost center analysis.

## Prerequisites

Before starting, determine:
1. **Legal entity ID** — which entity to report on
2. **Period / date** — reporting date (balance sheet) or date range (P&L, cash flow)
3. **Comparison** — whether user wants comparative periods (prior year, prior month, budget)

## Core Principle: Dynamic Account Discovery

NEVER hardcode account numbers or names. Every company has a different chart of accounts. Always discover accounts by their properties:

```
list_entities("account", {
    "legal_entity_id": ID,
    "account_type": "asset",       # asset, liability, equity, revenue, expense
    "account_category": "cash",    # cash, receivable, inventory, fixed_asset, payable, etc.
    "is_active": true
})
```

Use `account_type` and `account_category` to classify accounts into report sections. See **references/balance-sheet-classification.md** for the full mapping.

## Available Reports

### 1. Balance Sheet (`/balance-sheet`)

**Tool:** `generate_report("balance_sheet", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})`

**Workflow:**
1. Fetch the balance sheet data
2. Validate: Total Assets MUST equal Total Liabilities + Total Equity
3. If comparative period requested, fetch prior period and compute changes
4. Present in standard classification format (see **references/balance-sheet-classification.md**)
5. Highlight significant changes (>10% movement) with brief commentary
6. Calculate key ratios: current ratio, quick ratio, debt-to-equity

**Checkpoint:** If the balance sheet does not balance, STOP. Investigate:
- Check retained earnings calculation
- Verify current year P&L flows to equity
- Look for suspended/unclassified accounts

### 2. Profit & Loss (`/profit-and-loss`)

**Tool:** `generate_report("income_statement", {"legal_entity_id": ID, "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"})`

**Workflow:**
1. Fetch income statement data
2. If comparative period requested, fetch prior period
3. Present in structured format (see **references/income-statement-structure.md**)
4. Calculate margins: gross margin %, operating margin %, net margin %
5. Highlight line items with significant variance from prior period (>15%)
6. Provide brief analytical commentary on trends

**Checkpoint:** Net profit/loss must agree with the Balance Sheet current year profit line. If it doesn't, check for unposted journal entries or period mismatches.

### 3. Cash Flow Statement (`/cash-flow`)

**Tool:** `generate_report("cash_flow_statement", {"legal_entity_id": ID, "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"})`

**Workflow:**
1. Fetch cash flow data (indirect method)
2. Present in three sections: Operating, Investing, Financing (see **references/cash-flow-indirect-method.md**)
3. Validate: Net change in cash = Closing cash - Opening cash on the balance sheet
4. If validation fails, identify discrepancies (FX differences, reclassifications)
5. Highlight the largest cash inflows and outflows
6. Comment on cash generation quality (operating cash flow vs net income)

**Checkpoint:** Cash reconciliation must tie to the balance sheet. If it doesn't, fetch the trial balance for both dates and compare cash account movements.

### 4. Trial Balance (`/trial-balance`)

**Tool:** `generate_report("trial_balance", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})`

**Workflow:**
1. Fetch the trial balance
2. Verify total debits equal total credits
3. If comparative period requested, fetch prior period and show movements
4. Flag unusual balances:
   - Revenue accounts with debit balances
   - Expense accounts with credit balances
   - Accounts with balances inconsistent with their type
5. Present grouped by account type (assets, liabilities, equity, revenue, expense)

### 5. Financial Summary (`/financial-summary`)

**Workflow** (composite report):
1. Fetch balance sheet, income statement, and cash flow for the period
2. Present an executive summary with:
   - Key P&L metrics (revenue, gross profit, operating profit, net profit)
   - Key balance sheet metrics (total assets, total liabilities, equity)
   - Cash position and change in cash
3. Calculate and present financial ratios (see **references/financial-ratios.md**):
   - Liquidity: current ratio, quick ratio
   - Profitability: gross margin, operating margin, net margin, ROE, ROA
   - Leverage: debt-to-equity, interest coverage
   - Efficiency: receivable days, payable days, inventory days
4. Compare to prior period if available
5. Provide brief analytical narrative

### 6. Aged Receivables (`/aged-receivables`)

**Tool:** `generate_report("ar_aging", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})`

**Workflow:**
1. Fetch AR aging data
2. Present aging buckets: Current, 1-30 days, 31-60 days, 61-90 days, 90+ days
3. Show totals by customer, sorted by largest balance
4. Calculate collection metrics:
   - Days Sales Outstanding (DSO)
   - Percentage overdue (>30 days)
   - Concentration risk (% of AR from top 5 customers)
5. Provide collection priority recommendations (see **references/aging-analysis.md**):
   - **Urgent**: 90+ days, large balances — immediate follow-up
   - **Action needed**: 61-90 days — send formal reminder
   - **Monitor**: 31-60 days — soft follow-up
   - **Current**: No action needed
6. Flag customers with deteriorating payment trends

### 7. Aged Payables (`/aged-payables`)

**Tool:** `generate_report("ap_aging", {"legal_entity_id": ID, "as_of_date": "YYYY-MM-DD"})`

**Workflow:**
1. Fetch AP aging data
2. Present aging buckets: Current, 1-30 days, 31-60 days, 61-90 days, 90+ days
3. Show totals by vendor, sorted by largest balance
4. Calculate payment metrics:
   - Days Payable Outstanding (DPO)
   - Percentage overdue
   - Upcoming payment obligations (next 7, 14, 30 days)
5. Provide payment scheduling suggestions (see **references/aging-analysis.md**):
   - **Overdue**: Pay immediately to avoid relationship damage / late fees
   - **Due soon**: Schedule within payment terms
   - **Early payment**: Identify vendors offering early payment discounts
6. Cross-reference with cash position to assess payment capacity

### 8. Dimension Analysis (`/dimension-analysis`)

**Tool:** `generate_report("dimension_analysis", {"legal_entity_id": ID, "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "dimension_type": "DIMENSION"})`

**Workflow:**
1. Ask the user which dimension to analyze: department, project, cost center, or other custom dimension
2. Discover available dimensions:
   ```
   list_entities("dimension_value", {"legal_entity_id": ID})
   ```
3. Fetch dimension analysis report
4. Present P&L breakdown by dimension value (see **references/dimension-reporting.md**)
5. For each dimension value, show:
   - Revenue, direct costs, gross profit, overhead allocation, net contribution
   - Margin percentages
   - Comparison to prior period or budget if available
6. Rank dimensions by profitability / contribution
7. Identify underperforming dimensions (negative margin or declining trend)
8. If budget data exists, show variance analysis per dimension

## Output Format

All reports should be presented as:
1. **Header**: Report name, entity name, reporting date/period
2. **Data**: Clean markdown tables with proper number formatting (thousands separators, 2 decimal places for currencies)
3. **Validation**: Any checkpoint results (pass/fail)
4. **Analysis**: Brief commentary on significant findings
5. **Ratios/Metrics**: Relevant KPIs for the report type
6. **Recommendations**: Actionable next steps (if applicable)

## Error Handling

- If no data is returned, check that the period has posted transactions
- If accounts are unclassified, list them and ask the user to categorize
- If comparative data is unavailable, proceed with single period and note the limitation
