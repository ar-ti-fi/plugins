# XBRL Mapping Reference

Maps Arfiti chart of accounts to Estonian GAAP XBRL taxonomy elements.

## Taxonomy

- **Taxonomy**: et-gaap-2026
- **Source**: xbrl.eesti.ee
- **Based on**: XBRL 2.1 specification with Dimensions 1.0

## Balance Sheet Mapping

| Account Range | BS Line | XBRL Element |
|---|---|---|
| 1000-1099 | Cash | `et-gaap:Cash` |
| 1100-1199 | Short-term investments | `et-gaap:ShortTermFinancialInvestments` |
| 1200-1299 | Trade receivables | `et-gaap:TradeReceivables` |
| 1300-1349 | Tax receivables | `et-gaap:TaxReceivables` |
| 1350-1399 | Other ST receivables | `et-gaap:OtherShortTermReceivables` |
| 1400-1499 | Prepayments | `et-gaap:Prepayments` |
| 1500-1599 | Inventories | `et-gaap:Inventories` |
| 1600-1699 | Biological assets (CA) | `et-gaap:BiologicalAssetsCurrent` |
| 2000-2099 | LT investments | `et-gaap:LongTermFinancialInvestments` |
| 2100-2199 | Investment property | `et-gaap:InvestmentProperty` |
| 2200-2209 | Land | `et-gaap:Land` |
| 2210-2249 | Buildings | `et-gaap:Buildings` |
| 2250-2299 | Machinery & equipment | `et-gaap:MachineryAndEquipment` |
| 2300-2349 | Other tangible assets | `et-gaap:OtherTangibleAssets` |
| 2350-2399 | Assets under construction | `et-gaap:AssetsUnderConstruction` |
| 2400-2449 | Goodwill | `et-gaap:Goodwill` |
| 2450-2599 | Other intangible assets | `et-gaap:OtherIntangibleAssets` |
| 2600-2699 | Biological assets (NCA) | `et-gaap:BiologicalAssetsNonCurrent` |
| 3000-3099 | ST borrowings | `et-gaap:ShortTermBorrowings` |
| 3100-3199 | Trade payables | `et-gaap:TradePayables` |
| 3200-3249 | Employee payables | `et-gaap:EmployeePayables` |
| 3250-3349 | Tax liabilities | `et-gaap:TaxLiabilities` |
| 3350-3399 | Other ST payables | `et-gaap:OtherShortTermPayables` |
| 3400-3499 | Prepayments received | `et-gaap:PrepaymentsReceived` |
| 3500-3549 | ST provisions | `et-gaap:ShortTermProvisions` |
| 3550-3599 | Government grants (ST) | `et-gaap:GovernmentGrantsCurrent` |
| 3600-3699 | LT borrowings | `et-gaap:LongTermBorrowings` |
| 3700-3799 | Other LT payables | `et-gaap:OtherLongTermPayables` |
| 3800-3849 | LT provisions | `et-gaap:LongTermProvisions` |
| 3850-3899 | Government grants (LT) | `et-gaap:GovernmentGrantsNonCurrent` |
| 5000-5049 | Share capital | `et-gaap:ShareCapital` |
| 5050-5099 | Share premium | `et-gaap:SharePremium` |
| 5100-5149 | Treasury shares | `et-gaap:TreasuryShares` |
| 5150-5199 | Statutory reserve | `et-gaap:StatutoryReserve` |
| 5200-5249 | Other reserves | `et-gaap:OtherReserves` |
| 5300-5399 | Retained earnings | `et-gaap:RetainedEarnings` |

## Income Statement Mapping (Scheme 1)

| Account Range | IS Line | XBRL Element |
|---|---|---|
| 4000-4099 | Revenue | `et-gaap:Revenue` |
| 4100-4199 | Other operating income | `et-gaap:OtherOperatingIncome` |
| 4200-4249 | Change in inventories | `et-gaap:ChangeInInventories` |
| 5100-5199 | Goods, materials, services | `et-gaap:GoodsRawMaterialsServices` |
| 5200-5299 | Misc operating expenses | `et-gaap:MiscellaneousOperatingExpenses` |
| 5300-5349 | Wages and salaries | `et-gaap:WagesAndSalaries` |
| 5350-5379 | Social tax | `et-gaap:SocialTaxExpense` |
| 5380-5399 | Pension contributions | `et-gaap:PensionExpense` |
| 5400-5499 | Depreciation & amortization | `et-gaap:DepreciationAmortizationImpairment` |
| 5500-5599 | Other operating expenses | `et-gaap:OtherOperatingExpenses` |
| 6000-6499 | Financial income | `et-gaap:FinancialIncome` |
| 6500-6999 | Financial expenses | `et-gaap:FinancialExpenses` |
| 7000-7099 | Income tax expense | `et-gaap:IncomeTaxExpense` |

## Calculated Totals

| Total | XBRL Element |
|---|---|
| Total current assets | `et-gaap:TotalCurrentAssets` |
| Total non-current assets | `et-gaap:TotalNonCurrentAssets` |
| Total assets | `et-gaap:TotalAssets` |
| Total current liabilities | `et-gaap:TotalCurrentLiabilities` |
| Total non-current liabilities | `et-gaap:TotalNonCurrentLiabilities` |
| Total liabilities | `et-gaap:TotalLiabilities` |
| Total equity | `et-gaap:TotalEquity` |
| Total liabilities & equity | `et-gaap:TotalLiabilitiesAndEquity` |
| Operating profit/loss | `et-gaap:OperatingProfitLoss` |
| Profit before tax | `et-gaap:ProfitLossBeforeTax` |
| Net profit/loss | `et-gaap:NetProfitLoss` |
| Current year profit/loss (equity) | `et-gaap:CurrentYearProfitLoss` |
