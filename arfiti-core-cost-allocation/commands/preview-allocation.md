---
name: Preview Allocation
description: Calculate and preview an allocation without submitting it. Supports standalone and document-linked modes.
---

# Preview Allocation

Calculate and show me what a cost allocation would look like, but don't submit anything:

1. Ask which legal entity and period
2. Ask whether to allocate from GL balances (standalone) or from a specific document (bill, invoice, journal entry)
3. For standalone: ask what to allocate (source account/costs)
4. For document-linked: look up the source transaction, show its GL lines, and check existing allocations
5. Ask how to allocate (method: fixed %, headcount, revenue, custom)
6. Fetch data and calculate the splits
7. Show the preview table with source and target lines
8. Show the total debits and credits to verify balance
9. For document-linked: confirm source line accounts match the source transaction

Do NOT create an allocation run or submit any lines. This is preview-only.
