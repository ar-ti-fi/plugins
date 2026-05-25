# NAV calculation — formulas and account mapping

The mechanics of NAV strike on the Arfiti GL.

## NAV at the strike date

```
NAV_strike = ASSETS_at_FV − LIABILITIES_excluding_investor_capital
```

The accounts that contribute (using the fund COA additions documented in `fund-coa-additions.md`):

**Assets (DR-side):**
| Account | Type | Used in NAV |
|---|---|---|
| `1001` Cash and bank accounts | Asset | Include at par |
| `1002`, `1003` Other bank accounts | Asset | Include |
| `1820` Investments at fair value — holdings | Asset | Include at FV (this is the line being revalued) |
| `1825` Unrealized gain/(loss) on investments | Asset | Already counted via 1820's FV after strike (do not double-count) |
| `1830` Subscriptions receivable | Asset | Include — pledged but not settled cash |
| `1840` Management fee receivable | Asset | Only if applicable on SGR side, not fund side |
| `1400` Prepayments | Asset | Include — paid in advance |
| Other receivables | Asset | Include |

**Liabilities (CR-side, exclude investor capital):**
| Account | Type | Used in NAV |
|---|---|---|
| `2400` Redemptions payable | Liability | **Subtract** — promised to investors |
| `2410` Management fee payable (to SGR) | Liability | **Subtract** — accrued not yet paid |
| `2420` Performance fee accrued | Liability | **Subtract** |
| `2430` Distribution payable | Liability | **Subtract** |
| Other AP | Liability | **Subtract** |

**Equity (excluded from NAV calc — it IS the NAV):**
- `3100` Investor capital — Class A — paid in
- `3110` Investor capital — Class A — undistributed earnings

The point of the strike is to recompute what investor capital should now be, and reconcile it to the asset-side fair values.

## Mark-to-market for holdings

At the strike date:

```
new_unrealized_gain = sum(new_FV − cost_basis_per_holding)
prior_unrealized_gain = current 1825 balance
delta_unrealized = new_unrealized_gain − prior_unrealized_gain
```

The strike journal entry for revaluation:

```
If delta > 0:
    DR 1825 (Unrealized gain on investments)            delta
    CR 4720 (Unrealized gain/(loss) income)             delta

If delta < 0:
    DR 4720 (loss)                                       |delta|
    CR 1825                                              |delta|
```

After this entry, account `1820` (cost basis) + `1825` (unrealized) = current fair value.

(Alternative: post directly to `1820` and skip `1825`. Either is valid IFRS — `1825` keeps cost basis visible.)

## Management fee accrual

```
mgmt_fee = NAV_at_strike × (annual_fee_rate / 12)   # monthly accrual
```

Common annual rates:
- Active management: 1.0–1.5%
- Multi-manager: 1.5–2.0%
- Quant / index: 0.2–0.5%
- Performance-fee-only: 0% management base

Posting:
```
DR 5500 (Management fee expense — fund side)        mgmt_fee
CR 2410 (Management fee payable to SGR)             mgmt_fee
```

Pay-down later (separate transaction when the SGR actually collects the fee from the fund):
```
DR 2410 (Management fee payable)                    mgmt_fee
CR 1001 (Cash)                                       mgmt_fee
```

## Performance fee — high-water mark

```
nav_per_share_now = NAV_strike / shares_outstanding
nav_per_share_HWM = max(nav_per_share_history)

if nav_per_share_now > nav_per_share_HWM:
    excess_per_share = nav_per_share_now - nav_per_share_HWM
    excess_total = excess_per_share × shares_outstanding
    perf_fee = excess_total × perf_fee_rate           # typically 10-20%
```

Posting:
```
DR 5505 (Performance fee expense)                   perf_fee
CR 2420 (Performance fee accrued)                   perf_fee
```

For the demo / simple case: skip performance fee unless the fund has positive NAV growth above the HWM. Otherwise it's zero.

## NAV per share

```
shares_outstanding = total Class A shares from cap table BEFORE this strike's sub/red
NAV_per_share = NAV_strike / shares_outstanding
```

The order of operations matters:
1. First, revalue holdings and accrue fees — this gives you NAV_strike before sub/red
2. Then compute NAV per share at the OLD shares-outstanding
3. Then process subs (priced at this new NAV per share, increases shares outstanding)
4. Then process reds (priced at this new NAV per share, decreases shares outstanding)
5. New shares outstanding = old + sub_shares − red_shares
6. NAV after sub/red = NAV_strike + sub_cash − red_cash (cash impact)
   - Equivalently: NAV ÷ shares_outstanding stays the same per share (which is the point — sub/red at NAV doesn't change other investors' per-share value)

## Sanity checks before posting the strike

Before posting the strike JEs, validate:

1. **NAV per share in sane range.** For €1-face funds, typically €0.80–€2.00. Outside this, investigate (might be wrong cost basis, missing revaluation, or wrong shares-outstanding count).

2. **No negative NAV.** If liabilities > assets, the fund is technically insolvent. STOP and surface to user — this needs human review.

3. **Pending sub/red total < 30% of NAV.** Large pending activity is operationally normal but worth flagging.

4. **Performance fee crystallisation only on new HWM.** Don't accrue performance on volatility (NAV up then down) — only on new highs.

If any check fails, do NOT auto-post. Surface to the user, ask for confirmation.

## Frequency

NAV strikes are typically:
- **Daily** for liquid open-ended UCITS funds — heavy automation needed
- **Weekly / bi-weekly** for less liquid open-ended vehicles
- **Monthly** for FoFs and most multi-manager structures
- **Quarterly** for private market vehicles (PE, real estate, infrastructure)
- **Ad-hoc** for closed-end or tokenized structures with discrete events

This plugin's `nav-strike` works for monthly or less frequent. Daily NAV would need automation beyond a manual `/nav-strike` invocation — likely a scheduled-job pattern wrapping this skill.
