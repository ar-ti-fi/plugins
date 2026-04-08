# Reconciliation Types Reference

The ERP has four distinct reconciliation domains. This plugin handles **Transaction Reconciliation** (AR and AP). The other types are referenced here for context.

---

## 1. Transaction Reconciliation (This Plugin)

Matches payment transactions to invoice transactions. Updates invoice financials (amount_paid, amount_due, status).

### AR Reconciliation (Customer Receipts)

| Aspect | Value |
|--------|-------|
| Scope | `ar` (maps to DB scope `customer`) |
| Payment types | `AR_PAYMENT`, `AR_PREPAYMENT`, `AR_REFUND` |
| Invoice types | `AR_INVOICE`, `AR_CREDIT_MEMO` |
| Party column | `customer_id` |
| MCP tool | `submit("reconciliation", "match", {"scope": "ar", ...})` |

### AP Reconciliation (Vendor Payments)

| Aspect | Value |
|--------|-------|
| Scope | `ap` (maps to DB scope `vendor`) |
| Payment types | `AP_PAYMENT`, `AP_PREPAYMENT`, `AP_REFUND` |
| Invoice types | `AP_INVOICE`, `AP_CREDIT_MEMO` |
| Party column | `vendor_id` |
| MCP tool | `submit("reconciliation", "match", {"scope": "ap", ...})` |

### Submit Payload Format

```python
submit("reconciliation", "match", {
    "scope": "ar",                           # or "ap"
    "legal_entity_id": <id>,
    "source_transaction_id": <payment_id>,   # Payment/receipt transaction ID
    "applications": [                        # One or more invoices
        {
            "target_transaction_id": <inv_id>,
            "applied_amount": <decimal>       # How much to apply to this invoice
        }
    ],
    "write_off_amount": <decimal>,           # Optional (max 100)
    "write_off_account_number": "<acct>",    # Optional (default: 9100)
    "notes": "Match explanation"             # Optional
})
```

### Unmatch Payload

```python
submit("reconciliation", "unmatch", {
    "scope": "ar",                           # or "ap"
    "legal_entity_id": <id>,
    "source_transaction_id": <payment_id>,
    "reason": "Why unmatching"               # Optional
})
```

### Financial Updates Applied

When a match is confirmed:

| Field | Update |
|-------|--------|
| Invoice `amount_paid` | Increases by `applied_amount` |
| Invoice `amount_due` | Decreases by `applied_amount` |
| Invoice `status` | `'paid'` if fully paid, `'partial'` if balance remains |
| Invoice `recon_status` | `'reconciled'` if fully paid, `'partial'` if balance remains |
| Payment `recon_status` | `'reconciled'` if fully consumed, `'partial'` if balance remains |

### Audit Trail

Each match creates:
- `reconciliation_runs` row (scope, status, summary)
- `reconciliation_items` row(s) per application (source, target, amount, method='manual', confidence=1.0)

---

## 2. Bank Statement Reconciliation (Separate Workflow)

Matches bank statement lines to GL transactions. Does NOT update invoice financials.

**Not handled by this plugin.** Use:
- `submit("bank_statement_line", "match", {statement_line_id: X, gl_transaction_id: Y})`
- Claude interactive matching or `bank_transaction_processor` agent

---

## 3. Card Reconciliation (Separate Workflow)

Matches corporate card transactions to expense reports.

**Not handled by this plugin.** Use:
- `submit("reconciliation", "match", {"scope": "card", ...})`

---

## 4. Automated Reconciliation Agent

The `reconciliation_agent` handles bulk automated matching with a 6-pass algorithm. This plugin uses the agent in Mode 1 (Step 2) before doing manual matching.

**Agent trigger:**
```python
manage_agents(action="start", agent_type="reconciliation_agent", legal_entity_id=<id>)
```

**Agent scopes:** `vendor` (AP) and `customer` (AR) -- processes both by default.

**Auto-apply threshold:** 0.85 confidence. Matches below this appear as `manual_review` in the admin dashboard.
