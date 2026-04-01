# Employee Cost Planning Reference

## Fully Loaded Cost Formula

The total cost of an employee includes far more than base salary. A budget that only captures salary understates true cost by 25-40%.

### Cost Categories

```
Direct Costs:
├─ 6000: Base Salary
├─ 6010: Payroll Taxes & Social Contributions
├─ 6020: Bonus / Commission (if applicable)
└─ 6030: Stock Compensation (if applicable)

Indirect Costs:
├─ 6200: Depreciation (laptop, phone, equipment)
├─ 6400: Software Licenses (per-seat tools)
└─ 6500: Travel & Entertainment

Result:
└─ Fully Loaded Cost = Direct + Indirect
```

### Burden Rates by Country

| Country | Social Tax | Unemployment (Employer) | Typical Benefits | Total Burden |
|---------|-----------|------------------------|-----------------|-------------|
| Estonia (EE) | 33% | 0.8% | ~2-5% | ~36-39% |
| United States | ~7.65% (FICA) | ~3-6% (SUTA/FUTA) | ~15-25% (health) | ~25-40% |
| Germany | ~20% | ~1.5% | ~5% | ~26% |
| United Kingdom | ~13.8% (NIC) | — | ~5% | ~19% |

### Estonian Example (Detailed)

For an employee with gross salary of 3,500/month:

| Component | Rate | Monthly Amount |
|-----------|------|---------------|
| Base Salary | — | 3,500.00 |
| Social Tax (employer) | 33% | 1,155.00 |
| Unemployment Insurance (employer) | 0.8% | 28.00 |
| Benefits allowance | ~200 flat | 200.00 |
| **Total Employer Cost** | | **4,883.00** |

Additional indirect costs per employee:
| Component | Monthly Amount |
|-----------|---------------|
| Laptop depreciation | 50-100 |
| Software licenses (avg) | 100-200 |
| Office supplies | 30-50 |
| T&E budget | 200-500 |

**Fully loaded monthly**: ~5,300 - 5,700 (51-63% above base salary)

---

## Budget Line Structure Per Employee

Each employee generates multiple budget lines per month:

```python
# For Employee ID 67 (John Smith), January:
lines = [
    {"account_number": "6000", "period_sequence": 1, "amount": 3500.00,
     "dimensions": {"employee_id": "67", "department": "ENG"},
     "memo": "John Smith - Base salary"},

    {"account_number": "6010", "period_sequence": 1, "amount": 1183.00,
     "dimensions": {"employee_id": "67", "department": "ENG"},
     "memo": "John Smith - Social tax + unemployment (33.8%)"},

    {"account_number": "6200", "period_sequence": 1, "amount": 70.00,
     "dimensions": {"employee_id": "67"},
     "memo": "John Smith - Laptop depreciation"},

    {"account_number": "6400", "period_sequence": 1, "amount": 150.00,
     "dimensions": {"employee_id": "67"},
     "memo": "John Smith - Software licenses (JetBrains, Figma, etc.)"},

    {"account_number": "6500", "period_sequence": 1, "amount": 300.00,
     "dimensions": {"employee_id": "67"},
     "memo": "John Smith - T&E budget"}
]
```

Repeat for each of 12 months. For a team of 10 employees with 5 cost categories each: 10 x 5 x 12 = 600 budget lines. Use `bulk_upsert` for efficiency.

---

## Headcount Planning

### Existing Employees
Fetch active employees and their compensation to calculate budget amounts:

```python
employees = list_entities("employee", {
    "legal_entity_id": <entity_id>,
    "status": "active"
})
```

### Planned Hires (TBH Pattern)

For positions not yet filled, use placeholder identifiers:

```python
{"account_number": "6000", "period_sequence": 4, "amount": 3800.00,
 "dimensions": {"employee_id": "TBH-001", "department": "ENG", "cost_center": "ENG-001"},
 "memo": "Q2 New Hire - Senior Engineer (planned start April)"}
```

**Pro-rating**: If a hire starts mid-month, budget only the partial amount:
```
April hire, starts April 15: budget 50% of monthly cost for April, 100% from May onward
```

**When hired**: Update the budget line dimension from `TBH-001` to the actual employee ID.

### Terminations

If a departure is known, budget only through the expected last month:
```
Employee leaving March 31:
Jan: full cost, Feb: full cost, Mar: full cost
Apr-Dec: 0 (remove lines or set to 0)

If backfill planned:
Apr: 0 (transition gap)
May-Dec: TBH replacement cost
```

---

## Utilization-Based Budgeting (Billable Employees)

For professional services firms, budget both the cost and revenue sides:

### Cost Side
```
Employee monthly cost: 5,200 (fully loaded)
Annual cost: 62,400
```

### Revenue Side
```
Billing rate: 150/hour
Available hours: 168/month (21 days x 8 hours)
Target utilization: 80%
Billable hours: 134/month
Monthly revenue: 134 x 150 = 20,100
Annual revenue: 241,200
```

### Budget Lines (per employee)
```python
# Cost budget
{"account_number": "6000", "period_sequence": 1, "amount": 5200.00,
 "dimensions": {"employee_id": "67"}, "memo": "John Smith - Fully loaded cost"}

# Revenue budget (per project)
{"account_number": "4100", "period_sequence": 1, "amount": 12000.00,
 "project_id": 45, "dimensions": {"employee_id": "67"},
 "memo": "John Smith - Website Redesign (60% allocation)"}

{"account_number": "4100", "period_sequence": 1, "amount": 8100.00,
 "project_id": 52, "dimensions": {"employee_id": "67"},
 "memo": "John Smith - Mobile App (40% allocation)"}
```

### Utilization Tracking
```
Budget utilization: 80%
If actual drops to 70%: 10% revenue shortfall → unfavorable variance
If actual rises to 90%: 10% revenue surplus → favorable variance
```

---

## Team Budget Summary

Present the employee budget as a department summary:

| Employee | Role | Gross Salary | Burden | Indirect | Fully Loaded | Annual |
|----------|------|-------------|--------|----------|-------------|--------|
| John Smith | Sr Engineer | 3,500 | 1,183 | 520 | 5,203 | 62,436 |
| Jane Doe | Engineer | 3,000 | 1,014 | 470 | 4,484 | 53,808 |
| TBH-001 | Sr Engineer | 3,800 | 1,285 | 520 | 5,605 | 50,445* |
| **ENG Total** | | **10,300** | **3,482** | **1,510** | **15,292** | **166,689** |

*TBH-001 starts April (9 months)

---

## Best Practices

**DO:**
- Budget fully loaded costs (salary + all employer taxes + benefits + overhead)
- Include indirect costs (depreciation for assigned assets, per-seat software)
- Track both cost and revenue for billable employees
- Use `employee_id` + `department` dimensions together
- Pro-rate for mid-year hires and terminations
- Budget employee-specific expenses (T&E, training, conference attendance)
- Update budgets when actual hires/terminations happen

**DON'T:**
- Budget only base salary (missing 25-40% of true cost)
- Forget to update budgets for mid-year staffing changes
- Skip employee tagging on expense lines (loses cost allocation capability)
- Budget billable employees without utilization targets
- Mix employee costs across departments without dimension tagging
