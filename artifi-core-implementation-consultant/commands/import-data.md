---
name: Import Data
description: Import a specific type of data into Arfiti. Provides format guidance and walks through the import process for vendors, customers, items, employees, transactions, or opening balances.
---

# Import Data

Help me import data into Arfiti:

1. Ask which legal entity we're importing into
2. Ask what type of data to import (vendors, customers, items, employees, transactions, opening balances, fixed assets, dimensions, or accounts)
3. Show the required and optional fields for that import type using `manage_onboarding(action="get_support", support_type="import_<type>")`
4. Ask me to paste or upload the data
5. Validate with a dry run first: `manage_imports(action="<type>", records=[...], validate_only=true)`
6. Show validation results — fix any errors
7. Run the actual import
8. If async (>50 records), monitor progress with `get_import_status()`
9. Show final results: imported, skipped, errors

Use the Implementation Consultant skill for data quality rules and validation guidance.
