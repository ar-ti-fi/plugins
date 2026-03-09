---
name: generate-xbrl-mapping
description: Generate account-to-XBRL element mapping table for portal data entry
---

# Generate XBRL Mapping

Generate a mapping table from the entity's chart of accounts to Estonian GAAP XBRL taxonomy elements, ready for portal data entry at ariregister.rik.ee.

## Usage

```
/arfiti-ee:generate-xbrl-mapping
```

## What This Does

1. Fetches the entity's chart of accounts
2. Fetches the current year trial balance
3. Maps each account to the corresponding XBRL element using account number ranges
4. Generates a table showing: Account Number | Account Name | Balance | XBRL Element | Report Line

## Output

A mapping table that can be used to fill in the e-Business Register portal forms efficiently, showing exactly which value goes into which portal field.
