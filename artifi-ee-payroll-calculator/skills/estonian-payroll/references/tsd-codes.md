# TSD Code Tables

Code lookups used in the e-MTA TSD XML. Each section maps the universal slug used in `payment_classifications` (seeded from `mcp-server/src/data/onboarding/ee.json`) to the country-specific external code that must appear in the XML.

For the XML structure see `tsd-format.md`. For the list of slugs registered in the ERP, query at runtime:

```python
list_entities("payment_classification", filters={"country_code": "EE"})
```

---

## `c1020_ValiKood` — Payment-type code (Annex 1, per `tsd_L1_A_Vm`)

The payment classification on the gross payment. Drives whether unemployment insurance, social tax, etc. apply, and which sub-section of Annex 1 (1a/1b/1-2a) the row lands in.

| Slug (universal) | external_code | Description | Notes |
|---|---|---|---|
| `salary_wage` | `10` | Regular salary / wages | Standard employment income — full SS + UI + IT |
| `vacation_pay` | `11` | Vacation / holiday pay | Same treatment as salary |
| `sick_pay` | `12` | Sick pay (employer-paid) | Days 4-8 employer-paid; days 9+ from EHIF |
| `contractor_payment` | `13` | Service-contract / contractor payment | Subject to social tax + income tax; **no unemployment insurance** |
| `board_fee` | `21` | Board member fee (juhatuse liikme tasu) | Subject to social tax + income tax; **no unemployment insurance, no pension** |
| `fringe_benefit` | `27` | Fringe benefit (gross-up at 22/78) | Annex 4 territory — calculated differently. Future release. |

Subset shown — full table includes 30+ codes for less common scenarios (foreign-paid wages, ship crew, etc.). Add to `payment_classifications` as needed.

---

## `c1150_TuliKood` — Tax-free amount code (per `tsd_L1_A_Mvt`)

The type of deduction applied **before** income tax. Each row in `<mvtList>` reduces the income-tax base.

| Slug | external_code | Description |
|---|---|---|
| `basic_exemption` | `610` | Basic exemption (maksuvaba tulu) — €700/month standard, varies with annual income |
| `pension_contribution` | `620` | Mandatory pension contribution deducted (II pillar — feeds into c1110_Kp not c1160_Summa in some scenarios) |
| `unemployment_employee` | `630` | Employee unemployment insurance deducted |

**Important**: most plugins should only emit `610` (basic exemption) as a separate `tsd_L1_A_Mvt` sub-record. The pension and unemployment-employee deductions are typically reported via `c1110_Kp` (the combined column on the parent `tsd_L1_A_Vm`), not as separate Mvt sub-records. Use 620/630 only when a separate Mvt entry is genuinely required (rare — see e-MTA portal guidance).

---

## Annex 4 fringe benefit fields (`c4xxx_*`)

Annex 4 is scalar-only — these are header fields, not per-row codes. The generator's `ANNEX_4_FIELDS` list maps each input-key to the corresponding c-code element (in canonical filing order).

| Input key (in `annex_4` JSON block) | c-code element | Description |
|---|---|---|
| `accommodation`            | `c4000_ElKulu`     | Accommodation expenses |
| `insurance_premium`        | `c4010_KiKulu`     | Non-mandatory insurance premiums |
| `personal_car_above`       | `c4030_Is`         | Personal car compensation above threshold |
| `company_vehicle`          | `c4040_Ts`         | Company vehicle for personal use |
| `other_property`           | `c4050_Mv`         | Other employer property for personal use |
| `below_market_loan`        | `c4060_SoLaen`     | Below-market interest loan (calculated: `c4061 − c4062`) |
| `market_interest`          | `c4061_TuruIntr`   | Market-rate interest |
| `loan_agreement_interest`  | `c4062_LaenIntr`   | Loan-agreement interest |
| `below_market_transfer`    | `c4070_AllaTh`     | Below-market transfer (calculated: `c4071 − c4072`) |
| `market_price`             | `c4071_Th`         | Market price |
| `applied_price`            | `c4072_Rh`         | Applied (transfer) price |
| `ownership_transfer`       | `c4080_OoTulu`     | Ownership-transfer income |
| `ownership_market_price`   | `c4081_OoTh`       | Ownership market price |
| `ownership_paid_price`     | `c4082_ORh`        | Ownership applied price |
| `ownership_balance_value`  | `c4083_Op`         | Ownership balance-sheet value |
| `general_market_value`     | `c4090_YleTh`      | General market value |
| `general_applied_price`    | `c4091_Rh`         | General applied price |
| `general_market_diff`      | `c4092_Th`         | General market difference |
| `waived_claim`             | `c4100_LoobuRn`    | Waived claim/receivable |
| `training_expense`         | `c4110_KoKulu`     | Training expense (fringe portion) |
| `other_expense`            | `c4120_TeKulu`     | Other expense |
| `non_specific_value`       | `c4130_MEs`        | Non-specific value |
| `representation_amount`    | `c4140_EsSumma`    | Total taxable representation amount |
| `exempt_income_tax`        | `c4150_EiTm`       | Exempt amount (income tax) |
| `exempt_social_tax`        | `c4160_EiSm`       | Exempt amount (social tax) |
| `special_income_tax`       | `c4170_TmEj`       | Special income tax (= taxable × 22/78) — rolls into header `c114_TmEj` |
| `social_tax`               | `c4180_Sm`         | Social tax (= base × 33%) — rolls into header `c115_Sm` |
| `social_tax_base`          | `c4181_SmEs`       | Social tax base (= taxable + special income tax) |

---

## Annex 5 gift/donation/entertainment fields (`c5xxx_*`)

| Input key (in `annex_5` JSON block) | c-code element | Description |
|---|---|---|
| `general_gifts`                  | `c5000_Ki`         | Gifts/donations NOT to listed nonprofits |
| `listed_charity_month`           | `c5010_IKiKuu`     | Gifts to § 11(1) nonprofits this month |
| `listed_charity_year`            | `c5020_IKiAasta`   | ...calendar year cumulative |
| `personalized_distributions`     | `c5030_IIsmv`      | Personalized distributions × 3% (calculated) |
| `annual_profit`                  | `c5040_IKasSumma`  | Most recent year's profit |
| `ten_percent_threshold`          | `c5050_10Prots`    | 10% of `c5040` |
| `listed_charity_taxable`         | `c5060_IMs`        | Listed-charity amount above threshold |
| `listed_charity_income_tax`      | `c5070_ITm`        | Income tax on listed-charity excess |
| `listed_charity_payable_tax`     | `c5080_ITasTm`     | Payable income tax |
| `listed_charity_refundable_tax`  | `c5090_ITagTm`     | Refundable income tax |
| `entertainment_month`            | `c5100_KyKuluKuu`  | Entertainment expenses this month |
| `entertainment_year`             | `c5110_KyKuluAasta`| ...YTD cumulative |
| `entertainment_threshold`        | `c5120_KyIsmv`     | 2% of personalized payouts threshold |
| `entertainment_income_tax`       | `c5130_KyTm`       | Income tax on entertainment above threshold |
| `entertainment_payable_tax`      | `c5140_KyTasTm`    | Payable income tax (entertainment) |
| `entertainment_refundable_tax`   | `c5150_KyTagTm`    | Refundable income tax (entertainment) |
| `special_income_tax_payable`     | `c5160_TasTmEj`    | Total payable special income tax — rolls into header `c114_TmEj` |
| `special_income_tax_refundable`  | `c5170_TagTmEj`    | Total refundable special income tax |
| `other_taxable`                  | `c5180_MaKi`       | Other taxable amount |
| `other_special_income_tax`       | `c5190_TmEj`       | Other special income tax — rolls into header `c114_TmEj` |
| `year_total_giving`              | `c5220_TonnKiKokku`| Year-total giving |

---

## Annex 7 distribution fields (`c7xxx_*`)

Annex 7 is scalar-only. Generator's `ANNEX_7_FIELDS` map (input-key → c-code, in canonical filing order):

| Input key (in `annex_7` JSON block) | c-code element | Description |
|---|---|---|
| `dividends_total`                  | `c7008_DivKokku`             | Total dividends declared |
| `dividends_lower_rate`             | `c7009_DivMadal`             | Dividends at 14% reduced rate |
| `distribution_taxable`             | `c7010_VmMaksust`            | Taxable distribution |
| `distribution_central_total`       | `c7012_VmKeSum`              | Central distribution total |
| `exit_tax`                         | `c7014_Lahkumismaks`         | Exit tax |
| `cfc_income`                       | `c7016_Cfc`                  | CFC (controlled foreign corp) income |
| `equity_social_tax_pre2015`        | `c7020_OmakapSmEnne2015`     | Pre-2015 equity social tax |
| `tonnage_dividends_total`          | `c7022_TonnDivKokku`         | Tonnage-tax dividends total |
| `equity_social_tax`                | `c7030_OmakapSm`             | Equity social tax (current period) |
| `equity_social_tax_total`          | `c7040_OmakapSmKokku`        | Equity social tax total |
| `equity_social_tax_corrected`      | `c7050_OmakapSmKorrig`       | Corrected — **rolls into header `c115_Sm`** |
| `equity_distribution`              | `c7060_OmakapVm`             | Equity distribution amount |
| `equity_unpaid`                    | `c7070_OmakapValjamaksmata`  | Unpaid equity portion |
| `distribution_above_st_taxable`    | `c7080_VmYleSmMaksust`       | Distribution above ST taxable |
| `foreign_tax_paid`                 | `c7160_VrTasutudTm`          | Foreign tax paid (for credit) |
| `foreign_tax_paid_corrected`       | `c7170_VrTasutudTmKorrig`    | Foreign tax paid corrected |
| `foreign_tax_credit_used`          | `c7180_VrVahendus`           | Foreign tax credit used |
| `foreign_tax_credit_unused`        | `c7190_VrVmTmKasutamata`     | Unused FTC carry-forward |
| `payable_income_tax`               | `c7200_TasutavTm`            | **Rolls into header `c110_Tm`** |
| `dividend_equity_tax`              | `c7217_DivOmakapTm`          | Dividend-on-equity income tax |
| `foreign_tax_reduction`            | `c7218_TmVrVahendus`         | Income tax reduction via FTC |
| `credit_method_reduction`          | `c7219_TmKredasVahendus`     | Income tax reduction via credit method |
| `prior_period_distribution`        | `c7290_MvVm`                 | Prior period distribution |
| `prior_period_distribution_corr`   | `c7300_MvVmKorrig`           | Prior period distribution corrected |
| `prior_period_lower_rate_open`     | `c7301_MvMmDivAlgus`         | Prior period 14% rate opening |
| `prior_period_lower_rate_used`     | `c7302_MvMmDivYa`            | Prior period 14% rate used |
| `prior_period_tonnage_open`        | `c7303_MvTonnDivAlgus`       | Prior period tonnage opening |
| `prior_period_tonnage_used`        | `c7304_MvTonnDivYa`          | Prior period tonnage used |
| `prior_period_distribution_div`    | `c7310_MvVmDiv`              | Prior period distribution dividend |
| `prior_period_distribution_lower`  | `c7311_MvVmMmDiv`            | Prior period distribution at lower rate |
| `prior_period_equity`              | `c7320_MvVmOmakap`           | Prior period equity distribution |
| `prior_period_unused`              | `c7330_MvVmKasutamata`       | Prior period unused |

---

## INF1 distribution-type codes (`c13050_VmValiKood`)

| Slug | external_code | Description |
|---|---|---|
| `dividend_distribution`      | `DK`  | Dividend (declared distribution) |
| `tax_paid_dividend`          | `TDK` | Tax-paid dividend |
| `non_taxable_distribution`   | `AOT` | Non-taxable equity distribution |

Additional codes (from full e-MTA spec):
- `EH` — Liquidation distribution
- `MH` — Reorganization distribution
- `OK` — Equity-share buyback
(Add more as your filings require — register them in `payment_classifications` with `applicable_forms: ["TSD","INF1"]` and `metadata.code_field: "c13050_VmValiKood"`.)

INF1 recipient row fields (each row: `tsd_Inf1_1`):

| Input key (in `inf1.recipients[]`) | c-code element | Required? |
|---|---|---|
| `estonian_registry_code` | `c13000_EstRegkood`     | required if recipient is EE-registered |
| `foreign_registry_code`  | `c13010_ValisRegkood`   | required if non-resident |
| `name`                   | `c13020_Nimi`           | always required |
| `country_code`           | `c13030_RiikKood`       | required for non-resident |
| `foreign_address`        | `c13040_ValisAadress`   | optional |
| `distribution_type_code` | `c13050_VmValiKood`     | always required (DK/TDK/AOT/etc.) |
| `distribution_amount`    | `c13060_VmSumma`        | always required |
| `taxable_amount`         | `c13070_VmMaksustSumma` | optional |
| `exempt_amount`          | `c13072_MvtSumma`       | optional |
| `tax_rate`               | `c13073_TmMaar`         | optional |
| `withheld_tax`           | `c13074_KpTmSumma`      | optional |

INF1 header scalars: `withheld_tax_total` (`c13075_KpTmKokku`), `taxed_proportion` (`c13080_Osatahtsus` — 9 decimals).

---

## `c2030_ValiKood` — Non-resident persons (Annex 2)

Note: the XSD field is named `c2030_ValiKood` for Annex 2 (vs. `c1020` in Annex 1) — the canonical filing emits this in `<tsd_L2_A_Vm>`. The slug catalog uses `c2020_*` codes when referring to country-of-residence (`c2020_RiikKood` is on the same row). The slugs below map to `c2030_ValiKood` external codes.

| Slug | external_code | Description | Standard rate |
|---|---|---|---|
| `non_resident_salary`     | `110` | Non-resident salary | 22% |
| `non_resident_service`    | `120` | Non-resident service payment | 22% (treaty: 0% if EU service in EU) |
| `non_resident_royalty`    | `122` | Royalty payment to non-resident | 10% (treaty rates apply) |
| `non_resident_director`   | `121` | Director's fee paid to non-resident | 22% |
| `non_resident_rent`       | `123` | Rent for property in Estonia paid to non-resident | 22% |

**Tax-treaty rates** depend on the recipient's country (`c2020_RiikKood`) and the EE bilateral treaty registry — the Estonian Tax and Customs Board publishes the lookup. Plugins should consult this list at calc time; the generator just emits whatever rate the caller supplies in `c2160_TmMaar`.

## `c2154_TuliKood` — Tax-free amount code (Annex 2 mvt sub-record)

| Slug | external_code | Description |
|---|---|---|
| `non_resident_basic_exemption` | `610` | Basic exemption for non-residents (limited cases) |
| `non_resident_special_650`     | `650` | Non-resident-specific exemption code 650 |

---

## `c3010_TuliKood` — Legal-person withholding (Annex 3, future release)

Withholding tax on payments to companies (services, royalties, etc.).

| Slug | external_code | Description |
|---|---|---|
| `legal_person_service` | `320` | Service payment to legal person (WHT 20%) |
| `legal_person_royalty` | `322` | Royalty to legal person (WHT 10%) |

Annex 3 is a future release. Requires `master_vendors.metadata.tax_filing.is_withholding_subject` plus per-line withholding splits in the AP executor.

---

## Header-field codes (`master_accounts.metadata.filing_categories[]`)

For CoA-driven routing — each tagged GL account contributes to a specific TSD field. These are seeded automatically by the onboarding loader from `data/onboarding/ee.json` `account_filing_categories`.

| Account | Field | Purpose |
|---|---|---|
| `2410` Income Tax Payable | `c110_Tm` | Total income tax withheld |
| `2420` Social Tax Payable | `c115_Sm` | Total social tax |
| `2440` Unemployment Insurance Payable | `c116_Tk` | Total unemployment insurance |
| `2430` Pension Contributions Payable | `c117_Kp` | Total mandatory pension |

Annex 5 (gifts/donations/entertainment) routing tags are deferred to R3 alongside the new EE-specific accounts (`6530` Business Entertainment, `6540` Gifts & Hospitality, `6550` Charitable Donations).

---

## Amended-return reason codes (`c121_ParPohjusKood`)

Set on the header when refiling a previously-accepted return. Optional `<parPohjusTekst>` carries free-text detail when `MUU` (Other) is selected.

| Code | Reason |
|---|---|
| `VMA` | Errors in calculation of distributions and/or taxes |
| `VET` | Distribution did not actually occur |
| `VDV` | Distribution attributed to incorrect person |
| `VVK` | Incorrect distribution code entered |
| `TTM` | Pension for incapacity for work declared retroactively |
| `MTR` | Liable to taxation in another country |
| `DAM` | Change in submitted data |
| `DVK` | Submitted data in the wrong month |
| `VPV` | Errors arising from a change in accounting software |
| `AML` | Change as a result of tax audit |
| `MUU` | Other (requires `parPohjusTekst`) |

---

## Where to find more codes

Some codes are documented only in the official Estonian TSD User Guide PDF on the e-MTA portal. When you encounter an unmapped scenario:

1. Check `Downloads/csv_tsd_eng_failiformaadid_01.01.2023.docx` (full file-format guide in `~/Downloads`)
2. Check the latest version at https://www.emta.ee → e-MTA → Help → Forms → TSD
3. If you find a new code, add it as a `payment_classification` row in `mcp-server/src/data/onboarding/ee.json` under `payment_classifications[]` with a clear `metadata.code_field` (one of `c1020_ValiKood`, `c1150_TuliKood`, `c2020_ValiKood`, `c3010_TuliKood`)
