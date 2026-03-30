# VAT Declaration Validation Checklist

Run these checks before submitting the KMD to EMTA. Each check must pass.

## Pre-Submission Checks

### 1. Transaction Completeness

- [ ] All invoices for the period are posted (no drafts remaining)
- [ ] All credit notes for the period are posted
- [ ] No unposted journal entries affecting VAT accounts
- [ ] All transactions have tax codes assigned

**How to verify:**
```
# Check for draft transactions in the period
list_entities("transaction", {
    "legal_entity_id": ID,
    "status": "draft"
}, date_filters={"transaction_date": {"from": "YYYY-MM-01", "to": "YYYY-MM-DD"}})
```

### 2. Tax Code Coverage

- [ ] Every AR invoice line has a tax code assigned
- [ ] Every AP invoice line has a tax code assigned
- [ ] No transactions use inactive or invalid tax codes
- [ ] All tax codes are classified to a KMD line

### 3. KMD Calculation Integrity

- [ ] Line 1.1 = Line 1 x applicable rate (or sum of actual VAT from invoices)
- [ ] Line 2.1 = sum of VAT from reduced-rate invoices
- [ ] Line 10 = (Line 1.1 + Line 2.1) - Line 4 + Line 8
- [ ] If Line 10 + Line 11 > 0 → Line 12 is populated, Line 13 = 0
- [ ] If Line 10 + Line 11 < 0 → Line 13 is populated, Line 12 = 0
- [ ] Line 12 and Line 13 are mutually exclusive (not both > 0)

### 4. KMD INF Reconciliation

- [ ] All partners with total > EUR 1,000 are listed
- [ ] Partner registration codes are valid format (8 digits for Estonian)
- [ ] Sum of Part A taxable amounts is consistent with KMD output VAT lines
- [ ] Sum of Part B taxable amounts is consistent with total AP invoice base
- [ ] No duplicate partner entries

### 5. EC Sales List Reconciliation

- [ ] Form VD goods total = KMD Line 3.1
- [ ] Form VD services total = KMD Line 3.2
- [ ] All customer VAT numbers are in valid EU format
- [ ] Customer VAT numbers verified via VIES (or scheduled for verification)

### 6. GL Account Reconciliation

- [ ] VAT Output account balance matches KMD output VAT total (Lines 1.1 + 2.1)
- [ ] VAT Input account balance matches KMD Line 4
- [ ] VAT Payable/Receivable net matches Line 12 or Line 13
- [ ] No unexplained differences between GL and KMD

**How to verify:**
```
generate_report("trial_balance", {
    "legal_entity_id": ID,
    "as_of_date": "YYYY-MM-DD"
})
# Compare VAT account balances to KMD totals
```

### 7. Format Validation (for XML submission)

- [ ] XML files are UTF-8 encoded
- [ ] All amounts have exactly 2 decimal places
- [ ] Period year/month are correct
- [ ] Taxpayer registration code is correct (8 digits)
- [ ] All required XML elements are present

## Common Issues and Resolutions

| Issue | Resolution |
|---|---|
| Missing tax code on invoice | Review transaction, assign correct tax code |
| Invalid partner registration code | Verify against Estonian Business Registry (ariregister.rik.ee) |
| GL balance does not match KMD | Check for unposted entries, manual journal entries, or timing differences |
| KMD INF total differs from KMD | Check partners below threshold, credit notes, exempt transactions |
| EC Sales List does not match Lines 3.1/3.2 | Verify IC transaction classification, check customer VAT IDs |
| Duplicate in KMD INF | Merge entries for same partner, sum amounts |
| VAT on imports not matching | Verify customs declaration data, check Line 11 |

## Severity Levels

| Severity | Description | Action |
|---|---|---|
| **Blocker** | KMD calculation errors, GL mismatch > EUR 1 | Must fix before filing |
| **Warning** | Missing partner codes, rounding differences < EUR 1 | Should fix, can file with note |
| **Info** | No IC transactions (Form VD not needed), all checks pass | No action needed |
