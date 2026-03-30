#!/usr/bin/env python3
"""
generate_kmd.py — Generate Estonian VAT declaration XML files for EMTA.

Generates up to three files:
  KMD_YYYYMM_{REGCODE}.xml      — Main KMD form (Lines 1-13)
  KMDINF_YYYYMM_{REGCODE}.xml   — KMD INF annex (partner reporting, Parts A & B)
  VD_YYYYMM_{REGCODE}.xml       — EC Sales List (only if vd_entries are present)

Usage:
    python3 generate_kmd.py --input /tmp/kmd_data_12345678.json --output /tmp/

Input JSON format: see input_schema_kmd.json
"""

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

NS_VAT = "http://emta.ee/schemas/vat"
TOLERANCE = Decimal("0.02")

VALID_SUPPLY_TYPES = {"G", "S", "T"}


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


def d(data: dict, key: str) -> Decimal:
    """Get a decimal value from dict, defaulting to 0."""
    return Decimal(str(data.get(key, 0) or 0))


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

    lines = data.get("kmd_lines", {})
    if not lines:
        errors.append("kmd_lines is required")
    else:
        line1_1 = d(lines, "line1_1")
        line2_1 = d(lines, "line2_1")
        line4 = d(lines, "line4")
        line8 = d(lines, "line8")
        line10 = d(lines, "line10")
        line11 = d(lines, "line11")
        line12 = d(lines, "line12")
        line13 = d(lines, "line13")

        # Validate Line 10 formula: (Line 1.1 + Line 2.1) - Line 4 + Line 8
        expected_line10 = (line1_1 + line2_1) - line4 + line8
        if abs(line10 - expected_line10) > TOLERANCE:
            errors.append(
                f"kmd_lines.line10 ({fmt(line10)}) does not match formula "
                f"(line1_1 {fmt(line1_1)} + line2_1 {fmt(line2_1)}) "
                f"- line4 ({fmt(line4)}) + line8 ({fmt(line8)}) = {fmt(expected_line10)}"
            )

        # Validate Lines 12/13 mutual exclusion
        net = line10 + line11
        if line12 > Decimal("0") and line13 > Decimal("0"):
            errors.append(
                f"kmd_lines.line12 and line13 are mutually exclusive — "
                f"only one can be non-zero (line12={fmt(line12)}, line13={fmt(line13)})"
            )

        # Validate Line 12 = max(0, net)
        expected_line12 = max(Decimal("0"), net)
        if abs(line12 - expected_line12) > TOLERANCE:
            errors.append(
                f"kmd_lines.line12 ({fmt(line12)}) should be max(0, line10+line11) = {fmt(expected_line12)}"
            )

        # Validate Line 13 = max(0, -net)
        expected_line13 = max(Decimal("0"), -net)
        if abs(line13 - expected_line13) > TOLERANCE:
            errors.append(
                f"kmd_lines.line13 ({fmt(line13)}) should be max(0, -(line10+line11)) = {fmt(expected_line13)}"
            )

    # Validate VD entries
    for i, entry in enumerate(data.get("vd_entries", [])):
        prefix = f"vd_entries[{i}]"
        if not entry.get("customer_vat_number"):
            errors.append(f"{prefix}: customer_vat_number is required")
        if not entry.get("country_code") or len(str(entry.get("country_code", ""))) != 2:
            errors.append(f"{prefix}: country_code must be a 2-letter ISO country code")
        supply_type = entry.get("supply_type", "")
        if supply_type not in VALID_SUPPLY_TYPES:
            errors.append(f"{prefix}: supply_type must be G, S, or T (got '{supply_type}')")

    # Validate VD reconciles with KMD Lines 3.1 / 3.2
    if data.get("vd_entries") and lines:
        vd_goods = sum(
            Decimal(str(e.get("amount", 0)))
            for e in data["vd_entries"]
            if e.get("supply_type") in ("G", "T")
        )
        vd_services = sum(
            Decimal(str(e.get("amount", 0)))
            for e in data["vd_entries"]
            if e.get("supply_type") == "S"
        )
        line3_1 = d(lines, "line3_1")
        line3_2 = d(lines, "line3_2")
        if abs(vd_goods - line3_1) > TOLERANCE:
            errors.append(
                f"VD goods total ({fmt(vd_goods)}) does not match kmd_lines.line3_1 ({fmt(line3_1)})"
            )
        if abs(vd_services - line3_2) > TOLERANCE:
            errors.append(
                f"VD services total ({fmt(vd_services)}) does not match kmd_lines.line3_2 ({fmt(line3_2)})"
            )

    return errors


def generate_kmd(data: dict, output_dir: Path) -> Path:
    """Generate main KMD XML. Returns path of generated file."""
    regcode = data["regcode"]
    year = int(data["year"])
    month = int(data["month"])
    L = data.get("kmd_lines", {})

    # Line 9 is reserved/unused — include as 0
    lines_xml = [
        ("Line1",   d(L, "line1")),
        ("Line1_1", d(L, "line1_1")),
        ("Line2",   d(L, "line2")),
        ("Line2_1", d(L, "line2_1")),
        ("Line3",   d(L, "line3")),
        ("Line3_1", d(L, "line3_1")),
        ("Line3_2", d(L, "line3_2")),
        ("Line4",   d(L, "line4")),
        ("Line4_1", d(L, "line4_1")),
        ("Line5",   d(L, "line5")),
        ("Line5_1", d(L, "line5_1")),
        ("Line6",   d(L, "line6")),
        ("Line7",   d(L, "line7")),
        ("Line8",   d(L, "line8")),
        ("Line10",  d(L, "line10")),
        ("Line11",  d(L, "line11")),
        ("Line12",  d(L, "line12")),
        ("Line13",  d(L, "line13")),
    ]

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<KMD xmlns="{NS_VAT}">',
        f"  <TaxpayerRegCode>{esc(regcode)}</TaxpayerRegCode>",
        "  <Period>",
        f"    <Year>{year}</Year>",
        f"    <Month>{month:02d}</Month>",
        "  </Period>",
    ]

    for tag, value in lines_xml:
        xml_lines.append(f"  <{tag}>{fmt(value)}</{tag}>")

    xml_lines.append("</KMD>")

    filename = f"KMD_{year}{month:02d}_{regcode}.xml"
    output_path = output_dir / filename
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines) + "\n")

    return output_path


def generate_kmdinf(data: dict, output_dir: Path) -> Path:
    """Generate KMD INF annex XML. Returns path of generated file."""
    regcode = data["regcode"]
    year = int(data["year"])
    month = int(data["month"])
    inf = data.get("kmd_inf", {})
    part_a = inf.get("part_a", [])
    part_b = inf.get("part_b", [])

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<KMDINF xmlns="{NS_VAT}">',
        "  <Period>",
        f"    <Year>{year}</Year>",
        f"    <Month>{month:02d}</Month>",
        "  </Period>",
        "  <PartA>",
    ]

    for partner in part_a:
        xml_lines += [
            "    <Partner>",
            f"      <RegCode>{esc(partner.get('reg_code', ''))}</RegCode>",
            f"      <Name>{esc(partner.get('name', ''))}</Name>",
            f"      <InvoiceCount>{int(partner.get('invoice_count', 0))}</InvoiceCount>",
            f"      <TaxableAmount>{fmt(partner.get('taxable_amount', 0))}</TaxableAmount>",
            f"      <VATAmount>{fmt(partner.get('vat_amount', 0))}</VATAmount>",
            "    </Partner>",
        ]

    xml_lines.append("  </PartA>")
    xml_lines.append("  <PartB>")

    for partner in part_b:
        xml_lines += [
            "    <Partner>",
            f"      <RegCode>{esc(partner.get('reg_code', ''))}</RegCode>",
            f"      <Name>{esc(partner.get('name', ''))}</Name>",
            f"      <InvoiceCount>{int(partner.get('invoice_count', 0))}</InvoiceCount>",
            f"      <TaxableAmount>{fmt(partner.get('taxable_amount', 0))}</TaxableAmount>",
            f"      <VATAmount>{fmt(partner.get('vat_amount', 0))}</VATAmount>",
            "    </Partner>",
        ]

    xml_lines.append("  </PartB>")
    xml_lines.append("</KMDINF>")

    filename = f"KMDINF_{year}{month:02d}_{regcode}.xml"
    output_path = output_dir / filename
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines) + "\n")

    return output_path


def generate_vd(data: dict, output_dir: Path) -> Path:
    """Generate EC Sales List (Form VD) XML. Returns path of generated file."""
    regcode = data["regcode"]
    year = int(data["year"])
    month = int(data["month"])
    vat_number = data.get("vat_number", f"EE{regcode}")
    entries = data.get("vd_entries", [])

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<VD xmlns="{NS_VAT}">',
        "  <Period>",
        f"    <Year>{year}</Year>",
        f"    <Month>{month:02d}</Month>",
        "  </Period>",
        f"  <TaxpayerRegCode>{esc(regcode)}</TaxpayerRegCode>",
        f"  <TaxpayerVATNumber>{esc(vat_number)}</TaxpayerVATNumber>",
    ]

    for entry in entries:
        xml_lines += [
            "  <Entry>",
            f"    <CustomerVATNumber>{esc(entry.get('customer_vat_number', ''))}</CustomerVATNumber>",
            f"    <CountryCode>{esc(entry.get('country_code', ''))}</CountryCode>",
            f"    <SupplyType>{esc(entry.get('supply_type', ''))}</SupplyType>",
            f"    <Amount>{fmt(entry.get('amount', 0))}</Amount>",
            "  </Entry>",
        ]

    xml_lines.append("</VD>")

    filename = f"VD_{year}{month:02d}_{regcode}.xml"
    output_path = output_dir / filename
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines) + "\n")

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate Estonian VAT declaration XML files for EMTA"
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
    output_dir.mkdir(parents=True, exist_ok=True)

    kmd_path = generate_kmd(data, output_dir)
    print(f"Generated: {kmd_path}")

    inf = data.get("kmd_inf", {})
    if inf.get("part_a") or inf.get("part_b"):
        inf_path = generate_kmdinf(data, output_dir)
        print(f"Generated: {inf_path}")

    if data.get("vd_entries"):
        vd_path = generate_vd(data, output_dir)
        print(f"Generated: {vd_path}")

    # Print KMD summary
    L = data.get("kmd_lines", {})
    line10 = d(L, "line10")
    line12 = d(L, "line12")
    line13 = d(L, "line13")

    print(f"\nKMD Summary:")
    print(f"  Output VAT (Line 1.1 + 2.1): EUR {fmt(d(L, 'line1_1') + d(L, 'line2_1'))}")
    print(f"  Input VAT  (Line 4):          EUR {fmt(d(L, 'line4'))}")
    print(f"  Net VAT    (Line 10):         EUR {fmt(line10)}")
    if line12 > Decimal("0"):
        print(f"  VAT PAYABLE (Line 12):        EUR {fmt(line12)}")
    elif line13 > Decimal("0"):
        print(f"  VAT OVERPAID (Line 13):       EUR {fmt(line13)}")
    print(f"\nReady for upload to e-MTA portal (maasikas.emta.ee)")
    print(f"Filing deadline: 20th of the following month")


if __name__ == "__main__":
    main()
