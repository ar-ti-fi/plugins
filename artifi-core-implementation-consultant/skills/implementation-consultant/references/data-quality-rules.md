# Data Quality Rules

Validation rules to apply when importing data during migration. Run these checks before committing imports.

## General Rules (All Import Types)

### Required Field Validation
- All required fields must be non-empty
- String fields must not be whitespace-only
- Numeric fields must be valid numbers (no text, no special characters except decimal point and minus)
- Date fields must be valid dates in YYYY-MM-DD format

### Duplicate Detection
- Check for duplicates within the import batch (same name, email, or reference number)
- Check for duplicates against existing records: `search("<type>", "<name_or_reference>")`
- Use `on_duplicate="skip"` for safe imports, `on_duplicate="update"` to overwrite

### Cross-Reference Integrity
- Every transaction line must reference an existing account (by account_number)
- Every AP transaction must reference an existing vendor (by vendor_id or vendor_name)
- Every AR transaction must reference an existing customer (by customer_id or customer_name)
- Every bank transaction must reference an existing bank_account (by bank_account_id)

### Import Sequence
Import in this order to satisfy dependencies:
1. Accounts → 2. Dimensions → 3. Customers → 4. Vendors → 5. Items → 6. Employees → 7. Fixed Assets → 8. Opening Balances → 9. Transactions

## Account Import Rules

| Rule | Check | Action |
|------|-------|--------|
| Account number format | Alphanumeric, typically 4-6 digits | Normalize to consistent format |
| Account type required | Must be one of: asset, liability, equity, revenue, expense | Reject if missing or invalid |
| Normal balance | Must match type: asset/expense = debit, liability/equity/revenue = credit | Auto-set if missing |
| No duplicate numbers | Account number must be unique within entity | Flag for user review |
| All 5 types present | After import, verify at least one account of each type exists | Warn if any type missing |

## Vendor/Customer Import Rules

| Rule | Check | Action |
|------|-------|--------|
| Name required | vendor_name / customer_name must not be empty | Reject record |
| Email format | If email provided, must be valid email format | Warn if invalid |
| Country code | If provided, must be 2-letter ISO 3166-1 (US, EE, GB, DE, etc.) | Reject if invalid |
| Payment terms | If payment_terms_code provided, must exist in system | Default to NET30 if invalid |
| Duplicate names | Flag exact name matches for review | May be intentional (branches) |
| Phone format | If phone provided, normalize format | Clean but don't reject |

## Transaction Import Rules

| Rule | Check | Action |
|------|-------|--------|
| Transaction type valid | Must be a recognized type (AP_INVOICE, AR_INVOICE, JOURNAL_ENTRY, etc.) | Reject if invalid |
| Date in open period | transaction_date must fall in an open fiscal period | Warn if period closed |
| Lines balance | For journal entries: sum of debits must equal sum of credits | Reject if unbalanced |
| Reference unique | reference_number should be unique per transaction type | Skip if duplicate |
| Amount positive | Line amounts should be positive (direction determined by debit/credit) | Warn if negative |
| Account exists | account_number on each line must exist in CoA | Reject line if not found |
| Vendor/Customer exists | If AP/AR type, party must exist | Create party first or reject |

## Opening Balance Rules

| Rule | Check | Action |
|------|-------|--------|
| Only balance sheet accounts | Revenue and expense accounts should NOT be in opening balance | Warn and exclude |
| Total balance | Sum of debits must equal sum of credits (before balancing account) | Show imbalance amount |
| Balancing account exists | Account 3300 (or specified balancing account) must exist | Create if missing |
| Account mapping complete | Every line must map to an existing account | Flag unmapped lines |
| Fiscal period exists | The target fiscal period must exist and be open | Create period if needed |
| No prior opening balance | Check if opening balance already posted for this period | Warn if duplicate |

## Fixed Asset Import Rules

| Rule | Check | Action |
|------|-------|--------|
| Name required | Asset must have a description/name | Reject if missing |
| Cost positive | original_cost must be > 0 | Reject if zero or negative |
| Depreciation ≤ cost | accumulated_depreciation must not exceed original_cost | Warn if exceeded |
| Useful life positive | useful_life_months must be > 0 | Default to 60 if missing |
| Acquisition date valid | Must be a valid past date | Warn if future |
| Category exists | If asset_category provided, must exist in system | Create category or warn |

## Employee Import Rules

| Rule | Check | Action |
|------|-------|--------|
| Name required | first_name and last_name must not be empty | Reject if missing |
| Email format | work_email must be valid email | Reject if invalid |
| Hire date valid | Must be a valid date | Warn if future or very old |
| Employment type | Must be: full_time, part_time, contractor, intern | Default to full_time |
| Duplicate email | Email must be unique | Flag for review |

## Validation Workflow

For every import, follow this sequence:

1. **Dry run first**: `manage_imports(action="<type>", records=[...], validate_only=true)`
2. **Review errors**: Fix any validation failures
3. **Review warnings**: Decide whether to proceed with warnings
4. **Import**: `manage_imports(action="<type>", records=[...], legal_entity_id=ID)`
5. **Verify**: Check imported count matches expected count
6. **Spot check**: Query a few records to confirm data integrity
