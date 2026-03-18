#!/usr/bin/env python3
"""Format a Financial Summary (executive overview) combining BS, P&L, and ratios.

Usage:
    python3 format_financial_summary.py --input data.json --output report.md

Input: JSON with condensed BS, P&L, and cash data.
Output: Single-page executive financial overview with ratios.
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


def ratio_fmt(val: Decimal, suffix: str = "") -> str:
    return f"{val}{suffix}"


def margin_pct(amount: Decimal, revenue: Decimal) -> str:
    if revenue == 0:
        return "N/A"
    result = (amount / revenue * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return f"{result}%"


def change_str(current: Decimal, prior: Decimal) -> str:
    if prior == 0:
        return "N/A" if current == 0 else "New"
    result = ((current - prior) / abs(prior) * 100).quantize(Decimal("0.1"))
    sign = "+" if result > 0 else ""
    return f"{sign}{result}%"


def validate(data: dict) -> list:
    errors = []
    for field in ["entity_name", "period_end", "period_start"]:
        if field not in data:
            errors.append(f"Missing '{field}'")
    for section in ["pnl", "balance_sheet"]:
        if section not in data:
            errors.append(f"Missing '{section}' section")
    return errors


def build_report(data: dict) -> str:
    currency = data.get("currency", "USD")
    has_prior = "prior" in data

    pnl = data["pnl"]
    bs = data["balance_sheet"]
    cash = data.get("cash_flow", {})
    prior_pnl = data.get("prior", {}).get("pnl", {}) if has_prior else {}
    prior_bs = data.get("prior", {}).get("balance_sheet", {}) if has_prior else {}

    # P&L values
    revenue = d(pnl.get("revenue", 0))
    cogs = d(pnl.get("cogs", 0))
    gross_profit = revenue - cogs
    operating_expenses = d(pnl.get("operating_expenses", 0))
    operating_profit = gross_profit - operating_expenses
    depreciation = d(pnl.get("depreciation", 0))
    interest_expense = d(pnl.get("interest_expense", 0))
    net_profit = d(pnl.get("net_profit", 0))
    ebitda = operating_profit + depreciation

    # BS values
    total_assets = d(bs.get("total_assets", 0))
    current_assets = d(bs.get("current_assets", 0))
    cash_balance = d(bs.get("cash", 0))
    inventory = d(bs.get("inventory", 0))
    receivables = d(bs.get("receivables", 0))
    total_liabilities = d(bs.get("total_liabilities", 0))
    current_liabilities = d(bs.get("current_liabilities", 0))
    payables = d(bs.get("payables", 0))
    total_equity = d(bs.get("total_equity", 0))

    # Cash flow values
    operating_cf = d(cash.get("operating", 0))
    investing_cf = d(cash.get("investing", 0))
    financing_cf = d(cash.get("financing", 0))
    capex = d(cash.get("capex", 0))
    free_cash_flow = operating_cf - abs(capex)

    out = []
    out.append("# Financial Summary")
    out.append(f"**{data['entity_name']}** | Period: {data['period_start']} to {data['period_end']} | Currency: {currency}")
    out.append("")

    # --- P&L SNAPSHOT ---
    out.append("## Profit & Loss")
    out.append("")
    if has_prior:
        p_rev = d(prior_pnl.get("revenue", 0))
        p_gp = p_rev - d(prior_pnl.get("cogs", 0))
        p_op = d(prior_pnl.get("operating_profit", 0))
        p_net = d(prior_pnl.get("net_profit", 0))

        out.append("| | Current | Prior | Change |")
        out.append("|---|---------|-------|--------|")
        out.append(f"| Revenue | {fmt(revenue)} | {fmt(p_rev)} | {change_str(revenue, p_rev)} |")
        out.append(f"| Gross Profit | {fmt(gross_profit)} ({margin_pct(gross_profit, revenue)}) | {fmt(p_gp)} ({margin_pct(p_gp, p_rev)}) | {change_str(gross_profit, p_gp)} |")
        out.append(f"| Operating Profit | {fmt(operating_profit)} ({margin_pct(operating_profit, revenue)}) | {fmt(p_op)} ({margin_pct(p_op, p_rev)}) | {change_str(operating_profit, p_op)} |")
        out.append(f"| EBITDA | {fmt(ebitda)} ({margin_pct(ebitda, revenue)}) | | |")
        out.append(f"| **Net Profit** | **{fmt(net_profit)}** (**{margin_pct(net_profit, revenue)}**) | **{fmt(p_net)}** | **{change_str(net_profit, p_net)}** |")
    else:
        out.append("| | Amount | % of Revenue |")
        out.append("|---|--------|-------------|")
        out.append(f"| Revenue | {fmt(revenue)} | 100.0% |")
        out.append(f"| Gross Profit | {fmt(gross_profit)} | {margin_pct(gross_profit, revenue)} |")
        out.append(f"| Operating Profit | {fmt(operating_profit)} | {margin_pct(operating_profit, revenue)} |")
        out.append(f"| EBITDA | {fmt(ebitda)} | {margin_pct(ebitda, revenue)} |")
        out.append(f"| **Net Profit** | **{fmt(net_profit)}** | **{margin_pct(net_profit, revenue)}** |")
    out.append("")

    # --- BALANCE SHEET SNAPSHOT ---
    out.append("## Balance Sheet")
    out.append("")
    out.append("| | Amount |")
    out.append("|---|--------|")
    out.append(f"| Cash | {fmt(cash_balance)} |")
    out.append(f"| Total Current Assets | {fmt(current_assets)} |")
    out.append(f"| **Total Assets** | **{fmt(total_assets)}** |")
    out.append(f"| Total Current Liabilities | {fmt(current_liabilities)} |")
    out.append(f"| **Total Liabilities** | **{fmt(total_liabilities)}** |")
    out.append(f"| **Total Equity** | **{fmt(total_equity)}** |")
    out.append("")

    # --- CASH FLOW SNAPSHOT ---
    if cash:
        out.append("## Cash Flow")
        out.append("")
        out.append("| | Amount |")
        out.append("|---|--------|")
        out.append(f"| Operating activities | {fmt(operating_cf)} |")
        out.append(f"| Investing activities | {fmt(investing_cf)} |")
        out.append(f"| Financing activities | {fmt(financing_cf)} |")
        net_change = operating_cf + investing_cf + financing_cf
        out.append(f"| **Net change in cash** | **{fmt(net_change)}** |")
        out.append(f"| Free Cash Flow | {fmt(free_cash_flow)} |")
        out.append("")

    # --- RATIO DASHBOARD ---
    out.append("## Financial Ratios")
    out.append("")
    out.append("| Category | Ratio | Value | Assessment |")
    out.append("|----------|-------|-------|------------|")

    # Liquidity
    if current_liabilities > 0:
        cr = (current_assets / current_liabilities).quantize(Decimal("0.01"))
        cr_assess = "Healthy" if Decimal("1.5") <= cr <= Decimal("3.0") else ("Low" if cr < Decimal("1.0") else "Review")
        out.append(f"| Liquidity | Current Ratio | {cr} | {cr_assess} |")

        qr = ((current_assets - inventory) / current_liabilities).quantize(Decimal("0.01"))
        qr_assess = "Healthy" if Decimal("1.0") <= qr <= Decimal("2.0") else "Review"
        out.append(f"| Liquidity | Quick Ratio | {qr} | {qr_assess} |")

    # Profitability
    out.append(f"| Profitability | Gross Margin | {margin_pct(gross_profit, revenue)} | |")
    out.append(f"| Profitability | Operating Margin | {margin_pct(operating_profit, revenue)} | |")
    out.append(f"| Profitability | Net Margin | {margin_pct(net_profit, revenue)} | |")

    if total_equity > 0:
        roe = (net_profit / total_equity * 100).quantize(Decimal("0.1"))
        out.append(f"| Profitability | ROE | {roe}% | |")

    if total_assets > 0:
        roa = (net_profit / total_assets * 100).quantize(Decimal("0.1"))
        out.append(f"| Profitability | ROA | {roa}% | |")

    # Leverage
    if total_equity > 0:
        dte = (total_liabilities / total_equity).quantize(Decimal("0.01"))
        dte_assess = "Conservative" if dte < Decimal("1.0") else ("Moderate" if dte < Decimal("2.0") else "Leveraged")
        out.append(f"| Leverage | Debt-to-Equity | {dte} | {dte_assess} |")

    if interest_expense > 0:
        ic = (operating_profit / interest_expense).quantize(Decimal("0.1"))
        ic_assess = "Strong" if ic > Decimal("5") else ("Adequate" if ic > Decimal("3") else "Risky")
        out.append(f"| Leverage | Interest Coverage | {ic}x | {ic_assess} |")

    # Efficiency
    if revenue > 0:
        dso = (receivables / revenue * 365).quantize(Decimal("0"))
        out.append(f"| Efficiency | DSO | {dso} days | |")
    if cogs > 0:
        dpo = (payables / cogs * 365).quantize(Decimal("0"))
        inv_days = (inventory / cogs * 365).quantize(Decimal("0"))
        out.append(f"| Efficiency | DPO | {dpo} days | |")
        out.append(f"| Efficiency | Inventory Days | {inv_days} days | |")
        ccc = dso + inv_days - dpo if revenue > 0 else Decimal("0")
        out.append(f"| Efficiency | Cash Conversion Cycle | {ccc} days | |")

    out.append("")

    # --- KEY TAKEAWAYS ---
    out.append("## Key Takeaways")
    out.append("")

    takeaways = []
    if net_profit > 0:
        takeaways.append(f"- Net profit of {fmt(net_profit)} ({margin_pct(net_profit, revenue)} margin)")
    else:
        takeaways.append(f"- Net loss of {fmt(abs(net_profit))} — review cost structure")

    if cash and operating_cf > net_profit:
        takeaways.append(f"- Strong cash generation: operating CF ({fmt(operating_cf)}) exceeds net profit")
    elif cash and operating_cf < net_profit and operating_cf > 0:
        takeaways.append(f"- Cash conversion below net profit — check working capital changes")

    if current_liabilities > 0:
        cr_val = current_assets / current_liabilities
        if cr_val < Decimal("1.0"):
            takeaways.append(f"- **Liquidity concern**: Current ratio {cr_val.quantize(Decimal('0.01'))} — may struggle to meet short-term obligations")

    if has_prior:
        p_rev = d(prior_pnl.get("revenue", 0))
        if p_rev > 0 and revenue > p_rev:
            growth = ((revenue - p_rev) / p_rev * 100).quantize(Decimal("0.1"))
            takeaways.append(f"- Revenue grew {growth}% vs prior period")

    for t in takeaways:
        out.append(t)

    out.append("")
    out.append("---")
    out.append("*Generated by arfiti-core-financial-reports plugin*")

    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Format Financial Summary")
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

    print(f"Financial Summary written to {args.output}")
    print(f"Entity: {data['entity_name']} | Period: {data['period_start']} to {data['period_end']}")


if __name__ == "__main__":
    main()
