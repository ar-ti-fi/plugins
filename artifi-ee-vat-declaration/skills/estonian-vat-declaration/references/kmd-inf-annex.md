# KMD INF Annex (Transaction Partner Reporting)

The KMD INF is a mandatory annex to the KMD form that reports transaction partners
where the total amount for the period exceeds the threshold.

## Threshold

**EUR 1,000** — Report any partner where total invoiced amount (taxable + VAT) exceeds
EUR 1,000 in the reporting month.

## Structure

### Part A — Sales (Muuk)

Report customers where total AR invoices > EUR 1,000 in the period.

| Field | Description | Source |
|---|---|---|
| Partner registration code | Estonian business registry code (8 digits) or foreign ID | `customer.tax_id` |
| Partner name | Legal name | `customer.customer_name` |
| Number of invoices | Count of posted AR invoices in period | Aggregation |
| Taxable amount | Sum of taxable base amounts | Aggregation |
| VAT amount | Sum of VAT amounts | Aggregation |

**Query approach:**
```
aggregate_entities("transaction", ["party_name"], {"amount": "sum", "id": "count"},
    {"legal_entity_id": ID, "transaction_type": "ar_invoice"},
    date_filters={"transaction_date": {"from": "YYYY-MM-01", "to": "YYYY-MM-DD"}})
```
Then filter to partners where sum > 1000.

### Part B — Purchases (Ost)

Report vendors where total AP invoices > EUR 1,000 in the period.

| Field | Description | Source |
|---|---|---|
| Partner registration code | Estonian business registry code or foreign ID | `vendor.tax_id` |
| Partner name | Legal name | `vendor.vendor_name` |
| Number of invoices | Count of posted AP invoices in period | Aggregation |
| Taxable amount | Sum of taxable base amounts | Aggregation |
| VAT amount | Sum of VAT amounts | Aggregation |

## Registration Code Validation

- Estonian business registry codes are 8 digits
- Foreign partners: use their country's tax/VAT ID
- Invalid codes will cause EMTA rejection — validate before submission

## Reconciliation

- Sum of Part A taxable amounts should approximately match KMD Lines 1 + 2 (domestic sales)
- Sum of Part B taxable amounts should approximately match total AP invoice base amounts
- Small differences are acceptable due to rounding and partners below threshold

## Special Cases

| Scenario | Treatment |
|---|---|
| Credit notes | Reduce the partner's total (may drop below threshold) |
| Intra-community supplies | Included in Part A if domestic VAT applies; IC supplies (Lines 3.1/3.2) may be excluded |
| Cash transactions without partner | Aggregate as "Cash sales" if > threshold |
| Multiple invoices to same partner | Combine into single partner entry |

## Format (KMD2)

KMD INF A/B are the `salesAnnex` and `purchasesAnnex` parts of the **single**
`vatDeclaration` document (see `references/kmd-form-structure.md`). There is no
separate `<KMDINF>` file and no `http://emta.ee/schemas/vat` namespace. When no
partner exceeds the threshold, set `noSales` / `noPurchases` to `true` in
`declarationBody` and omit the annex entirely.

Feed the generator via the `sales_annex` / `purchases_annex` blocks in the input JSON.
In summed-per-partner mode (`sum_per_partner: true`) each line is one partner:

```json
"sales_annex": {
  "sum_per_partner": true,
  "lines": [
    {"buyerRegCode": "87654321", "buyerName": "Customer OÜ",
     "invoiceSum": 13000.00, "taxRate": "24", "sumForRateInPeriod": 13000.00}
  ]
},
"purchases_annex": {
  "sum_per_partner": true,
  "lines": [
    {"sellerRegCode": "11223344", "sellerName": "Vendor AS",
     "invoiceSumVat": 3660.00, "vatInPeriod": 660.00}
  ]
}
```

`generate_kmd.py` renders these into schema-valid `<salesAnnex>` / `<purchasesAnnex>`
elements:

```xml
<salesAnnex>
  <saleLine>
    <buyerRegCode>87654321</buyerRegCode>
    <buyerName>Customer OÜ</buyerName>
    <invoiceSum>13000.00</invoiceSum>
    <taxRate>24</taxRate>
    <sumForRateInPeriod>13000.00</sumForRateInPeriod>
  </saleLine>
</salesAnnex>
<purchasesAnnex>
  <purchaseLine>
    <sellerRegCode>11223344</sellerRegCode>
    <sellerName>Vendor AS</sellerName>
    <invoiceSumVat>3660.00</invoiceSumVat>
    <vatInPeriod>660.00</vatInPeriod>
  </purchaseLine>
</purchasesAnnex>
```

Per-invoice (detailed) mode is also valid: set `sum_per_partner: false` and add
`invoiceNumber` + `invoiceDate` to each line (one line per invoice). Mandatory fields
per the XSD: A → `invoiceSum`, `taxRate`; B → `invoiceSumVat`, `vatInPeriod`.
