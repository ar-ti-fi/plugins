#!/usr/bin/env python3
"""
generate_tsd.py — Generate Estonian TSD (monthly tax declaration) XML for EMTA.

Usage:
    python3 generate_tsd.py --input /tmp/tsd_data_12345678.json --output /tmp/

Input JSON format: see input_schema_tsd.json
Output: TSD_YYYYMM_{REGCODE}.xml
"""

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

NS_TSD = "http://emta.ee/tsd"
TOLERANCE = Decimal("0.02")


def fmt(value) -> str:
    """Format a numeric value as 2-decimal string."""
    return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def esc(s: str) -> str:
    """Escape XML special characters."""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def validate(data: dict) -> list:
    """Validate input data. Returns list of error strings."""
    errors = []

    if not data.get("regcode"):
        errors.append("regcode is required")
    if not data.get("year"):
        errors.append("year is required")
    month = data.get("month")
    if not month or not (1 <= int(month) <= 12):
        errors.append("month is required and must be 1-12")

    employees = data.get("employees", [])
    if not employees:
        errors.append("At least one employee is required")

    for i, emp in enumerate(employees):
        pid = emp.get("personal_id", "no ID")
        prefix = f"Employee {i+1} ({pid})"

        if not emp.get("personal_id"):
            errors.append(f"{prefix}: personal_id is required")
        if not emp.get("first_name"):
            errors.append(f"{prefix}: first_name is required")
        if not emp.get("last_name"):
            errors.append(f"{prefix}: last_name is required")

        # Validate net pay formula:
        # net_pay = gross_pay - income_tax - unemployment_employee - funded_pension - total_deductions
        try:
            gross = Decimal(str(emp.get("gross_pay", 0)))
            income_tax = Decimal(str(emp.get("income_tax", 0)))
            unemp_ee = Decimal(str(emp.get("unemployment_employee", 0)))
            pension = Decimal(str(emp.get("funded_pension", 0)))
            net_pay = Decimal(str(emp.get("net_pay", 0)))
            deductions = Decimal(str(emp.get("total_deductions", 0)))
            expected_net = gross - income_tax - unemp_ee - pension - deductions
            if abs(net_pay - expected_net) > TOLERANCE:
                errors.append(
                    f"{prefix}: net_pay {fmt(net_pay)} does not match formula "
                    f"gross({fmt(gross)}) - income_tax({fmt(income_tax)}) "
                    f"- unemp_ee({fmt(unemp_ee)}) - pension({fmt(pension)}) "
                    f"- deductions({fmt(deductions)}) = {fmt(expected_net)}"
                )
        except Exception as e:
            errors.append(f"{prefix}: invalid numeric value — {e}")

    return errors


def generate_tsd(data: dict, output_dir: Path) -> Path:
    """Generate TSD XML and write to output_dir. Returns path of generated file."""
    regcode = data["regcode"]
    year = int(data["year"])
    month = int(data["month"])
    employees = data.get("employees", [])

    # Compute summary totals
    total_gross = sum(Decimal(str(e.get("gross_pay", 0))) for e in employees)
    total_income_tax = sum(Decimal(str(e.get("income_tax", 0))) for e in employees)
    total_social_tax = sum(Decimal(str(e.get("social_tax", 0))) for e in employees)
    total_unemp_er = sum(Decimal(str(e.get("unemployment_employer", 0))) for e in employees)
    total_unemp_ee = sum(Decimal(str(e.get("unemployment_employee", 0))) for e in employees)
    total_pension = sum(Decimal(str(e.get("funded_pension", 0))) for e in employees)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<TSD xmlns="{NS_TSD}">',
        "  <Header>",
        f"    <TaxpayerRegCode>{esc(regcode)}</TaxpayerRegCode>",
        "    <Period>",
        f"      <Year>{year}</Year>",
        f"      <Month>{month:02d}</Month>",
        "    </Period>",
        "  </Header>",
        "  <Summary>",
        f"    <TotalGrossPayments>{fmt(total_gross)}</TotalGrossPayments>",
        f"    <TotalIncomeTax>{fmt(total_income_tax)}</TotalIncomeTax>",
        f"    <TotalSocialTax>{fmt(total_social_tax)}</TotalSocialTax>",
        f"    <TotalUnemploymentEmployer>{fmt(total_unemp_er)}</TotalUnemploymentEmployer>",
        f"    <TotalUnemploymentEmployee>{fmt(total_unemp_ee)}</TotalUnemploymentEmployee>",
        f"    <TotalFundedPension>{fmt(total_pension)}</TotalFundedPension>",
        "  </Summary>",
        "  <Annex1>",
    ]

    for emp in employees:
        basic_exemption = Decimal(str(emp.get("basic_exemption_amount", 0)))
        taxable = Decimal(str(emp.get("taxable_amount", 0)))

        lines += [
            "    <Person>",
            f"      <PersonalId>{esc(emp['personal_id'])}</PersonalId>",
            f"      <FirstName>{esc(emp['first_name'])}</FirstName>",
            f"      <LastName>{esc(emp['last_name'])}</LastName>",
            f"      <GrossPayment>{fmt(emp.get('gross_pay', 0))}</GrossPayment>",
            f"      <TaxFreeAmount>{fmt(basic_exemption)}</TaxFreeAmount>",
            f"      <TaxableAmount>{fmt(taxable)}</TaxableAmount>",
            f"      <IncomeTax>{fmt(emp.get('income_tax', 0))}</IncomeTax>",
            f"      <UnemploymentEmployee>{fmt(emp.get('unemployment_employee', 0))}</UnemploymentEmployee>",
            f"      <FundedPension>{fmt(emp.get('funded_pension', 0))}</FundedPension>",
            "    </Person>",
        ]

    lines += [
        "  </Annex1>",
        "</TSD>",
    ]

    filename = f"TSD_{year}{month:02d}_{regcode}.xml"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate Estonian TSD declaration XML for EMTA"
    )
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument(
        "--output", default=".", help="Output directory (default: current directory)"
    )
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    errors = validate(data)
    if errors:
        print("VALIDATION ERRORS:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output)
    tsd_path = generate_tsd(data, output_dir)

    print(f"Generated: {tsd_path}")

    employees = data.get("employees", [])
    total_gross = sum(Decimal(str(e.get("gross_pay", 0))) for e in employees)
    total_income_tax = sum(Decimal(str(e.get("income_tax", 0))) for e in employees)
    total_social_tax = sum(Decimal(str(e.get("social_tax", 0))) for e in employees)
    total_unemp_ee = sum(Decimal(str(e.get("unemployment_employee", 0))) for e in employees)
    total_pension = sum(Decimal(str(e.get("funded_pension", 0))) for e in employees)

    print(f"\nSummary ({len(employees)} employee(s)):")
    print(f"  Total gross:                EUR {fmt(total_gross)}")
    print(f"  Total income tax:           EUR {fmt(total_income_tax)}")
    print(f"  Total social tax:           EUR {fmt(total_social_tax)}")
    print(f"  Total unemployment (EE):    EUR {fmt(total_unemp_ee)}")
    print(f"  Total funded pension:       EUR {fmt(total_pension)}")
    print(f"\nReady for upload to e-MTA portal (maasikas.emta.ee)")
    print(f"Filing deadline: 10th of the following month")


if __name__ == "__main__":
    main()
