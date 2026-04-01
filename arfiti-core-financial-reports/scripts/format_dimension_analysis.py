#!/usr/bin/env python3
"""Format a Dimension Analysis (P&L by department/project/cost center) into markdown.

Usage:
    python3 format_dimension_analysis.py --input data.json --output report.md

Input: JSON with P&L data broken down by dimension values.
Output: Formatted markdown with P&L matrix, profitability ranking, and recommendations.
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


def margin_pct(amount: Decimal, revenue: Decimal) -> str:
    if revenue == 0:
        return "N/A"
    result = (amount / revenue * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return f"{result}%"


def change_pct(current: Decimal, prior: Decimal) -> str:
    if prior == 0:
        return "N/A" if current == 0 else "New"
    result = ((current - prior) / abs(prior) * 100).quantize(Decimal("0.1"))
    sign = "+" if result > 0 else ""
    return f"{sign}{result}%"


def validate(data: dict) -> list:
    errors = []
    if "entity_name" not in data:
        errors.append("Missing 'entity_name'")
    if "dimension_type" not in data:
        errors.append("Missing 'dimension_type'")
    if "dimensions" not in data or not isinstance(data["dimensions"], list):
        errors.append("Missing or invalid 'dimensions' array")
    return errors


def build_report(data: dict) -> str:
    currency = data.get("currency", "USD")
    dim_type = data.get("dimension_type", "Department")
    has_prior = any("prior" in dim for dim in data.get("dimensions", []))
    has_budget = any("budget" in dim for dim in data.get("dimensions", []))

    dims = data.get("dimensions", [])

    out = []
    out.append("# Dimension Analysis")
    out.append(f"**{data['entity_name']}** | {data.get('start_date', '?')} to {data.get('end_date', '?')} | By: {dim_type} | Currency: {currency}")
    out.append("")

    # --- P&L MATRIX ---
    out.append("## P&L by " + dim_type.title())
    out.append("")

    # Build header
    dim_names = [dim.get("name", "?") for dim in dims]
    header = f"| | " + " | ".join(dim_names) + " | **Total** |"
    separator = "|---|" + "|".join(["---"] * len(dims)) + "|---|"

    out.append(header)
    out.append(separator)

    # Calculate totals
    total_revenue = Decimal("0.00")
    total_direct = Decimal("0.00")
    total_gross = Decimal("0.00")
    total_opex = Decimal("0.00")
    total_contribution = Decimal("0.00")

    dim_data = []
    for dim in dims:
        revenue = d(dim.get("revenue", 0))
        direct_costs = d(dim.get("direct_costs", 0))
        gross_profit = revenue - direct_costs
        operating_expenses = d(dim.get("operating_expenses", 0))
        contribution = gross_profit - operating_expenses

        total_revenue += revenue
        total_direct += direct_costs
        total_gross += gross_profit
        total_opex += operating_expenses
        total_contribution += contribution

        dim_data.append({
            "name": dim.get("name", "?"),
            "revenue": revenue,
            "direct_costs": direct_costs,
            "gross_profit": gross_profit,
            "operating_expenses": operating_expenses,
            "contribution": contribution,
            "prior": dim.get("prior"),
            "budget": dim.get("budget"),
        })

    # Revenue row
    rev_cols = " | ".join(fmt(dd["revenue"]) if dd["revenue"] > 0 else "—" for dd in dim_data)
    out.append(f"| Revenue | {rev_cols} | **{fmt(total_revenue)}** |")

    # Direct costs row
    dc_cols = " | ".join(f"({fmt(abs(dd['direct_costs']))})" if dd["direct_costs"] > 0 else "—" for dd in dim_data)
    out.append(f"| Direct costs | {dc_cols} | **({fmt(abs(total_direct))})** |")

    # Separator
    sep_cols = " | ".join(["───"] * len(dims))
    out.append(f"| | {sep_cols} | ─── |")

    # Gross profit row
    gp_cols = " | ".join(fmt(dd["gross_profit"]) for dd in dim_data)
    out.append(f"| **Gross profit** | {gp_cols} | **{fmt(total_gross)}** |")

    # Gross margin row
    gm_cols = " | ".join(margin_pct(dd["gross_profit"], dd["revenue"]) for dd in dim_data)
    out.append(f"| *Gross margin %* | {gm_cols} | *{margin_pct(total_gross, total_revenue)}* |")

    # Operating expenses row
    opex_cols = " | ".join(f"({fmt(abs(dd['operating_expenses']))})" if dd["operating_expenses"] > 0 else "—" for dd in dim_data)
    out.append(f"| Operating expenses | {opex_cols} | **({fmt(abs(total_opex))})** |")

    # Separator
    out.append(f"| | {sep_cols} | ─── |")

    # Contribution row
    cont_cols = " | ".join(fmt(dd["contribution"]) for dd in dim_data)
    out.append(f"| **Contribution** | {cont_cols} | **{fmt(total_contribution)}** |")

    # Contribution margin row
    cm_cols = " | ".join(margin_pct(dd["contribution"], dd["revenue"]) for dd in dim_data)
    out.append(f"| *Margin %* | {cm_cols} | *{margin_pct(total_contribution, total_revenue)}* |")

    out.append("")

    # --- PROFITABILITY RANKING ---
    out.append("## Profitability Ranking")
    out.append("")
    out.append(f"| Rank | {dim_type.title()} | Contribution | Margin | Status |")
    out.append("|------|---|---|---|---|")

    ranked = sorted(dim_data, key=lambda x: x["contribution"], reverse=True)
    for i, dd in enumerate(ranked, 1):
        m = margin_pct(dd["contribution"], dd["revenue"])
        if dd["contribution"] < 0:
            status = "Below breakeven"
        elif dd["revenue"] == 0:
            status = "Cost center"
        elif dd["contribution"] / dd["revenue"] < Decimal("0.10"):
            status = "Low margin"
        else:
            status = "Healthy"
        out.append(f"| {i} | {dd['name']} | {fmt(dd['contribution'])} | {m} | {status} |")

    out.append("")

    # --- UNALLOCATED WARNING ---
    unallocated = d(data.get("unallocated_amount", 0))
    if unallocated > 0:
        unalloc_pct = margin_pct(unallocated, total_revenue + unallocated)
        out.append("## Unallocated Amounts")
        out.append("")
        out.append(f"**{fmt(unallocated)}** ({unalloc_pct}) of transactions have no {dim_type.lower()} tag.")
        if total_revenue + unallocated > 0 and unallocated / (total_revenue + unallocated) > Decimal("0.20"):
            out.append(f"> **WARNING**: Unallocated exceeds 20%. Improve {dim_type.lower()} tagging on transactions for more accurate analysis.")
        out.append("")

    # --- COMPARATIVE ---
    if has_prior:
        out.append("## Period Comparison")
        out.append("")
        out.append(f"| {dim_type.title()} | Current | Prior | Change | % |")
        out.append("|---|---|---|---|---|")
        for dd in dim_data:
            if dd["prior"]:
                prior_contrib = d(dd["prior"].get("contribution", 0))
                diff = dd["contribution"] - prior_contrib
                sign = "+" if diff >= 0 else ""
                pct = change_pct(dd["contribution"], prior_contrib)
                flag = " ⚠️" if prior_contrib != 0 and abs(diff) / abs(prior_contrib) > Decimal("0.15") else ""
                out.append(f"| {dd['name']} | {fmt(dd['contribution'])} | {fmt(prior_contrib)} | {sign}{fmt(diff)} | {pct}{flag} |")
        out.append("")

    # --- BUDGET VARIANCE ---
    if has_budget:
        out.append("## Budget Variance")
        out.append("")
        out.append(f"| {dim_type.title()} | Actual | Budget | Variance | % |")
        out.append("|---|---|---|---|---|")
        for dd in dim_data:
            if dd["budget"]:
                budget_contrib = d(dd["budget"].get("contribution", 0))
                variance = dd["contribution"] - budget_contrib
                sign = "+" if variance >= 0 else ""
                pct = change_pct(dd["contribution"], budget_contrib)
                status = "Favorable" if variance >= 0 else "Unfavorable ⚠️"
                out.append(f"| {dd['name']} | {fmt(dd['contribution'])} | {fmt(budget_contrib)} | {sign}{fmt(variance)} ({pct}) | {status} |")
        out.append("")

    # --- RECOMMENDATIONS ---
    out.append("## Recommendations")
    out.append("")
    for dd in ranked:
        if dd["contribution"] < 0 and dd["revenue"] > 0:
            out.append(f"- **{dd['name']}**: Negative contribution ({fmt(dd['contribution'])}). Review pricing, cost structure, or consider restructuring.")
        elif dd["revenue"] == 0 and dd["operating_expenses"] > 0:
            out.append(f"- **{dd['name']}**: Cost center with {fmt(dd['operating_expenses'])} in expenses. Verify allocation methodology.")

    if unallocated > 0 and total_revenue + unallocated > 0 and unallocated / (total_revenue + unallocated) > Decimal("0.10"):
        out.append(f"- **Unallocated**: {fmt(unallocated)} untagged. Assign {dim_type.lower()} tags to improve analysis accuracy.")

    out.append("")
    out.append("---")
    out.append("*Generated by arfiti-core-financial-reports plugin*")

    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Format Dimension Analysis")
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

    print(f"Dimension Analysis written to {args.output}")
    print(f"Entity: {data['entity_name']} | Dimension: {data.get('dimension_type', '?')}")


if __name__ == "__main__":
    main()
