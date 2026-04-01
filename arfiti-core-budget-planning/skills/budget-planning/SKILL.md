---
name: Budget Planning
description: Builds budgets from scratch, copies forward with adjustments, forecasts from actuals, plans employee costs with burden rates, and creates project budgets. Reads GL data, employees, projects, and existing budgets to calculate amounts and submits via the ERP workflow system.
---

## Trigger

Activate when the user mentions: create budget, build budget, budget planning, annual budget, forecast budget, budget from scratch, copy budget, roll forward budget, employee budget, project budget, headcount planning, what-if budget, budget scenario, operating budget, capital budget, department budget.

## Four Planning Modes

### Mode 1: Build from Scratch
Create a new budget by analyzing prior year GL actuals, applying growth assumptions and seasonal patterns.

### Mode 2: Copy Forward
Clone a prior year budget and apply adjustments (global growth %, per-account overrides, seasonal changes).

### Mode 3: Forecast
Create a mid-year forecast by blending YTD actuals with projected amounts for remaining months.

### Mode 4: Specialized
Employee cost budgeting (fully loaded costs with burden rates) or project budgeting (cost structures with profitability targets).

Ask the user which mode applies. If they mention "forecast" or "revision", use Mode 3. If they mention employees/headcount, use Mode 4 (Employee). If they mention a specific project, use Mode 4 (Project). Default to Mode 1 or 2 depending on whether a prior budget exists.

## Prerequisites

Before starting, confirm with the user:
1. **Legal entity ID** — which entity to budget for
2. **Fiscal year** — which year (e.g., 2026)
3. **Scenario** — budget (baseline), forecast (revised), or stretch (aspirational)
4. **Granularity** — monthly (12 periods), quarterly (4), or annual (1)
5. **Mode** — which of the four modes to use

## Mandatory Checkpoints

You MUST verify each checkpoint before proceeding. If a checkpoint fails, STOP and inform the user.

- **CP1**: Legal entity has an active chart of accounts (`list_entities("account", {"legal_entity_id": <id>})` returns results)
- **CP2**: Prior year data is available (for copy-forward and forecast modes)
- **CP3**: All account numbers used in budget lines exist in `v_accounts_effective` for the entity
- **CP4**: Budget amounts are reasonable — no single line exceeds 50% of total unless the user explicitly confirms
- **CP5**: Revenue vs expense ratio passes sanity check — inform user if expenses exceed revenue by >20%
- **CP6**: User has reviewed and confirmed the preview before submission
- **CP7**: Submission via `bulk_upsert` or `create` succeeds

---

## Workflow Steps — Mode 1: Build from Scratch

### Step 1: Discover Chart of Accounts

Fetch the entity's active accounts to know what to budget:

```python
accounts = list_entities("account", {
    "legal_entity_id": <entity_id>,
    "is_active": true
})
```

Group accounts by type (revenue, expense, asset, liability) to build the budget structure.

### Step 2: Fetch Prior Year Actuals

Get actual GL balances for the prior fiscal year as a baseline:

```python
# Trial balance for prior year
actuals = generate_report("trial_balance", {
    "legal_entity_id": <entity_id>,
    "date_from": "2025-01-01",
    "date_to": "2025-12-31"
})
```

Or for monthly detail:

```python
# Monthly actuals per account
monthly = search("gl_balance", "", {
    "legal_entity_id": <entity_id>,
    "period_name": "2025-01"
})
```

**CP1 checkpoint**: Confirm accounts exist.
**CP2 checkpoint**: Confirm prior year actuals are available. If not, inform the user they need to enter amounts manually.

### Step 3: Determine Growth Assumptions

Ask the user how to adjust from prior year actuals:

- **Global growth rate**: "Apply 5% increase across all accounts"
- **Per-account rates**: "Revenue +10%, Salaries +3%, Rent flat"
- **Seasonal patterns**: "Revenue peaks in Q4 (40% of annual), flat in Q1-Q3"
- **Step changes**: "New hire starts in April — salary expense increases from April onward"

See `references/budget-building-methods.md` for all calculation methods.

### Step 4: Calculate Monthly Amounts

Apply the chosen method to calculate amounts for each account and period. Show the user a clear preview table:

| Account | Jan | Feb | Mar | ... | Dec | Annual Total |
|---------|-----|-----|-----|-----|-----|-------------|
| 4000 Revenue | 45,000 | 45,000 | 45,000 | ... | 60,000 | 555,000 |
| 6000 Salaries | 25,000 | 25,000 | 25,000 | ... | 25,000 | 300,000 |
| 6100 Rent | 5,000 | 5,000 | 5,000 | ... | 5,000 | 60,000 |
| **Total** | | | | | | |

**CP3 checkpoint**: Verify all account numbers exist.
**CP4 checkpoint**: Flag any single line > 50% of total budget.
**CP5 checkpoint**: Compare total revenue vs total expense.

### Step 5: User Confirmation

**CP6 checkpoint**: Show the complete preview and ask: "Shall I create this budget?"

Show summary:
- Total Revenue: $XXX
- Total Expenses: $XXX
- Net Income: $XXX
- Number of lines: XX

Wait for explicit user confirmation.

### Step 6: Create Budget Version

```python
result = submit("budget_version", "create", {
    "legal_entity_id": <entity_id>,
    "version_name": "FY2026 Operating Budget",
    "fiscal_year": 2026,
    "scenario": "budget",
    "version_type": "monthly",
    "currency_code": "EUR",
    "notes": "Built from 2025 actuals with 5% growth"
})
budget_version_id = result["budget_version_id"]
```

### Step 7: Submit Budget Lines

```python
result = submit("budget_line", "bulk_upsert", {
    "budget_version_id": <budget_version_id>,
    "lines": [
        {"account_number": "4000", "period_sequence": 1, "amount": 45000.00, "description": "January Revenue"},
        {"account_number": "4000", "period_sequence": 2, "amount": 45000.00, "description": "February Revenue"},
        // ... all lines
    ]
})
```

See `references/submission-format.md` for the complete payload format.

**CP7 checkpoint**: Verify submission succeeded.

### Step 8: Add Dimensions (Optional)

If the user wants to tag lines by department, project, etc.:

```python
submit("budget_line_dimension", "bulk_set", {
    "budget_line_id": <line_id>,
    "dimensions": [
        {"dimension_type_code": "DEPARTMENT", "dimension_value_code": "SALES"}
    ]
})
```

### Step 9: Next Steps

Inform the user:
1. Budget version is in **draft** status with XX lines
2. They can submit for approval: `submit("budget_workflow", "submit", {"budget_version_id": <id>})`
3. After approval, it can be locked to prevent edits

---

## Workflow Steps — Mode 2: Copy Forward

### Step 1: Find Source Budget

```python
versions = list_entities("budget_version", {
    "legal_entity_id": <entity_id>,
    "fiscal_year": 2025,
    "scenario": "budget",
    "status": "approved"
})
```

If multiple versions exist, show the user the options and ask which to copy.

### Step 2: Create New Version with Copy

```python
result = submit("budget_version", "create", {
    "legal_entity_id": <entity_id>,
    "version_name": "FY2026 Operating Budget",
    "fiscal_year": 2026,
    "scenario": "budget",
    "version_type": "monthly",
    "copy_from_version_id": <source_version_id>,
    "copy_lines": true,
    "notes": "Copied from FY2025 approved budget"
})
```

### Step 3: Determine Adjustments

Ask the user what changes to apply:
- **Global growth %**: "Increase all lines by 5%"
- **Per-account overrides**: "Revenue +10%, keep expenses flat"
- **Remove/add accounts**: "Drop account 6500, add account 6600"
- **Seasonal rebalancing**: "Shift more revenue to Q4"

### Step 4: Calculate Adjusted Amounts

Fetch the copied lines, apply adjustments, and show a comparison:

| Account | 2025 Budget | Adjustment | 2026 Budget | Change |
|---------|-------------|------------|-------------|--------|
| 4000 Revenue | 500,000 | +10% | 550,000 | +50,000 |
| 6000 Salaries | 300,000 | +3% | 309,000 | +9,000 |
| 6100 Rent | 60,000 | Flat | 60,000 | 0 |

**CP3-CP5 checkpoints**: Same as Mode 1.

### Step 5: User Confirmation

**CP6 checkpoint**: Show comparison and ask for confirmation.

### Step 6: Apply Adjustments

Overwrite copied lines with adjusted amounts:

```python
result = submit("budget_line", "bulk_upsert", {
    "budget_version_id": <new_version_id>,
    "lines": [
        // adjusted lines — bulk_upsert matches on account+period and updates
    ]
})
```

**CP7 checkpoint**: Verify submission succeeded.

---

## Workflow Steps — Mode 3: Forecast

### Step 1: Load Approved Budget

```python
budget = list_entities("budget_version", {
    "legal_entity_id": <entity_id>,
    "fiscal_year": 2026,
    "scenario": "budget",
    "status": "approved"
})
```

Also fetch budget lines:
```python
budget_lines = list_entities("budget_line", {
    "budget_version_id": <budget_version_id>
})
```

### Step 2: Load YTD Actuals

Determine which months have passed. For each completed month, fetch actual GL amounts:

```python
actuals = generate_report("trial_balance", {
    "legal_entity_id": <entity_id>,
    "date_from": "2026-01-01",
    "date_to": "2026-06-30"  # Through end of last completed month
})
```

### Step 3: Show YTD Comparison

| Account | Budget YTD | Actual YTD | Variance | Variance % |
|---------|-----------|------------|----------|------------|
| 4000 Revenue | 270,000 | 285,000 | +15,000 | +5.6% |
| 6000 Salaries | 150,000 | 148,000 | -2,000 | -1.3% |

### Step 4: Choose Forecast Method

Ask the user which method to apply for remaining months. See `references/forecasting-methods.md`:

1. **Run Rate** — (YTD Actual / months elapsed) x remaining months
2. **Budget + Trend** — Adjust remaining budget months by YTD variance trend
3. **Seasonal Adjusted** — Apply prior year seasonal pattern to current run rate
4. **Manual Override** — User specifies amounts for remaining months

### Step 5: Calculate Full-Year Forecast

Replace past months with actuals, project remaining months:

| Account | Jan (A) | Feb (A) | ... | Jun (A) | Jul (F) | ... | Dec (F) | Full Year |
|---------|---------|---------|-----|---------|---------|-----|---------|-----------|
| 4000 | 47,500 | 48,000 | ... | 47,000 | 47,500 | ... | 52,000 | 580,000 |

(A) = Actual, (F) = Forecast

### Step 6: User Confirmation

**CP6 checkpoint**: Show full forecast with comparison to original budget.

### Step 7: Create Forecast Version and Submit

```python
# Create forecast version
result = submit("budget_version", "create", {
    "legal_entity_id": <entity_id>,
    "version_name": "FY2026 Q2 Forecast",
    "fiscal_year": 2026,
    "scenario": "forecast",
    "version_type": "monthly",
    "notes": "Q2 forecast: Jan-Jun actuals + Jul-Dec projected (run rate method)"
})

# Submit all lines (actuals + projections)
submit("budget_line", "bulk_upsert", {
    "budget_version_id": <forecast_version_id>,
    "lines": [...]
})
```

---

## Workflow Steps — Mode 4a: Employee Cost Budget

### Step 1: Fetch Active Employees

```python
employees = list_entities("employee", {
    "legal_entity_id": <entity_id>,
    "status": "active"
})
```

Also fetch compensation records if available:
```python
compensation = search("employee_compensation", "", {
    "legal_entity_id": <entity_id>
})
```

### Step 2: Calculate Fully Loaded Cost

For each employee, calculate the full burden. See `references/employee-cost-planning.md` for formulas:

| Employee | Base Salary | Social Tax (33%) | Unemployment (0.8%) | Benefits | Fully Loaded |
|----------|------------|-------------------|---------------------|----------|-------------|
| John Smith | 3,500/mo | 1,155 | 28 | 200 | 4,883/mo |
| Jane Doe | 4,000/mo | 1,320 | 32 | 200 | 5,552/mo |
| TBH (Q3 hire) | 3,800/mo | 1,254 | 30 | 200 | 5,284/mo |

### Step 3: Add Headcount Plans

Ask the user about planned hires/terminations:
- "Any planned hires? When do they start?"
- "Any expected terminations?"

Use TBH (To Be Hired) placeholders for planned positions. Pro-rate partial months.

### Step 4: Preview Employee Budget

Show a summary per department or per employee, with monthly breakdown.

**CP3-CP6 checkpoints**: Validate accounts, check reasonableness, get confirmation.

### Step 5: Submit with Employee Dimensions

```python
submit("budget_line", "bulk_upsert", {
    "budget_version_id": <id>,
    "lines": [
        {
            "account_number": "6000",
            "period_sequence": 1,
            "amount": 3500.00,
            "dimensions": {"employee_id": "67", "department": "ENG"},
            "memo": "John Smith - Base salary"
        },
        {
            "account_number": "6010",
            "period_sequence": 1,
            "amount": 1155.00,
            "dimensions": {"employee_id": "67", "department": "ENG"},
            "memo": "John Smith - Social tax (33%)"
        },
        // ... more lines per employee per period
    ]
})
```

---

## Workflow Steps — Mode 4b: Project Budget

### Step 1: Fetch Active Projects

```python
projects = list_entities("project", {
    "legal_entity_id": <entity_id>,
    "status": "active"
})
```

### Step 2: Determine Cost Structure

For each project, determine the budget categories. See `references/project-budgeting.md`:

- Revenue accounts (if billable): 4100, 4200, 4300
- Expense accounts: 6000 (Labor), 6100 (Infrastructure), 6300 (Contractors), etc.

### Step 3: Calculate Project Budget Lines

For each project and period, calculate revenue and expense amounts:

| Project | Account | Monthly Budget | Annual Total |
|---------|---------|---------------|-------------|
| Website Redesign | 4100 Consulting Revenue | 12,000 | 144,000 |
| Website Redesign | 6000 Employee Time | 8,000 | 96,000 |
| Website Redesign | 6300 Contractors | 3,000 | 36,000 |
| **Gross Profit** | | **1,000** | **12,000** |

### Step 4: Preview with Profitability Summary

Show total revenue, total expense, and gross profit per project.

**CP3-CP6 checkpoints**: Validate, check, confirm.

### Step 5: Submit with Project IDs

```python
submit("budget_line", "bulk_upsert", {
    "budget_version_id": <id>,
    "lines": [
        {
            "account_number": "4100",
            "period_sequence": 1,
            "amount": 12000.00,
            "project_id": 45,
            "memo": "Website Redesign - Consulting revenue"
        },
        // ... more project lines
    ]
})
```

---

## Approval and Locking

After successful line submission (any mode):

```python
# Submit for approval
submit("budget_workflow", "submit", {
    "budget_version_id": <id>,
    "comments": "FY2026 budget ready for CFO review"
})

# Approve (by authorized user)
submit("budget_workflow", "approve", {
    "budget_version_id": <id>,
    "comments": "Approved by CFO"
})

# Lock (prevent further edits)
submit("budget_workflow", "lock", {
    "budget_version_id": <id>
})
```

Tell the user:
- Budget is now locked and visible in variance analysis
- They can view it in the Admin Dashboard under Master Data > Budgets
- Variance reports are available at Reports > Budget vs Actual

---

## Error Handling

- **"Account XXXX not found"**: Check the chart of accounts. Use `search("account", "XXXX")` to find the correct account.
- **"Budget version is locked/archived"**: Cannot modify. Create a new forecast version instead.
- **"Duplicate budget line"**: A line with the same account/period/dimension combination already exists. Use `bulk_upsert` to update it.
- **"No prior year data"**: Build from scratch with manual amounts instead of growth-based.
- **"Period sequence out of range"**: Must be 1-12 for monthly, 1-4 for quarterly, 1 for annual.
- **"Currency mismatch"**: All lines must use the same currency as the budget version.
- **"Version already exists"**: An active budget/forecast/stretch version already exists for this entity/year/scenario. Archive the old one first or create a different scenario.
