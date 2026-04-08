---
name: Payment Reconciliation
description: Matches payment transactions to invoices — automated via the reconciliation agent, then manual matching for complex cases (N:N splits, partial payments, rounding write-offs). Covers both AR (customer receipts to sales invoices) and AP (vendor payments to bills). Provides a complete reconciliation workflow from assessment through resolution.
---

## Trigger

Activate when the user mentions: reconcile payments, match invoices, reconciliation, apply payment, cash application, payment matching, match receipts, unmatched payments, open invoices, AR reconciliation, AP reconciliation, payment to invoice, match payment to bill, reconcile AR, reconcile AP, recon status, what's unmatched, unreconciled transactions, apply receipt, settle invoice.

## Three Modes

### Mode 1: Full Reconciliation
Run the automated agent first, then manually handle what the agent couldn't match. Best for periodic (weekly/monthly) reconciliation.

### Mode 2: Quick Manual Match
Directly match a specific payment to one or more invoices. No agent run. Best when the user already knows which payment goes to which invoice.

### Mode 3: Reconciliation Health Check
Read-only status report. Show what's matched, what's open, and what needs attention. No changes made.

Ask the user which mode applies. If they say "reconcile everything" or "run reconciliation", use Mode 1. If they mention a specific payment or invoice, use Mode 2. If they say "status" or "what's outstanding", use Mode 3.

## Prerequisites

Before starting, confirm with the user:
1. **Legal entity ID** -- which entity to reconcile
2. **Scope** -- AR (customer), AP (vendor), or both (default: both)
3. **Mode** -- which of the three modes (infer from context if possible)

## Mandatory Checkpoints

You MUST verify each checkpoint before proceeding. If a checkpoint fails, STOP and inform the user.

- **CP1**: Legal entity exists and has posted transactions (`list_entities("transaction", {"legal_entity_id": <id>, "status": "posted"})` returns results)
- **CP2**: For Mode 1 -- agent run completed successfully (check agent instance status)
- **CP3**: All proposed manual matches are valid -- amounts sum correctly, same party, invoice has amount_due > 0
- **CP4**: User has reviewed and confirmed the match preview before applying
- **CP5**: Post-reconciliation verification -- compare before/after counts to confirm changes applied

---

## Workflow Steps -- Mode 1: Full Reconciliation

### Step 1: Assess Current State

Load the reconciliation landscape in parallel:

```python
# Get unreconciled payment and invoice counts
batch_lookup([
    {"entity_type": "transaction", "filters": {
        "legal_entity_id": <id>, "transaction_type": "AP_PAYMENT",
        "recon_status_is_null": true
    }, "limit": 100},
    {"entity_type": "transaction", "filters": {
        "legal_entity_id": <id>, "transaction_type": "AR_PAYMENT",
        "recon_status_is_null": true
    }, "limit": 100}
])

# Get totals by recon status
aggregate_entities("transaction",
    group_by=["transaction_type", "recon_status"],
    aggregates={"id": "count", "amount": "sum"},
    filters={"legal_entity_id": <id>,
             "transaction_type": ["AP_PAYMENT", "AR_PAYMENT", "AP_INVOICE", "AR_INVOICE"]}
)
```

Present a summary table:

```
| Category | Count | Amount | Status |
|----------|-------|--------|--------|
| AP Payments (unmatched) | X | $Y | Needs matching |
| AP Payments (reconciled) | X | $Y | Done |
| AR Payments (unmatched) | X | $Y | Needs matching |
| AR Payments (reconciled) | X | $Y | Done |
| AP Invoices (open) | X | $Y | Awaiting payment match |
| AR Invoices (open) | X | $Y | Awaiting receipt match |
```

**CP1 checkpoint**: Confirm the entity has transactions to reconcile. If all payments are already reconciled, inform the user and stop.

### Step 2: Run Automated Reconciliation Agent

Start the reconciliation agent which runs a 6-pass matching algorithm:

```python
result = manage_agents(
    action="start",
    agent_type="reconciliation_agent",
    legal_entity_id=<id>
)
```

Monitor progress:

```python
status = manage_agents(
    action="get_status",
    _agent_instance_id=<instance_id>
)
```

Wait for completion. The agent handles:
- Pass 1: Exact amount match (confidence 1.0)
- Pass 2: Reference number match (confidence 0.95)
- Pass 2.5: Cross-reference in descriptions (confidence 0.92-0.95)
- Pass 3: Approximate amount with FX tolerance (confidence 0.85-0.95)
- Pass 4: Amount grouping -- 1:N, N:1, credit memos (confidence 0.50-0.95)
- Pass 5: Haiku fuzzy match (confidence 0.70)

**CP2 checkpoint**: Agent run completed. Check the agent summary for match counts.

Show the agent results:
```
Agent matched X payments automatically.
- Exact matches: Y
- Reference matches: Z
- Approximate: W
Remaining unmatched: N payments, M open invoices.
```

If everything matched, congratulate the user and skip to Step 7.

### Step 3: Analyze Remaining Unmatched Items

Group unmatched items by party to find patterns:

```python
# Unmatched AP payments by vendor
aggregate_entities("transaction",
    group_by=["vendor_id"],
    aggregates={"id": "count", "amount": "sum"},
    filters={"legal_entity_id": <id>, "transaction_type": "AP_PAYMENT",
             "recon_status_is_null": true}
)

# Unmatched AR payments by customer
aggregate_entities("transaction",
    group_by=["customer_id"],
    aggregates={"id": "count", "amount": "sum"},
    filters={"legal_entity_id": <id>, "transaction_type": "AR_PAYMENT",
             "recon_status_is_null": true}
)
```

For each party with unmatched payments, load BOTH payments and open invoices:

```python
# For a specific vendor
payments = list_entities("transaction", filters={
    "legal_entity_id": <id>, "vendor_id": <party_id>,
    "transaction_type": "AP_PAYMENT", "recon_status_is_null": true
})
invoices = list_entities("transaction", filters={
    "legal_entity_id": <id>, "vendor_id": <party_id>,
    "transaction_type": "AP_INVOICE", "status": "posted"
})
```

### Step 4: Propose Manual Matches

For each party, apply matching strategies in order (see **references/matching-strategies.md**):

**Strategy 1: Exact 1:1** -- payment amount equals one invoice amount exactly.

**Strategy 2: Partial match** -- payment amount < invoice amount. Apply what we have, invoice stays open with reduced `amount_due`.

**Strategy 3: 1:N split** -- payment amount equals the sum of multiple invoices (within rounding tolerance of 0.05).

**Strategy 4: N:1 group** -- multiple payments sum to one invoice amount.

**Strategy 5: N:N complex** -- multiple payments map to multiple invoices. Find the combination where totals balance (within rounding tolerance).

**Strategy 6: Rounding write-off** -- match is close but has a small difference (less than 1.00). Propose write-off.

For each proposed match, present as a table:

```
Vendor: Acme Corp (3 unmatched payments, 5 open invoices)

| # | Payment | Date | Amount | --> | Invoice(s) | Amount | Diff | Action |
|---|---------|------|--------|-----|------------|--------|------|--------|
| 1 | PAY001 | Feb 16 | 14,250.16 | --> | INV013 (partial) | 15,903.00 | -1,652.84 rem | Partial apply |
| 2 | PAY002 | Mar 2 | 1,767.00 | --> | INV013 (1,652.84) + INV012 (114.16) | 1,767.00 | 0.01 w/o | Split + write-off |
| 3 | PAY003 | Mar 15 | 500.00 | --> | No match found | -- | -- | Investigate |
```

Explain the matching logic for each proposal. Show the math clearly.

**CP3 checkpoint**: Verify all proposed matches are valid:
- Payment and invoice belong to the same party
- Applied amounts don't exceed invoice `amount_due`
- Applied amounts don't exceed payment available amount
- Write-off amounts are within threshold (max 100)

**CP4 checkpoint**: Ask the user: "Here are the proposed matches. Shall I apply them? You can also modify individual matches or skip any."

Wait for explicit confirmation.

### Step 5: Apply Confirmed Matches

For each confirmed match:

```python
result = submit("reconciliation", "match", {
    "scope": "ar",  # or "ap" for vendor bills
    "legal_entity_id": <id>,
    "source_transaction_id": <payment_id>,
    "applications": [
        {"target_transaction_id": <invoice_id>, "applied_amount": <amount>}
    ],
    "write_off_amount": <rounding_diff>,  # optional, max 100
    "notes": "Matched: <explanation>"
})
```

For N:N splits (one payment across multiple invoices):

```python
result = submit("reconciliation", "match", {
    "scope": "ar",
    "legal_entity_id": <id>,
    "source_transaction_id": <payment_id>,
    "applications": [
        {"target_transaction_id": <inv1_id>, "applied_amount": <amount1>},
        {"target_transaction_id": <inv2_id>, "applied_amount": <amount2>}
    ],
    "write_off_amount": 0.01,
    "notes": "Split payment across 2 invoices, 0.01 rounding write-off"
})
```

Report each result immediately. If any match fails, explain the error and continue with the next.

### Step 6: Categorize Unresolvable Items

After all possible matches are applied, categorize what remains:

**Category A: Missing bills/invoices** -- payment exists but no corresponding invoice is posted.
- Common for: tax payments, contractor payments, subscriptions
- Action: "You need to post the corresponding bill/invoice first, then run reconciliation again"

**Category B: Overpayments** -- payment exceeds all available invoices for this party.
- Action: "Contact the party to clarify, or create a credit memo"

**Category C: Unknown parties** -- payment to a party with zero invoices.
- Action: "Check if the payment was assigned to the wrong vendor/customer"

**Category D: Complex cross-currency** -- amounts don't match due to FX differences > 5%.
- Action: "Review the exchange rates at payment vs invoice date"

Present the categorized list:

```
Unresolvable items (need manual action):

| Payment | Party | Amount | Category | Recommended Action |
|---------|-------|--------|----------|--------------------|
| PAY003 | Tax Authority | 2,883.92 | Missing bill | Post the tax bill, then re-reconcile |
| PAY007 | Unknown Vendor | 500.00 | Unknown party | Verify vendor assignment |
```

### Step 7: Post-Reconciliation Summary

Compare before and after:

```python
# Re-check totals
aggregate_entities("transaction",
    group_by=["transaction_type", "recon_status"],
    aggregates={"id": "count", "amount": "sum"},
    filters={"legal_entity_id": <id>,
             "transaction_type": ["AP_PAYMENT", "AR_PAYMENT"]}
)
```

**CP5 checkpoint**: Verify the numbers changed as expected.

Present final summary:

```
Reconciliation Complete for Entity <id>

Before:
- Unmatched AP payments: 20 ($45,000)
- Unmatched AR payments: 16 ($79,000)

After:
- Matched (agent): 25 payments ($68,000)
- Matched (manual): 5 payments ($16,000)
- Remaining unmatched: 6 payments ($40,000) -- see categorized list above

Match rate: 83% (30/36 payments matched)
```

---

## Workflow Steps -- Mode 2: Quick Manual Match

### Step 1: Identify the Payment

Ask the user for the payment transaction ID or search for it:

```python
# If user provides a transaction number
payment = search("transaction", "<number>", filters={"legal_entity_id": <id>})

# Or list recent unmatched payments
list_entities("transaction", filters={
    "legal_entity_id": <id>,
    "transaction_type": ["AP_PAYMENT", "AR_PAYMENT"],
    "recon_status_is_null": true
}, sort_by="transaction_date", sort_order="desc", limit=20)
```

### Step 2: Identify the Invoice(s)

Ask the user for invoice ID(s) or search:

```python
# Search invoices for the same party
invoices = list_entities("transaction", filters={
    "legal_entity_id": <id>,
    "vendor_id": <payment.vendor_id>,  # or customer_id
    "transaction_type": "AP_INVOICE",  # or AR_INVOICE
    "status": ["posted", "partial"]
})
```

Show available invoices with amounts due.

### Step 3: Preview and Confirm

Show what will happen:

```
Match Preview:
  Payment: PAY000123 ($5,000.00) -- Vendor: Acme Corp
  Apply to:
    INV000456 ($3,000.00) -- full payment, closes invoice
    INV000789 ($2,000.00 of $4,500.00) -- partial, $2,500 remains open

  Write-off: $0.00
  Payment status after: reconciled
```

**CP3 + CP4 checkpoint**: Validate and get user confirmation.

### Step 4: Apply

```python
result = submit("reconciliation", "match", {
    "scope": "<ar or ap>",
    "legal_entity_id": <id>,
    "source_transaction_id": <payment_id>,
    "applications": [
        {"target_transaction_id": <inv1>, "applied_amount": 3000.00},
        {"target_transaction_id": <inv2>, "applied_amount": 2000.00}
    ],
    "notes": "Manual match per user request"
})
```

Report the result.

---

## Workflow Steps -- Mode 3: Reconciliation Health Check

### Step 1: Load Status

```python
# Payment recon status breakdown
aggregate_entities("transaction",
    group_by=["transaction_type", "recon_status"],
    aggregates={"id": "count", "amount": "sum"},
    filters={"legal_entity_id": <id>,
             "transaction_type": ["AP_PAYMENT", "AR_PAYMENT",
                                  "AP_INVOICE", "AR_INVOICE"]}
)

# Aging of unmatched payments
aggregate_entities("transaction",
    group_by=["transaction_type"],
    aggregates={"id": "count", "amount": "sum"},
    filters={"legal_entity_id": <id>,
             "transaction_type": ["AP_PAYMENT", "AR_PAYMENT"],
             "recon_status_is_null": true}
)
```

### Step 2: Present Dashboard

```
Reconciliation Status -- Entity <id>

AP (Vendor Payments):
  Reconciled: X payments ($Y)
  Partial: X payments ($Y)
  Unmatched: X payments ($Y) -- oldest: <date>

AR (Customer Receipts):
  Reconciled: X payments ($Y)
  Partial: X payments ($Y)
  Unmatched: X payments ($Y) -- oldest: <date>

Open Invoices:
  AP: X bills ($Y due)
  AR: X invoices ($Y due)

Recommendation:
  [Based on counts, suggest: "Run full reconciliation (Mode 1)" or
   "All looks good, no action needed"]
```

---

## Reversing a Match

If the user wants to undo a match:

```python
result = submit("reconciliation", "unmatch", {
    "scope": "<ar or ap>",
    "legal_entity_id": <id>,
    "source_transaction_id": <payment_id>,
    "reason": "Incorrect match -- wrong invoice"
})
```

This reverses all financial updates: invoice `amount_due` restored, payment `recon_status` reset to NULL.

---

## Error Handling

- **"Payment transaction not found"**: Double-check the transaction ID. Use `search("transaction", "<number>")` to find it.
- **"Transaction is already fully reconciled"**: The payment was already matched. Use `get_entity("transaction", id=<id>)` to see its current status. To change the match, unmatch first, then re-match.
- **"Invoice belongs to different vendor/customer"**: Payment and invoice must be for the same party. Check party assignments on both transactions.
- **"Applied amount exceeds amount_due"**: The invoice doesn't have enough remaining balance. Check `amount_due` on the invoice -- it may have been partially paid already.
- **"Write-off exceeds maximum (100)"**: For differences larger than 100, create an adjusting journal entry instead of using write-off. Post a JE (DR write-off account / CR AR or AP control account), then match normally.
- **"Agent run failed"**: Check agent logs via admin dashboard. Common causes: FX posting profile missing (agent needs this for multi-currency entities), no transactions to process.

---

## Important Rules

1. **Always check the schema first** -- before any `submit()` call, run `get_workflow_schema("reconciliation", "match")` to discover the exact required fields.
2. **Never guess amounts** -- always calculate from actual transaction data. Show the math to the user.
3. **One confirmation per batch** -- group related matches (same party) and confirm together, don't ask for each individual match.
4. **Partial is OK** -- if a payment only partially covers an invoice, apply what we have. The invoice stays open with reduced `amount_due` for future matching.
5. **Write-off threshold** -- write-offs up to 0.05 can be applied without asking. 0.05-1.00 mention to user. Above 1.00 always ask. Above 100 always use JE instead.
6. **Order matters** -- always run the agent first (Mode 1) before doing manual matches. The agent handles the easy cases; manual work is for complex patterns.
