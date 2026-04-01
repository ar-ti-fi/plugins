# Budget Submission Format Reference

## Create Budget Version

```python
result = submit("budget_version", "create", {
    "legal_entity_id": 12,                         # Required: entity ID
    "version_name": "FY2026 Operating Budget",     # Required: human-readable name
    "fiscal_year": 2026,                           # Required: year (2000-2100)
    "scenario": "budget",                          # Optional: budget (default), forecast, stretch, actual_snapshot
    "version_type": "monthly",                     # Optional: monthly (default), quarterly, annual
    "currency_code": "EUR",                        # Optional: defaults to entity currency
    "template_id": 1,                              # Optional: budget template reference
    "notes": "Built from 2025 actuals + 5% growth", # Optional
    "copy_from_version_id": 5,                     # Optional: clone lines from existing version
    "copy_lines": true                             # Optional: copy all lines when cloning
})

# Returns:
# {
#   "success": true,
#   "budget_version_id": 8,
#   "version_number": "BUD-000008",
#   "status": "draft"
# }
```

### Create Fields

| Field | Required | Description |
|-------|----------|-------------|
| `legal_entity_id` | Yes | Legal entity ID |
| `version_name` | Yes | Budget name (max 100 chars) |
| `fiscal_year` | Yes | Year (2000-2100) |
| `scenario` | No | `budget` (default), `forecast`, `stretch`, `actual_snapshot` |
| `version_type` | No | `monthly` (default), `quarterly`, `annual` |
| `currency_code` | No | ISO currency code, defaults to entity currency |
| `template_id` | No | FK to budget_templates |
| `notes` | No | Description/notes text |
| `copy_from_version_id` | No | Clone lines from this version |
| `copy_lines` | No | If true, copies all lines from source version |

### Constraint
Only ONE active (non-archived) version per `(legal_entity_id, fiscal_year, scenario)`. Archive old versions first if needed.

---

## Submit Budget Lines (Bulk)

The primary way to submit budget lines — handles both insert and update:

```python
result = submit("budget_line", "bulk_upsert", {
    "budget_version_id": 8,
    "lines": [
        {
            "account_number": "4000",
            "period_sequence": 1,
            "amount": 45000.00,
            "description": "January Revenue",
            "memo": "Based on 2025 actual + 10% growth",
            "source": "formula",
            "project_id": null,
            "customer_id": null,
            "vendor_id": null,
            "dimensions": {"department": "SALES", "cost_center": "CC001"}
        },
        {
            "account_number": "4000",
            "period_sequence": 2,
            "amount": 47000.00,
            "description": "February Revenue"
        },
        {
            "account_number": "6000",
            "period_sequence": 1,
            "amount": 25000.00,
            "description": "January Salaries",
            "dimensions": {"department": "ENG"}
        }
    ]
})

# Returns:
# {
#   "success": true,
#   "inserted": 3,
#   "updated": 0,
#   "total": 3
# }
```

### Line Fields

| Field | Required | Description |
|-------|----------|-------------|
| `account_number` | Yes | GL account number (must exist in v_accounts_effective) |
| `period_sequence` | Yes | Period number: 1-12 (monthly), 1-4 (quarterly), 1 (annual) |
| `amount` | Yes | Budget amount (positive for debit-normal, negative for credit-normal) |
| `description` | No | Human-readable line description |
| `memo` | No | Internal notes (calculation basis, assumptions) |
| `source` | No | `manual` (default), `formula`, `import`, `template`, `copy` |
| `currency_code` | No | Defaults to version currency |
| `project_id` | No | First-class project reference (direct column) |
| `customer_id` | No | First-class customer reference |
| `vendor_id` | No | First-class vendor reference |
| `dimensions` | No | Flexible dimensions as JSON: `{"department": "SALES", "cost_center": "CC001"}` |

### Matching Logic (Upsert)
Lines are matched by: `budget_version_id + account_number + period_sequence + project_id + customer_id + vendor_id + dimension_combo_hash`

If a match is found, the line is **updated**. Otherwise, it is **inserted**.

---

## Submit Single Budget Line

For adding individual lines:

```python
result = submit("budget_line", "create", {
    "budget_version_id": 8,
    "account_number": "6500",
    "period_sequence": 4,
    "amount": 5000.00,
    "description": "Q2 Training Budget",
    "dimensions": {"department": "ENG"}
})

# Returns: {"success": true, "budget_line_id": 142}
```

---

## Set Line Dimensions

Add or replace dimension tags on a budget line:

```python
submit("budget_line_dimension", "bulk_set", {
    "budget_line_id": 142,
    "dimensions": [
        {"dimension_type_code": "DEPARTMENT", "dimension_value_code": "SALES"},
        {"dimension_type_code": "COST_CENTER", "dimension_value_code": "CC001"}
    ]
})
```

This **replaces** all existing dimensions on the line.

---

## Status Transitions

```python
# Submit for approval (draft -> submitted)
submit("budget_workflow", "submit", {
    "budget_version_id": 8,
    "comments": "Ready for CFO review"
})

# Approve (submitted -> approved)
submit("budget_workflow", "approve", {
    "budget_version_id": 8,
    "comments": "Approved by CFO"
})

# Reject (submitted -> draft)
submit("budget_workflow", "reject", {
    "budget_version_id": 8,
    "rejection_reason": "Need to revise Q3 projections"  # Required
})

# Lock (approved -> locked)
submit("budget_workflow", "lock", {
    "budget_version_id": 8
})

# Archive (draft/approved/locked -> archived)
submit("budget_workflow", "archive", {
    "budget_version_id": 8
})

# Reopen (submitted/archived -> draft)
submit("budget_workflow", "reopen", {
    "budget_version_id": 8
})
```

### Status Flow
```
draft -> submitted -> approved -> locked -> archived
          |                         |
        draft (if rejected)     archived
```

---

## Validation Rules

1. **Version editable**: Lines can only be created/updated when version status is `draft` or `submitted`
2. **Account exists**: All `account_number` values must exist in `v_accounts_effective` for the entity
3. **Account active**: Accounts must not be deactivated
4. **Period range**: `period_sequence` must be valid for the version's granularity
5. **No duplicates**: Same account + period + dimension combination cannot appear twice
6. **Currency match**: Line currency must match version currency
7. **Dimensions valid**: All dimension types/values must exist and be active for the entity
8. **Unique version**: Only one active version per entity/year/scenario

---

## Common Submission Patterns

### Full Monthly Budget (12 months x N accounts)
Build all lines in a single `bulk_upsert` call. A typical operating budget might have 10-20 accounts x 12 months = 120-240 lines.

### Copy + Adjust
1. `budget_version.create` with `copy_from_version_id` + `copy_lines: true`
2. `budget_line.bulk_upsert` with adjusted amounts (matches existing lines and updates)

### Employee Budget with Dimensions
Each employee gets separate lines tagged with `dimensions: {"employee_id": "67", "department": "ENG"}`. Multiple cost categories per employee (salary, taxes, benefits).

### Project Budget with First-Class IDs
Use `project_id` field (not dimensions) for project budgets — it's a first-class column with FK constraint and fast querying.
