# XBRL Mapping Reference

Maps Artifi chart of accounts to Estonian GAAP XBRL taxonomy elements.

## Taxonomy

- **Taxonomy**: et-gaap_2026-01-01
- **Source**: xbrl.eesti.ee
- **Based on**: XBRL 2.1 specification with Dimensions 1.0

## Balance Sheet Mapping

| Account Range | BS Line | XBRL Element |
|---|---|---|
| 1000-1099 | Cash and cash equivalents | `et-gaap:CashAndCashEquivalents` |
| 1100-1199 | Short-term financial investments | `et-gaap:ShortTermFinancialInvestments` |
| 1200-1499 | Short-term receivables and prepayments | `et-gaap:ShortTermReceivablesAndPrepayments` |
| 1200-1299 | Trade receivables (note detail) | `et-gaap:AccountsReceivables` |
| 1300-1349 | Tax receivables (note detail) | `et-gaap:TaxPrepaymentsAndReceivables` |
| 1350-1399 | Other ST receivables (note detail) | `et-gaap:OtherReceivablesTotal` |
| 1400-1499 | Prepayments (note detail) | `et-gaap:PrepaymentsTotal` |
| 1500-1599 | Inventories | `et-gaap:Inventories` |
| 1600-1699 | Biological assets (current) | `et-gaap:ShortTermBiologicalAssets` |
| 2000-2049 | Investments in subsidiaries/associates | `et-gaap:InvestmentsInSubsidiariesAndAssociates` |
| 2050-2099 | Long-term financial investments | `et-gaap:LongTermFinancialInvestments` |
| 2100-2199 | Investment property | `et-gaap:InvestmentProperty` |
| 2200-2399 | Property, plant and equipment | `et-gaap:PropertyPlantAndEquipment` |
| 2200-2209 | Land | `et-gaap:Land` |
| 2210-2249 | Buildings | `et-gaap:Buildings` |
| 2250-2299 | Machinery & equipment | `et-gaap:MachineryAndEquipment` |
| 2300-2349 | Other tangible assets | `et-gaap:OtherTangibleAssets` |
| 2350-2399 | Assets under construction | `et-gaap:AssetsUnderConstruction` |
| 2400-2599 | Intangible assets | `et-gaap:IntangibleAssets` |
| 2400-2449 | Goodwill | `et-gaap:Goodwill` |
| 2450-2599 | Other intangible assets | `et-gaap:OtherIntangibleAssets` |
| 2600-2699 | Biological assets (non-current) | `et-gaap:LongTermBiologicalAssets` |
| 3000-3099 | Short-term loan liabilities | `et-gaap:ShortTermLoanLiabilities` |
| 3100-3499 | Short-term payables and prepayments | `et-gaap:ShortTermPayablesAndPrepayments` |
| 3100-3199 | Trade payables (note detail) | `et-gaap:TradePayablesTotal` |
| 3200-3249 | Employee payables (note detail) | `et-gaap:EmployeePayablesTotal` |
| 3250-3349 | Tax liabilities (note detail) | `et-gaap:TaxPayables` |
| 3350-3399 | Other ST payables (note detail) | `et-gaap:OtherPayablesTotal` |
| 3400-3499 | Prepayments received (note detail) | `et-gaap:PrepaymentsReceivedTotal` |
| 3500-3549 | Short-term provisions | `et-gaap:ShortTermProvisions` |
| 3550-3599 | Government grants (current) | `et-gaap:ShortTermGovernmentGrants` |
| 3600-3699 | Long-term loan liabilities | `et-gaap:LongTermLoanLiabilities` |
| 3700-3799 | Long-term payables and prepayments | `et-gaap:LongTermPayablesAndPrepayments` |
| 3800-3849 | Long-term provisions | `et-gaap:LongTermProvisions` |
| 3850-3899 | Government grants (non-current) | `et-gaap:LongTermGovernmentGrants` |
| 5000-5049 | Issued capital | `et-gaap:IssuedCapital` |
| 5050-5099 | Share premium | `et-gaap:SharePremium` |
| 5100-5149 | Treasury shares | `et-gaap:TreasuryShares` |
| 5150-5199 | Statutory reserve capital | `et-gaap:StatutoryReserveCapital` |
| 5200-5249 | Other reserves | `et-gaap:OtherReserves` |
| 5300-5399 | Retained earnings (loss) | `et-gaap:RetainedEarningsLoss` |

## Income Statement Mapping (Scheme 1)

| Account Range | IS Line | XBRL Element |
|---|---|---|
| 4000-4099 | Revenue | `et-gaap:Revenue` |
| 4100-4199 | Other income | `et-gaap:OtherIncome` |
| 4200-4249 | Change in inventories of finished goods/WIP | `et-gaap:ChangesInInventoriesOfFinishedGoodsAndWorkInProgress` |
| 5100-5199 | Raw materials and consumables used | `et-gaap:RawMaterialsAndConsumablesUsed` |
| 5200-5299 | Other operating expense | `et-gaap:OtherOperatingExpense` |
| 5300-5399 | Employee expense | `et-gaap:EmployeeExpense` |
| 5300-5349 | Wages and salaries (note detail) | `et-gaap:WageAndSalaryExpense` |
| 5350-5379 | Social tax (note detail) | `et-gaap:SocialSecurityTaxes` |
| 5380-5399 | Pension expense (note detail) | `et-gaap:PensionExpense` |
| 5400-5499 | Depreciation and impairment loss/reversal | `et-gaap:DepreciationAndImpairmentLossReversal` |
| 5500-5599 | Other expense | `et-gaap:OtherExpense` |
| 6000-6099 | Gain/loss from financial investments | `et-gaap:GainLossFromFinancialInvestments` |
| 6100-6199 | Interest income | `et-gaap:InterestIncome` |
| 6500-6599 | Interest expenses | `et-gaap:InterestExpenses` |
| 6600-6999 | Other financial income and expense | `et-gaap:OtherFinancialIncomeAndExpense` |
| 7000-7099 | Income tax expense | `et-gaap:IncomeTaxExpense` |

## Calculated Totals

| Total | XBRL Element |
|---|---|
| Total current assets | `et-gaap:CurrentAssets` |
| Total non-current assets | `et-gaap:NonCurrentAssets` |
| Total assets | `et-gaap:Assets` |
| Total current liabilities | `et-gaap:CurrentLiabilities` |
| Total non-current liabilities | `et-gaap:NonCurrentLiabilities` |
| Total liabilities | `et-gaap:Liabilities` |
| Total equity | `et-gaap:Equity` |
| Total liabilities & equity | `et-gaap:LiabilitiesAndEquity` |
| Operating profit/loss | `et-gaap:TotalProfitLoss` |
| Profit before tax | `et-gaap:TotalProfitLossBeforeTax` |
| Net profit/loss | `et-gaap:TotalAnnualPeriodProfitLoss` |
| Current year profit/loss (equity) | `et-gaap:AnnualPeriodProfitLoss` |
