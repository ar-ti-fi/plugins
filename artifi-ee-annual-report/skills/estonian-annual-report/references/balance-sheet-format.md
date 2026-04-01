# Balance Sheet Format (Bilanss) — Annex 1

The balance sheet follows the format prescribed by Annex 1 of the Estonian Accounting Act (Raamatupidamise seadus). One standard format for all companies.

## ASSETS (VARAD)

### A. Current Assets (Käibevara)

| Line | Estonian | English | Account Range | XBRL Element |
|---|---|---|---|---|
| A.I | Raha | Cash and cash equivalents | 1000-1099 | `et-gaap:CashAndCashEquivalents` |
| A.II | Lühiajalised finantsinvesteeringud | Short-term financial investments | 1100-1199 | `et-gaap:ShortTermFinancialInvestments` |
| A.III | Nõuded ja ettemaksed | Receivables and prepayments | 1200-1499 | `et-gaap:ShortTermReceivablesAndPrepayments` |
| A.III.1 | Ostjate nõuded | Trade receivables | 1200-1299 | `et-gaap:AccountsReceivables` |
| A.III.2 | Maksu- ja lõivunõuded | Tax and levy receivables | 1300-1349 | `et-gaap:TaxPrepaymentsAndReceivables` |
| A.III.3 | Muud lühiajalised nõuded | Other short-term receivables | 1350-1399 | `et-gaap:OtherReceivablesTotal` |
| A.III.4 | Ettemaksed | Prepayments | 1400-1499 | `et-gaap:PrepaymentsTotal` |
| A.IV | Varud | Inventories | 1500-1599 | `et-gaap:Inventories` |
| A.V | Bioloogilised varad | Biological assets (current) | 1600-1699 | `et-gaap:ShortTermBiologicalAssets` |
| | **Käibevara kokku** | **Total current assets** | | `et-gaap:CurrentAssets` |

### B. Non-Current Assets (Põhivara)

| Line | Estonian | English | Account Range | XBRL Element |
|---|---|---|---|---|
| B.I | Investeeringud tütar- ja sidusettevõtjatesse | Investments in subsidiaries and associates | 2000-2049 | `et-gaap:InvestmentsInSubsidiariesAndAssociates` |
| B.I.2 | Pikaajalised finantsinvesteeringud | Long-term financial investments | 2050-2099 | `et-gaap:LongTermFinancialInvestments` |
| B.I.3 | Pikaajalised nõuded ja ettemaksed | Long-term receivables and prepayments | (LT portion) | `et-gaap:LongTermReceivablesAndPrepayments` |
| B.II | Kinnisvarainvesteeringud | Investment property | 2100-2199 | `et-gaap:InvestmentProperty` |
| B.III | Materiaalne põhivara | Property, plant and equipment | 2200-2399 | `et-gaap:PropertyPlantAndEquipment` |
| B.III.1 | Maa | Land | 2200-2209 | `et-gaap:Land` |
| B.III.2 | Ehitised | Buildings | 2210-2249 | `et-gaap:Buildings` |
| B.III.3 | Masinad ja seadmed | Machinery and equipment | 2250-2299 | `et-gaap:MachineryAndEquipment` |
| B.III.4 | Muu materiaalne põhivara | Other tangible fixed assets | 2300-2349 | `et-gaap:OtherTangibleAssets` |
| B.III.5 | Lõpetamata põhivara | Assets under construction | 2350-2399 | `et-gaap:AssetsUnderConstruction` |
| B.IV | Immateriaalne põhivara | Intangible assets | 2400-2599 | `et-gaap:IntangibleAssets` |
| B.IV.1 | Firmaväärtus | Goodwill | 2400-2449 | `et-gaap:Goodwill` |
| B.IV.2 | Muu immateriaalne põhivara | Other intangible assets | 2450-2599 | `et-gaap:OtherIntangibleAssets` |
| B.V | Bioloogilised varad | Biological assets (non-current) | 2600-2699 | `et-gaap:LongTermBiologicalAssets` |
| | **Põhivara kokku** | **Total non-current assets** | | `et-gaap:NonCurrentAssets` |
| | **VARAD KOKKU** | **TOTAL ASSETS** | | `et-gaap:Assets` |

## LIABILITIES AND EQUITY (KOHUSTISED JA OMAKAPITAL)

### C. Current Liabilities (Lühiajalised kohustised)

| Line | Estonian | English | Account Range | XBRL Element |
|---|---|---|---|---|
| C.I | Laenukohustised | Loan liabilities (short-term) | 3000-3099 | `et-gaap:ShortTermLoanLiabilities` |
| C.II | Võlad ja ettemaksed | Payables and prepayments received | 3100-3499 | `et-gaap:ShortTermPayablesAndPrepayments` |
| C.II.1 | Tarnijate võlad | Trade payables | 3100-3199 | `et-gaap:TradePayablesTotal` |
| C.II.2 | Töövõtjate võlad | Employee payables | 3200-3249 | `et-gaap:EmployeePayablesTotal` |
| C.II.3 | Maksuvõlad | Tax liabilities | 3250-3349 | `et-gaap:TaxPayables` |
| C.II.4 | Muud lühiajalised võlad | Other short-term payables | 3350-3399 | `et-gaap:OtherPayablesTotal` |
| C.II.5 | Saadud ettemaksed | Prepayments received | 3400-3499 | `et-gaap:PrepaymentsReceivedTotal` |
| C.III | Eraldised | Provisions (short-term) | 3500-3549 | `et-gaap:ShortTermProvisions` |
| C.IV | Sihtfinantseerimine | Government grants (short-term) | 3550-3599 | `et-gaap:ShortTermGovernmentGrants` |
| | **Lühiajalised kohustised kokku** | **Total current liabilities** | | `et-gaap:CurrentLiabilities` |

### D. Non-Current Liabilities (Pikaajalised kohustised)

| Line | Estonian | English | Account Range | XBRL Element |
|---|---|---|---|---|
| D.I | Pikaajalised laenukohustised | Long-term loan liabilities | 3600-3699 | `et-gaap:LongTermLoanLiabilities` |
| D.II | Muud pikaajalised võlad | Other long-term payables | 3700-3799 | `et-gaap:LongTermPayablesAndPrepayments` |
| D.III | Eraldised | Provisions (long-term) | 3800-3849 | `et-gaap:LongTermProvisions` |
| D.IV | Sihtfinantseerimine | Government grants (long-term) | 3850-3899 | `et-gaap:LongTermGovernmentGrants` |
| | **Pikaajalised kohustised kokku** | **Total non-current liabilities** | | `et-gaap:NonCurrentLiabilities` |
| | **KOHUSTISED KOKKU** | **TOTAL LIABILITIES** | | `et-gaap:Liabilities` |

### E. Equity (Omakapital)

| Line | Estonian | English | Account Range | XBRL Element |
|---|---|---|---|---|
| E.I | Osakapital / Aktsiakapital | Issued capital | 5000-5049 | `et-gaap:IssuedCapital` |
| E.I.2 | Registreerimata osakapital | Unregistered equity | (if applicable) | `et-gaap:UnregisteredEquity` |
| E.I.3 | Sissemaksmata osakapital | Unpaid capital | (if applicable) | `et-gaap:UnpaidCapital` |
| E.II | Ülekurss | Share premium | 5050-5099 | `et-gaap:SharePremium` |
| E.III | Oma osad / aktsiad | Treasury shares (negative) | 5100-5149 | `et-gaap:TreasuryShares` |
| E.IV | Reservid | Reserves | 5150-5249 | (sum of E.IV.1 and E.IV.2) |
| E.IV.1 | Kohustuslik reservkapital | Statutory reserve capital | 5150-5199 | `et-gaap:StatutoryReserveCapital` |
| E.IV.2 | Muud reservid | Other reserves | 5200-5249 | `et-gaap:OtherReserves` |
| E.V | Eelmiste perioodide jaotamata kasum (kahjum) | Retained earnings (losses) | 5300-5399 | `et-gaap:RetainedEarningsLoss` |
| E.VI | Aruandeaasta kasum (kahjum) | Current year profit (loss) | Calculated | `et-gaap:AnnualPeriodProfitLoss` |
| | **Omakapital kokku** | **Total equity** | | `et-gaap:Equity` |
| | **KOHUSTISED JA OMAKAPITAL KOKKU** | **TOTAL LIABILITIES AND EQUITY** | | `et-gaap:LiabilitiesAndEquity` |

## Validation

**Total Assets MUST equal Total Liabilities + Total Equity.** If they do not balance, check retained earnings calculation and verify current year P&L flows correctly to equity.
