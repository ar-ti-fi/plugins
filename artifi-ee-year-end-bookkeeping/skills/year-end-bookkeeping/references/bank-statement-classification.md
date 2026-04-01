# Bank Statement Line Classification Guide

This reference helps classify each bank statement line into the correct transaction type for posting.

## Classification Decision Tree

Process each bank line through these rules **in order**. The first matching rule wins.

### 1. Transfers Between Own Accounts → BANK_TRANSFER

If the counterparty IBAN belongs to another bank account of the same company:
- **Type**: BANK_TRANSFER
- **Example**: Transfer from LHV to Wise, or from main account to savings
- **Clue**: Both IBANs belong to the entity's bank accounts in the system

### 2. Bank Fees → BANK_FEE

Description contains any of these Estonian/English keywords:
- `teenustasu`, `tasu`, `komisjonitasu`, `konto hooldustasu`
- `pangateenuse tasu`, `kaardimakse tasu`, `konverteerimistasu`
- `fee`, `commission`, `service charge`, `account maintenance`
- `monthly fee`, `card fee`, `conversion fee`

**Type**: BANK_FEE (always an outflow)

### 3. Bank Interest → BANK_INTEREST

Description contains:
- `intress`, `intressitulu`, `hoiuseintress`
- `interest`, `deposit interest`, `savings interest`

**Type**: BANK_INTEREST (usually an inflow; if negative/outflow = loan interest, use JOURNAL_ENTRY)

### 4. Tax Payments to EMTA → JOURNAL_ENTRY

Counterparty is **EMTA** (Maksu- ja Tolliamet / Estonian Tax and Customs Board):
- IBAN: usually EE28 2200 2210 ... or similar EMTA account
- Name contains: `EMTA`, `Maksu- ja Tolliamet`, `Tax and Customs`

Common EMTA payments and their accounts:
| Description Pattern | What It Is | Typical Account |
|---|---|---|
| `sotsiaalmaks`, `social tax` | Social tax (33%) | Social tax expense |
| `tulumaks`, `income tax` | Income tax (on dividends) | Income tax expense |
| `toojouhumaks`, `unemployment ins.` | Unemployment insurance | Employment expense |
| `kaibemaks`, `VAT`, `KMD` | VAT payment | VAT payable |
| `kogumispension`, `pension` | Funded pension | Employment expense |
| General EMTA payment | Combined tax payment | Tax liability clearing |

**Type**: JOURNAL_ENTRY — debit the appropriate tax expense/liability account, credit bank.

### 5. Pension Fund → JOURNAL_ENTRY

Counterparty contains:
- `pensionikeskus`, `pension centre`, `II sammas`, `III sammas`
- `Pensionikeskus AS`

**Type**: JOURNAL_ENTRY — pension fund contribution (employee withholding).

### 6. Loan Transactions → LOAN_DISBURSEMENT or LOAN_REPAYMENT

Description contains:
- `laen`, `laenumakse`, `laenu tagasimakse`, `loan`, `loan repayment`
- `liisingumakse`, `leasing`, `lease payment`

**Direction determines type:**
- Money IN from a bank/lender → LOAN_DISBURSEMENT (receiving a loan)
- Money OUT to a bank/lender → LOAN_REPAYMENT (repaying a loan)

**Important**: Loan repayments often include both principal and interest. If the user has a loan amortization schedule, split accordingly. If not, post the full amount as LOAN_REPAYMENT and note that the interest/principal split should be done in Phase 4.

### 7. Dividend / Profit Distribution → OWNER_DISTRIBUTION

Description contains:
- `dividend`, `dividendimakse`, `kasumijaotus`, `kasumi valjamakse`
- `profit distribution`, `dividend payment`

**Type**: OWNER_DISTRIBUTION (always an outflow to owners/shareholders).

### 8. Capital Contribution → CAPITAL_CONTRIBUTION

Description contains:
- `osakapital`, `osakapitali sissemakse`, `share capital`
- `capital contribution`, `investment into company`

**Type**: CAPITAL_CONTRIBUTION (inflow from owners increasing capital).

### 9. Salary Payments → JOURNAL_ENTRY

Description contains:
- `palk`, `palga`, `palga ulekanne`, `salary`, `wage`
- `toovotasu`, `compensation`

**Type**: JOURNAL_ENTRY — debit salary liability (already accrued) or salary expense, credit bank.

### 10. Known Vendor (Outflow) → AP_PAYMENT

If the counterparty matches a known vendor AND the amount is negative (outflow):
- **Type**: AP_PAYMENT
- Link to the vendor_id
- If there's a matching AP_INVOICE, link to it

### 11. Known Customer (Inflow) → AR_PAYMENT

If the counterparty matches a known customer AND the amount is positive (inflow):
- **Type**: AR_PAYMENT
- Link to the customer_id
- If there's a matching AR_INVOICE, link to it

### 12. Unknown Outflow → AP_PAYMENT (default)

Outflow to an unknown counterparty:
- Create as vendor first (Step 8), then post as AP_PAYMENT
- Mark for review in Phase 4 — may need a matching bill

### 13. Unknown Inflow → AR_PAYMENT (default)

Inflow from an unknown counterparty:
- Create as customer first (Step 8), then post as AR_PAYMENT
- Mark for review in Phase 4 — may need a matching invoice

---

## Estonian-Specific Patterns

### Common Counterparty Names and Their Classifications

| Counterparty | Type | Notes |
|---|---|---|
| EMTA / Maksu- ja Tolliamet | Tax authority | Always JOURNAL_ENTRY |
| AS Pensionikeskus | Pension fund | JOURNAL_ENTRY |
| Eesti Haigekassa | Health insurance | JOURNAL_ENTRY |
| Eesti Tootukassa | Unemployment fund | JOURNAL_ENTRY |
| Telia Eesti AS | Telecom vendor | AP_PAYMENT |
| Elektrilevi OU | Electricity vendor | AP_PAYMENT |
| Eesti Energia AS | Energy vendor | AP_PAYMENT |
| Tallinna Vesi AS | Water vendor | AP_PAYMENT |
| AS SEB Pank / AS LHV Pank | Bank (own or fees) | BANK_FEE or BANK_TRANSFER |
| Bolt Operations OU | Transport/taxi | AP_PAYMENT |
| Wolt Technology OU | Food delivery | AP_PAYMENT |

### Bank Statement CSV Column Names by Bank

**LHV**: Kuupaev; Saaja/Maksja; Saaja/Maksja konto; Selgitus; Summa; Saldo
**SEB**: Kuupaev; Saaja/Maksja nimi; Saaja/Maksja konto nr; Selgitus; Summa; Saldo
**Swedbank**: Kuupaev; Saaja/Maksja; Konto; Selgitus; Summa; Saldo paev lopus
**Wise**: Date; Description; Target name; Target account; Amount; Balance

All banks use semicolons as delimiters (except Wise which uses commas). Dates are in DD.MM.YYYY format (except Wise which uses YYYY-MM-DD).

---

## Classification Summary Table

| Rule # | Pattern | Transaction Type | Direction |
|--------|---------|-----------------|-----------|
| 1 | Own account transfer | BANK_TRANSFER | Both |
| 2 | Fee keywords | BANK_FEE | Out |
| 3 | Interest keywords | BANK_INTEREST | In (usually) |
| 4 | EMTA / tax authority | JOURNAL_ENTRY | Out |
| 5 | Pension fund | JOURNAL_ENTRY | Out |
| 6 | Loan keywords | LOAN_DISBURSEMENT / LOAN_REPAYMENT | Both |
| 7 | Dividend keywords | OWNER_DISTRIBUTION | Out |
| 8 | Capital keywords | CAPITAL_CONTRIBUTION | In |
| 9 | Salary keywords | JOURNAL_ENTRY | Out |
| 10 | Known vendor | AP_PAYMENT | Out |
| 11 | Known customer | AR_PAYMENT | In |
| 12 | Unknown outflow | AP_PAYMENT (default) | Out |
| 13 | Unknown inflow | AR_PAYMENT (default) | In |
