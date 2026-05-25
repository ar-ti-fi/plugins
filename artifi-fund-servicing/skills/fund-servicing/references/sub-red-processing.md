# Subscription and redemption processing

How sub/red flow through the GL during a NAV strike.

## The pending queue

Between strikes, sub and red requests sit on the books as "pending" transactions — already posted but flagged for processing at the next strike.

For the demo seed, these look like:

```
PENDING SUBSCRIPTION — Banca Mediolanum SpA — for March 2026 NAV strike
DR 1830 (Subscriptions receivable)               500,000
CR 3100 (Investor capital — Class A — paid in)   500,000

PENDING REDEMPTION — Marco Esposito (HNW) — for March 2026 NAV strike
DR 3100 (Investor capital — paid in)             200,000
CR 2400 (Redemptions payable)                    200,000
```

Note: the pre-strike pending sub entry already moves capital into 3100. This is the "pledged" capital that's part of NAV for the strike calculation. The post-strike processing converts the receivable to actual cash.

## At the NAV strike — processing the queue

The strike workflow processes each pending transaction:

### Subscriptions

When the investor's wire arrives (typically T+2 to T+5 days after the sub request):

```
DR 1001 (Cash — Fund operating account)          subscription_amount
CR 1830 (Subscriptions receivable)               subscription_amount
```

This clears the receivable. The shares issued to the investor are computed at the strike-date NAV per share:

```
shares_issued = subscription_amount / NAV_per_share_at_strike
```

In the cap table, increment the investor's holdings by `shares_issued`.

For the demo / simple case where strike date = sub date, the cash side hits at the same time:

```
DR 1001 (Cash)                                   subscription_amount
CR 1830 (Subscriptions receivable)               subscription_amount
```

And the investor's shares are at the strike NAV per share, so they "subscribe at par" if first strike.

### Redemptions

Redemption is the reverse — the fund owes the investor cash:

Before strike, redemption_request was posted as:
```
DR 3100 (Investor capital — paid in)             redemption_amount
CR 2400 (Redemptions payable)                    redemption_amount
```

Note: the amount above is the **EUR amount requested** (or computed from shares being redeemed × NAV per share).

At strike, the redemption is priced:
```
shares_redeemed = redemption_amount / NAV_per_share_at_strike
```

Reduce the investor's holdings by `shares_redeemed` in the cap table.

After strike, when the fund actually wires the redemption proceeds:
```
DR 2400 (Redemptions payable)                    redemption_amount
CR 1001 (Cash)                                   redemption_amount
```

Settlement typically T+2 to T+5 after the strike.

## Per-share vs per-EUR redemption requests

Investors typically request redemption in one of two ways:

1. **By amount** ("redeem €200,000"): fix the EUR, compute shares = €200k / NAV_per_share. Risky for the investor — if NAV falls between request and strike, they get fewer shares' worth.

2. **By shares** ("redeem 200,000 shares"): fix the share count, EUR = shares × NAV_per_share. Risky for the investor in different direction.

Most retail-friendly funds use **by amount**. Institutional/private vehicles often use **by shares**.

The pending transaction's `metadata` should record which type — the strike workflow handles them differently.

## Cut-off times

Real funds have a **dealing cut-off** — sub/red requests received before time T on date D are processed at date D's NAV. After cut-off, they roll to the next strike.

For the demo: ignore cut-offs. The script processes whatever's pending at strike time.

For a production fund administrator: cut-off enforcement would be a separate workflow that flags requests received late and moves them to the next period.

## Equalisation (out of scope v0.1)

Equalisation is a technique to ensure new investors don't subsidize existing investors' performance fees, or vice versa. For demo / v0.1 we skip this entirely.

If/when equalisation is added: the strike workflow gets an extra step that computes per-investor equalisation credits/debits based on each investor's entry NAV per share vs current.

## Special cases worth flagging

When processing the queue, the strike workflow should warn / flag:

- **Sub larger than 10% of NAV in a single strike.** Indicates a large institutional inflow that might change the fund's character. Surface to the operator.
- **Net outflow > 5% of NAV.** Liquidity pressure — may need to sell holdings to fund the red. Flag for treasury.
- **First subscription from a new investor.** Trigger KYC/AML check confirmation before processing — the strike workflow should pause if the customer record lacks KYC clearance flags.
- **Cancelled or amended request.** If the investor cancelled before strike, the pending transaction needs to be voided. Pending requests shouldn't auto-process without re-confirmation.

These flags are out of scope for v0.1 — but the design should expose them as configurable checks.
