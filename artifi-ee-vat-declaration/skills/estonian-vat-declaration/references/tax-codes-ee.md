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
| `tax_scope` | String | Jurisdictional scope, the PRIMARY line-6-vs-7 signal (vocabulary enforced by a DB CHECK, see migration 464): `domestic`, `intra_union_goods`, `intra_union_services`, `import`, `foreign_reverse_charge`, `export`, `exempt`. NULL on unclassified org-local/imported codes — ask the user how to report those. |
| `country_code` | String | Always 'EE' for Estonian codes |
| `metadata` | JSONB | Additional flags (e.g., `{"kmd_element": "importVat", "is_import": true}`) |
| `reporting_code_override` | String | Entity-level KMD element override (if set, use this directly) |

## Classification Decision Tree

Targets are **KMD2 element names** (see `references/kmd-form-structure.md`). Reverse-charge
purchases map to a **base** line (6/7); their deductible VAT is separately accumulated
into `inputVatTotal` (line 5).

```
1. Does the tax code have `reporting_code_override`?
   YES → Use that KMD2 element directly
   NO  → Continue to step 2

2. Is `is_reverse_charge = true`?  (base line derived from `tax_scope`.
   `reporting_code_override` is the only explicit override — step 1;
   `metadata.kmd_line` is a FALLBACK for NULL-scope codes only: legacy seed
   packs carry stale kmd_line values that do not match the official form)
   YES → by tax_scope:
         - `intra_union_goods` or `intra_union_services` (IC acquisition, EU supplier)
                                    → euAcquisitionsGoodsAndServicesTotal (line 6)
             · `intra_union_goods` subset → euAcquisitionsGoods (line 6.1)
         - `foreign_reverse_charge` (services from a non-EU supplier)
                                    → acquisitionOtherGoodsAndServicesTotal (line 7)
         - `domestic` (§ 41¹ domestic reverse charge: immovables/scrap/precious metal)
                                    → acquisitionImmovablesAndScrapMetalAndGold (line 7.1)
         - NULL scope → do NOT guess between line 6 and 7: fall back to
           `metadata.kmd_line` if present, otherwise ask the user.
         (If recoverable, also add the self-assessed VAT to inputVatTotal, line 5.)
   NO  → Continue to step 3

3. Check `default_rate` on the SALES side (base):
   - 0.24 → transactions24 (line 1)        - 0.05 → transactions5 (line 2¹)
   - 0.22 → transactions22 (line 1)         - 0.13 → transactions13 (line 2²)
   - 0.20 → transactions20 (line 1¹)        - 0.09 → transactions9 (line 2)
   - 0    → by counterparty:
            - Non-EU customer          → exportZeroVat (line 3.2)
            - EU business + goods      → euSupplyGoodsZeroVat (3.1.1) within euSupplyInclGoodsAndServicesZeroVat (3.1)
            - EU business + services   → euSupplyInclGoodsAndServicesZeroVat (3.1)
            - other zero-rated         → transactionsZeroVat (line 3)

4. For PURCHASE-side tax codes (VAT amounts):
   - `is_recoverable = true` → add to inputVatTotal (line 5)
            · on a fixed-asset account → also fixedAssetsVat (line 5.2)
            · import VAT paid in customs (`tax_type='import'` / `metadata.is_import`) → also importVat (line 5.1)
```

## Standard Estonian Tax Codes (Examples)

These are the default codes shipped with Arfiti. Clients may rename or create their own.

| Example Code | Rate | Reverse Charge | Recoverable | KMD2 element (line) |
|---|---|---|---|---|
| `EE_VAT_24` | 24% | No | - | `transactions24` (1) |
| `EE_VAT_13` | 13% | No | - | `transactions13` (2²) |
| `EE_VAT_9` | 9% | No | - | `transactions9` (2) |
| `EE_VAT_0_EXPORT` | 0% | No | - | `exportZeroVat` (3.2) |
| `EE_VAT_0_IC_GOODS` | 0% | No | - | `euSupplyGoodsZeroVat` (3.1.1) |
| `EE_VAT_0_IC_SERVICES` | 0% | No | - | `euSupplyInclGoodsAndServicesZeroVat` (3.1) |
| `EE_VAT_IC_ACQ_GOODS` | 24% | Yes | Yes | `euAcquisitionsGoods` (6.1) → base in line 6; VAT in line 5 |
| `EE_VAT_IC_ACQ_SERVICES` | 24% | Yes | Yes | `euAcquisitionsGoodsAndServicesTotal` (6); VAT in line 5 |
| `EE_VAT_RC_SERVICES_NONEU` | 24% | Yes | Yes | `acquisitionOtherGoodsAndServicesTotal` (7); VAT in line 5 |
| `EE_VAT_RC_REAL_ESTATE` | 24% | Yes | Yes | `acquisitionImmovablesAndScrapMetalAndGold` (7.1) |
| `EE_VAT_RC_SCRAP` | 24% | Yes | Yes | `acquisitionImmovablesAndScrapMetalAndGold` (7.1) |
| `EE_VAT_IMPORT` | 24% | No | Yes | `inputVatTotal` (5) + `importVat` (5.1) |
| `EE_VAT_EXEMPT` | 0% | No | No | `supplyExemptFromTax` (8) |

## Discovery Query

Always start by fetching the entity's actual tax codes:

```
list_entities("tax_code", {"legal_entity_id": <id>, "country_code": "EE", "is_active": true})
```

Then classify each code using the decision tree above. Present the classification
to the user for confirmation before calculating KMD amounts.
