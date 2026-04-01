# Project Budgeting Reference

## Project Cost Structure

### Typical Revenue Accounts (Billable Projects)
```
4100: Professional Services Revenue
4200: Milestone Revenue
4300: Time & Materials Revenue
```

### Typical Expense Accounts
```
6000: Employee Time (salaries, benefits)
6100: Cloud Hosting / Infrastructure
6200: Depreciation (assigned assets)
6300: Consulting / Contractors
6400: Software Licenses
6500: Travel & Entertainment
```

### Profitability Calculation
```
Project Gross Profit = Revenue - Direct Expenses
Project Net Margin = Gross Profit / Revenue x 100%
```

---

## Budgeting Approaches by Project Type

### Fixed-Price Projects

Revenue is known upfront. Budget expenses to hit target margin.

```
Contract value: 120,000 (recognized over 6 months)
Target margin: 30%
Max expense budget: 120,000 x 0.70 = 84,000

Monthly budget:
  Revenue: 120,000 / 6 = 20,000/month
  Expenses: 84,000 / 6 = 14,000/month
  Gross profit: 6,000/month (30% margin)
```

### Time & Materials Projects

Revenue = billable hours x rate. Budget based on planned resource allocation.

```
Team: 2 consultants at 150/hour
Planned hours: 160/month each (80% utilization)
Monthly revenue: 2 x 160 x 150 = 48,000
Monthly cost: 2 x 5,200 (fully loaded) = 10,400
Monthly margin: 37,600 (78%)
```

### Internal Projects (Non-Billable)

No revenue — budget only expenses. Track to ensure project stays within approved cost envelope.

```
Annual budget cap: 50,000
Monthly burn rate: ~4,200
Expected duration: 12 months
```

---

## Milestone-Based Budgeting

Align budget periods with project milestones instead of even distribution.

**Example: Website Redesign (6-month project)**

| Phase | Months | Revenue | Expenses | Margin |
|-------|--------|---------|----------|--------|
| Discovery | Month 1 | 15,000 | 12,000 | 3,000 |
| Design | Month 2-3 | 30,000 | 22,000 | 8,000 |
| Development | Month 3-5 | 45,000 | 35,000 | 10,000 |
| Testing & Launch | Month 5-6 | 30,000 | 15,000 | 15,000 |
| **Total** | | **120,000** | **84,000** | **36,000** |

Budget lines follow milestone timing, not even monthly distribution.

---

## Multi-Project Portfolio Budget

Budget all active projects in a single budget version using `project_id` to distinguish:

```python
submit("budget_line", "bulk_upsert", {
    "budget_version_id": <id>,
    "lines": [
        # Project A: Website Redesign
        {"account_number": "4100", "period_sequence": 1, "amount": 20000.00,
         "project_id": 45, "memo": "Website Redesign - Revenue"},
        {"account_number": "6000", "period_sequence": 1, "amount": 10000.00,
         "project_id": 45, "memo": "Website Redesign - Labor"},
        {"account_number": "6300", "period_sequence": 1, "amount": 4000.00,
         "project_id": 45, "memo": "Website Redesign - Contractors"},

        # Project B: Mobile App
        {"account_number": "4100", "period_sequence": 1, "amount": 15000.00,
         "project_id": 52, "memo": "Mobile App - Revenue"},
        {"account_number": "6000", "period_sequence": 1, "amount": 8000.00,
         "project_id": 52, "memo": "Mobile App - Labor"},
        {"account_number": "6100", "period_sequence": 1, "amount": 2000.00,
         "project_id": 52, "memo": "Mobile App - Cloud hosting"},

        # ... repeat for all periods
    ]
})
```

### Portfolio Summary View

| Project | Annual Revenue | Annual Expense | Gross Profit | Margin % |
|---------|---------------|---------------|-------------|----------|
| Website Redesign | 120,000 | 84,000 | 36,000 | 30% |
| Mobile App | 180,000 | 120,000 | 60,000 | 33% |
| Internal Tools | — | 50,000 | (50,000) | — |
| **Portfolio Total** | **300,000** | **254,000** | **46,000** | **15%** |

---

## Project + Employee Combined Budget

For detailed resource planning, combine `project_id` and employee dimensions:

```python
# John Smith working on Website Redesign (60% allocation)
{"account_number": "4100", "period_sequence": 1, "amount": 12000.00,
 "project_id": 45, "dimensions": {"employee_id": "67"},
 "memo": "John Smith - Website Redesign billable (60%)"}

# John Smith working on Mobile App (40% allocation)
{"account_number": "4100", "period_sequence": 1, "amount": 8100.00,
 "project_id": 52, "dimensions": {"employee_id": "67"},
 "memo": "John Smith - Mobile App billable (40%)"}
```

This enables:
- **By project**: "How much is the Website Redesign costing us?"
- **By employee**: "What's John Smith's total billable output?"
- **By both**: "How much of John's time goes to each project?"

---

## Variance Analysis for Projects

After budget is approved, track project performance via `v_budget_vs_actual`:

```sql
SELECT
    p.project_number,
    p.project_name,
    bva.account_number,
    bva.account_name,
    SUM(bva.budget_amount) AS budget,
    SUM(bva.actual_amount) AS actual,
    SUM(bva.variance_amount) AS variance
FROM company_63.v_budget_vs_actual bva
JOIN company_63.budget_lines bl ON bl.budget_version_id = bva.budget_version_id
    AND bl.account_number = bva.account_number
    AND bl.period_sequence = bva.period_sequence
JOIN company_63.projects p ON bl.project_id = p.id
WHERE bva.budget_version_id = 8
GROUP BY p.project_number, p.project_name, bva.account_number, bva.account_name
ORDER BY p.project_number, bva.account_number;
```

---

## Best Practices

**DO:**
- Budget all project costs (employee time, contractors, infrastructure, depreciation)
- Include revenue budgets for billable projects
- Update forecasts monthly based on actuals
- Tag all project transactions with `project_id` for accurate variance tracking
- Budget by quarter for long-running projects (>6 months)
- Track profitability per project (revenue - all direct expenses)

**DON'T:**
- Forget indirect costs (depreciation, allocated overhead)
- Budget revenue without expense budget (incomplete profitability picture)
- Mix internal and client-billable projects without clear separation
- Skip variance analysis (defeats the purpose of budgeting)
- Budget at too granular a level for early-stage projects (monthly detail for 2-year project — use quarterly)
