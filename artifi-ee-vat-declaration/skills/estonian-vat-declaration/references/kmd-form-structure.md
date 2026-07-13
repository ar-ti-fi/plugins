# KMD Form Structure (Käibemaksudeklaratsioon) — KMD2 format

The Estonian VAT return is the **KMD2** dataset, defined by e-MTA in
`vatdeclaration.xsd` (bundled at `scripts/vatdeclaration.xsd`). The generator
`scripts/generate_kmd.py` produces two artifacts from this data:

- **`KMD_YYYYMM_{regcode}.csv`** — the KMD2 **machine CSV** (fixed 31-column format;
  see `references/emta-filing-guide.md`). **Primary artifact** — the format e-MTA
  accepts for CSV upload (not the English prose-header export, which is rejected).
- **`vatDeclaration_YYYYMM_{regcode}.xml`** — the full KMD2 XML (main form + KMD INF
  A/B annexes), validated against the XSD.

There is **no** `<KMD>` element and **no** `http://emta.ee/schemas/vat` namespace —
that earlier format was fabricated. The root is `vatDeclaration` with **no XML
namespace** (the schema has no `targetNamespace`).

## Document shape

```
vatDeclaration                     (root, no namespace)
├── taxPayerRegCode                 mandatory — reg/personal code
├── submitterPersonCode             optional — required for the machine interface
├── year                            mandatory
├── month                           mandatory (1–12)
├── declarationType                 mandatory — 1 = normal, 2 = bankruptcy
├── version                         mandatory — KMD4 (2024) / KMD5 (01–06.2025) / KMD6 (07.2025+)
├── declarationBody                 the KMD main form (optional part, see below)
├── salesAnnex        [0..n]        KMD INF A — sales partners
└── purchasesAnnex    [0..n]        KMD INF B — purchase partners
```

Each of the three data parts (`declarationBody`, `salesAnnex`, `purchasesAnnex`) is
independently optional — you may file one, two, or all three — but the general part
(reg code, year, month, declarationType, version) is **always** mandatory.

## declarationBody — the main form

The four flags are mandatory; every value element is optional and carries a taxable
**base** by rate, except the input-VAT lines (5.x) which are VAT **amounts**.

### Mandatory flags

| Element | Meaning |
|---|---|
| `noSales` | `true` when no sales partner exceeds the KMD INF threshold (then omit `salesAnnex`) |
| `noPurchases` | `true` when no purchase partner exceeds the threshold (then omit `purchasesAnnex`) |
| `sumPerPartnerSales` | `true` = KMD INF A reported summed per partner (invoice no./date optional) |
| `sumPerPartnerPurchases` | `true` = KMD INF B reported summed per partner |

`generate_kmd.py` derives all four automatically from whether annex lines are present.

### Output side — taxable bases by rate

| KMD line | Element | Classification rule (property-based) |
|---|---|---|
| **1** | `transactions24` | `default_rate = 0.24`, not reverse charge, sales — **standard rate from 07.2025** |
| **1** | `transactions22` | `default_rate = 0.22` (legacy standard rate, 2024) |
| **1¹** | `transactions20` | `default_rate = 0.20` (legacy standard rate, ≤2023) |
| **2** | `transactions9` | `default_rate = 0.09` |
| **2¹** | `transactions5` | `default_rate = 0.05` |
| **2²** | `transactions13` | `default_rate = 0.13` (from 01.2025) |
| **3** | `transactionsZeroVat` | `default_rate = 0`, zero-rated (incl. total) |
| **3.1** | `euSupplyInclGoodsAndServicesZeroVat` | intra-Community supply of goods + services to EU-VAT-registered customers, total |
| **3.1.1** | `euSupplyGoodsZeroVat` | intra-Community supply of **goods** (subset of 3.1) |
| **3.2** | `exportZeroVat` | export of goods (non-EU) |
| **3.2.1** | `salePassengersWithReturnVat` | sale to passengers with VAT refund (subset of 3.2) |

### Input side — deductible VAT amounts

| KMD line | Element | Meaning |
|---|---|---|
| **5** | `inputVatTotal` | **total deductible input VAT** (the whole line-5 figure) |
| **5.1** | `importVat` | VAT paid on import in customs (subset of 5) |
| **5.2** | `fixedAssetsVat` | input VAT on acquisition of fixed assets (subset of 5) |
| **5.3** | `carsVat` + `numberOfCars` | input VAT + count of 100%-business cars |
| **5.4** | `carsPartialVat` + `numberOfCarsPartial` | input VAT + count of partial-business cars |

### Reverse charge / acquisitions

| KMD line | Element | Classification rule |
|---|---|---|
| **6** | `euAcquisitionsGoodsAndServicesTotal` | intra-Community acquisitions of goods + services received from an EU supplier, total |
| **6.1** | `euAcquisitionsGoods` | intra-Community acquisitions of **goods** (subset of 6) |
| **7** | `acquisitionOtherGoodsAndServicesTotal` | services received from a **non-EU** supplier + domestic reverse charge |
| **7.1** | `acquisitionImmovablesAndScrapMetalAndGold` | § 41¹ special-scheme acquisitions (subset of 7) |

### Exempt / special / adjustments

| KMD line | Element | Meaning |
|---|---|---|
| **8** | `supplyExemptFromTax` | supply exempt from VAT |
| **9** | `supplySpecialArrangements` | § 41¹ special-scheme supply + goods installed/assembled in another MS |
| **10** | `adjustmentsPlus` | adjustments (+), non-negative |
| **11** | `adjustmentsMinus` | adjustments (−), non-negative |

## Lines computed by e-MTA — never emitted in the XML

e-MTA derives these itself from the bases + `inputVatTotal`. There are **no** XSD
elements for them, so the XML must not contain them:

e-MTA derives these itself; **neither the XSD nor the machine CSV has fields for
them**, so never emit them:

| KMD line | Meaning | Formula e-MTA uses |
|---|---|---|
| **4** | Total VAT | `Σ(base × rate)` over the six standard rates — the rate-line bases **include reverse-charge/IC acquisitions** |
| **12** | VAT payable | `max(0, line4 + line4¹ − line5 + line10 − line11)` |
| **13** | VAT overpaid / refundable | `max(0, −(…))` |

`generate_kmd.py` computes line 4 / 12 / 13 for the console summary only; they are for
human eyeballing and appear in no output file.

> **Reverse charge — critical (corrected 2026-07-13 per EMTA's official
> completion guidance).** The KMD declares taxable transactions **by rate,
> including** intra-Community acquisitions and services received under reverse
> charge ("sealhulgas kauba ühendusesisene soetamine … teenuste saamine
> (pöördmaksustamine)"). So the acquisition bases go **inside the rate lines**
> (`transactions24` for 24%) — that is what produces the self-assessed VAT in
> e-MTA's line 4 — and the deductible side goes into `inputVatTotal` (line 5).
> Lines **6 / 6.1 / 7 / 7.1 are "informatiivsed lahtrid" (informative)**: fill
> them with the acquisition breakout, but a base that appears only there never
> enters the calculation. For a full-deduction taxpayer the RC output and
> deduction cancel (refund unchanged); a partial-deduction taxpayer puts only
> the deductible portion in line 5 while line 4 carries the full self-assessed
> VAT. `generate_kmd.py` rejects inputs whose lines 6+7 exceed the rate-line
> bases.
>
> **History:** an earlier version of this plugin prescribed the opposite
> ("bases only on 6/7, never grossed into lines 1/5"). Both conventions yield
> identical lines 12/13 for a full-deduction taxpayer — which is why returns
> filed under the old rule were still accepted by e-MTA — but the official
> guidance is unambiguous, and only the corrected form is right for partial
> deduction.
> Source: https://www.emta.ee/ariklient/maksud-ja-tasumine/kaibemaks/kaibedeklaratsiooni-ja-aruannete-esitamine/kaibedeklaratsiooni-taitmine

## How to classify tax codes

Do **not** hardcode tax-code names. Query the entity's codes and classify by
properties (see `references/tax-codes-ee.md`):

```
list_entities("tax_code", {"legal_entity_id": <id>, "country_code": "EE", "is_active": true})
```

For each code, in order:

1. **`reporting_code_override`** — if the entity pins a code to a specific KMD line, use it.
2. **`is_reverse_charge = true`** → line 6 (EU) or line 7 (non-EU / domestic reverse charge).
3. **`default_rate`** on the sales side → `transactions24/22/20/9/5/13`, `transactionsZeroVat`, or an EU/export line by counterparty.
4. **Purchase side, recoverable** → accumulate into `inputVatTotal`; split `importVat` / `fixedAssetsVat` / `carsVat` where the account or metadata says so.

## Distinguishing the zero-rated lines

`transactionsZeroVat`, `euSupplyInclGoodsAndServicesZeroVat`, and `exportZeroVat` all
have `default_rate = 0` but differ by counterparty:

- **Export (`exportZeroVat`, 3.2)** — customer outside the EU.
- **EU supply (`euSupplyInclGoodsAndServicesZeroVat`, 3.1)** — customer is an
  EU-VAT-registered business; `euSupplyGoodsZeroVat` (3.1.1) is the goods subset. The
  same figures feed the EC Sales List (Form VD).
- **Other zero-rated (`transactionsZeroVat`, 3)** — the incl. total for line 3.
