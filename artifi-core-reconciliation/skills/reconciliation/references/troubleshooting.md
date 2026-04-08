# Troubleshooting Reference

Common reconciliation issues and how to resolve them.

---

## No Matches Found

**Symptom:** Agent or manual analysis finds zero matches for a party.

**Causes and fixes:**

| Cause | How to Check | Fix |
|-------|-------------|-----|
| Invoices not posted | `list_entities("transaction", {"vendor_id": <id>, "transaction_type": "AP_INVOICE", "status": "draft"})` | Post the invoices first |
| Invoices assigned to wrong party | `get_entity("transaction", id=<inv_id>)` -- check `vendor_id`/`customer_id` | Update the invoice party assignment |
| No invoices exist | No invoice results for this party | Post the corresponding bill/invoice |
| Payments in wrong currency | Compare `currency` on payment vs invoice | Check if FX matching is needed |
| Date range too narrow | Agent default: 90 days | Check if payment and invoice are >90 days apart |

---

## Tax Payments Without Bills

**Symptom:** Payments to a tax authority (e.g., "Maksu- ja Tolliamet") have no matching invoices.

**Cause:** Tax payments are typically made based on declarations, not bills. The ERP may not have tax bills posted.

**Fix options:**
1. **Create tax bills** -- post AP_INVOICE for each tax payment with the tax authority as vendor
2. **Mark as reconciled manually** -- if the tax return confirms the amount, match the payment to the tax bill
3. **Skip** -- document these as "tax payments without backing documents" in the reconciliation report

---

## Rounding Differences

**Symptom:** Match is close but off by 0.01-0.05.

**Cause:** Different precision in source systems, currency conversion rounding, or bank fee deductions.

**Fix:**
- Differences <= 0.05: write off automatically via the `write_off_amount` parameter
- Differences 0.06 -- 100: propose write-off to user
- Differences > 100: create an adjusting journal entry

```python
# For small rounding
submit("reconciliation", "match", {
    "scope": "ar",
    "legal_entity_id": <id>,
    "source_transaction_id": <payment_id>,
    "applications": [{"target_transaction_id": <inv_id>, "applied_amount": <payment_amount>}],
    "write_off_amount": 0.03,
    "notes": "Rounding difference"
})
```

---

## Payment Already Reconciled

**Symptom:** Error "Payment is already fully reconciled."

**Cause:** The payment was matched in a previous reconciliation run.

**Fix:**
1. Check current status: `get_entity("transaction", id=<payment_id>)` -- look at `recon_status`
2. If the match is wrong, unmatch first:
```python
submit("reconciliation", "unmatch", {
    "scope": "ar",
    "legal_entity_id": <id>,
    "source_transaction_id": <payment_id>,
    "reason": "Incorrect match"
})
```
3. Then re-match to the correct invoice

---

## Applied Amount Exceeds Amount Due

**Symptom:** Error "Application amount X exceeds invoice Y amount due Z."

**Cause:** The invoice was already partially paid (by a previous match or payment application).

**Fix:**
1. Check invoice status: `get_entity("transaction", id=<invoice_id>)` -- look at `amount_due`, `amount_paid`
2. Reduce the `applied_amount` to match the remaining `amount_due`
3. If the payment has a remainder after this invoice, apply it to another invoice

---

## Party Mismatch

**Symptom:** Error "Invoice belongs to vendor X, but payment belongs to vendor Y."

**Cause:** Payment or invoice assigned to the wrong party.

**Fix:**
1. Check which is correct -- look at descriptions, reference numbers, bank details
2. If the invoice party is wrong, update it (requires admin access)
3. If the payment party is wrong, update the payment's vendor/customer assignment

---

## Agent Run Failed

**Symptom:** Reconciliation agent completes with status "failed."

**Common causes:**

| Cause | Fix |
|-------|-----|
| FX posting profile missing | The agent needs FX posting profiles for multi-currency entities. Check agent progress log for "FX posting profile missing" message. Configure via admin dashboard. |
| No transactions to process | All payments already reconciled. Nothing for agent to do. |
| Database constraint error | Check agent error message for specific constraint. May need admin intervention. |
| Timeout (>30 min) | Too many transactions. Try filtering by scope or date range. |

---

## Contractor/Payroll Payments

**Symptom:** Payments to individuals (not vendors) have no matching invoices.

**Cause:** These are typically payroll runs or contractor payments processed through the bank but without corresponding AP invoices.

**Fix options:**
1. **Create the AP invoice** -- post a bill for the contractor's services
2. **Post as payroll** -- if it's a salary payment, process through the payroll system instead
3. **Skip** -- document as "payroll/contractor payment" and reconcile after proper invoicing

---

## Multi-Currency Mismatches

**Symptom:** Payment in EUR, invoice in USD -- amounts don't match in document currency.

**Fix:**
1. The system compares amounts in **functional currency** (entity's base currency)
2. If the functional amounts are close (within 5%), it's likely a valid match with FX variance
3. The reconciliation system can auto-post FX gain/loss journal entries for matched items
4. If the FX difference is >5%, investigate: check exchange rates at payment date vs invoice date

---

## Duplicate Matches

**Symptom:** Same payment appears matched to different invoices in different runs.

**Cause:** Should not happen -- the system checks `recon_status` before matching. But could occur if:
- Two concurrent reconciliation runs process the same payments
- Manual match applied while agent is running

**Fix:**
1. Check reconciliation items: `list_entities("reconciliation_item", {"source_transaction_id": <payment_id>})`
2. Identify the duplicate
3. Unmatch the incorrect one
4. Agent concurrency is limited to 1 run at a time to prevent this
