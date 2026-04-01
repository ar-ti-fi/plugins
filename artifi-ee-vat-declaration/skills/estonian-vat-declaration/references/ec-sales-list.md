# EC Sales List (Form VD / VDP)

The EC Sales List (Form VD — Uhenduseisisese kauba tarnete ja teenuste osutamise aruanne)
reports intra-community B2B supplies to VAT-registered customers in other EU member states.

## Filing Requirements

| Attribute | Detail |
|---|---|
| **Form** | VD (report) / VDP (amendments to prior periods) |
| **Frequency** | Monthly (same period as KMD) |
| **Deadline** | 20th of the following month (same as KMD) |
| **Authority** | EMTA (Estonian Tax and Customs Board) |
| **Required when** | Company has intra-community B2B supplies of goods or services |

## When to File

File Form VD when the entity has any of:
- Intra-community supply of goods to VAT-registered buyers in other EU states
- Cross-border B2B services subject to reverse charge in the customer's country
- Triangular transaction involvement (as intermediary/reseller)
- Call-off stock transfers to another EU member state

## Data Required Per Customer

| Field | Description | Source |
|---|---|---|
| Customer VAT number | EU VAT ID (must be verified via VIES) | `customer.tax_id` |
| Customer country | 2-letter EU country code | `customer.country` |
| Total supply amount | Sum of invoices for the period (EUR) | AR invoice aggregation |
| Supply type | **G** = Goods, **S** = Services, **T** = Triangular | Invoice classification |

## How to Identify IC Transactions

Use tax code properties to find intra-community supplies:

1. Filter AR invoices for the period
2. Identify transactions where the tax code has:
   - `default_rate = 0` AND customer is in EU (not Estonia) AND customer has EU VAT ID
3. Classify supply type:
   - **Goods (G)**: Physical goods shipped to another EU state
   - **Services (S)**: B2B services where place of supply is customer's country
   - **Triangular (T)**: Triangular/chain transactions as intermediary

## Preparing Form VD

```
# Step 1: Find IC supply invoices
# Filter transactions where tax code properties indicate IC supply
# AND customer country is EU (not EE) AND customer has VAT ID

# Step 2: Group by customer VAT number
# For each customer:
# - Sum all IC invoice amounts for the period
# - Determine supply type (G, S, or T)
# - One entry per customer per supply type

# Step 3: Validate VAT numbers via VIES before submission
```

## Reconciliation with KMD

| VD Supply Type | Must Reconcile With KMD Line |
|---|---|
| Goods (G) | Line 3.1 (Intra-Community supply of goods) |
| Services (S) | Line 3.2 (Intra-Community supply of services) |
| Triangular (T) | Line 3.1 |

**Critical**: The total of all Form VD amounts for goods MUST equal KMD line 3.1,
and services MUST equal KMD line 3.2. Any discrepancy will trigger EMTA review.

## VAT Number Verification

Before including a customer on Form VD:
1. Verify their VAT number using the EU VIES database (ec.europa.eu/taxation_customs/vies)
2. Record verification date and result
3. If VAT number is invalid, the supply **cannot be zero-rated** — standard rate applies

## XML Format

```xml
<VD xmlns="http://emta.ee/schemas/vat">
  <Period>
    <Year>2025</Year>
    <Month>01</Month>
  </Period>
  <TaxpayerRegCode>12345678</TaxpayerRegCode>
  <TaxpayerVATNumber>EE123456789</TaxpayerVATNumber>
  <Entry>
    <CustomerVATNumber>FI12345678</CustomerVATNumber>
    <CountryCode>FI</CountryCode>
    <SupplyType>G</SupplyType>
    <Amount>15000.00</Amount>
  </Entry>
  <Entry>
    <CustomerVATNumber>DE987654321</CustomerVATNumber>
    <CountryCode>DE</CountryCode>
    <SupplyType>S</SupplyType>
    <Amount>8500.00</Amount>
  </Entry>
</VD>
```
