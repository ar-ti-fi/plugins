---
name: Run Allocation
description: Create and execute a cost allocation from start to finish. Supports standalone (from GL balances) and document-linked (from a specific bill/invoice).
---

# Run Allocation

Guide me through a cost allocation step by step:

1. Ask which legal entity and period
2. Ask whether to allocate from GL balances (standalone) or from a specific document (bill, invoice, journal entry)
3. For standalone: ask what to allocate (source account/costs)
4. For document-linked: look up the source transaction, show its GL lines, and check if any accounts are already allocated
5. Ask how to allocate (method: fixed %, headcount, revenue, custom)
6. Fetch data and calculate the splits
7. Show me a preview table (for document-linked: verify source line account matches the source transaction)
8. After I confirm, create the allocation run and submit lines
9. Ask if I want to approve and post now

Use the Cost Allocation skill for the full workflow.
