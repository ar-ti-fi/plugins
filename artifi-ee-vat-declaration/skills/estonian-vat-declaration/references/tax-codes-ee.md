# Estonian Tax Code Classification

This reference describes how to classify Estonian tax codes into KMD lines
using their **properties**. Do NOT rely on specific tax code names — clients
may have custom codes. Always classify by properties.

## Classification Properties

Each tax code in `v_tax_codes_effective` has these relevant properties:

| Property | Type | Description |
|---|---|---|
| `default_rate` | Decimal | Tax rate (0.24, 0.13, 0.09, 0) |
| `is_reverse_charge` | Boolean | Whether reverse charge mechanism applies |
| `is_recoverable` | Boolean | Whether input VAT is recoverable |
| `tax_type` | String | Category (e.g., 'output', 'input', 'import', 'reverse_charge') |
| `tax_scope` | String | Scope (e.g., 'domestic', 'intra_community', 'export') |
| `country_code` | String | Always 'EE' for Estonian codes |
| `metadata` | JSONB | Additional flags (e.g., `{"kmd_line": "5", "is_import": true}`) |
| `reporting_code_override` | String | Entity-level KMD line override (if set, use this directly) |

## Classification Decision Tree

```
1. Does the tax code have `reporting_code_override`?
   YES → Use that value as the KMD line directly
   NO  → Continue to step 2

2. Is `is_reverse_charge = true`?
   YES → Check tax_type/metadata:
         - IC acquisition goods    → Line 5
         - IC acquisition services → Line 5.1
         - Domestic RC goods       → Line 6
         - Domestic RC real estate/scrap → Line 7
   NO  → Continue to step 3

3. Check `default_rate`:
   - 0.24 → Output: Line 1 (sales) / Input: Line 4 (purchases)
   - 0.13 or 0.09 → Line 2 (sales only)
   - 0    → Check transaction context:
            - Non-EU customer       → Line 3 (export)
            - EU customer + goods   → Line 3.1
            - EU customer + services → Line 3.2

4. For purchase-side tax codes:
   - `is_recoverable = true` → Line 4 (or 4.1 if on asset account)
   - Check for import: `tax_type = 'import'` or `metadata.is_import` → Line 11
```

## Standard Estonian Tax Codes (Examples)

These are the default codes shipped with Arfiti. Clients may rename or create their own.

| Example Code | Rate | Reverse Charge | Recoverable | Typical KMD Line |
|---|---|---|---|---|
| `EE_VAT_24` | 24% | No | - | 1 (sales) |
| `EE_VAT_13` | 13% | No | - | 2 (sales) |
| `EE_VAT_9` | 9% | No | - | 2 (sales) |
| `EE_VAT_0_EXPORT` | 0% | No | - | 3 |
| `EE_VAT_0_IC_GOODS` | 0% | No | - | 3.1 |
| `EE_VAT_0_IC_SERVICES` | 0% | No | - | 3.2 |
| `EE_VAT_IC_ACQ_GOODS` | 24% | Yes | Yes | 5 |
| `EE_VAT_IC_ACQ_SERVICES` | 24% | Yes | Yes | 5.1 |
| `EE_VAT_RC_GOODS` | 24% | Yes | Yes | 6 |
| `EE_VAT_RC_REAL_ESTATE` | 24% | Yes | Yes | 7 |
| `EE_VAT_RC_SCRAP` | 24% | Yes | Yes | 7 |
| `EE_VAT_IMPORT` | 24% | No | Yes | 11 |
| `EE_VAT_EXEMPT` | 0% | No | No | - (not reported) |

## Discovery Query

Always start by fetching the entity's actual tax codes:

```
list_entities("tax_code", {"legal_entity_id": <id>, "country_code": "EE", "is_active": true})
```

Then classify each code using the decision tree above. Present the classification
to the user for confirmation before calculating KMD amounts.
