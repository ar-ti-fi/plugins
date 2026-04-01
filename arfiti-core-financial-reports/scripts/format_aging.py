#!/usr/bin/env python3
"""Format AR or AP Aging report from JSON data into consistent markdown output.

Usage:
    python3 format_aging.py --input data.json --output report.md --type ar
    python3 format_aging.py --input data.json --output report.md --type ap

Input: JSON with aging data by party (customer or vendor).
Output: Formatted markdown aging report with priorities and metrics.
"""

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


def d(val) -> Decimal:
    if val is None:
        return Decimal("0.00")
    return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def fmt(val: Decimal) -> str:
    sign = "-" if val < 0 else ""
    abs_val = abs(val)
    integer_part = int(abs_val)
    decimal_part = abs_val - integer_part
    return f"{sign}{integer_part:,}{f'{decimal_part:.2f}'[1:]}"


def pct(part: Decimal, total: Decimal) -> str:
    if total == 0:
        return "0.0%"
    return f"{(part / total * 100).quantize(Decimal('0.1'))}%"


def validate(data: dict) -> list:
    errors = []
    if "entity_name" not in data:
        errors.append("Missing 'entity_name'")
    if "as_of_date" not in data:
        errors.append("Missing 'as_of_date'")
    if "parties" not in data:
        errors.append("Missing 'parties' array")
    return errors


def build_report(data: dict, aging_type: str) -> str:
    is_ar = aging_type == "ar"
    currency = data.get("currency", "USD")
    party_label = "Customer" if is_ar else "Vendor"
    title = "Aged Receivables" if is_ar else "Aged Payables"
    annual_revenue = d(data.get("annual_revenue", 0))
    annual_cogs = d(data.get("annual_cogs", 0))
    cash_balance = d(data.get("cash_balance", 0))

    parties = data.get("parties", [])

    # Calculate totals per bucket
    buckets = ["current", "days_1_30", "days_31_60", "days_61_90", "days_90_plus"]
    bucket_labels = ["Current", "1-30 days", "31-60 days", "61-90 days", "90+ days"]

    grand_totals = {b: Decimal("0.00") for b in buckets}
    party_totals = []

    for party in parties:
        row_total = Decimal("0.00")
        row = {"name": party.get("name", "Unknown")}
        for b in buckets:
            val = d(party.get(b, 0))
            row[b] = val
            row_total += val
            grand_totals[b] += val
        row["total"] = row_total
        party_totals.append(row)

    # Sort by total descending
    party_totals.sort(key=lambda x: x["total"], reverse=True)

    grand_total = sum(grand_totals.values())
    total_overdue = grand_totals["days_1_30"] + grand_totals["days_31_60"] + grand_totals["days_61_90"] + grand_totals["days_90_plus"]

    out = []
    out.append(f"# {title}")
    out.append(f"**{data['entity_name']}** | As of {data['as_of_date']} | Currency: {currency}")
    out.append("")

    # --- AGING MATRIX ---
    out.append("## Aging Summary")
    out.append("")
    out.append(f"| {party_label} | Current | 1-30 days | 31-60 days | 61-90 days | 90+ days | **Total** |")
    out.append("|---|---------|-----------|------------|------------|----------|-----------|")

    for row in party_totals:
        cols = [fmt(row[b]) if row[b] > 0 else "—" for b in buckets]
        out.append(f"| {row['name']} | {cols[0]} | {cols[1]} | {cols[2]} | {cols[3]} | {cols[4]} | **{fmt(row['total'])}** |")

    # Totals row
    total_cols = [fmt(grand_totals[b]) for b in buckets]
    out.append(f"| **TOTAL** | **{total_cols[0]}** | **{total_cols[1]}** | **{total_cols[2]}** | **{total_cols[3]}** | **{total_cols[4]}** | **{fmt(grand_total)}** |")
    out.append("")

    # --- BUCKET DISTRIBUTION ---
    out.append("## Distribution")
    out.append("")
    out.append("| Bucket | Amount | % of Total |")
    out.append("|--------|--------|-----------|")
    for b, label in zip(buckets, bucket_labels):
        out.append(f"| {label} | {fmt(grand_totals[b])} | {pct(grand_totals[b], grand_total)} |")
    out.append(f"| **Total** | **{fmt(grand_total)}** | **100.0%** |")
    out.append(f"| *Overdue (>0 days)* | *{fmt(total_overdue)}* | *{pct(total_overdue, grand_total)}* |")
    out.append("")

    # --- KEY METRICS ---
    out.append("## Key Metrics")
    out.append("")
    out.append("| Metric | Value |")
    out.append("|--------|-------|")

    if is_ar:
        # DSO
        if annual_revenue > 0:
            dso = (grand_total / annual_revenue * 365).quantize(Decimal("1"))
            out.append(f"| Days Sales Outstanding (DSO) | {dso} days |")
        out.append(f"| Total Outstanding | {fmt(grand_total)} |")
        out.append(f"| Overdue Amount | {fmt(total_overdue)} ({pct(total_overdue, grand_total)}) |")

        # Concentration
        if len(party_totals) >= 5:
            top5 = sum(p["total"] for p in party_totals[:5])
            out.append(f"| Top 5 Concentration | {fmt(top5)} ({pct(top5, grand_total)}) |")
        elif len(party_totals) > 0:
            top = party_totals[0]
            out.append(f"| Largest Balance | {top['name']}: {fmt(top['total'])} ({pct(top['total'], grand_total)}) |")
    else:
        # DPO
        if annual_cogs > 0:
            dpo = (grand_total / annual_cogs * 365).quantize(Decimal("1"))
            out.append(f"| Days Payable Outstanding (DPO) | {dpo} days |")
        out.append(f"| Total Outstanding | {fmt(grand_total)} |")
        out.append(f"| Overdue Amount | {fmt(total_overdue)} ({pct(total_overdue, grand_total)}) |")

        # Cash coverage
        if cash_balance > 0:
            coverage = pct(cash_balance, grand_total)
            status = "Sufficient" if cash_balance >= grand_total else "Insufficient"
            out.append(f"| Cash Balance | {fmt(cash_balance)} |")
            out.append(f"| Cash Coverage | {coverage} — {status} |")

        # Upcoming 7/14/30 days
        due_7 = d(data.get("due_within_7_days", 0))
        due_14 = d(data.get("due_within_14_days", 0))
        due_30 = d(data.get("due_within_30_days", 0))
        if due_7 > 0 or due_14 > 0 or due_30 > 0:
            out.append(f"| Due within 7 days | {fmt(due_7)} |")
            out.append(f"| Due within 14 days | {fmt(due_14)} |")
            out.append(f"| Due within 30 days | {fmt(due_30)} |")

    out.append("")

    # --- PRIORITY / RECOMMENDATIONS ---
    if is_ar:
        out.append("## Collection Priorities")
        out.append("")

        urgent = [p for p in party_totals if p["days_90_plus"] > 0]
        action = [p for p in party_totals if p["days_61_90"] > 0 and p not in urgent]
        monitor = [p for p in party_totals if p["days_31_60"] > 0 and p not in urgent and p not in action]

        if urgent:
            out.append(f"### Urgent — 90+ Days ({len(urgent)} {party_label.lower()}s)")
            out.append("Immediate follow-up required. Consider escalation or collection agency.")
            out.append("")
            out.append(f"| {party_label} | 90+ Amount | Total Balance | Action |")
            out.append("|---|---|---|---|")
            for p in urgent:
                out.append(f"| {p['name']} | {fmt(p['days_90_plus'])} | {fmt(p['total'])} | Phone call + formal demand letter |")
            out.append("")

        if action:
            out.append(f"### Action Needed — 61-90 Days ({len(action)} {party_label.lower()}s)")
            out.append("Send formal payment reminder with invoice copies.")
            out.append("")
            out.append(f"| {party_label} | 61-90 Amount | Total Balance | Action |")
            out.append("|---|---|---|---|")
            for p in action:
                out.append(f"| {p['name']} | {fmt(p['days_61_90'])} | {fmt(p['total'])} | Written reminder + phone follow-up |")
            out.append("")

        if monitor:
            out.append(f"### Monitor — 31-60 Days ({len(monitor)} {party_label.lower()}s)")
            out.append("Soft follow-up. Verify invoices are in payment queue.")
            out.append("")
            out.append(f"| {party_label} | 31-60 Amount | Total Balance | Action |")
            out.append("|---|---|---|---|")
            for p in monitor:
                out.append(f"| {p['name']} | {fmt(p['days_31_60'])} | {fmt(p['total'])} | Email reminder |")
            out.append("")

        current_only = [p for p in party_totals if p not in urgent and p not in action and p not in monitor]
        if current_only:
            out.append(f"### Current — No Action ({len(current_only)} {party_label.lower()}s)")
            out.append(f"All balances within terms. Total: {fmt(sum(p['total'] for p in current_only))}")
            out.append("")

    else:
        out.append("## Payment Recommendations")
        out.append("")

        overdue = [p for p in party_totals if p["days_1_30"] + p["days_31_60"] + p["days_61_90"] + p["days_90_plus"] > 0]
        current_due = [p for p in party_totals if p not in overdue and p["current"] > 0]

        if overdue:
            out.append(f"### Overdue — Pay Immediately ({len(overdue)} vendors)")
            out.append("Avoid late fees and relationship damage.")
            out.append("")
            out.append(f"| {party_label} | Overdue Amount | Total Balance | Priority |")
            out.append("|---|---|---|---|")
            for p in overdue:
                overdue_amt = p["days_1_30"] + p["days_31_60"] + p["days_61_90"] + p["days_90_plus"]
                priority = "CRITICAL" if p["days_90_plus"] > 0 else ("HIGH" if p["days_61_90"] > 0 else "MEDIUM")
                out.append(f"| {p['name']} | {fmt(overdue_amt)} | {fmt(p['total'])} | {priority} |")
            out.append("")

        if current_due:
            out.append(f"### Due Within Terms ({len(current_due)} vendors)")
            out.append("Schedule in regular payment run.")
            out.append("")
            out.append(f"| {party_label} | Amount | Action |")
            out.append("|---|---|---|")
            for p in current_due:
                out.append(f"| {p['name']} | {fmt(p['current'])} | Include in next payment batch |")
            out.append("")

        # Early payment discount analysis
        discounts = data.get("early_payment_discounts", [])
        if discounts:
            out.append("### Early Payment Discount Opportunities")
            out.append("")
            out.append(f"| {party_label} | Terms | Discount | Annualized Return | Recommendation |")
            out.append("|---|---|---|---|---|")
            for disc in discounts:
                disc_pct = d(disc.get("discount_percent", 0))
                full_days = int(disc.get("full_days", 30))
                disc_days = int(disc.get("discount_days", 10))
                if disc_pct > 0 and full_days > disc_days:
                    annualized = (disc_pct / (100 - disc_pct) * 365 / (full_days - disc_days) * 100).quantize(Decimal("0.1"))
                    rec = "Take discount" if annualized > Decimal("10") else "Pay at terms"
                    out.append(f"| {disc.get('name', '?')} | {disc_pct}%/{disc_days} NET {full_days} | {disc_pct}% | {annualized}% | {rec} |")
            out.append("")

    # Footer
    out.append("---")
    out.append("*Generated by arfiti-core-financial-reports plugin*")

    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Format Aging Report")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--output", required=True, help="Output markdown file")
    parser.add_argument("--type", required=True, choices=["ar", "ap"], help="Report type: ar or ap")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        data = json.load(f)

    errors = validate(data)
    if errors:
        print(f"Validation errors: {', '.join(errors)}", file=sys.stderr)
        sys.exit(1)

    report = build_report(data, args.type)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        f.write(report)

    title = "AR Aging" if args.type == "ar" else "AP Aging"
    print(f"{title} written to {args.output}")
    print(f"Entity: {data['entity_name']} | Date: {data['as_of_date']}")
    print(f"Parties: {len(data.get('parties', []))} | Total: {fmt(sum(d(p.get('current', 0)) + d(p.get('days_1_30', 0)) + d(p.get('days_31_60', 0)) + d(p.get('days_61_90', 0)) + d(p.get('days_90_plus', 0)) for p in data.get('parties', [])))}")


if __name__ == "__main__":
    main()
