# KMD Form Structure (Kaibemaksudeklaratsioon)

The Estonian VAT return (KMD) has lines 1-13. Each line is populated by classifying
the entity's tax codes based on their **properties**, not their names.

## Property-Based Classification Rules

Use these rules to map any tax code to the correct KMD line. Query tax codes via:

```
list_entities("tax_code", {"legal_entity_id": <id>, "country_code": "EE", "is_active": true})
```

Each tax code has: `default_rate`, `is_reverse_charge`, `is_recoverable`, `tax_type`, `tax_scope`, `metadata`.

### Output VAT Lines (Sales)

| KMD Line | Description (Estonian) | Classification Rule | Formula |
|---|---|---|---|
| **1** | 24% maariga maksustatav kaive | `default_rate = 0.24` AND `is_reverse_charge = false` AND sales transactions | Sum of taxable base amounts |
| **1.1** | Kaibemaks (24%) | - | VAT amount from Line 1 transactions (or Line 1 x 0.24) |
| **2** | Maariga 13% / 9% maksustatav kaive | `default_rate IN (0.13, 0.09)` AND `is_reverse_charge = false` AND sales transactions | Sum of taxable base amounts |
| **2.1** | Kaibemaks ridadelt 2 | - | VAT amount from Line 2 transactions |
| **3** | 0% maariga maksustatav kaive (eksport) | `default_rate = 0` AND NOT intra-community AND sales to non-EU customers | Sum of export amounts |
| **3.1** | Uhenduseisisene kaupade tarne | `default_rate = 0` AND intra-community goods supply (EU B2B customer with VAT ID) | Sum of IC goods supply amounts |
| **3.2** | Uhenduseisisene teenuste osutamine | `default_rate = 0` AND intra-community services supply (EU B2B services) | Sum of IC services amounts |

### Input VAT Lines (Purchases)

| KMD Line | Description (Estonian) | Classification Rule | Formula |
|---|---|---|---|
| **4** | Sisendkaibemaks kokku | `is_recoverable = true` AND purchase transactions | Sum of VAT amounts from AP invoices |
| **4.1** | Sisendkaibemaks pohinvaralt | `is_recoverable = true` AND posted to fixed asset accounts (1500-1599) | Subset of Line 4 |

### Reverse Charge / IC Acquisition Lines

| KMD Line | Description (Estonian) | Classification Rule | Formula |
|---|---|---|---|
| **5** | Uhenduseisisene kaupade soetamine | `is_reverse_charge = true` AND `tax_type` indicates IC acquisition of goods | Sum of taxable base amounts |
| **5.1** | Uhenduseisisene teenuste saamine | `is_reverse_charge = true` AND `tax_type` indicates IC acquisition of services | Sum of taxable base amounts |
| **6** | Poordomaksustamine - kaup | `is_reverse_charge = true` AND domestic reverse charge goods (e.g., investment gold) | Sum of taxable base amounts |
| **7** | Poordomaksustamine - kinnisvara, metallijaam | `is_reverse_charge = true` AND domestic reverse charge for real estate or scrap metal | Sum of taxable base amounts |

### Adjustment and Total Lines

| KMD Line | Description | Formula |
|---|---|---|
| **8** | Korrigeerimine (+/-) | Manual adjustments: credit notes, corrections, bad debt relief |
| **9** | Reserved | Not currently used |
| **10** | Kaibemaks kokku | (Line 1.1 + Line 2.1) - Line 4 + adjustments |
| **11** | Impordi kaibemaks | Import VAT from customs declarations (`tax_type = 'import'` or `metadata.is_import = true`) |
| **12** | Tasumisele kuuluv kaibemaks | If (Line 10 + Line 11) > 0: amount payable |
| **13** | Enammakstud kaibemaks | If (Line 10 + Line 11) < 0: overpayment (refund) |

## How to Classify Tax Codes

For each tax code returned by the API, apply these rules in order:

1. **Check `is_reverse_charge`**: If true, classify into Lines 5/5.1/6/7 based on `tax_type` or `metadata`
2. **Check `default_rate`**:
   - `0.24` → Line 1 (sales) or input VAT (purchases)
   - `0.13` or `0.09` → Line 2 (sales)
   - `0` → Lines 3/3.1/3.2 depending on customer type (EU vs non-EU)
3. **Check `is_recoverable`**: If true on purchase side → Line 4
4. **Check `tax_type` or `metadata`** for import VAT → Line 11

## Distinguishing Lines 3, 3.1, 3.2

These three lines all have `default_rate = 0` but differ by transaction context:

- **Line 3**: Customer is outside EU (export)
- **Line 3.1**: Customer is in EU with valid VAT ID + supply is goods
- **Line 3.2**: Customer is in EU with valid VAT ID + supply is services

To determine this, check the customer's `country_code` and `tax_id` (EU VAT number).
