# Income Statement Format (Kasumiaruanne) — Annex 2

Two permitted formats under Annex 2 of the Accounting Act. Most Estonian SMEs use Scheme 1.

## Scheme 1 — By Nature of Expense (Kasumiaruanne skeem 1)

Most common for micro, small, and medium companies.

| Line | Estonian | English | Account Range | XBRL Element |
|---|---|---|---|---|
| 1 | Muugitulu | Revenue (sales) | 4000-4099 | `et-gaap:Revenue` |
| 2 | Muud aritulud | Other operating income | 4100-4199 | `et-gaap:OtherOperatingIncome` |
| 3 | Valmis- ja lopetamata toodangu varude muutus | Change in inventories of finished goods/WIP | 4200-4249 | `et-gaap:ChangeInInventories` |
| 4 | Kaup, toore, materjal ja teenused | Goods, raw materials, and services | 5100-5199 | `et-gaap:GoodsRawMaterialsServices` |
| 5 | Mitmesugused tegevuskulud | Miscellaneous operating expenses | 5200-5299 | `et-gaap:MiscellaneousOperatingExpenses` |
| 6 | Toojoukulud | Personnel expenses | 5300-5399 | `et-gaap:PersonnelExpenses` |
| 6a | palgakulu | Wages and salaries | 5300-5349 | `et-gaap:WagesAndSalaries` |
| 6b | sotsiaalmaksud | Social tax | 5350-5379 | `et-gaap:SocialTaxExpense` |
| 6c | pensionikulu | Pension contributions | 5380-5399 | `et-gaap:PensionExpense` |
| 7 | Pohi- ja immateriaalne vara kulum ja vaartuse langus | Depreciation, amortization, and impairment | 5400-5499 | `et-gaap:DepreciationAmortizationImpairment` |
| 8 | Muud arikulud | Other operating expenses | 5500-5599 | `et-gaap:OtherOperatingExpenses` |
| | **Arikasum (-kahjum)** | **Operating profit (loss)** | Calculated | `et-gaap:OperatingProfitLoss` |
| 9 | Finantstulud ja -kulud | Financial income and expenses | 6000-6999 | `et-gaap:FinancialIncomeExpenses` |
| 9a | Finantstulud | Financial income | 6000-6499 | `et-gaap:FinancialIncome` |
| 9b | Finantskulud | Financial expenses | 6500-6999 | `et-gaap:FinancialExpenses` |
| | **Kasum (kahjum) enne tulumaksu** | **Profit (loss) before income tax** | Calculated | `et-gaap:ProfitLossBeforeTax` |
| 10 | Tulumaks | Income tax expense | 7000-7099 | `et-gaap:IncomeTaxExpense` |
| | **Aruandeaasta puhaskasum (-kahjum)** | **Net profit (loss) for the year** | Calculated | `et-gaap:NetProfitLoss` |

## Scheme 2 — By Function of Expense (Kasumiaruanne skeem 2)

Used by companies that organize costs by department/function.

| Line | Estonian | English | XBRL Element |
|---|---|---|---|
| 1 | Muugitulu | Revenue (sales) | `et-gaap:Revenue` |
| 2 | Muudud kaupade ja teenuste kulu | Cost of goods sold | `et-gaap:CostOfGoodsSold` |
| | **Brutokasum (-kahjum)** | **Gross profit (loss)** | `et-gaap:GrossProfitLoss` |
| 3 | Turustuskulud | Distribution costs | `et-gaap:DistributionCosts` |
| 4 | Uldhaldukulud | General and administrative expenses | `et-gaap:AdministrativeExpenses` |
| 5 | Muud aritulud | Other operating income | `et-gaap:OtherOperatingIncome` |
| 6 | Muud arikulud | Other operating expenses | `et-gaap:OtherOperatingExpenses` |
| | **Arikasum (-kahjum)** | **Operating profit (loss)** | `et-gaap:OperatingProfitLoss` |
| 7 | Finantstulud ja -kulud | Financial income and expenses | `et-gaap:FinancialIncomeExpenses` |
| | **Kasum (kahjum) enne tulumaksu** | **Profit (loss) before income tax** | `et-gaap:ProfitLossBeforeTax` |
| 8 | Tulumaks | Income tax expense | `et-gaap:IncomeTaxExpense` |
| | **Aruandeaasta puhaskasum (-kahjum)** | **Net profit (loss) for the year** | `et-gaap:NetProfitLoss` |

## Estonian CIT Note

Estonia has a unique corporate income tax system — no tax on retained earnings. CIT is levied only when profits are distributed as dividends at 20/80 rate (20% on the net distribution, equivalent to 25% on the gross amount). Line 10 (Tulumaks) only has a value if dividends were paid during the reporting period.
