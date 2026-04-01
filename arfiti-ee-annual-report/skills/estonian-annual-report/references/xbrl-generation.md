# XBRL File Generation Reference

Generate valid XBRL files for upload to ariregister.rik.ee. Based on the official `et-gaap_2026-01-01` taxonomy from xbrl.eesti.ee.

## CRITICAL RULES — Read Before Generating

These rules are absolute. Violating any of them causes portal validation to fail.

1. **Exact namespace URI** — The et-gaap taxonomy namespace is EXACTLY:
   `http://xbrl.eesti.ee/taxonomy/et-gaap_2026-01-01/`
   With a trailing slash. NEVER use `et-gaap-2026`, `et-gaap_2026`, or any other variant.

2. **No invented element names** — Use ONLY elements listed in the mapping tables below. Never invent elements like `Cash` (correct: `CashAndCashEquivalents`) or `NetProfit`. If an account has no matching element, use the parent aggregate element.

3. **No other taxonomies** — NEVER add `dei:`, `us-gaap:`, `ifrs:`, or any namespace other than `et-gaap:`, `xbrli:`, `link:`, `xlink:`, `iso4217:`, and `xbrldi:`.

4. **Entity identifier scheme** — Always exactly: `http://xbrl.eesti.ee/estonian_commercial_register` (no trailing slash).

5. **Currency unit only** — Only declare `iso4217:EUR`. NEVER declare `xbrli:pure` or any other unit type.

6. **No XML comments** — The portal rejects any `<!-- ... -->` XML comments in XBRL files. Do not include them.

7. **No zero-value facts** — Omit facts where the value is 0, except for required aggregate totals.

8. **Always include prior year comparatives** — The XBRL file MUST include prior year data using I1 (balance sheet) and D11 (income statement, cash flow) contexts. The BTM portal expects comparative columns. Populate `balance_sheet.prior`, `income_statement_prior`, and `cash_flow_prior` in the input JSON. This ensures consistency between the current and previously filed report.

## Overview

Two files are generated:
1. **`Vormid_{REGCODE}.xsd`** — Companion schema declaring which forms/notes are included
2. **`Aruanne_{REGCODE}.xbrl`** — Instance document with financial data

## File 1: Companion Schema Template (Vormid_{REGCODE}.xsd)

```xml
<?xml version='1.0' encoding='UTF-8'?>
<xsd:schema xmlns:link="http://www.xbrl.org/2003/linkbase"
            xmlns:xlink="http://www.w3.org/1999/xlink"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            targetNamespace="http://temporaryEntryFile"
            elementFormDefault="qualified">
  <xsd:annotation>
    <xsd:appinfo>
      <!-- INSERT LINKBASE REFS FOR EACH SELECTED ROLE (see Role Catalog below) -->

      <!-- ALWAYS include label and reference linkbases -->
      <link:linkbaseRef xlink:type="simple" xlink:href="et-gaap_2026-01-01/label/et-gaap_2026-01-01-label-et.xml" xlink:role="http://www.xbrl.org/2003/role/labelLinkbaseRef" xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>
      <link:linkbaseRef xlink:type="simple" xlink:href="et-gaap_2026-01-01/label/et-gaap_2026-01-01-label-en.xml" xlink:role="http://www.xbrl.org/2003/role/labelLinkbaseRef" xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>
      <link:linkbaseRef xlink:type="simple" xlink:href="et-gaap_2026-01-01/reference/et-gaap_2026-01-01-reference.xml" xlink:role="http://www.xbrl.org/2003/role/referenceLinkbaseRef" xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>
    </xsd:appinfo>
  </xsd:annotation>
  <xsd:import namespace="http://www.xbrl.org/2003/instance" schemaLocation="http://www.xbrl.org/2003/xbrl-instance-2003-12-31.xsd"/>
  <!-- INSERT XSD:IMPORT FOR EACH SELECTED ROLE -->
  <xsd:import namespace="http://xbrl.eesti.ee/taxonomy/et-gaap_2026-01-01/" schemaLocation="et-gaap-cor_2026-01-01.xsd"/>
</xsd:schema>
```

### XSD Role Linkbase Pattern

For each selected role, add 2-3 linkbase references + 1 xsd:import:

```xml
<!-- Linkbase references (inside <xsd:appinfo>) -->
<link:linkbaseRef xlink:type="simple" xlink:href="et-gaap_2026-01-01/role-{MAJOR}/cal_{FormName}_role-{FULL}.xml" xlink:role="http://www.xbrl.org/2003/role/calculationLinkbaseRef" xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>
<link:linkbaseRef xlink:type="simple" xlink:href="et-gaap_2026-01-01/role-{MAJOR}/def_{FormName}_role-{FULL}.xml" xlink:role="http://www.xbrl.org/2003/role/definitionLinkbaseRef" xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>
<link:linkbaseRef xlink:type="simple" xlink:href="et-gaap_2026-01-01/role-{MAJOR}/pre_{FormName}_role-{FULL}.xml" xlink:role="http://www.xbrl.org/2003/role/presentationLinkbaseRef" xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>

<!-- XSD import (inside <xsd:schema>, after annotation) -->
<xsd:import namespace="http://xbrl.eesti.ee/role/et-gaap_2026-01-01/role-{MAJOR}" schemaLocation="et-gaap_2026-01-01/role-{MAJOR}/role-{MAJOR}.xsd"/>
```

Where `{MAJOR}` = first 6 digits (e.g., `201000`), `{FULL}` = full role code (e.g., `201010`).

**Note:** Some roles have only `def_` and `pre_` (no `cal_`), e.g., role-811020 (Loan Receivables). Check the Role Catalog below.

---

## File 2: Instance Document Template (Aruanne_{REGCODE}.xbrl)

```xml
<?xml version='1.0' encoding='UTF-8'?>
<xbrli:xbrl xmlns:iso4217="http://www.xbrl.org/2003/iso4217"
            xmlns:et-gaap="http://xbrl.eesti.ee/taxonomy/et-gaap_2026-01-01/"
            xmlns:xlink="http://www.w3.org/1999/xlink"
            xmlns:link="http://www.xbrl.org/2003/linkbase"
            xmlns:xbrli="http://www.xbrl.org/2003/instance"
            xmlns:xbrldi="http://xbrl.org/2006/xbrldi">
  <link:schemaRef xlink:type="simple" xlink:href="Vormid_{REGCODE}.xsd"/>

  <!-- CONTEXT DEFINITIONS (see Context Rules below) -->

  <!-- UNIT DEFINITION -->
  <xbrli:unit id="valuuta">
    <xbrli:measure>iso4217:EUR</xbrli:measure>
  </xbrli:unit>

  <!-- FACT VALUES (see Element Mapping below) -->

</xbrli:xbrl>
```

---

## Context Generation Rules

### Standard Contexts (always needed)

**Instant contexts** — for balance sheet facts:
```xml
<!-- Current year end (e.g., 2025-12-31) -->
<xbrli:context id="I2">
  <xbrli:entity>
    <xbrli:identifier scheme="http://xbrl.eesti.ee/estonian_commercial_register">{REGCODE}</xbrli:identifier>
  </xbrli:entity>
  <xbrli:period>
    <xbrli:instant>{CURRENT_YEAR}-12-31</xbrli:instant>
  </xbrli:period>
</xbrli:context>

<!-- Prior year end (used for BS comparatives and some notes) -->
<xbrli:context id="I1">
  <xbrli:entity>
    <xbrli:identifier scheme="http://xbrl.eesti.ee/estonian_commercial_register">{REGCODE}</xbrli:identifier>
  </xbrli:entity>
  <xbrli:period>
    <xbrli:instant>{PRIOR_YEAR}-12-31</xbrli:instant>
  </xbrli:period>
</xbrli:context>
```

**Duration contexts** — for income statement / cash flow / equity changes:
```xml
<!-- Current year (fiscal year) -->
<xbrli:context id="D21">
  <xbrli:entity>
    <xbrli:identifier scheme="http://xbrl.eesti.ee/estonian_commercial_register">{REGCODE}</xbrli:identifier>
  </xbrli:entity>
  <xbrli:period>
    <xbrli:startDate>{CURRENT_YEAR}-01-01</xbrli:startDate>
    <xbrli:endDate>{CURRENT_YEAR}-12-31</xbrli:endDate>
  </xbrli:period>
</xbrli:context>

<!-- Prior year (for IS/CF comparatives) -->
<xbrli:context id="D11">
  <xbrli:entity>
    <xbrli:identifier scheme="http://xbrl.eesti.ee/estonian_commercial_register">{REGCODE}</xbrli:identifier>
  </xbrli:entity>
  <xbrli:period>
    <xbrli:startDate>{PRIOR_YEAR}-01-01</xbrli:startDate>
    <xbrli:endDate>{PRIOR_YEAR}-12-31</xbrli:endDate>
  </xbrli:period>
</xbrli:context>
```

### Dimensional Contexts (for notes)

**Explicit-only dimension** (ID prefix: `HE`):
```xml
<xbrli:context id="HE{N}">
  <xbrli:entity>
    <xbrli:identifier scheme="http://xbrl.eesti.ee/estonian_commercial_register">{REGCODE}</xbrli:identifier>
  </xbrli:entity>
  <xbrli:period>
    <xbrli:instant>{YEAR}-12-31</xbrli:instant>
  </xbrli:period>
  <xbrli:scenario>
    <xbrldi:explicitMember dimension="et-gaap:{DimensionName}">et-gaap:{MemberName}</xbrldi:explicitMember>
  </xbrli:scenario>
</xbrli:context>
```

**Typed + explicit dimension** (ID prefix: `HT`):
```xml
<xbrli:context id="HT{N}">
  <xbrli:entity>
    <xbrli:identifier scheme="http://xbrl.eesti.ee/estonian_commercial_register">{REGCODE}</xbrli:identifier>
  </xbrli:entity>
  <xbrli:period>
    <xbrli:instant>{YEAR}-12-31</xbrli:instant>
  </xbrli:period>
  <xbrli:scenario>
    <xbrldi:explicitMember dimension="et-gaap:{DimensionName}">et-gaap:{MemberName}</xbrldi:explicitMember>
    <xbrldi:typedMember dimension="et-gaap:{TypedDimensionName}">
      <et-gaap:{TypedItemElement}>{value}</et-gaap:{TypedItemElement}>
    </xbrldi:typedMember>
  </xbrli:scenario>
</xbrli:context>
```

### Maturity Dimension Members

Used by notes: Receivables (804010), Loan Receivables (811020), Payables (822000), Loan Commitments (821000).

| Dimension | Member (explicit) | Meaning |
|---|---|---|
| `AllocationByRemainingMaturityDimension` | `AllocationByRemainingMaturityTotalAbstract` | Total |
| `AllocationByRemainingMaturityDimension` | `AllocationByRemainingMaturityWithin12MonthsAbstract` | Within 12 months |
| `AllocationByRemainingMaturityDimension` | `AllocationByRemainingMaturityWithin1to5YearsAbstract` | 1-5 years |
| `AllocationByRemainingMaturityDimension` | `AllocationByRemainingMaturityWithinOver5YearsAbstract` | Over 5 years |

### Related Parties Given Loans Dimension Members

Used by note: Related Parties (843000).

| Dimension | Member (explicit) | Meaning |
|---|---|---|
| `RelatedPartiesAllocationByGivenLoansDimension` | `RelatedPartiesGivenLoansAtEndOfPreviousPeriodAbstract` | Balance at prior year end |
| `RelatedPartiesAllocationByGivenLoansDimension` | `RelatedPartiesGivenLoansAbstract` | Loans given during period |
| `RelatedPartiesAllocationByGivenLoansDimension` | `RelatedPartiesGivenLoansRepaymentsAbstract` | Repayments during period |
| `RelatedPartiesAllocationByGivenLoansDimension` | `RelatedPartiesGivenLoansAtEndOfPeriodAbstract` | Balance at current year end |
| `RelatedPartiesAllocationByGivenLoansDimension` | `RelatedPartiesGivenLoansInterestAccruedForPeriodAbstract` | Interest accrued |

### Additional Dimension for Loan Details

Used by notes: Loan Receivables (811020), Loan Commitments (821000).

| Dimension | Member (explicit) | Meaning |
|---|---|---|
| `AdditionalDimensionalAllocationByInterestRateBaseCurrenciesAndDueDateDimension` | `InterestRateAbstract` | Interest rate |
| `AdditionalDimensionalAllocationByInterestRateBaseCurrenciesAndDueDateDimension` | `BaseCurrenciesAbstract` | Currency |
| `AdditionalDimensionalAllocationByInterestRateBaseCurrenciesAndDueDateDimension` | `DueDateAbstract` | Due date |

### Equity Changes Dimension Members

Used by: Statement of Changes in Equity (601010).

| Dimension | Member (explicit) | Meaning |
|---|---|---|
| `ChangesInEquityDimension` | `EquityAtEndOfPreviousPeriodAbstract` | Opening balance |
| `ChangesInEquityDimension` | `EffectOfChangesInAccountingPoliciesAbstract` | Accounting policy changes |
| `ChangesInEquityDimension` | `EffectOfCorrectionOfErrorsAbstract` | Error corrections |
| `ChangesInEquityDimension` | `RestatedBalanceAbstract` | Restated balance |
| `ChangesInEquityDimension` | `ChangesInEquityAnnualPeriodProfitLossAbstract` | Period profit/loss |
| `ChangesInEquityDimension` | `IssueOfEquityAbstract` | Share issuance |
| `ChangesInEquityDimension` | `DeclaredDividendsAbstract` | Dividends declared |
| `ChangesInEquityDimension` | `ChangesInReservsAbstract` | Reserve transfers |
| `ChangesInEquityDimension` | `OtherChangesInEquityAbstract` | Other changes |
| `ChangesInEquityDimension` | `EquityAtEndOfPeriodAbstract` | Closing balance |

### Income Tax Dimension Members

Used by: Note Income Tax (842000).

| Dimension | Member (explicit) | Meaning |
|---|---|---|
| `AllocationByIncomeTaxExpenseComponentsDimension` | `TaxableAmountAbstract` | Taxable amount |
| `AllocationByIncomeTaxExpenseComponentsDimension` | `IncomeTaxExpenseAbstract` | Tax expense |
| `AllocationByIncomeTaxExpenseComponentsDimension` | `DeferredIncomeTaxAbstract` | Deferred tax |

---

## Fact Value Patterns

### Monetary fact
```xml
<et-gaap:{ElementName} decimals="0" unitRef="valuuta" contextRef="{contextId}">{integer_value}</et-gaap:{ElementName}>
```

### String fact (no unitRef or decimals)
```xml
<et-gaap:{ElementName} contextRef="{contextId}">{text_value}</et-gaap:{ElementName}>
```

### Rules
- Use `decimals="0"` for all monetary values (round to whole EUR)
- Use `contextRef="I2"` for current year BS, `contextRef="I1"` for prior year BS
- Use `contextRef="D21"` for current year IS/CF/equity changes
- Use `contextRef="D11"` for prior year IS/CF comparatives
- Omit facts that are zero/empty unless they are totals required by the form
- Negative values: use negative numbers (e.g., `-5000` for losses, treasury shares)

---

## Balance Sheet Element Mapping (role-201010)

### Assets

| BS Line | Account Range | XBRL Element | Context |
|---|---|---|---|
| Cash and cash equivalents | 1000-1099 | `CashAndCashEquivalents` | I2, I1 |
| Short-term financial investments | 1100-1199 | `ShortTermFinancialInvestments` | I2, I1 |
| Short-term receivables and prepayments | 1200-1499 | `ShortTermReceivablesAndPrepayments` | I2, I1 |
| Inventories | 1500-1599 | `Inventories` | I2, I1 |
| Short-term biological assets | 1600-1699 | `ShortTermBiologicalAssets` | I2, I1 |
| **Total current assets** | | `CurrentAssets` | I2, I1 |
| Investments in subsidiaries/associates | 2000-2049 | `InvestmentsInSubsidiariesAndAssociates` | I2, I1 |
| Long-term financial investments | 2050-2099 | `LongTermFinancialInvestments` | I2, I1 |
| Long-term receivables and prepayments | (LT portion) | `LongTermReceivablesAndPrepayments` | I2, I1 |
| Investment property | 2100-2199 | `InvestmentProperty` | I2, I1 |
| Property, plant and equipment | 2200-2399 | `PropertyPlantAndEquipment` | I2, I1 |
| Long-term biological assets | 2600-2699 | `LongTermBiologicalAssets` | I2, I1 |
| Intangible assets | 2400-2599 | `IntangibleAssets` | I2, I1 |
| **Total non-current assets** | | `NonCurrentAssets` | I2, I1 |
| **TOTAL ASSETS** | | `Assets` | I2, I1 |

### Liabilities

| BS Line | Account Range | XBRL Element | Context |
|---|---|---|---|
| Short-term loan liabilities | 3000-3099 | `ShortTermLoanLiabilities` | I2, I1 |
| Short-term payables and prepayments | 3100-3499 | `ShortTermPayablesAndPrepayments` | I2, I1 |
| Short-term provisions | 3500-3549 | `ShortTermProvisions` | I2, I1 |
| Short-term government grants | 3550-3599 | `ShortTermGovernmentGrants` | I2, I1 |
| **Total current liabilities** | | `CurrentLiabilities` | I2, I1 |
| Long-term loan liabilities | 3600-3699 | `LongTermLoanLiabilities` | I2, I1 |
| Long-term payables and prepayments | 3700-3799 | `LongTermPayablesAndPrepayments` | I2, I1 |
| Long-term provisions | 3800-3849 | `LongTermProvisions` | I2, I1 |
| Long-term government grants | 3850-3899 | `LongTermGovernmentGrants` | I2, I1 |
| **Total non-current liabilities** | | `NonCurrentLiabilities` | I2, I1 |
| **TOTAL LIABILITIES** | | `Liabilities` | I2, I1 |

### Equity

| BS Line | Account Range | XBRL Element | Context |
|---|---|---|---|
| Issued capital | 5000-5049 | `IssuedCapital` | I2, I1 |
| Unregistered equity | (if applicable) | `UnregisteredEquity` | I2, I1 |
| Unpaid capital | (if applicable) | `UnpaidCapital` | I2, I1 |
| Share premium | 5050-5099 | `SharePremium` | I2, I1 |
| Treasury shares | 5100-5149 | `TreasuryShares` | I2, I1 |
| Statutory reserve capital | 5150-5199 | `StatutoryReserveCapital` | I2, I1 |
| Other reserves | 5200-5249 | `OtherReserves` | I2, I1 |
| Other equity | (if applicable) | `OtherEquity` | I2, I1 |
| Retained earnings (loss) | 5300-5399 | `RetainedEarningsLoss` | I2, I1 |
| Annual period profit (loss) | Calculated | `AnnualPeriodProfitLoss` | I2, I1 |
| **TOTAL EQUITY** | | `Equity` | I2, I1 |
| **TOTAL LIABILITIES AND EQUITY** | | `LiabilitiesAndEquity` | I2, I1 |

---

## Income Statement Element Mapping — Scheme 1 (role-301011)

Current year uses `D21`, prior year comparatives use `D11`. The generator auto-fills `0` in D11 for lines that exist in the current year but have no prior year data.

| IS Line | Account Range | XBRL Element | Context |
|---|---|---|---|
| Revenue | 4000-4099 | `Revenue` | D21, D11 |
| Other income | 4100-4199 | `OtherIncome` | D21, D11 |
| Change in inventories of agricultural production | (if applicable) | `ChangesInInventoriesOfAgriculturalProduction` | D21, D11 |
| Profit/loss from biological assets | (if applicable) | `ProfitLossFromBiologicalAssets` | D21, D11 |
| Change in inventories of finished goods/WIP | 4200-4249 | `ChangesInInventoriesOfFinishedGoodsAndWorkInProgress` | D21, D11 |
| Work performed by entity and capitalised | (if applicable) | `WorkPerformedByEntityAndCapitalised` | D21, D11 |
| Raw materials and consumables used | 5100-5199 | `RawMaterialsAndConsumablesUsed` | D21, D11 |
| Other operating expense | 5200-5299 | `OtherOperatingExpense` | D21, D11 |
| Employee expense | 5300-5399 | `EmployeeExpense` | D21, D11 |
| Depreciation and impairment loss/reversal | 5400-5499 | `DepreciationAndImpairmentLossReversal` | D21, D11 |
| Significant impairment of current assets | (if applicable) | `SignificantImpairmentOfCurrentAssets` | D21, D11 |
| Other expense | 5500-5599 | `OtherExpense` | D21, D11 |
| **Operating profit (loss)** | Calculated | `TotalProfitLoss` | D21, D11 |
| Profit/loss from subsidiaries | (if applicable) | `ProfitLossFromSubsidiaries` | D21, D11 |
| Profit/loss from associates | (if applicable) | `ProfitLossFromAssociates` | D21, D11 |
| Gain/loss from financial investments | 6000-6099 | `GainLossFromFinancialInvestments` | D21, D11 |
| Interest income | 6100-6199 | `InterestIncome` | D21, D11 |
| Interest expenses | 6500-6599 | `InterestExpenses` | D21, D11 |
| Other financial income and expense | 6600-6999 | `OtherFinancialIncomeAndExpense` | D21, D11 |
| **Profit (loss) before tax** | Calculated | `TotalProfitLossBeforeTax` | D21, D11 |
| Income tax expense | 7000-7099 | `IncomeTaxExpense` | D21, D11 |
| **Net profit (loss) for the year** | Calculated | `TotalAnnualPeriodProfitLoss` | D21, D11 |

---

## Cash Flow Statement Elements (role-401010, indirect method)

All elements use duration context `D21`.

### Operating Activities
| Element | Description |
|---|---|
| `TotalProfitLoss` | Operating profit (loss) — starting point |
| `DepreciationAndImpairmentLossReversalNeg` | Depreciation adjustment (add back) |
| `ProfitLossFromSaleOfNonCurrentAssets` | Gain/loss on disposal |
| `OtherAdjustments` | Other non-cash adjustments |
| `Adjustments` | Total adjustments |
| `ChangesInReceivablesAndPrepaymentsRelatedToOperatingActivities` | Change in receivables |
| `OperatingActivitiesChangesInInventories` | Change in inventories |
| `ChangesInPayablesAndPrepaymentsRelatedToOperatingActivities` | Change in payables |
| `OperatingActivitiesIntrestReceived` | Interest received |
| `OperatingActivitiesIntrestPaid` | Interest paid |
| `OperatingActivitiesIncomeTaxRefundPaid` | Income tax paid |
| `OperatingActivitiesProceedsFromGovernmentGrants` | Government grants received |
| `OperatingActivitiesDividendsReceived` | Dividends received |
| `OtherCashFlowsFromOperatingActivities` | Other operating cash flows |
| `CashFlowsFromOperatingActivities` | **Net operating cash flow** |

### Investing Activities
| Element | Description |
|---|---|
| `InvestingActivitiesPurchaseOfPropertyPlantAndEquipmentAndIntangibleAssets` | PP&E/IA purchases |
| `InvestingActivitiesProceedsFromSalesOfPropertyPlantAndEquipmentAndIntangibleAssets` | PP&E/IA sales |
| `InvestingActivitiesLoansGiven` | Loans given |
| `InvestingActivitiesRepaymentsOfLoansGiven` | Loan repayments received |
| `InvestingActivitiesIntrestReceived` | Interest received (investing) |
| `InvestingActivitiesDividendsReceived` | Dividends received (investing) |
| `OtherCashOutflowsFromInvestingActivities` | Other investing outflows |
| `OtherCashInflowsFromInvestingActivities` | Other investing inflows |
| `CashFlowsFromInvestingActivities` | **Net investing cash flow** |

### Financing Activities
| Element | Description |
|---|---|
| `FinancingActivitiesLoansReceived` | Loans received |
| `FinancingActivitiesRepaymentsOfLoansReceived` | Loan repayments |
| `FinancingActivitiesProceedsFromOverdraft` | Overdraft proceeds |
| `FinancingActivitiesProceedsFromFinanceLease` | Finance lease payments |
| `FinancingActivitiesIntrestPaid` | Interest paid (financing) |
| `FinancingActivitiesProceedsFromIssuingShares` | Share issuance proceeds |
| `FinancingActivitiesDividendsPaid` | Dividends paid |
| `FinancingActivitiesIncomeTaxRefundPaid` | Tax on dividends paid |
| `OtherCashInflowsFromFinancingActivities` | Other financing inflows |
| `OtherCashOutflowsFromFinancingActivities` | Other financing outflows |
| `CashFlowsFromFinancingActivities` | **Net financing cash flow** |

### Summary
| Element | Description |
|---|---|
| `CashFlows` | Total cash flows (sum of all 3 activities) |
| `CashAndCashEquivalentsAtBeginningOfPeriod` | Opening cash balance |
| `ChangeInCashAndCashEquivalents` | Net change in cash |
| `EffectOnExchangeRateChangesOnCashAndCashEquivalents` | FX effect on cash |
| `CashAndCashEquivalentsAtEndOfPeriod` | Closing cash balance |

---

## Equity Changes Elements (role-601010)

Uses dimensional contexts with `ChangesInEquityDimension`. Each column is a separate element:

| Element | Description |
|---|---|
| `ChangesInEquityIssuedCapital` | Issued capital column |
| `ChangesInEquityUnregisteredEquity` | Unregistered equity column |
| `ChangesInEquitySharePremium` | Share premium column |
| `ChangesInEquityTreasuryShares` | Treasury shares column |
| `ChangesInEquityStatutoryReserveCapital` | Statutory reserve column |
| `ChangesInEquityOtherReserves` | Other reserves column |
| `ChangesInEquityUnpaidCapital` | Unpaid capital column |
| `ChangesInEquityOtherEquity` | Other equity column |
| `ChangesInEquityRetainedEarningsLoss` | Retained earnings column |
| `ChangesInEquity` | Total equity column |

Each element is reported with a different `ChangesInEquityDimension` member for each row (opening balance, profit/loss, dividends, etc.).

---

## Profit Allocation Proposal Elements (role-702010)

All use instant context `I2`.

| Element | Description |
|---|---|
| `RetainedEarningsLoss` | Retained earnings brought forward |
| `AnnualPeriodProfitLoss` | Current year profit/loss |
| `RetainedEarningsLossWithAnnualPeriodProfitLoss` | Total distributable |
| `ProposalStatutoryReserveCapitalIncreaseDecrease` | Transfer to statutory reserve |
| `ProposalOtherReservesIncreaseDecrease` | Transfer to other reserves |
| `ProposalDividends` | Proposed dividends |
| `ProposalRetainedEarningsAfterDistributionCovering` | Retained earnings after distribution |
| `ProposalDistributionCoveringTotal` | Total distributed/covered |

---

## Note Element Reference

### Note: Receivables and Prepayments (role-804010)

Uses `AllocationByRemainingMaturityDimension` for maturity breakdown.

| Element | Description |
|---|---|
| `AccountsReceivables` | Trade receivables |
| `AllowanceForDoubtfulReceivables` | Doubtful receivable allowance |
| `ReceivablesFromRelatedParties` | Related party receivables |
| `TaxPrepaymentsAndReceivables` | Tax prepayments/receivables |
| `LoanReceivables` | Loan receivables |
| `InterestReceivables` | Interest receivables (child of `OtherReceivablesTotal`) |
| `DividendReceivables` | Dividend receivables |
| `AccruedIncome` | Accrued income |
| `OtherReceivablesTotal` | Other receivables total |
| `DeferredExpenses` | Deferred expenses (child of `PrepaymentsTotal`) |
| `OtherPaidPrepayments` | Other prepayments |
| `PrepaymentsTotal` | Prepayments total |
| `ReceivablesAndPrepayments` | **Grand total** |

Each element is reported with 4 maturity contexts (Total, <12m, 1-5y, >5y).

### Note: Loan Receivables (role-811020)

Uses `LoanReceivablesByAllocationDimension` (typed) + `AllocationByRemainingMaturityDimension` (explicit).

| Element | Context Type |
|---|---|
| `LoanReceivablesByAllocation` | Typed+Explicit (counterparty name + maturity) |
| `LoanReceivablesByAllocationForAdditionalDimensionalAllocation` | Typed+Explicit (counterparty + interest rate/currency/due date) — string value |
| `LoanReceivables` | Explicit only (maturity total) |

### Note: Contingent Liabilities and Assets (role-828000)

| Element | Description |
|---|---|
| `DistributableDividends` | Distributable dividends |
| `IncomeTaxLiabilityOnDistributableDividends` | Tax liability on distributable dividends |
| `GuaranteesThatAreNotIncludedInBalanceSheet` | Off-balance-sheet guarantees |
| `ContingentLiabilitiesTotal` | Total contingent liabilities |

### Note: Related Parties (role-843000)

**Period types are mixed** — most balance elements are `instant` (I2), but `Remuneration`, `RelatedPartiesSales*`, and `RelatedPartiesPurchases*` are `duration` (D21). The generator script handles this automatically.

| Element | Context | Applies to |
|---|---|---|
| `RelatedPartiesShortTermReceivablesAndPrepayments{Suffix}` | I2 (instant) | ST receivables by party type |
| `RelatedPartiesLongTermReceivablesAndPrepayments{Suffix}` | I2 (instant) | LT receivables by party type |
| `RelatedPartiesLongTermLoanLiabilities{Suffix}` | I2 (instant) | LT loan liabilities by party type |
| `RelatedPartiesGivenLoansOf{Suffix}` | I2 (instant) | Given loans by party type |
| `Remuneration` | **D21 (duration)** | Board/management remuneration |
| `RelatedPartiesSalesTotal` | **D21 (duration)** | Sales to related parties |
| `RelatedPartiesPurchasesTotal` | **D21 (duration)** | Purchases from related parties |

Party type suffixes: `ParentCompany`, `Subsidiaries`, `Associates`, `ManagementAndHigherSupervisoryBodyAndIndividualsWithMaterialOwnershipInterest`, `Total`.

### Note: Revenue (role-832000)

Uses tuples for breakdown by activity and geography.

| Element | Description |
|---|---|
| `NetSalesByOperatingActivitiesName` | Activity name (EMTAK code) |
| `NetSalesByOperatingActivitiesValue` | Revenue amount |
| `NetSalesByOperatingActivitiesTotal` | Total revenue |
| `NetSalesInEuropeanUnionTotal` | EU revenue total |
| `NetSalesOutsideOfEuropeanUnionTotal` | Non-EU revenue total |
| `NetSalesByGeographicalLocation` | Grand total by geography |

### Note: Personnel Expenses (role-839000)

| Element | Description |
|---|---|
| `WageAndSalaryExpense` | Wages and salaries |
| `SocialSecurityTaxes` | Social security taxes |
| `PensionExpense` | Pension expense |
| `LaborExpenseOther` | Other labor expenses |
| `LaborExpense` | Total labor expense |
| `AverageNumberOfEmployeesInFullTimeEquivalentUnits` | Average FTE count |

### Note: Income Tax (role-842000)

Uses `AllocationByIncomeTaxExpenseComponentsDimension` (periodType=**instant** — use instant context I2).

| Element | Description |
|---|---|
| `DeclaredDividends` | Dividends declared |
| `DeclaredDividendsEstonia` | Of which: Estonia |
| `DeclaredDividendsOtherCountries` | Of which: other countries |
| `IncomeTaxOnProfitForFinancialYear` | Income tax calculated |
| `IncomeTaxExpenseComponentsTotal` | Total income tax expense |

### Note: PP&E (role-816000)

**IMPORTANT: All `PropertyPlantAndEquipment*` elements are periodType=`duration` — use context D21.**

Uses `PropertyPlantAndEquipmentHypercube` with asset categories as dimension.

| Element | Description |
|---|---|
| `PropertyPlantAndEquipmentAtEndOfPreviousPeriodCarriedAtCost` | Opening cost |
| `PropertyPlantAndEquipmentAtEndOfPreviousPeriodAccumulatedDepreciation` | Opening accumulated depreciation |
| `PropertyPlantAndEquipmentAtEndOfPreviousPeriodResidualCost` | Opening NBV |
| `PropertyPlantAndEquipmentAcquisitionsAndAdditions` | Additions during period |
| `PropertyPlantAndEquipmentDepreciation` | Depreciation charge |
| `PropertyPlantAndEquipmentDisposals` | Disposals |
| `PropertyPlantAndEquipmentAtEndOfPeriodCarriedAtCost` | Closing cost |
| `PropertyPlantAndEquipmentAtEndOfPeriodAccumulatedDepreciation` | Closing accumulated depreciation |
| `PropertyPlantAndEquipmentAtEndOfPeriodResidualCost` | Closing NBV |

### Note: Intangible Assets (role-818000)

**All `IntangibleAssets*` elements are periodType=`instant` — use context I2** (opposite of PP&E).

Similar structure to PP&E with `IntangibleAssets` prefix. Uses dimension `IntangibleAssetsDimension` with members: `GoodwillAbstract`, `DevelopmentExpendituresAbstract`, `ComputerSoftwareAbstract`, `ConcessionsPatentsLicencesTrademarksAbstract`, `OtherIntangibleAssetsAbstract`.

### Note: Payables and Prepayments (role-822000)

Uses `AllocationByRemainingMaturityDimension` for maturity breakdown.

| Element | Description |
|---|---|
| `TradePayablesTotal` | Trade payables |
| `EmployeePayablesTotal` | Employee payables |
| `RelatedPartiesPayables` | Related party payables |
| `TaxPayables` | Tax payables |
| `InterestPayables` | Interest payables (child of `OtherPayablesTotal`) |
| `DividendPayables` | Dividend payables |
| `OtherAccruedExpenses` | Other accrued expenses |
| `OtherPayablesTotal` | Other payables total |
| `PrepaymentsReceivedTotal` | Prepayments received total |
| `PayablesAndPrepayments` | **Grand total** |

### Note: Loan Commitments (role-821000)

Similar to Loan Receivables with maturity dimension + typed counterparty dimension.

| Element | Description |
|---|---|
| `CurrentLoans` | Short-term loans (by counterparty + maturity) |
| `CurrentLoansTotal` | Short-term loans total |
| `NonCurrentLoans` | Long-term loans (by counterparty + maturity) |
| `NonCurrentLoansTotal` | Long-term loans total |
| `LoanCommitmentsTotal` | Grand total loan commitments |

### Note: Share Capital (role-831010)

| Element | Description |
|---|---|
| `ShareCapital2` | Share capital amount |
| `NumberOfShares2` | Number of shares |
| `NominalValueOfShares2` | Nominal value per share |

---

## Role Catalog for OÜ (osaühing)

### Core Financial Statements

| Role Code | Name | Linkbases | When to Include |
|---|---|---|---|
| `201010` | Balance Sheet (standard) | cal, def, pre | Medium/Large |
| `201012` | Balance Sheet (small) | cal, def, pre | Micro/Small |
| `301011` | Income Statement Scheme 1 | cal, def, pre | When user selects Scheme 1 |
| `301022` | Income Statement Scheme 2 | cal, def, pre | When user selects Scheme 2 |
| `401010` | Cash Flow (indirect) | cal, def, pre | Medium/Large only |
| `601010` | Equity Changes | def, pre | Medium/Large only |
| `702010` | Profit Allocation Proposal | cal, def, pre | When profit > 0 |
| `702020` | Loss Coverage Proposal | cal, def, pre | When loss |

### Notes

| Role Code | Name | Linkbases | When to Include |
|---|---|---|---|
| `801000` | Accounting Policies | def, pre | Small/Medium/Large |
| `801030` | Accounting Policies (Micro) | def, pre | Micro only |
| `802000` | Cash | def, pre | When cash data exists |
| `804010` | Receivables & Prepayments | cal, def, pre | When receivables exist |
| `805000` | Trade Receivables | def, pre | When trade receivables exist |
| `806000` | Tax Prepayments & Liabilities | def, pre | When tax items exist |
| `811020` | Loan Receivables | def, pre | When loan receivables exist |
| `816000` | PP&E | cal, def, pre | When fixed assets exist |
| `818000` | Intangible Assets | cal, def, pre | When intangible assets exist |
| `821000` | Loan Commitments | def, pre | When loan liabilities exist |
| `822000` | Payables & Prepayments | cal, def, pre | When payables exist |
| `828000` | Contingent Liabilities | cal, def, pre | Always (required) |
| `831010` | Share Capital | def, pre | When share capital details needed |
| `832000` | Revenue | def, pre | When revenue exists |
| `839000` | Personnel Expenses | cal, def, pre | When employees exist |
| `842000` | Income Tax | def, pre | When tax paid |
| `843000` | Related Parties | cal, def, pre | Always (required) |
| `844000` | Post-BS Events | def, pre | When post-BS events exist |

### Linkbase File Naming Convention

```
et-gaap_2026-01-01/role-{MAJOR}/cal_{FormName}_role-{FULL}.xml
et-gaap_2026-01-01/role-{MAJOR}/def_{FormName}_role-{FULL}.xml
et-gaap_2026-01-01/role-{MAJOR}/pre_{FormName}_role-{FULL}.xml
```

Form names by role code:
| Role | FormName |
|---|---|
| 201010 | `StatementOfFinancialPosition` |
| 201012 | `StatementOfFinancialPositionSmall` |
| 301011 | `IncomeStatementScheme1` |
| 301022 | `IncomeStatementScheme2` |
| 401010 | `StatementOfCashFlowsIndirectMethod` |
| 601010 | `StatementOfChangesInEquity` |
| 702010 | `ProfitDistributionProposal` |
| 702020 | `LossCoveringProposal` |
| 801000 | `NoteAccountingPolicies` |
| 801030 | `NoteAccountingPoliciesMicro` |
| 802000 | `NoteCashAndCashEquivalents` |
| 804010 | `NoteReceivablesAndPrepayments` |
| 805000 | `NoteAccountsReceivable` |
| 806000 | `NoteTaxPrepaymentsAndLiabilities` |
| 811020 | `NoteLoanReceivables` |
| 816000 | `NotePropertyPlantAndEquipment` |
| 818000 | `NoteIntangibleAssets` |
| 821000 | `NoteLoanCommitments` |
| 822000 | `NotePayablesAndPrepayments` |
| 828000 | `NoteContingentLiabilitiesAndAssets` |
| 831010 | `NoteShareCapital` |
| 832000 | `NoteNetSales` |
| 839000 | `NoteLaborExpense` |
| 842000 | `NoteIncomeTax` |
| 843000 | `NoteRelatedParties` |
| 844000 | `NoteEventsAfterReportingDate` |

---

## Validation Checklist

Before writing files, verify:

1. **Balance sheet balances**: `Assets` == `Liabilities` + `Equity` (context I2 and I1)
2. **Net profit consistency**: IS `TotalAnnualPeriodProfitLoss` == BS `AnnualPeriodProfitLoss`
3. **Cash flow reconciliation**: `CashAndCashEquivalentsAtEndOfPeriod` == BS `CashAndCashEquivalents`
4. **All contexts used**: Every `contextRef` in facts points to a defined context
5. **No orphan contexts**: Every context is referenced by at least one fact
6. **Monetary facts have unitRef**: All numeric facts include `unitRef="valuuta"` and `decimals="0"`
7. **XSD has matching roles**: Each role used in facts has corresponding linkbase refs in XSD
