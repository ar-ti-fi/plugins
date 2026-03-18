#!/usr/bin/env python3
"""Format an Income Statement (P&L) from JSON data into consistent markdown output.

Usage:
    python3 format_income_statement.py --input data.json --output report.md

Input: JSON with current (and optional prior) P&L data.
Output: Formatted markdown P&L with margins, variance analysis, and commentary.
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


def margin(amount: Decimal, revenue: Decimal) -> str:
    if revenue == 0:
        return "N/A"
    result = (amount / revenue * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return f"{result}%"


def change_str(current: Decimal, prior: Decimal) -> tuple:
    diff = current - prior
    sign = "+" if diff >= 0 else ""
    if prior == 0:
        pct = "N/A" if current == 0 else "New"
    else:
        pct_val = ((current - prior) / abs(prior) * 100).quantize(Decimal("0.1"))
        pct_sign = "+" if pct_val > 0 else ""
        pct = f"{pct_sign}{pct_val}%"
    return f"{sign}{fmt(diff)}", pct


def validate(data: dict) -> list:
    errors = []
    if "entity_name" not in data:
        errors.append("Missing 'entity_name'")
    if "start_date" not in data or "end_date" not in data:
        errors.append("Missing 'start_date' or 'end_date'")
    if "revenue" not in data:
        errors.append("Missing 'revenue' section")
    if "expenses" not in data:
        errors.append("Missing 'expenses' section")
    return errors


def sum_section(items: list) -> Decimal:
    return sum(d(i.get("amount", 0)) for i in items)


def build_report(data: dict) -> str:
    currency = data.get("currency", "USD")
    has_prior = "prior" in data
    fmt_type = data.get("format", "nature")  # "nature" or "function"

    out = []
    out.append("# Profit & Loss Statement")
    out.append(f"**{data['entity_name']}** | {data['start_date']} to {data['end_date']} | Currency: {currency}")
    if has_prior:
        prior = data["prior"]
        out.append(f"Comparative: {prior.get('start_date', '?')} to {prior.get('end_date', '?')}")
    out.append("")

    # Calculate current period
    revenue_items = data.get("revenue", [])
    other_income_items = data.get("other_income", [])
    cogs_items = data.get("cogs", [])
    expense_items = data.get("expenses", [])
    financial_income_items = data.get("financial_income", [])
    financial_expense_items = data.get("financial_expenses", [])
    tax_items = data.get("income_tax", [])

    total_revenue = sum_section(revenue_items)
    total_other_income = sum_section(other_income_items)
    total_cogs = sum_section(cogs_items)
    total_expenses = sum_section(expense_items)
    total_fin_income = sum_section(financial_income_items)
    total_fin_expense = sum_section(financial_expense_items)
    total_tax = sum_section(tax_items)

    gross_profit = total_revenue - total_cogs
    total_income = total_revenue + total_other_income
    operating_profit = total_income - total_cogs - total_expenses
    profit_before_tax = operating_profit + total_fin_income - total_fin_expense
    net_profit = profit_before_tax - total_tax

    # --- MAIN STATEMENT ---
    if has_prior:
        prior = data["prior"]
        p_revenue = sum_section(prior.get("revenue", []))
        p_other_income = sum_section(prior.get("other_income", []))
        p_cogs = sum_section(prior.get("cogs", []))
        p_expenses = sum_section(prior.get("expenses", []))
        p_fin_income = sum_section(prior.get("financial_income", []))
        p_fin_expense = sum_section(prior.get("financial_expenses", []))
        p_tax = sum_section(prior.get("income_tax", []))
        p_gross = p_revenue - p_cogs
        p_total_income = p_revenue + p_other_income
        p_operating = p_total_income - p_cogs - p_expenses
        p_pbt = p_operating + p_fin_income - p_fin_expense
        p_net = p_pbt - p_tax

        out.append("| | Current | Prior | Change | % |")
        out.append("|---|---------|-------|--------|---|")

        def row(label, curr, prev, bold=False):
            ch, pct = change_str(curr, prev)
            flag = " ⚠️" if prev != 0 and abs(curr - prev) / abs(prev) > Decimal("0.15") else ""
            if bold:
                return f"| **{label}** | **{fmt(curr)}** | **{fmt(prev)}** | {ch} | {pct}{flag} |"
            return f"| {label} | {fmt(curr)} | {fmt(prev)} | {ch} | {pct}{flag} |"

        # Revenue
        for item in revenue_items:
            out.append(row(item["name"], d(item["amount"]), d(_find_prior(prior.get("revenue", []), item["name"]))))
        out.append(row("Total Revenue", total_revenue, p_revenue, bold=True))
        out.append("| | | | | |")

        if other_income_items:
            out.append(row("Other income", total_other_income, p_other_income))

        if cogs_items:
            for item in cogs_items:
                out.append(row(item["name"], d(item["amount"]), d(_find_prior(prior.get("cogs", []), item["name"]))))
            out.append(row("Gross Profit", gross_profit, p_gross, bold=True))
            out.append("| | | | | |")

        for item in expense_items:
            out.append(row(item["name"], d(item["amount"]), d(_find_prior(prior.get("expenses", []), item["name"]))))
        out.append(row("Operating Profit", operating_profit, p_operating, bold=True))
        out.append("| | | | | |")

        if financial_income_items or financial_expense_items:
            out.append(row("Financial income", total_fin_income, p_fin_income))
            out.append(row("Financial expenses", total_fin_expense, p_fin_expense))
        out.append(row("Profit Before Tax", profit_before_tax, p_pbt, bold=True))

        if tax_items:
            out.append(row("Income tax", total_tax, p_tax))
        out.append(row("Net Profit / (Loss)", net_profit, p_net, bold=True))

    else:
        # Single period
        out.append("| | Amount | % of Revenue |")
        out.append("|---|--------|-------------|")

        for item in revenue_items:
            out.append(f"| {item['name']} | {fmt(d(item['amount']))} | {margin(d(item['amount']), total_revenue)} |")
        out.append(f"| **Total Revenue** | **{fmt(total_revenue)}** | **100.0%** |")
        out.append("| | | |")

        if other_income_items:
            out.append(f"| Other income | {fmt(total_other_income)} | {margin(total_other_income, total_revenue)} |")

        if cogs_items:
            for item in cogs_items:
                out.append(f"| {item['name']} | ({fmt(abs(d(item['amount'])))}) | {margin(d(item['amount']), total_revenue)} |")
            out.append(f"| **Gross Profit** | **{fmt(gross_profit)}** | **{margin(gross_profit, total_revenue)}** |")
            out.append("| | | |")

        for item in expense_items:
            out.append(f"| {item['name']} | ({fmt(abs(d(item['amount'])))}) | {margin(d(item['amount']), total_revenue)} |")
        out.append(f"| **Operating Profit** | **{fmt(operating_profit)}** | **{margin(operating_profit, total_revenue)}** |")
        out.append("| | | |")

        if financial_income_items or financial_expense_items:
            out.append(f"| Financial income | {fmt(total_fin_income)} | |")
            out.append(f"| Financial expenses | ({fmt(abs(total_fin_expense))}) | |")
        out.append(f"| **Profit Before Tax** | **{fmt(profit_before_tax)}** | **{margin(profit_before_tax, total_revenue)}** |")

        if tax_items:
            out.append(f"| Income tax | ({fmt(abs(total_tax))}) | |")
        out.append(f"| **Net Profit / (Loss)** | **{fmt(net_profit)}** | **{margin(net_profit, total_revenue)}** |")

    out.append("")

    # --- MARGINS ---
    out.append("## Margin Analysis")
    out.append("")
    out.append("| Metric | Value |")
    out.append("|--------|-------|")
    if total_cogs > 0 or cogs_items:
        out.append(f"| Gross Margin | {margin(gross_profit, total_revenue)} |")
    out.append(f"| Operating Margin | {margin(operating_profit, total_revenue)} |")
    out.append(f"| Net Margin | {margin(net_profit, total_revenue)} |")

    # EBITDA
    depreciation = Decimal("0.00")
    for item in expense_items:
        name_lower = item.get("name", "").lower()
        if "depreci" in name_lower or "amortiz" in name_lower:
            depreciation += abs(d(item.get("amount", 0)))
    ebitda = operating_profit + depreciation
    out.append(f"| EBITDA | {fmt(ebitda)} ({margin(ebitda, total_revenue)}) |")
    out.append("")

    if has_prior:
        out.append("> Items marked ⚠️ changed by more than 15% — investigate significant variances.")
        out.append("")

    out.append("---")
    out.append("*Generated by arfiti-core-financial-reports plugin*")

    return "\n".join(out)


def _find_prior(items: list, name: str) -> float:
    """Find matching item in prior period by name."""
    for item in items:
        if item.get("name") == name:
            return item.get("amount", 0)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Format Income Statement")
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

    print(f"Income Statement written to {args.output}")
    print(f"Entity: {data['entity_name']} | Period: {data['start_date']} to {data['end_date']}")
    print(f"Net Profit: {fmt(sum_section(data.get('revenue', [])) - sum_section(data.get('cogs', [])) - sum_section(data.get('expenses', [])) + sum_section(data.get('financial_income', [])) - sum_section(data.get('financial_expenses', [])) - sum_section(data.get('income_tax', [])))}")


if __name__ == "__main__":
    main()
