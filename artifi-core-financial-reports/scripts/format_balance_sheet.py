#!/usr/bin/env python3
"""Format a Balance Sheet from JSON data into consistent markdown output.

Usage:
    python3 format_balance_sheet.py --input data.json --output report.md

Input: JSON with current (and optional prior) balance sheet data.
Output: Formatted markdown balance sheet with validation and ratios.
"""

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


def d(val) -> Decimal:
    """Convert to Decimal safely."""
    if val is None:
        return Decimal("0.00")
    return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def fmt(val: Decimal) -> str:
    """Format number with thousands separator and 2 decimals."""
    sign = "-" if val < 0 else ""
    abs_val = abs(val)
    integer_part = int(abs_val)
    decimal_part = abs_val - integer_part
    formatted_int = f"{integer_part:,}"
    formatted_dec = f"{decimal_part:.2f}"[1:]  # .XX
    return f"{sign}{formatted_int}{formatted_dec}"


def pct(numerator: Decimal, denominator: Decimal) -> str:
    """Calculate percentage safely."""
    if denominator == 0:
        return "N/A"
    result = (numerator / denominator * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return f"{result}%"


def change_pct(current: Decimal, prior: Decimal) -> str:
    """Calculate change percentage."""
    if prior == 0:
        return "N/A" if current == 0 else "New"
    result = ((current - prior) / abs(prior) * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    sign = "+" if result > 0 else ""
    return f"{sign}{result}%"


def validate(data: dict) -> list:
    """Validate input data, return list of errors."""
    errors = []
    if "entity_name" not in data:
        errors.append("Missing 'entity_name'")
    if "as_of_date" not in data:
        errors.append("Missing 'as_of_date'")
    if "currency" not in data:
        errors.append("Missing 'currency'")
    for section in ["current_assets", "noncurrent_assets", "current_liabilities", "noncurrent_liabilities", "equity"]:
        if section not in data:
            errors.append(f"Missing '{section}' section")
    return errors


def format_section(items: list, indent: str = "  ") -> tuple:
    """Format a list of line items, return (lines, total)."""
    lines = []
    total = Decimal("0.00")
    for item in items:
        amount = d(item.get("amount", 0))
        total += amount
        name = item.get("name", "Unknown")
        lines.append(f"{indent}{name:<45} {fmt(amount):>15}")
    return lines, total


def build_report(data: dict) -> str:
    """Build the full balance sheet markdown report."""
    currency = data.get("currency", "USD")
    has_prior = "prior" in data

    out = []
    out.append(f"# Balance Sheet")
    out.append(f"**{data['entity_name']}** | As of {data['as_of_date']} | Currency: {currency}")
    if has_prior:
        out.append(f"Comparative: {data['prior'].get('as_of_date', 'Prior Period')}")
    out.append("")

    # --- ASSETS ---
    out.append("## ASSETS")
    out.append("")

    # Current Assets
    out.append("### Current Assets")
    out.append("")
    ca_lines, total_ca = format_section(data["current_assets"])
    out.extend(ca_lines)
    out.append(f"  {'─' * 60}")
    out.append(f"  {'**Total Current Assets**':<45} **{fmt(total_ca):>13}**")
    out.append("")

    # Non-Current Assets
    out.append("### Non-Current Assets")
    out.append("")
    nca_lines, total_nca = format_section(data["noncurrent_assets"])
    out.extend(nca_lines)
    out.append(f"  {'─' * 60}")
    out.append(f"  {'**Total Non-Current Assets**':<45} **{fmt(total_nca):>13}**")
    out.append("")

    total_assets = total_ca + total_nca
    out.append(f"### **TOTAL ASSETS** {fmt(total_assets):>46}")
    out.append("")

    # --- LIABILITIES ---
    out.append("## LIABILITIES")
    out.append("")

    # Current Liabilities
    out.append("### Current Liabilities")
    out.append("")
    cl_lines, total_cl = format_section(data["current_liabilities"])
    out.extend(cl_lines)
    out.append(f"  {'─' * 60}")
    out.append(f"  {'**Total Current Liabilities**':<45} **{fmt(total_cl):>13}**")
    out.append("")

    # Non-Current Liabilities
    out.append("### Non-Current Liabilities")
    out.append("")
    ncl_lines, total_ncl = format_section(data["noncurrent_liabilities"])
    out.extend(ncl_lines)
    out.append(f"  {'─' * 60}")
    out.append(f"  {'**Total Non-Current Liabilities**':<45} **{fmt(total_ncl):>13}**")
    out.append("")

    total_liabilities = total_cl + total_ncl
    out.append(f"### **TOTAL LIABILITIES** {fmt(total_liabilities):>41}")
    out.append("")

    # --- EQUITY ---
    out.append("## EQUITY")
    out.append("")
    eq_lines, total_equity = format_section(data["equity"])
    out.extend(eq_lines)
    out.append(f"  {'─' * 60}")
    out.append(f"  {'**TOTAL EQUITY**':<45} **{fmt(total_equity):>13}**")
    out.append("")

    total_le = total_liabilities + total_equity
    out.append(f"### **TOTAL LIABILITIES AND EQUITY** {fmt(total_le):>30}")
    out.append("")

    # --- VALIDATION ---
    out.append("## Validation")
    out.append("")
    balance_diff = total_assets - total_le
    if balance_diff == 0:
        out.append("| Check | Result |")
        out.append("|-------|--------|")
        out.append(f"| Assets = Liabilities + Equity | **PASS** ({fmt(total_assets)} = {fmt(total_le)}) |")
    else:
        out.append("| Check | Result |")
        out.append("|-------|--------|")
        out.append(f"| Assets = Liabilities + Equity | **FAIL** (difference: {fmt(balance_diff)}) |")
        out.append("")
        out.append(f"> **WARNING**: Balance sheet does not balance. Difference of {fmt(balance_diff)}. ")
        out.append("> Check retained earnings, current year P&L, and unclassified accounts.")
    out.append("")

    # --- RATIOS ---
    out.append("## Key Ratios")
    out.append("")
    out.append("| Ratio | Value | Interpretation |")
    out.append("|-------|-------|----------------|")

    # Current Ratio
    if total_cl > 0:
        current_ratio = (total_ca / total_cl).quantize(Decimal("0.01"))
        interp = "Healthy" if Decimal("1.5") <= current_ratio <= Decimal("3.0") else "Review"
        out.append(f"| Current Ratio | {current_ratio} | {interp} (target: 1.5-3.0) |")
    else:
        out.append("| Current Ratio | N/A | No current liabilities |")

    # Quick Ratio (exclude inventory)
    inventory = Decimal("0.00")
    for item in data["current_assets"]:
        cat = item.get("category", "").lower()
        if "inventor" in cat:
            inventory += d(item.get("amount", 0))
    if total_cl > 0:
        quick_ratio = ((total_ca - inventory) / total_cl).quantize(Decimal("0.01"))
        interp = "Healthy" if Decimal("1.0") <= quick_ratio <= Decimal("2.0") else "Review"
        out.append(f"| Quick Ratio | {quick_ratio} | {interp} (target: 1.0-2.0) |")

    # Debt-to-Equity
    if total_equity > 0:
        dte = (total_liabilities / total_equity).quantize(Decimal("0.01"))
        interp = "Conservative" if dte < Decimal("1.0") else ("Moderate" if dte < Decimal("2.0") else "Leveraged")
        out.append(f"| Debt-to-Equity | {dte} | {interp} |")

    # Equity Ratio
    if total_assets > 0:
        eq_ratio = pct(total_equity, total_assets)
        out.append(f"| Equity Ratio | {eq_ratio} | Owner-financed portion of assets |")

    out.append("")

    # --- COMPARATIVE ---
    if has_prior:
        prior = data["prior"]
        out.append("## Comparative Analysis")
        out.append("")
        out.append("| Item | Current | Prior | Change | % |")
        out.append("|------|---------|-------|--------|---|")

        prior_ca = sum(d(i.get("amount", 0)) for i in prior.get("current_assets", []))
        prior_nca = sum(d(i.get("amount", 0)) for i in prior.get("noncurrent_assets", []))
        prior_cl = sum(d(i.get("amount", 0)) for i in prior.get("current_liabilities", []))
        prior_ncl = sum(d(i.get("amount", 0)) for i in prior.get("noncurrent_liabilities", []))
        prior_eq = sum(d(i.get("amount", 0)) for i in prior.get("equity", []))
        prior_assets = prior_ca + prior_nca
        prior_liab = prior_cl + prior_ncl

        rows = [
            ("Total Current Assets", total_ca, prior_ca),
            ("Total Non-Current Assets", total_nca, prior_nca),
            ("**Total Assets**", total_assets, prior_assets),
            ("Total Current Liabilities", total_cl, prior_cl),
            ("Total Non-Current Liabilities", total_ncl, prior_ncl),
            ("**Total Liabilities**", total_liabilities, prior_liab),
            ("**Total Equity**", total_equity, prior_eq),
        ]

        for name, curr, prev in rows:
            diff = curr - prev
            sign = "+" if diff >= 0 else ""
            pct_chg = change_pct(curr, prev)
            flag = " ⚠️" if prev != 0 and abs(diff) / abs(prev) > Decimal("0.10") else ""
            out.append(f"| {name} | {fmt(curr)} | {fmt(prev)} | {sign}{fmt(diff)} | {pct_chg}{flag} |")

        out.append("")
        out.append("> Items marked ⚠️ changed by more than 10% — review for material movements.")
        out.append("")

    # Footer
    out.append("---")
    out.append(f"*Generated by artifi-core-financial-reports plugin*")

    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Format Balance Sheet")
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument("--output", required=True, help="Output markdown file")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        data = json.load(f)

    errors = validate(data)
    if errors:
        print(f"Validation errors: {', '.join(errors)}", file=sys.stderr)
        sys.exit(1)

    report = build_report(data)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        f.write(report)

    print(f"Balance Sheet written to {args.output}")
    print(f"Entity: {data['entity_name']} | Date: {data['as_of_date']}")


if __name__ == "__main__":
    main()
