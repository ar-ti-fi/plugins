# Balance Sheet Format (Bilanss) — Annex 1

The balance sheet follows the format prescribed by Annex 1 of the Estonian Accounting Act (Raamatupidamise seadus). One standard format for all companies.

## ASSETS (VARAD)

### A. Current Assets (Kaibevara)

| Line | Estonian | English | Account Range | XBRL Element |
|---|---|---|---|---|
| A.I | Raha | Cash and cash equivalents | 1000-1099 | `et-gaap:Cash` |
| A.II | Luhiajalised finantsinvesteeringud | Short-term financial investments | 1100-1199 | `et-gaap:ShortTermFinancialInvestments` |
| A.III | Nouded ja ettemaksed | Receivables and prepayments | 1200-1499 | `et-gaap:ReceivablesAndPrepayments` |
| A.III.1 | Ostjate nouded | Trade receivables | 1200-1299 | `et-gaap:TradeReceivables` |
| A.III.2 | Maksu- ja loidunouded | Tax and levy receivables | 1300-1349 | `et-gaap:TaxReceivables` |
| A.III.3 | Muud luhiajalised nouded | Other short-term receivables | 1350-1399 | `et-gaap:OtherShortTermReceivables` |
| A.III.4 | Ettemaksed | Prepayments | 1400-1499 | `et-gaap:Prepayments` |
| A.IV | Varud | Inventories | 1500-1599 | `et-gaap:Inventories` |
| A.V | Bioloogilised varad | Biological assets (current) | 1600-1699 | `et-gaap:BiologicalAssetsCurrent` |
| | **Kaibevara kokku** | **Total current assets** | | `et-gaap:TotalCurrentAssets` |

### B. Non-Current Assets (Pohivara)

| Line | Estonian | English | Account Range | XBRL Element |
|---|---|---|---|---|
| B.I | Pikaajalised finantsinvesteeringud | Long-term financial investments | 2000-2099 | `et-gaap:LongTermFinancialInvestments` |
| B.II | Kinnisvarainvesteeringud | Investment property | 2100-2199 | `et-gaap:InvestmentProperty` |
| B.III | Materiaalne pohivara | Property, plant and equipment | 2200-2399 | `et-gaap:PropertyPlantEquipment` |
| B.III.1 | Maa | Land | 2200-2209 | `et-gaap:Land` |
| B.III.2 | Ehitised | Buildings | 2210-2249 | `et-gaap:Buildings` |
| B.III.3 | Masinad ja seadmed | Machinery and equipment | 2250-2299 | `et-gaap:MachineryAndEquipment` |
| B.III.4 | Muu materiaalne pohivara | Other tangible fixed assets | 2300-2349 | `et-gaap:OtherTangibleAssets` |
| B.III.5 | Lophimata pohivara | Assets under construction | 2350-2399 | `et-gaap:AssetsUnderConstruction` |
| B.IV | Immateriaalne pohivara | Intangible assets | 2400-2599 | `et-gaap:IntangibleAssets` |
| B.IV.1 | Firmavaartus | Goodwill | 2400-2449 | `et-gaap:Goodwill` |
| B.IV.2 | Muu immateriaalne pohivara | Other intangible assets | 2450-2599 | `et-gaap:OtherIntangibleAssets` |
| B.V | Bioloogilised varad | Biological assets (non-current) | 2600-2699 | `et-gaap:BiologicalAssetsNonCurrent` |
| | **Pohivara kokku** | **Total non-current assets** | | `et-gaap:TotalNonCurrentAssets` |
| | **VARAD KOKKU** | **TOTAL ASSETS** | | `et-gaap:TotalAssets` |

## LIABILITIES AND EQUITY (KOHUSTISED JA OMAKAPITAL)

### C. Current Liabilities (Luhiajalised kohustised)

| Line | Estonian | English | Account Range | XBRL Element |
|---|---|---|---|---|
| C.I | Laenukohustised | Borrowings (short-term) | 3000-3099 | `et-gaap:ShortTermBorrowings` |
| C.II | Votlad ja ettemaksed | Payables and prepayments received | 3100-3499 | `et-gaap:PayablesAndPrepayments` |
| C.II.1 | Tarnijate votlad | Trade payables | 3100-3199 | `et-gaap:TradePayables` |
| C.II.2 | Tovotjate votlad | Employee payables | 3200-3249 | `et-gaap:EmployeePayables` |
| C.II.3 | Maksuvotlad | Tax liabilities | 3250-3349 | `et-gaap:TaxLiabilities` |
| C.II.4 | Muud luhiajalised votlad | Other short-term payables | 3350-3399 | `et-gaap:OtherShortTermPayables` |
| C.II.5 | Saadud ettemaksed | Prepayments received | 3400-3499 | `et-gaap:PrepaymentsReceived` |
| C.III | Eraldised | Provisions (short-term) | 3500-3549 | `et-gaap:ShortTermProvisions` |
| C.IV | Sihtfinantseerimine | Government grants (short-term) | 3550-3599 | `et-gaap:GovernmentGrantsCurrent` |
| | **Luhiajalised kohustised kokku** | **Total current liabilities** | | `et-gaap:TotalCurrentLiabilities` |

### D. Non-Current Liabilities (Pikaajalised kohustised)

| Line | Estonian | English | Account Range | XBRL Element |
|---|---|---|---|---|
| D.I | Pikaajalised laenukohustised | Long-term borrowings | 3600-3699 | `et-gaap:LongTermBorrowings` |
| D.II | Muud pikaajalised votlad | Other long-term payables | 3700-3799 | `et-gaap:OtherLongTermPayables` |
| D.III | Eraldised | Provisions (long-term) | 3800-3849 | `et-gaap:LongTermProvisions` |
| D.IV | Sihtfinantseerimine | Government grants (long-term) | 3850-3899 | `et-gaap:GovernmentGrantsNonCurrent` |
| | **Pikaajalised kohustised kokku** | **Total non-current liabilities** | | `et-gaap:TotalNonCurrentLiabilities` |
| | **KOHUSTISED KOKKU** | **TOTAL LIABILITIES** | | `et-gaap:TotalLiabilities` |

### E. Equity (Omakapital)

| Line | Estonian | English | Account Range | XBRL Element |
|---|---|---|---|---|
| E.I | Osakapital / Aktsiakapital | Share capital | 5000-5049 | `et-gaap:ShareCapital` |
| E.II | Ulekurss | Share premium | 5050-5099 | `et-gaap:SharePremium` |
| E.III | Oma osad / aktsiad | Treasury shares (negative) | 5100-5149 | `et-gaap:TreasuryShares` |
| E.IV | Reservid | Reserves | 5150-5249 | `et-gaap:Reserves` |
| E.IV.1 | Kohustuslik reservkapital | Statutory reserve | 5150-5199 | `et-gaap:StatutoryReserve` |
| E.IV.2 | Muud reservid | Other reserves | 5200-5249 | `et-gaap:OtherReserves` |
| E.V | Eelmiste perioodide jaotamata kasum (kahjum) | Retained earnings (losses) | 5300-5399 | `et-gaap:RetainedEarnings` |
| E.VI | Aruandeaasta kasum (kahjum) | Current year profit (loss) | Calculated | `et-gaap:CurrentYearProfitLoss` |
| | **Omakapital kokku** | **Total equity** | | `et-gaap:TotalEquity` |
| | **KOHUSTISED JA OMAKAPITAL KOKKU** | **TOTAL LIABILITIES AND EQUITY** | | `et-gaap:TotalLiabilitiesAndEquity` |

## Validation

**Total Assets MUST equal Total Liabilities + Total Equity.** If they do not balance, check retained earnings calculation and verify current year P&L flows correctly to equity.
