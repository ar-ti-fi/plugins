# Dimension Analysis — P&L by Department, Project, Cost Center

Reference guide for the `/dimension-analysis` command.

## What Are Dimensions?

Dimensions are additional classification axes applied to transactions beyond the chart of accounts. They allow analysis of the same P&L data sliced by different business perspectives:

- **Department** — Marketing, Engineering, Sales, Operations, HR
- **Project** — Customer projects, internal initiatives, R&D programs
- **Cost Center** — Functional cost pools, location-based tracking
- **Custom dimensions** — Product line, region, team, or any other classification

## Discovering Available Dimensions

```
# List dimension types configured for this entity
list_entities("dimension_value", {"legal_entity_id": ID})
```

This returns all dimension values grouped by dimension type. Present options to the user and let them choose which dimension to analyze.

## Report Structure: P&L by Dimension

For each dimension value, present a condensed P&L:

```
P&L BY DEPARTMENT — Period: Jan 2026 - Mar 2026
═════════════════════════════════════════════════════════════════════
                    Marketing  Engineering   Sales    Operations  Unallocated   TOTAL
─────────────────────────────────────────────────────────────────────────────────────
Revenue              50,000     —           380,000    20,000       —          450,000
Direct costs        (15,000)  (120,000)    (95,000)  (45,000)      —         (275,000)
─────────────────────────────────────────────────────────────────────────────────────
Gross profit         35,000   (120,000)    285,000   (25,000)      —          175,000
Gross margin %       70.0%      N/A         75.0%      N/A                     38.9%

Operating expenses  (42,000)   (85,000)    (38,000)  (32,000)   (18,000)    (215,000)
─────────────────────────────────────────────────────────────────────────────────────
Contribution        (7,000)   (205,000)    247,000   (57,000)   (18,000)     (40,000)
Margin %            -14.0%      N/A         65.0%      N/A                     -8.9%
═════════════════════════════════════════════════════════════════════════════════════
```

## Key Analysis Points

### 1. Revenue Attribution

Not all dimensions generate revenue. Cost centers like Engineering or HR may only have expenses — this is normal. Revenue-generating dimensions (Sales, Projects) should show positive contribution.

### 2. Direct vs Indirect Costs

- **Direct costs**: Directly attributed to the dimension (materials for a project, salaries of a department)
- **Indirect costs / Overhead**: Shared costs allocated by formula (rent by headcount, IT by usage)
- Present both if allocation data is available, otherwise show only directly attributed costs

### 3. Unallocated Amounts

Transactions without dimension tagging appear in the "Unallocated" column. High unallocated amounts indicate:
- Incomplete dimension tagging on transactions
- Need for allocation rules
- Shared costs not yet distributed

Flag if unallocated > 20% of total — recommend the user improve dimension tagging.

### 4. Profitability Ranking

Rank dimension values by contribution (profit after direct costs):

```
PROFITABILITY RANKING
  1. Sales            247,000  (65.0% margin)
  2. Marketing         (7,000) (-14.0% margin)  ⚠️ Below breakeven
  3. Operations       (57,000) (N/A — cost center)
  4. Engineering     (205,000) (N/A — cost center)
```

### 5. Comparative Analysis

When comparative data is available:

```
                  Current Period    Prior Period    Change      %
Sales              247,000          198,000        +49,000    +24.7%
Marketing           (7,000)          (3,000)       (4,000)   -133.3%  ⚠️
Engineering       (205,000)        (190,000)      (15,000)    -7.9%
```

Flag dimensions with:
- Margin deterioration > 5 percentage points
- Cost growth > revenue growth
- New dimensions (no prior period data)

## Project-Specific Analysis

For project dimensions, additional metrics:

| Metric | Formula | Notes |
|--------|---------|-------|
| Project margin % | (Revenue - Direct costs) / Revenue × 100 | Per-project profitability |
| Budget utilization | Actual costs / Budget × 100 | Over/under budget |
| Revenue per hour | Revenue / Logged hours | If time tracking is available |
| Remaining budget | Budget - Actual costs | Burn rate indicator |

```
# If budget data exists for the dimension
generate_report("variance_summary", {
    "legal_entity_id": ID,
    "start_date": "...",
    "end_date": "...",
    "dimension_type": "project",
    "dimension_value": "PROJECT_CODE"
})
```

## Recommendations by Scenario

| Finding | Recommendation |
|---------|---------------|
| Dimension consistently unprofitable | Review pricing, cost structure, or consider discontinuing |
| High unallocated costs | Improve dimension tagging on transactions |
| One dimension dominates revenue | Concentration risk — explore diversification |
| Cost center costs growing faster than revenue | Investigate efficiency, headcount, vendor contracts |
| Project over budget | Review scope, timeline, resource allocation |
