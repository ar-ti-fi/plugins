#!/usr/bin/env python3
"""
format_credit_memo.py — render the credit-intelligence input JSON into a
consistently-formatted markdown credit memo.

The skill builds an input JSON per input_schema_credit_memo.json from
generate_report() + list_entities() calls. This script renders it. Keeping
the formatting deterministic ensures the same data always produces the
same memo — important for portfolio review and audit trails.

Usage:
    python3 format_credit_memo.py --input <path.json> --output <path.md>
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def money(amount, currency="EUR"):
    """Format a money amount: €12,345.67 or €(123,456.78) for negative."""
    if amount is None:
        return "—"
    sign = "(" if amount < 0 else ""
    closing = ")" if amount < 0 else ""
    return f"€{sign}{abs(amount):,.0f}{closing}" if currency == "EUR" else f"{currency} {amount:,.0f}"


def pct(p):
    """Format a percentage with 1 decimal."""
    if p is None:
        return "—"
    return f"{p:+.1f}%" if p < 0 else f"{p:.1f}%"


def days(d):
    if d is None:
        return "—"
    return f"{d:.0f} days"


def ratio(r, suffix="x"):
    if r is None:
        return "—"
    return f"{r:.2f}{suffix}"


def severity_badge(s):
    return {"HIGH": "🔴 HIGH", "MEDIUM": "🟡 MEDIUM", "LOW": "🟢 LOW"}.get(s, s)


def render(data: dict) -> str:
    out = []
    entity = data["entity"]
    snap = data.get("snapshot", {})
    currency = entity.get("currency", "EUR")

    # ─── Header ──────────────────────────────────────────────────────────
    out.append(f"# Credit Memo — {entity['name']}")
    out.append("")
    out.append(f"**Entity ID:** {entity['id']}  |  **Country:** {entity.get('country', '—')}  |  **Industry:** {entity.get('industry', '—')}  |  **Reporting currency:** {currency}")
    out.append(f"**As of date:** {data['as_of_date']}  |  **Run timestamp:** {data.get('run_timestamp', datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))}")
    out.append("")
    out.append("---")
    out.append("")

    # ─── 1. Snapshot ─────────────────────────────────────────────────────
    out.append("## 1. Snapshot")
    out.append("")
    out.append("| Metric | Value |")
    out.append("|---|---:|")
    out.append(f"| Total assets | {money(snap.get('total_assets'), currency)} |")
    out.append(f"| Total equity | {money(snap.get('total_equity'), currency)} |")
    out.append(f"| Cash & equivalents | {money(snap.get('cash'), currency)} |")
    out.append(f"| Net debt | {money(snap.get('net_debt'), currency)} |")
    out.append(f"| Revenue (TTM) | {money(snap.get('revenue_ttm'), currency)} |")
    out.append(f"| EBITDA (TTM) | {money(snap.get('ebitda_ttm'), currency)} |")
    out.append(f"| **DSCR** | **{ratio(snap.get('dscr'))}** |")
    out.append(f"| Leverage (Net Debt / EBITDA) | {ratio(snap.get('leverage'))} |")
    out.append(f"| Interest Coverage (ICR) | {ratio(snap.get('icr'))} |")
    out.append(f"| DSO | {days(snap.get('dso_days'))} |")
    out.append(f"| DPO | {days(snap.get('dpo_days'))} |")
    out.append(f"| DIO | {days(snap.get('dio_days'))} |")
    out.append(f"| Cash Conversion Cycle | {days(snap.get('ccc_days'))} |")
    top_cust = snap.get("top_customer_share")
    if top_cust is not None:
        out.append(f"| Top customer share of AR | {top_cust:.1f}% |")
    out.append("")

    # ─── 2. Trajectory ────────────────────────────────────────────────────
    traj = data.get("trajectory", {}).get("months", [])
    if traj:
        out.append("## 2. Financial trajectory (13 months)")
        out.append("")
        out.append("| Period | Revenue | COGS | GP | GM% | OpEx | EBITDA | EBITDA% |")
        out.append("|---|---:|---:|---:|---:|---:|---:|---:|")
        for m in traj:
            gm = m.get("gross_margin_pct")
            em = m.get("ebitda_margin_pct")
            out.append(
                f"| {m.get('period', '—')} "
                f"| {money(m.get('revenue'), currency)} "
                f"| {money(m.get('cogs'), currency)} "
                f"| {money(m.get('gross_profit'), currency)} "
                f"| {pct(gm) if gm is not None else '—'} "
                f"| {money(m.get('opex'), currency)} "
                f"| {money(m.get('ebitda'), currency)} "
                f"| {pct(em) if em is not None else '—'} |"
            )
        out.append("")
        # Trend commentary
        if len(traj) >= 6:
            first_3_avg_gm = sum(m.get("gross_margin_pct", 0) for m in traj[:3]) / 3
            last_3_avg_gm = sum(m.get("gross_margin_pct", 0) for m in traj[-3:]) / 3
            delta_gm = last_3_avg_gm - first_3_avg_gm
            direction = "compressed" if delta_gm < 0 else "expanded"
            out.append(f"> **GM trend:** {direction} **{abs(delta_gm):.1f} pp** from {first_3_avg_gm:.1f}% (first 3 months in window) to {last_3_avg_gm:.1f}% (last 3 months).")
            out.append("")

    # ─── 3. Liquidity & working capital ──────────────────────────────────
    liq = data.get("liquidity", {})
    if liq:
        out.append("## 3. Liquidity & working capital")
        out.append("")
        cash_accounts = liq.get("cash_by_account", [])
        if cash_accounts:
            out.append("**Cash position by account:**")
            out.append("")
            out.append("| Account | Name | Balance |")
            out.append("|---|---|---:|")
            total_cash = 0
            for a in cash_accounts:
                bal = a.get("balance", 0)
                total_cash += bal
                out.append(f"| {a.get('account_number', '')} | {a.get('account_name', '')} | {money(bal, currency)} |")
            out.append(f"| | **Total cash** | **{money(total_cash, currency)}** |")
            out.append("")

        cf = liq.get("monthly_operating_cf", [])
        if cf:
            out.append("**Operating cash flow (last 3 months):**")
            out.append("")
            out.append("| Period | Operating CF |")
            out.append("|---|---:|")
            for c in cf:
                out.append(f"| {c.get('period', '—')} | {money(c.get('operating_cf'), currency)} |")
            avg = sum(c.get("operating_cf", 0) for c in cf) / max(1, len(cf))
            out.append(f"| **Avg** | **{money(avg, currency)}** |")
            out.append("")

        runway = liq.get("runway_months")
        if runway is not None:
            badge = ("🔴 SHORT" if runway < 3 else
                     "🟡 WATCH" if runway < 6 else
                     "🟢 OK")
            out.append(f"**Runway:** {runway:.1f} months at current burn  {badge}")
            if liq.get("available_revolver"):
                out.append(f"**Available revolver:** {money(liq['available_revolver'], currency)}")
            out.append("")

    # ─── 4. Capital structure & coverage ─────────────────────────────────
    cov = data.get("coverage", {})
    if cov:
        out.append("## 4. Capital structure & coverage")
        out.append("")
        out.append(f"- EBITDA (TTM): **{money(cov.get('ebitda_ttm'), currency)}**")
        out.append(f"- Interest expense (TTM): {money(cov.get('interest_expense_ttm'), currency)}")
        out.append(f"- Principal paid (TTM, proxy for next-12 schedule): {money(cov.get('principal_paid_ttm'), currency)}")
        out.append(f"- Total debt service: **{money(cov.get('total_debt_service'), currency)}**")
        out.append("")
        out.append(f"- **DSCR:** {ratio(cov.get('dscr'))}")
        out.append(f"- **ICR:** {ratio(cov.get('icr'))}")
        out.append(f"- **Leverage:** {ratio(cov.get('leverage'))}")
        out.append("")
        covenants = cov.get("covenants", [])
        if covenants:
            out.append("**Covenants:**")
            out.append("")
            out.append("| Covenant | Operator | Threshold | Current | Headroom | Status |")
            out.append("|---|---|---:|---:|---:|---|")
            for c in covenants:
                badge = {"OK": "🟢 OK", "WATCH": "🟡 WATCH",
                         "TIGHT": "🟠 TIGHT", "BREACH": "🔴 BREACH"}.get(c.get("status", ""), c.get("status", ""))
                out.append(
                    f"| {c.get('name')} "
                    f"| {c.get('operator')} "
                    f"| {ratio(c.get('threshold'))} "
                    f"| {ratio(c.get('current'))} "
                    f"| {ratio(c.get('headroom'))} "
                    f"| {badge} |"
                )
            out.append("")

    # ─── 5. Concentration & quality ──────────────────────────────────────
    conc = data.get("concentration", {})
    if conc:
        out.append("## 5. Concentration & quality")
        out.append("")
        top_c = conc.get("top_customers", [])
        if top_c:
            out.append("**Top customers by open AR:**")
            out.append("")
            out.append("| # | Customer | Open AR | % of AR | % of TTM Revenue |")
            out.append("|---|---|---:|---:|---:|")
            for i, c in enumerate(top_c[:5], start=1):
                out.append(
                    f"| {i} | {c.get('name')} "
                    f"| {money(c.get('open_ar'), currency)} "
                    f"| {c.get('share_of_ar_pct', 0):.1f}% "
                    f"| {c.get('share_of_ttm_revenue_pct', 0):.1f}% |"
                )
            out.append("")

        top_v = conc.get("top_vendors", [])
        if top_v:
            out.append("**Top vendors by open AP:**")
            out.append("")
            out.append("| # | Vendor | Open AP | % of AP | % of TTM Spend |")
            out.append("|---|---|---:|---:|---:|")
            for i, v in enumerate(top_v[:5], start=1):
                out.append(
                    f"| {i} | {v.get('name')} "
                    f"| {money(v.get('open_ap'), currency)} "
                    f"| {v.get('share_of_ap_pct', 0):.1f}% "
                    f"| {v.get('share_of_ttm_spend_pct', 0):.1f}% |"
                )
            out.append("")

        ar_b = conc.get("ar_aging_buckets")
        if ar_b:
            out.append("**AR aging:**")
            out.append("")
            out.append("| Current | 1-30 | 31-60 | 61-90 | 91+ | % 60+ |")
            out.append("|---:|---:|---:|---:|---:|---:|")
            out.append(
                f"| {money(ar_b.get('current'), currency)} "
                f"| {money(ar_b.get('days_1_30'), currency)} "
                f"| {money(ar_b.get('days_31_60'), currency)} "
                f"| {money(ar_b.get('days_61_90'), currency)} "
                f"| {money(ar_b.get('days_91_plus'), currency)} "
                f"| **{ar_b.get('pct_60_plus', 0):.1f}%** |"
            )
            out.append("")

        ap_b = conc.get("ap_aging_buckets")
        if ap_b:
            out.append("**AP aging:**")
            out.append("")
            out.append("| Current | 1-30 | 31-60 | 61-90 | 91+ | % 60+ | In dispute |")
            out.append("|---:|---:|---:|---:|---:|---:|---:|")
            in_disp = f"{ap_b.get('in_dispute_count', 0)} bill(s) · {money(ap_b.get('in_dispute_amount'), currency)}"
            out.append(
                f"| {money(ap_b.get('current'), currency)} "
                f"| {money(ap_b.get('days_1_30'), currency)} "
                f"| {money(ap_b.get('days_31_60'), currency)} "
                f"| {money(ap_b.get('days_61_90'), currency)} "
                f"| {money(ap_b.get('days_91_plus'), currency)} "
                f"| **{ap_b.get('pct_60_plus', 0):.1f}%** "
                f"| {in_disp} |"
            )
            out.append("")

    # ─── 6. Early warning signals ────────────────────────────────────────
    signals = data.get("signals", [])
    out.append("## 6. Early warning signals")
    out.append("")
    if not signals:
        out.append("> No EWS triggered at this read. Borrower is operating within normal credit parameters across all monitored thresholds.")
        out.append("")
    else:
        # Sort by severity
        sev_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        for s in sorted(signals, key=lambda x: sev_order.get(x.get("severity", "LOW"), 3)):
            out.append(f"### {severity_badge(s['severity'])}  ·  `{s['code']}`")
            out.append("")
            out.append(f"**{s.get('headline', '')}**")
            out.append("")
            for c in s.get("citations", []):
                out.append(f"- {c}")
            out.append("")

    # Footer
    out.append("---")
    out.append("")
    out.append(f"_Generated by `artifi-credit-intelligence` / `/credit-read` from live general-ledger data at {data.get('run_timestamp', datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))}._  ")
    out.append("_Each citation in this memo traces to a specific GL transaction or aggregation; drill into any number via the Arfiti admin dashboard or by asking Claude to fetch the underlying detail._")
    out.append("")

    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Render the credit-intelligence input JSON into a markdown memo.")
    ap.add_argument("--input", "-i", required=True, help="Path to input JSON")
    ap.add_argument("--output", "-o", required=True, help="Path to write markdown")
    args = ap.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        print(f"ERROR: input file not found: {inp}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(inp.read_text())
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in {inp}: {e}", file=sys.stderr)
        sys.exit(1)

    if "entity" not in data or "as_of_date" not in data:
        print("ERROR: input must contain at minimum 'entity' and 'as_of_date'", file=sys.stderr)
        sys.exit(1)

    out_md = render(data)
    Path(args.output).write_text(out_md)
    print(f"Wrote credit memo: {args.output}")


if __name__ == "__main__":
    main()
