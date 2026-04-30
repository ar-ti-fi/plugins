# TSD XML Format Reference

**Authoritative XSD:** `tsd_schema_01.01.2025_eng.xsd` (also valid against `tsd_schema_eng_01.01.2023.xsd` for v1 scope).
**Filing portal:** https://maasikas.emta.ee
**Sample reference filing:** `/Users/andrewrudchuk/Downloads/TSD 2026 4.xml` (April 2026 board-fee filing — used as the golden master for `test_tsd_round_trip.py`).

This document covers the **real e-MTA XML format** produced by `scripts/generate_tsd.py`. For payment-type and exemption-type code lookups, see `tsd-codes.md`.

---

## Top-level structure

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<tsd_vorm>
    <c108_Aasta>2026</c108_Aasta>
    <c109_Kuu>4</c109_Kuu>
    <c110_Tm>169.40</c110_Tm>            <!-- Income tax withheld (calculated rollup) -->
    <c114_TmEj>0.00</c114_TmEj>          <!-- Special income tax (capital distributions, fringe benefits) -->
    <c115_Sm>495.00</c115_Sm>            <!-- Social tax -->
    <c116_Tk>0.00</c116_Tk>              <!-- Unemployment insurance (employee + employer) -->
    <c117_Kp>30.00</c117_Kp>             <!-- Mandatory funded pension (II pillar) -->
    <c118_KohustKokku>694.40</c118_KohustKokku>   <!-- Total tax obligation -->
    <c119_TagastKokku>0.00</c119_TagastKokku>     <!-- Refund total (negative obligation, sign-flipped) -->
    <laadimisViis>P</laadimisViis>       <!-- L = new; P = amend in-progress (default) -->
    <regKood>17266831</regKood>          <!-- 8-digit company registry code -->

    <tsd_L1_0>...</tsd_L1_0>             <!-- Annex 1 (resident natural persons) -->

    <vorm>TSD</vorm>                     <!-- Mandatory; always TSD for this form -->
</tsd_vorm>
```

**Critical rules:**
1. **No XML namespace.** The root is `<tsd_vorm>`, not `<TSD xmlns="...">`. Do NOT add `xmlns`.
2. **Element naming is `c{NNN}_{EstonianFieldName}`** — `c1020_ValiKood`, `c1150_TuliKood`, `c108_Aasta`, etc. The number prefix is always 3-4 digits + underscore.
3. **`<vorm>TSD</vorm>` is mandatory** and must be present. Without it the filing is rejected.
4. **`<regKood>` placement varies** in real filings (canonical example places it after `c119_TagastKokku`). Because the XSD uses `<xs:all>`, child order doesn't matter for validation — but matching the canonical layout minimizes diff noise.
5. **UTF-8 with BOM.** The generator writes with `utf-8-sig` so the BOM is included; the e-MTA portal expects this.
6. **Decimals: `xs:decimal` with `fractionDigits=2`.** We always emit 2 decimals (`1500.00`, `169.40`); the canonical filing strips trailing zeros (`1500`, `169.4`) — both are valid; the semantic round-trip test compares numerically.

---

## Annex 1 — Resident natural persons (`tsd_L1_0`)

Annex 1 is the only annex implemented in v1. Annexes 2-8 + INF1 follow in later releases.

```xml
<tsd_L1_0>
    <aIsikList>
        <tsd_L1_A_Isik>
            <c1000_Kood>38704290190</c1000_Kood>          <!-- Personal ID (isikukood) -->
            <c1010_Nimi>ANDRII RUDCHUK</c1010_Nimi>       <!-- Single field, "FIRST LAST" uppercase -->
            <vmList>
                <tsd_L1_A_Vm>
                    <c1020_ValiKood>21</c1020_ValiKood>   <!-- Payment type (10/11/12/13/21/27/...) -->
                    <c1030_Summa>1500.00</c1030_Summa>    <!-- Gross -->
                    <c1060_Smvm>1500.00</c1060_Smvm>      <!-- Social tax base (usually = gross) -->
                    <c1100_Sm>495.00</c1100_Sm>           <!-- Social tax = base × 33% -->
                    <c1110_Kp>30.00</c1110_Kp>            <!-- COMBINED: pension + unemp_employee -->
                    <c1170_Tm>169.40</c1170_Tm>           <!-- Income tax = (gross − Kp − exemptions) × 22% -->
                    <mvtList>
                        <tsd_L1_A_Mvt>
                            <c1150_TuliKood>610</c1150_TuliKood>    <!-- Exemption type (610=basic) -->
                            <c1160_Summa>700.00</c1160_Summa>       <!-- Exemption amount -->
                        </tsd_L1_A_Mvt>
                    </mvtList>
                </tsd_L1_A_Vm>
            </vmList>
        </tsd_L1_A_Isik>
    </aIsikList>

    <!-- Annex 1 totals (computed automatically by the generator) -->
    <c1200_Smvm>1500.00</c1200_Smvm>
    <c1210_Sm>495.00</c1210_Sm>
    <c1220_Kp>30.00</c1220_Kp>
    <c1250_Tm>169.40</c1250_Tm>
</tsd_L1_0>
```

### `c1110_Kp` — combined column

This is the part of the schema that surprises plugin authors most often: `c1110_Kp` is **one field** that combines both:
- Mandatory funded pension (II pillar, 2% / 4% / 6%)
- Employee unemployment insurance (1.6%)

These are calculated separately during payroll but reported as a single number per payment row. Header-level `c117_Kp` rolls up the **pension portion only**; `c116_Tk` rolls up unemployment insurance (employee + employer); the per-row `c1110_Kp` is the sum withheld from the employee's pay.

The canonical April 2026 filing has `c1110_Kp = 30.00` for a 1500 gross salary at 2% pension (no unemployment). For a 1500 salary at 2% pension + 1.6% unemployment-employee, `c1110_Kp` would be 1500 × (2% + 1.6%) = 54.00.

---

## Header roll-up math

The generator computes header c110-c119 from per-payment rows. Any value provided by the caller in `header_overrides` takes precedence (use sparingly — only for amended returns).

| Header field | Formula |
|---|---|
| `c110_Tm` | Σ `c1170_Tm` across all `tsd_L1_A_Vm` rows |
| `c114_TmEj` | Special income tax (capital distributions, fringe benefits — Annexes 4/5/6) — **0 in v1** |
| `c115_Sm` | Σ `c1100_Sm` |
| `c116_Tk` | Σ `c1130_Tk` (employee unemp) + Σ `c1140_Ttk` (employer unemp) |
| `c117_Kp` | Σ `c1220_Kp` (pension portion of `c1110_Kp` — for v1 with no separate-funded handling, this is Σ `c1110_Kp`) |
| `c118_KohustKokku` | `c110 + c114 + c115 + c116 + c117` if ≥ 0; else 0 |
| `c119_TagastKokku` | `−(c110 + c114 + c115 + c116 + c117)` if < 0; else 0 |

### Sign convention

`c1110_Kp` increases the obligation — the employer withholds it from the employee's gross and remits it to MTA along with social tax. So it's a positive number on the employer's filing. (It's negative on the employee's payslip from the employee's perspective, but the TSD is the employer's filing.)

---

## Tax-free amount sub-records (`tsd_L1_A_Mvt`)

Optional `<mvtList>` inside each `<tsd_L1_A_Vm>` carries the deductions applied **before** income tax:

```xml
<mvtList>
    <tsd_L1_A_Mvt>
        <c1150_TuliKood>610</c1150_TuliKood>     <!-- Basic exemption -->
        <c1160_Summa>700.00</c1160_Summa>
    </tsd_L1_A_Mvt>
    <tsd_L1_A_Mvt>
        <c1150_TuliKood>620</c1150_TuliKood>     <!-- Pension contribution deduction -->
        <c1160_Summa>30.00</c1160_Summa>
    </tsd_L1_A_Mvt>
</mvtList>
```

The income-tax base is `c1030_Summa − c1110_Kp − Σ c1160_Summa`. The generator validates this identity within ±0.02.

For the full code table see `tsd-codes.md` (c1150_TuliKood section).

---

## Payment validation rules (enforced by `validate()` in generate_tsd.py)

1. **Per-row social tax**: `c1100_Sm` must equal `c1060_Smvm × 33%` within ±0.02
2. **Per-row income tax**: `c1170_Tm` must equal `(c1030_Summa − c1110_Kp − Σ c1160_Summa) × 22%` within ±0.02
3. **Personal ID present** on every `tsd_L1_A_Isik`
4. **payment_type_code (`c1020_ValiKood`) present** on every `tsd_L1_A_Vm`
5. **gross > 0** on every `tsd_L1_A_Vm`

The portal additionally validates:
- Personal ID checksum (Estonian isikukood)
- regKood format (8 digits)
- payment_type_code ↔ tax-type business rules (e.g., board fee → no unemployment insurance)

If the portal rejects a generated XML, paste the error here and we'll add a check to the generator.

---

## Annex 2 — Non-resident natural persons (`tsd_L2_0`)

Annex 2 mirrors Annex 1's structure but for non-residents (e.g. Finnish contractor, German board member working remotely). The c-code numbering is parallel: c1xxx → c2xxx.

```xml
<tsd_L2_0>
    <aIsikList>
        <tsd_L2_A_Isik>
            <c2000_Kood>FI-12345-67890</c2000_Kood>            <!-- Foreign personal/registry ID -->
            <c2010_Nimi>MIKKO VIRTANEN</c2010_Nimi>             <!-- Full name (uppercase) -->
            <vmList>
                <tsd_L2_A_Vm>
                    <c2020_RiikKood>FI</c2020_RiikKood>          <!-- ISO 3166-1 country of residence (REQUIRED) -->
                    <c2030_ValiKood>120</c2030_ValiKood>         <!-- Payment type (120 = service, 122 = royalty, etc.) -->
                    <c2040_Summa>1000.00</c2040_Summa>           <!-- Gross -->
                    <c2060_RiikKood>FI</c2060_RiikKood>          <!-- A1/E101 certificate country (optional; signals SS treaty) -->
                    <c2070_Smvm>0.00</c2070_Smvm>                <!-- Social tax base (0 if non-resident with no A1) -->
                    <c2110_Sm>0.00</c2110_Sm>                    <!-- Social tax (typically 0 for non-residents w/o A1) -->
                    <c2150_Tmvm>1000.00</c2150_Tmvm>             <!-- Income tax base -->
                    <c2160_TmMaar>22.00</c2160_TmMaar>           <!-- Income tax rate (treaty: 10%, 0%, etc.) -->
                    <c2170_Tm>220.00</c2170_Tm>                  <!-- Income tax withheld -->
                    <mvtList>
                        <tsd_L2_A_Mvt>
                            <c2154_TuliKood>650</c2154_TuliKood> <!-- Non-resident-specific exemption code -->
                            <c2155_Summa>704.00</c2155_Summa>
                        </tsd_L2_A_Mvt>
                    </mvtList>
                </tsd_L2_A_Vm>
            </vmList>
        </tsd_L2_A_Isik>
    </aIsikList>

    <c2200_Smvm>0.00</c2200_Smvm>      <!-- Annex 2 totals (auto-computed) -->
    <c2210_Sm>0.00</c2210_Sm>
    <c2220_Tk>0.00</c2220_Tk>
    <c2230_Ttk>0.00</c2230_Ttk>
    <c2240_Tmvm>1000.00</c2240_Tmvm>
    <c2250_Tm>220.00</c2250_Tm>
</tsd_L2_0>
```

**Roll-up into header:**
- `c2210_Sm` → header `c115_Sm`
- `c2220_Tk + c2230_Ttk` → header `c116_Tk`
- `c2250_Tm` → header `c110_Tm`

**Differences from Annex 1:**
- Income tax rate is **explicit per-row** (`c2160_TmMaar`) — Annex 1 implicitly uses 22%; Annex 2 supports treaty rates (0%, 10%, 22%).
- Country of residence (`c2020_RiikKood`) is mandatory — drives treaty-rate lookup at the portal.
- Income-tax math is **looser** — generator doesn't cross-check `gross × rate = tax` because some treaty cases include exemptions that don't fit the simple formula. Caller is responsible for the math.
- Funded pension (II pillar) typically doesn't apply to non-residents and isn't part of `<tsd_L2_A_Vm>` rows.

**Routing:** the calling skill splits ERP `persons[]` into resident → Annex 1 `persons` and non-resident → `non_resident_persons` based on `master_employees.metadata.tax_filing.residency`. Empty Annex 1 is fine (only emit `<tsd_L1_0>` when there's at least one resident person).

For the c2030_ValiKood / c2154_TuliKood code tables, see `tsd-codes.md`.

---

## Annex 4 — Fringe benefits (`tsd_L4_0`)

Annex 4 is a **scalar-only** block — no per-person nesting. The caller fills in the categories that apply for the period; the generator emits a `<tsd_L4_0>` only when at least one field is populated.

```xml
<tsd_L4_0>
    <c4040_Ts>300.00</c4040_Ts>           <!-- Company vehicle for non-business use -->
    <c4140_EsSumma>300.00</c4140_EsSumma> <!-- Total taxable representation amount -->
    <c4170_TmEj>84.62</c4170_TmEj>        <!-- Special income tax (= 300 × 22/78 ≈ 84.62) -->
    <c4180_Sm>125.27</c4180_Sm>           <!-- Social tax (= (300 + 84.62) × 33% ≈ 126.92, see note) -->
    <c4181_SmEs>379.62</c4181_SmEs>       <!-- Social tax base (taxable + grossed-up income tax) -->
</tsd_L4_0>
```

**Roll-up into header:**
- `c4170_TmEj` rolls into `c114_TmEj`
- `c4180_Sm` rolls into `c115_Sm`

**Tax math (calculated by the caller, validated by e-MTA):**
- `c4170_TmEj = c4140_EsSumma × 22/78` (gross-up — the employer pays 22% income tax on the value of the benefit, treating the benefit as the net amount)
- `c4180_Sm = c4181_SmEs × 33%` where `c4181_SmEs = c4140_EsSumma + c4170_TmEj`

The full c4xxx field list (with input-key names) is in `tsd-codes.md`.

## Annex 5 — Gifts, donations, entertainment (`tsd_L5_0`)

Same scalar-only pattern as Annex 4. Three logical sections:

```xml
<tsd_L5_0>
    <c5000_Ki>200.00</c5000_Ki>             <!-- General gifts/donations -->
    <c5010_IKiKuu>0.00</c5010_IKiKuu>       <!-- Gifts to listed nonprofits this month -->
    <c5020_IKiAasta>0.00</c5020_IKiAasta>   <!-- ...YTD cumulative -->
    <c5100_KyKuluKuu>100.00</c5100_KyKuluKuu>   <!-- Entertainment expenses this month -->
    <c5110_KyKuluAasta>100.00</c5110_KyKuluAasta>  <!-- ...YTD -->
    <c5120_KyIsmv>50.00</c5120_KyIsmv>      <!-- 2% threshold of personalized payouts -->
    <c5160_TasTmEj>12.82</c5160_TasTmEj>    <!-- Special income tax payable -->
</tsd_L5_0>
```

**Roll-up into header:**
- `c5160_TasTmEj` and `c5190_TmEj` roll into `c114_TmEj`

**CoA-driven sourcing (Annex 5 only):** transactions touching accounts whose `metadata.filing_categories[]` includes `{form: TSD, annex: 5, code: ...}` aggregate into the matching c-code. EE seed tags accounts:

| EE account | Annex 5 c-code | Bucket |
|---|---|---|
| `6850` Business Entertainment | `c5100_KyKuluKuu` | Entertainment |
| `6860` Gifts and Hospitality (Non-Employee) | `c5000_Ki` | General gifts |
| `6870` Charitable Donations and Sponsorship | `c5010_IKiKuu` | Listed-charity gifts |

These accounts are created by the EE onboarding seeder (`setup_account_filing_categories`) — no manual setup needed in fresh orgs. In orgs with customized CoAs where `6850–6870` are already used for unrelated purposes, the seeder skips them with a warning (it only tags accounts whose name matches the country template).

## Annex 7 — Dividends + equity distributions (`tsd_L7_0`)

Annex 7 is **scalar-only** (the recipient list lives in INF1). The XSD has 30+ optional fields; service-business filings populate only a handful.

```xml
<tsd_L7_0>
    <c7008_DivKokku>5000.00</c7008_DivKokku>             <!-- Total dividends declared -->
    <c7050_OmakapSmKorrig>1090.00</c7050_OmakapSmKorrig> <!-- Equity-social-tax corrected → header c115_Sm -->
    <c7200_TasutavTm>1410.26</c7200_TasutavTm>           <!-- Payable income tax → header c110_Tm -->
</tsd_L7_0>
```

**Roll-up into header:** `c7200_TasutavTm` → `c110_Tm`; `c7050_OmakapSmKorrig` → `c115_Sm`.

**Source data:** transactions of type `DIVIDEND_PAYMENT` (universal, registered in migration 382). The plugin reads them and aggregates totals at filing time. Tax-math fields (c7200, c7050, etc.) are the caller's responsibility — Estonia uses 22% on standard distributions, 14% reduced rate for repeated distributions (c7009_DivMadal).

The full c7xxx field list is in `tsd-codes.md`.

## INF1 — Annual companion form (`tsd_Inf1_0`)

Filed alongside the December TSD. One row per dividend/distribution recipient.

```xml
<tsd_Inf1_0>
    <c13075_KpTmKokku>1410.26</c13075_KpTmKokku>          <!-- Total withheld income tax -->
    <c13080_Osatahtsus>1.000000000</c13080_Osatahtsus>    <!-- Taxed-distribution proportion (9 decimals) -->
    <tsd_Inf1_1List>
        <tsd_Inf1_1>
            <c13000_EstRegkood>38704290190</c13000_EstRegkood>      <!-- Estonian ID -->
            <c13020_Nimi>ANDRII RUDCHUK</c13020_Nimi>               <!-- REQUIRED -->
            <c13050_VmValiKood>DK</c13050_VmValiKood>               <!-- REQUIRED — DK=dividend, TDK=tax-paid, AOT=non-taxable -->
            <c13060_VmSumma>5000.00</c13060_VmSumma>                <!-- REQUIRED -->
            <c13073_TmMaar>22.00</c13073_TmMaar>                    <!-- Tax rate -->
            <c13074_KpTmSumma>1100.00</c13074_KpTmSumma>            <!-- Withheld tax -->
        </tsd_Inf1_1>
        <!-- Foreign recipient: c13010_ValisRegkood + c13030_RiikKood + c13040_ValisAadress -->
    </tsd_Inf1_1List>
</tsd_Inf1_0>
```

INF1 distribution-type codes (`c13050_VmValiKood`) are in `tsd-codes.md`.

## Roadmap

| Annex | Status |
|---|---|
| Header (`c108–c121`) | ✅ R2 |
| Annex 1 (`tsd_L1_0`) — resident natural persons | ✅ R2 (1A only) |
| Annex 2 (`tsd_L2_0`) — non-resident natural persons + companies | ✅ R4 (1A only) |
| Annex 4 (`tsd_L4_0`) — fringe benefits | ✅ R3 (caller provides values) |
| Annex 5 (`tsd_L5_0`) — gifts/donations/entertainment | ✅ R3 (CoA-tagged accounts 6850/6860/6870) |
| Annex 7 (`tsd_L7_0`) — dividends + equity distributions | ✅ R5 (source = `DIVIDEND_PAYMENT` transactions) |
| INF1 (`tsd_Inf1_0`) — annual companion form | ✅ R5 |
| `DIVIDEND_PAYMENT` transaction type | ✅ R5 (universal, migration 382) |
| Annex 3 (`tsd_L3_0`) — corporate income tax / investment income carry-forward | 🚧 Deferred (rare; samples don't include L3) |
| Annex 6 (`tsd_L6_0`) — transfer-pricing / fines / bribes | 🚧 Deferred (rare for service businesses) |
| Annex 8 (`tsd_L8_0`) — tonnage tax | 🚧 Deferred (shipping companies only) |

---

## See also

- `tsd-codes.md` — `c1020_ValiKood`, `c1150_TuliKood`, `c3010_TuliKood` lookup tables
- `submission-format.md` — `payroll_run.submit_calculation` payload contract (calc side)
- `estonian-tax-formulas.md` — payroll calculation formulas (gross-to-net)
- `../../scripts/generate_tsd.py` — the XML generator
- `../../scripts/test_tsd_round_trip.py` — golden-master test against the canonical filing
