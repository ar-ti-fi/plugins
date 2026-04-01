---
name: Cost Allocation
description: Allocates costs across departments, projects, or dimensions. Supports two modes — standalone (from GL balances) and document-linked (from a specific transaction like an AP invoice). Reads data, calculates target splits using any method (fixed %, proportional, by headcount, custom formula), and submits allocation runs to the ERP with full validation.
---

## Trigger

Activate when the user mentions: allocate costs, cost allocation, distribute overhead, allocation run, split costs, allocate expenses, department allocation, intercompany allocation, revenue allocation, allocate from bill, allocate from invoice, distribute invoice costs.

## Two Allocation Modes

### Mode 1: Standalone Allocation
Allocate from GL account balances (e.g., "Allocate IT overhead across departments").
No source document — you read GL balances and split them.

### Mode 2: Document-Linked Allocation
Allocate from a specific transaction (e.g., "Allocate this Slack invoice across teams").
Links to a source document — the system validates accounts and prevents double-allocation.

Ask the user which mode applies. If they mention a specific bill, invoice, or transaction, use Mode 2.

## Prerequisites

Before starting, confirm with the user:
1. **Legal entity ID** — which entity to run allocation for
2. **Mode** — standalone or from a specific document
3. For standalone: **Source account(s)** — which account(s) to allocate from
4. For document-linked: **Source transaction** — which bill/invoice/JE to allocate from
5. **Period** — which period to allocate (e.g., "2026-03")

## Mandatory Checkpoints

You MUST verify each checkpoint before proceeding. If a checkpoint fails, STOP and inform the user.

- **CP1**: Source data exists (account has balance OR source transaction has allocatable lines)
- **CP2**: Target accounts exist and are active
- **CP3**: Total debits equal total credits (balanced)
- **CP4**: At least one source line and one target line
- **CP5**: For document-linked: source line accounts match the source transaction
- **CP6**: For document-linked: account is not already fully allocated
- **CP7**: User has reviewed and confirmed the preview
- **CP8**: Submission via `submit_lines` succeeds

## Workflow Steps — Standalone Mode

### Step 1: Identify Source Costs

Fetch the balance of the source account(s) for the allocation period:

```python
# Get account balance
balances = search("gl_balance", "", {
    "legal_entity_id": <entity_id>,
    "account_number": "<source_account>",
    "period_name": "<period>"
})
```

Or use `generate_report` for a trial balance if allocating across multiple accounts.

**CP1 checkpoint**: Confirm source account has a non-zero balance to allocate.

### Step 2: Determine Allocation Method

Ask the user which method to use. Common methods (see references/allocation-methods.md):

1. **Fixed percentage** — "Split IT costs 60/40 between Sales and Marketing"
2. **By headcount** — "Allocate based on employee count per department"
3. **By revenue** — "Allocate proportional to each department's revenue"
4. **Custom formula** — "Allocate first $10K equally, remainder by revenue"

For data-driven methods, fetch the relevant data:

```python
# Example: headcount by department
employees = search("employee", "", {
    "legal_entity_id": <entity_id>,
    "status": "active"
})
```

### Step 3: Calculate Target Splits

Apply the chosen method to calculate how much goes to each target. Show the user a clear preview table:

| Line | Type | Account | Dept | DR/CR | Amount |
|------|------|---------|------|-------|--------|
| 1 | Source | 6900 IT Overhead | IT | CR | 10,000.00 |
| 2 | Target | 6900 IT Overhead | SALES | DR | 6,000.00 |
| 3 | Target | 6900 IT Overhead | MARKETING | DR | 2,500.00 |
| 4 | Target | 6900 IT Overhead | FINANCE | DR | 1,500.00 |
| | | | **Total** | | **DR 10,000 = CR 10,000** |

**CP2 checkpoint**: Verify all target accounts exist in the chart of accounts.
**CP3 checkpoint**: Verify total debits = total credits.
**CP4 checkpoint**: Verify at least one source and one target line.

### Step 4: User Confirmation

**CP7 checkpoint**: Show the preview and ask: "Shall I submit this allocation?"

Wait for explicit user confirmation before proceeding.

### Step 5: Create and Submit

```python
# Create the run
result = submit("allocation_run", "create", {
    "legal_entity_id": <entity_id>,
    "run_date": "<today>",
    "period_name": "<period>",
    "description": "<user description or auto-generated>",
    "allocation_type": "cost_allocation",
    "source_plugin": "artifi-core-cost-allocation"
})
allocation_run_id = result["allocation_run_id"]

# Submit lines
result = submit("allocation_run", "submit_lines", {
    "allocation_run_id": allocation_run_id,
    "lines": [ ... ]  # See references/submission-format.md
})
```

**CP8 checkpoint**: Verify submission succeeded (status = "calculated").

### Step 6: Next Steps

Inform the user the run is in **calculated** status and ask if they want to approve and post now.

---

## Workflow Steps — Document-Linked Mode

### Step 1: Identify Source Transaction

Find the source transaction. The user may provide a transaction number, or you can search:

```python
# Search for the transaction
results = search("transaction", "<transaction_number or description>", {
    "legal_entity_id": <entity_id>
})
```

Then fetch the transaction details to see its GL lines:

```python
tx = get_entity("transaction", <transaction_id>)
```

**CP1 checkpoint**: Confirm the source transaction exists and has allocatable lines. Show the user the transaction lines:

| Account | Description | Amount |
|---------|-------------|--------|
| 60002 Bürookulud | Slack subscription | 120.00 |
| 2000 Accounts Payable | AP control | 120.00 |

Identify the **expense/revenue lines** (not control accounts like AP/AR) — those are what can be allocated.

### Step 2: Check Existing Allocations

Check if this transaction (or specific accounts from it) has already been allocated:

```python
# Search for existing allocation runs from this source
results = search("allocation_run", "", {
    "source_transaction_id": <tx_id>
})
```

**CP6 checkpoint**: If any active (non-voided) allocations exist for the same account, inform the user of the remaining allocatable balance. If fully allocated, the user must void the existing allocation first.

### Step 3: Determine Which Line(s) to Allocate

If the source transaction has multiple expense lines, ask the user which to allocate:
- "Allocate all expense lines" — create one allocation per account, or one run with multiple source lines
- "Allocate only account 60002" — allocate just that line

**CRITICAL**: The source line `account_number` in the allocation MUST match the `gl_account_number` from the source transaction. The backend validates this.

### Step 4: Determine Allocation Method

Same as standalone mode — ask how to split (fixed %, headcount, etc.)

### Step 5: Calculate Target Splits

Show a preview table using the **correct account from the source transaction**:

| Line | Type | Account | Dept | DR/CR | Amount |
|------|------|---------|------|-------|--------|
| 1 | Source | 60002 Bürookulud | — | CR | 120.00 |
| 2 | Target | 60002 Bürookulud | ENGINEERING | DR | 60.00 |
| 3 | Target | 60002 Bürookulud | PRODUCT | DR | 36.00 |
| 4 | Target | 60002 Bürookulud | SALES | DR | 24.00 |
| | | | **Total** | | **DR 120 = CR 120** |

**CP2**: All accounts exist and are active.
**CP3**: Balanced (DR = CR).
**CP4**: Has source and target lines.
**CP5**: Source line account (60002) matches the source transaction's GL lines.

### Step 6: User Confirmation

**CP7 checkpoint**: Show the preview including the source document reference.

"This will allocate 120.00 from EE-BILL000527 (account 60002) across 3 departments. Shall I submit?"

### Step 7: Create and Submit

```python
# Create the run WITH source_transaction_id
result = submit("allocation_run", "create", {
    "legal_entity_id": <entity_id>,
    "run_date": "<today>",
    "period_name": "<period>",
    "description": "Allocate Slack costs from EE-BILL000527 across teams",
    "allocation_type": "cost_allocation",
    "source_transaction_id": <source_tx_id>,  # KEY: links to source document
    "source_plugin": "artifi-core-cost-allocation"
})
allocation_run_id = result["allocation_run_id"]
# Returns: source_transaction_number for confirmation

# Submit lines with correct source account
result = submit("allocation_run", "submit_lines", {
    "allocation_run_id": allocation_run_id,
    "lines": [
        {
            "line_type": "source",
            "account_number": "60002",  # MUST match source transaction
            "amount": "120.00",
            "debit_credit": "CR",
            "description": "Slack Business+ - source"
        },
        {
            "line_type": "target",
            "account_number": "60002",
            "amount": "60.00",
            "debit_credit": "DR",
            "description": "Slack to Engineering (50%)",
            "dimension_1_code": "DEPT",
            "dimension_1_value": "ENGINEERING"
        },
        // ... more target lines
    ]
})
```

**CP8 checkpoint**: Verify submission succeeded.

### Step 8: Next Steps

Same as standalone — ask about approval and posting.

---

## Approval and Posting

After successful submission (either mode):

```python
# Approve
submit("allocation_run", "approve", {"allocation_run_id": <id>})

# Execute (post GL journal entry)
result = submit("allocation_run", "execute", {"allocation_run_id": <id>})
# Returns: transaction_id, transaction_number
```

Tell the user:
- The GL journal entry has been posted
- For document-linked: they can see the full document chain in the admin dashboard
- The allocation run links Source Transaction -> Allocation Run -> Target GL Entry

## Voiding and Correcting

If the user needs to undo an allocation:

```python
submit("allocation_run", "void", {
    "allocation_run_id": <id>,
    "void_reason": "Incorrect percentages, will recalculate"
})
```

This creates a reversing GL entry and frees up the source account for re-allocation.

## Error Handling

- **"Source line account(s) X do not appear in the source transaction's GL lines"**: The source line in the allocation uses the wrong account. Check the source transaction's GL lines and use the correct account number.
- **"Account X from source transaction is already fully allocated"**: The source document has already been allocated. The user must void the existing allocation before creating a new one.
- **"Source amount X exceeds remaining unallocated balance"**: Only part of the source line is available. Reduce the allocation amount or void existing allocations.
- **Account not found**: Suggest the user check the chart of accounts. Use `search("account", "<number>")`.
- **Unbalanced lines**: Recalculate. Adjust the largest target line to absorb rounding differences.
- **Period closed**: The fiscal period must be open for posting.
- **Run not in draft**: If the run is already calculated, lines will be replaced (recalculation is supported).
