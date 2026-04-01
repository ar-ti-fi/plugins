# Income Statement Format (Kasumiaruanne) — Annex 2

Two permitted formats under Annex 2 of the Accounting Act. Most Estonian SMEs use Scheme 1.

## Scheme 1 — By Nature of Expense (Kasumiaruanne skeem 1)

Most common for micro, small, and medium companies.

| Line | Estonian | English | Account Range | XBRL Element |
|---|---|---|---|---|
| 1 | Müügitulu | Revenue (sales) | 4000-4099 | `et-gaap:Revenue` |
| 2 | Muud äritulud | Other income | 4100-4199 | `et-gaap:OtherIncome` |
| 2a | Põllumajandustoodangu varude muutus | Change in inventories of agricultural production | (if applicable) | `et-gaap:ChangesInInventoriesOfAgriculturalProduction` |
| 2b | Kasum (kahjum) bioloogilistelt varadelt | Profit/loss from biological assets | (if applicable) | `et-gaap:ProfitLossFromBiologicalAssets` |
| 3 | Valmis- ja lõpetamata toodangu varude muutus | Change in inventories of finished goods/WIP | 4200-4249 | `et-gaap:ChangesInInventoriesOfFinishedGoodsAndWorkInProgress` |
| 3a | Kapitaliseeritud väljaminekud oma tarbeks | Work performed by entity and capitalised | (if applicable) | `et-gaap:WorkPerformedByEntityAndCapitalised` |
| 4 | Kaubad, toore, materjal ja teenused | Raw materials and consumables used | 5100-5199 | `et-gaap:RawMaterialsAndConsumablesUsed` |
| 5 | Mitmesugused tegevuskulud | Other operating expense | 5200-5299 | `et-gaap:OtherOperatingExpense` |
| 6 | Tööjõukulud | Employee expense | 5300-5399 | `et-gaap:EmployeeExpense` |
| 6a | palgakulu | Wages and salaries | 5300-5349 | `et-gaap:WageAndSalaryExpense` |
| 6b | sotsiaalmaksud | Social security taxes | 5350-5379 | `et-gaap:SocialSecurityTaxes` |
| 6c | pensionikulu | Pension expense | 5380-5399 | `et-gaap:PensionExpense` |
| 7 | Põhi- ja immateriaalne vara kulum ja väärtuse langus | Depreciation, amortization, and impairment | 5400-5499 | `et-gaap:DepreciationAndImpairmentLossReversal` |
| 7a | Käibevara allahindlus | Significant impairment of current assets | (if applicable) | `et-gaap:SignificantImpairmentOfCurrentAssets` |
| 8 | Muud ärikulud | Other expense | 5500-5599 | `et-gaap:OtherExpense` |
| | **Ärikasum (-kahjum)** | **Operating profit (loss)** | Calculated | `et-gaap:TotalProfitLoss` |
| 9a | Kasum (kahjum) tütarettevõtjatelt | Profit/loss from subsidiaries | (if applicable) | `et-gaap:ProfitLossFromSubsidiaries` |
| 9b | Kasum (kahjum) sidusettevõtjatelt | Profit/loss from associates | (if applicable) | `et-gaap:ProfitLossFromAssociates` |
| 9c | Kasum (kahjum) finantsinvesteeringutelt | Gain/loss from financial investments | 6000-6099 | `et-gaap:GainLossFromFinancialInvestments` |
| 9d | Intressitulud | Interest income | 6100-6199 | `et-gaap:InterestIncome` |
| 9e | Intressikulud | Interest expenses | 6500-6599 | `et-gaap:InterestExpenses` |
| 9f | Muud finantstulud ja -kulud | Other financial income and expense | 6600-6999 | `et-gaap:OtherFinancialIncomeAndExpense` |
| | **Kasum (kahjum) enne tulumaksu** | **Profit (loss) before income tax** | Calculated | `et-gaap:TotalProfitLossBeforeTax` |
| 10 | Tulumaks | Income tax expense | 7000-7099 | `et-gaap:IncomeTaxExpense` |
| | **Aruandeaasta puhaskasum (-kahjum)** | **Net profit (loss) for the year** | Calculated | `et-gaap:TotalAnnualPeriodProfitLoss` |

## Scheme 2 — By Function of Expense (Kasumiaruanne skeem 2)

Used by companies that organize costs by department/function.

| Line | Estonian | English | XBRL Element |
|---|---|---|---|
| 1 | Müügitulu | Revenue (sales) | `et-gaap:Revenue` |
| 2 | Müüdud kaupade ja teenuste kulu | Cost of goods sold | `et-gaap:CostOfGoodsSold` |
| | **Brutokasum (-kahjum)** | **Gross profit (loss)** | `et-gaap:GrossProfitLoss` |
| 3 | Turustuskulud | Distribution costs | `et-gaap:DistributionCosts` |
| 4 | Üldhalduskulud | General and administrative expenses | `et-gaap:AdministrativeExpenses` |
| 5 | Muud äritulud | Other income | `et-gaap:OtherIncome` |
| 6 | Muud ärikulud | Other expense | `et-gaap:OtherExpense` |
| | **Ärikasum (-kahjum)** | **Operating profit (loss)** | `et-gaap:TotalProfitLoss` |
| 7a | Kasum (kahjum) tütarettevõtjatelt | Profit/loss from subsidiaries | `et-gaap:ProfitLossFromSubsidiaries` |
| 7b | Kasum (kahjum) sidusettevõtjatelt | Profit/loss from associates | `et-gaap:ProfitLossFromAssociates` |
| 7c | Kasum (kahjum) finantsinvesteeringutelt | Gain/loss from financial investments | `et-gaap:GainLossFromFinancialInvestments` |
| 7d | Intressitulud | Interest income | `et-gaap:InterestIncome` |
| 7e | Intressikulud | Interest expenses | `et-gaap:InterestExpenses` |
| 7f | Muud finantstulud ja -kulud | Other financial income and expense | `et-gaap:OtherFinancialIncomeAndExpense` |
| | **Kasum (kahjum) enne tulumaksu** | **Profit (loss) before income tax** | `et-gaap:TotalProfitLossBeforeTax` |
| 8 | Tulumaks | Income tax expense | `et-gaap:IncomeTaxExpense` |
| | **Aruandeaasta puhaskasum (-kahjum)** | **Net profit (loss) for the year** | `et-gaap:TotalAnnualPeriodProfitLoss` |

## Estonian CIT Note

Estonia has a unique corporate income tax system — no tax on retained earnings. CIT is levied only when profits are distributed as dividends at 20/80 rate (20% on the net distribution, equivalent to 25% on the gross amount). Line 10 (Tulumaks) only has a value if dividends were paid during the reporting period.
