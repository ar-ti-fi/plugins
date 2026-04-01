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

## XML Format

```xml
<KMDINF xmlns="http://emta.ee/schemas/vat">
  <Period>
    <Year>2025</Year>
    <Month>01</Month>
  </Period>
  <PartA>
    <Partner>
      <RegCode>87654321</RegCode>
      <Name>Customer OU</Name>
      <InvoiceCount>5</InvoiceCount>
      <TaxableAmount>5000.00</TaxableAmount>
      <VATAmount>1200.00</VATAmount>
    </Partner>
  </PartA>
  <PartB>
    <Partner>
      <RegCode>11223344</RegCode>
      <Name>Vendor AS</Name>
      <InvoiceCount>3</InvoiceCount>
      <TaxableAmount>3000.00</TaxableAmount>
      <VATAmount>720.00</VATAmount>
    </Partner>
  </PartB>
</KMDINF>
```
