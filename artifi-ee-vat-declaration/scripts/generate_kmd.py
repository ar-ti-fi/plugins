#!/usr/bin/env python3
"""
generate_kmd.py — Generate the Estonian VAT return (KMD) in the official KMD2 format.

Produces two artifacts for a single legal entity and period:

  1. KMD_YYYYMM_{REGCODE}.csv           — the KMD2 machine CSV (e-MTA's fixed-column
                                          upload format). **PRIMARY ARTIFACT.**
  2. vatDeclaration_YYYYMM_{REGCODE}.xml — the KMD2 XML: general part + main form
                                          (declarationBody) + KMD INF A/B annexes
                                          (salesAnnex / purchasesAnnex). Validated
                                          against the bundled vatdeclaration.xsd
                                          before it is written.

The KMD2 format is defined by e-MTA:
  Technical info : https://www.emta.ee/en/business-client/e-services-training-courses/how-use-e-services/technical-information-services
  XSD (07.2025+) : https://ncfailid.emta.ee/s/W5ncAiYRyye2of3/download/vatdeclaration.xsd
  Format desc.   : https://www.emta.ee/media/1096/download

Key facts (verified against the bundled XSD and e-MTA's own examples
`vatdeclaration_example6.csv` and the Hala `KMD_202606_14276473.csv`):

  * Root element `vatDeclaration`, NO XML namespace. The old
    `<KMD xmlns="http://emta.ee/schemas/vat">` output was fabricated and is gone.
  * General part order: taxPayerRegCode, submitterPersonCode (optional; required for
    the machine interface), year, month, declarationType (1=normal), version.
    `version` is period-dependent: KMD4 for 2024, KMD5 for 01.2025–06.2025,
    KMD6 from 07.2025 onward.
  * declarationBody holds taxable BASES by rate (transactions24 first, from 07.2025),
    plus zero-rated / EU / export bases, `inputVatTotal` (line 5, a VAT amount), the
    EU-acquisition / other-acquisition (reverse charge) bases, and adjustments. There
    are NO Line1_1 / Line4 / Line12 elements — e-MTA computes total VAT (line 4),
    VAT due (line 12) and overpaid (line 13) itself.
  * The machine CSV is a fixed-column, 31-field-per-row, semicolon-separated file with
    CRLF line endings, dot decimals and TRUE/FALSE flags. Row types: `header` (general
    part), the version row (declarationBody), `A` rows (salesAnnex saleLine), `B` rows
    (purchasesAnnex purchaseLine, dates as DD.MM.YYYY). It carries NO total-VAT or
    payable columns — do not emit them. This is NOT the English prose-header human
    export, which e-MTA rejects.

Reverse charge: e-MTA computes line 4 (total VAT) from SALES only
(24%×line1 + 9%×line2 + …); it does NOT add the self-assessed VAT on lines 6/7. For a
full-deduction taxpayer the reverse charge therefore nets out and must be declared ONLY
as the base in line 6 (`euAcquisitionsGoodsAndServicesTotal`, EU suppliers) or line 7
(`acquisitionOtherGoodsAndServicesTotal`, non-EU + domestic reverse charge) — do NOT
gross it into `inputVatTotal` (line 5), which is the deductible input VAT on
domestic/import purchases only. A partial/limited-deduction taxpayer must handle the
non-deductible reverse-charge output separately; this script warns when it cannot
assume 100% deduction (see `input_vat_full_deduction`).

Usage:
    python3 generate_kmd.py --input /tmp/kmd_data_14276473.json --output /tmp/

Input JSON format: see input_schema_kmd.json (real KMD2 element names).
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Bundled official schema, kept next to this script so validation works offline.
XSD_PATH = Path(__file__).resolve().parent / "vatdeclaration.xsd"

TOLERANCE = Decimal("0.02")

# declarationBody child elements in the exact order the XSD requires (and the exact
# order the machine CSV's 26 body columns use), omitting the obsolete selfSupply20 /
# selfSupply9. The two car-count fields are integers; everything else is a 2-decimal
# monetary value. This list is a strict subsequence of the XSD sequence, so emitting
# the present elements in this order is schema-valid.
BODY_ELEMENTS: List[str] = [
    "transactions24",                       # line 1   (24%, valid from 07.2025)
    "transactions22",                       # line 1   (22%)
    "transactions20",                       # line 1¹  (20%)
    "transactions9",                        # line 2   (9%)
    "transactions5",                        # line 2¹  (5%)
    "transactions13",                       # line 2²  (13%, valid from 01.2025)
    "transactionsZeroVat",                  # line 3   (0%)
    "euSupplyInclGoodsAndServicesZeroVat",  # line 3.1
    "euSupplyGoodsZeroVat",                 # line 3.1.1
    "exportZeroVat",                        # line 3.2
    "salePassengersWithReturnVat",          # line 3.2.1
    "inputVatTotal",                        # line 5   (total deductible input VAT)
    "importVat",                            # line 5.1 (import VAT paid in customs)
    "fixedAssetsVat",                       # line 5.2 (input VAT on fixed assets)
    "carsVat",                              # line 5.3 (input VAT on 100% cars)
    "numberOfCars",                         # line 5.3 (count, integer)
    "carsPartialVat",                       # line 5.4 (input VAT on partial cars)
    "numberOfCarsPartial",                  # line 5.4 (count, integer)
    "euAcquisitionsGoodsAndServicesTotal",  # line 6   (EU acquisitions + services)
    "euAcquisitionsGoods",                  # line 6.1
    "acquisitionOtherGoodsAndServicesTotal",# line 7   (non-EU services + reverse charge)
    "acquisitionImmovablesAndScrapMetalAndGold",  # line 7.1
    "supplyExemptFromTax",                  # line 8
    "supplySpecialArrangements",            # line 9
    "adjustmentsPlus",                      # line 10  (+ adjustment, non-negative)
    "adjustmentsMinus",                     # line 11  (- adjustment, non-negative)
]

INTEGER_ELEMENTS = {"numberOfCars", "numberOfCarsPartial"}
NON_NEGATIVE_ELEMENTS = {"adjustmentsPlus", "adjustmentsMinus"}

# Every machine-CSV row is padded to this many semicolon-separated fields.
CSV_FIELDS = 31

# Standard VAT rates that feed the computed "total VAT" (line 4) shown in the console
# summary. Reverse-charge lines (6 / 7) are intentionally NOT here: e-MTA's line 4 is
# domestic sales VAT only.
LINE4_RATES: Dict[str, Decimal] = {
    "transactions24": Decimal("0.24"),
    "transactions22": Decimal("0.22"),
    "transactions20": Decimal("0.20"),
    "transactions9":  Decimal("0.09"),
    "transactions5":  Decimal("0.05"),
    "transactions13": Decimal("0.13"),
}

REVERSE_CHARGE_BASE_ELEMENTS = (
    "euAcquisitionsGoodsAndServicesTotal",
    "acquisitionOtherGoodsAndServicesTotal",
)


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def dec(value) -> Decimal:
    """Coerce any input (None/str/number) to a Decimal, treating None/'' as 0."""
    if value is None or value == "":
        return Decimal("0")
    return Decimal(str(value))


def q2(value) -> Decimal:
    """Quantize to 2 decimals, half-up."""
    return dec(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def amount(value) -> str:
    """Monetary value: 2 decimals, dot separator (e.g. '910.00'). Used by CSV and XML."""
    return f"{q2(value):.2f}"


def esc(text) -> str:
    """Escape XML special characters."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def xml_flag(value: bool) -> str:
    return "true" if value else "false"


def csv_flag(value: bool) -> str:
    return "TRUE" if value else "FALSE"


def csv_date(value) -> str:
    """Convert an ISO date (YYYY-MM-DD, as the XML uses) to the CSV's DD.MM.YYYY."""
    text = str(value or "").strip()
    if not text:
        return ""
    parts = text.split("-")
    if len(parts) == 3 and len(parts[0]) == 4:
        year, month, day = parts
        return f"{int(day):02d}.{int(month):02d}.{year}"
    return text  # already DD.MM.YYYY or unrecognised — pass through unchanged


def compute_version(year: int, month: int) -> str:
    """
    Return the mandatory KMD2 version string for the given period.

    Per the XSD: KMD4 for 01.2024–12.2024, KMD5 for 01.2025–06.2025,
    KMD6 from 07.2025 onward.
    """
    period = year * 100 + month
    if period >= 202507:
        return "KMD6"
    if period >= 202501:
        return "KMD5"
    if period >= 202401:
        return "KMD4"
    raise ValueError(
        f"Period {year}-{month:02d} predates the KMD2 format (valid from 01.2024)"
    )


def compute_totals(body: dict) -> Dict[str, Decimal]:
    """
    Compute line 4 (total VAT), line 12 (VAT due) and line 13 (overpaid) the way e-MTA
    does — for the console summary only. These are NOT emitted in the CSV or XML.

    line 4  = Σ(base × rate) over the six domestic standard rates (SALES only; reverse
              charge on lines 6/7 is excluded).
    net     = line4 + adjustmentsPlus − inputVatTotal − adjustmentsMinus.
    line 12 = max(0, net)   (payable);  line 13 = max(0, −net)   (overpaid).
    """
    line4 = sum((q2(body.get(key, 0)) * rate for key, rate in LINE4_RATES.items()),
                Decimal("0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    net = (
        line4
        + q2(body.get("adjustmentsPlus", 0))
        - q2(body.get("inputVatTotal", 0))
        - q2(body.get("adjustmentsMinus", 0))
    )
    return {
        "_line4": line4,
        "_line12": max(Decimal("0"), net),
        "_line13": max(Decimal("0"), -net),
    }


# --------------------------------------------------------------------------- #
# Validation (structural; the XSD is the authority for the XML)
# --------------------------------------------------------------------------- #
def validate(data: dict) -> List[str]:
    """Validate input data structurally. Returns a list of error strings."""
    errors: List[str] = []

    if not data.get("regcode"):
        errors.append("regcode is required")
    if not data.get("year"):
        errors.append("year is required")
    month = data.get("month")
    if month is None or not (1 <= int(month) <= 12):
        errors.append("month is required and must be 1-12")
    elif data.get("year") and (int(data["year"]) * 100 + int(month)) < 202401:
        errors.append(
            f"period {data['year']}-{int(month):02d} predates the KMD2 format "
            "(valid from 01.2024)"
        )

    if int(data.get("declaration_type", 1)) not in (1, 2):
        errors.append("declaration_type must be 1 (normal) or 2 (bankruptcy)")

    body = data.get("declaration_body", {})
    if not isinstance(body, dict):
        errors.append("declaration_body must be an object")
        body = {}

    # No fabricated Line1_1/Line4/Line12 keys, and no removed importVatPayable field.
    stale = [k for k in body if k.lower().startswith("line") or k == "importVatPayable"]
    if stale:
        errors.append(
            "declaration_body uses removed keys "
            f"({', '.join(sorted(stale))}); use KMD2 element names "
            "(transactions24, inputVatTotal, …) — see input_schema_kmd.json"
        )

    unknown = [k for k in body if k not in BODY_ELEMENTS and not k.lower().startswith("line")
               and k != "importVatPayable"]
    if unknown:
        errors.append(
            f"declaration_body has unknown element(s): {', '.join(sorted(unknown))}"
        )

    for key in NON_NEGATIVE_ELEMENTS:
        if key in body and dec(body[key]) < 0:
            errors.append(f"declaration_body.{key} must be >= 0")

    if dec(body.get("euAcquisitionsGoods", 0)) - dec(
        body.get("euAcquisitionsGoodsAndServicesTotal", 0)
    ) > TOLERANCE:
        errors.append(
            "declaration_body.euAcquisitionsGoods (line 6.1) cannot exceed "
            "euAcquisitionsGoodsAndServicesTotal (line 6)"
        )

    errors += _validate_annex(data.get("sales_annex"), "sales_annex",
                              "buyerRegCode", "buyerName", "invoiceSum", "taxRate")
    errors += _validate_annex(data.get("purchases_annex"), "purchases_annex",
                              "sellerRegCode", "sellerName", "invoiceSumVat",
                              "vatInPeriod")
    return errors


def _validate_annex(annex, name, id_field, name_field, *required_fields) -> List[str]:
    """Validate a sales/purchases annex block. Empty/None annex is valid (omitted)."""
    errors: List[str] = []
    if not annex:
        return errors
    if not isinstance(annex, dict):
        return [f"{name} must be an object"]
    for i, line in enumerate(annex.get("lines", []) or []):
        prefix = f"{name}.lines[{i}]"
        if not line.get(id_field) and not line.get(name_field):
            errors.append(f"{prefix}: at least one of {id_field} / {name_field} is required")
        for field in required_fields:
            if line.get(field) in (None, ""):
                errors.append(f"{prefix}: {field} is required")
    return errors


def reverse_charge_warnings(data: dict) -> List[str]:
    """
    Return warnings (not errors) about reverse-charge handling. e-MTA does not add
    self-assessed VAT on lines 6/7 to line 4, so the netting only holds at 100% input
    deduction. Flag partial deduction loudly.
    """
    body = data.get("declaration_body", {}) or {}
    rc = sum((q2(body.get(k, 0)) for k in REVERSE_CHARGE_BASE_ELEMENTS), Decimal("0"))
    if rc <= 0:
        return []
    warnings = [
        f"Reverse-charge bases present (lines 6/7 total {rc:.2f}). e-MTA computes "
        "line 4 from sales only, so inputVatTotal (line 5) must be the deductible "
        "input VAT on domestic/import purchases ONLY — do not gross the reverse "
        "charge into it."
    ]
    if not bool(data.get("input_vat_full_deduction", True)):
        warnings.append(
            "input_vat_full_deduction is false: the reverse charge does NOT net out. "
            "The non-deductible portion of the self-assessed VAT is still payable and "
            "must be added (e.g. via adjustmentsPlus / line 10). Review before filing."
        )
    return warnings


# --------------------------------------------------------------------------- #
# XML generation
# --------------------------------------------------------------------------- #
def _body_xml(body: dict) -> List[str]:
    """Render the declarationBody child elements that carry a non-zero value."""
    out: List[str] = []
    for key in BODY_ELEMENTS:
        if key not in body or body[key] in (None, ""):
            continue
        if key in INTEGER_ELEMENTS:
            ival = int(dec(body[key]))
            if ival != 0:
                out.append(f"    <{key}>{ival}</{key}>")
        elif q2(body[key]) != 0:
            out.append(f"    <{key}>{amount(body[key])}</{key}>")
    return out


def _sales_annex_xml(annex: Optional[dict]) -> List[str]:
    """Render <salesAnnex> when partner lines exist, else nothing."""
    lines = (annex or {}).get("lines") or []
    if not lines:
        return []
    out = ["  <salesAnnex>"]
    for line in lines:
        out.append("    <saleLine>")
        if line.get("buyerRegCode"):
            out.append(f"      <buyerRegCode>{esc(line['buyerRegCode'])}</buyerRegCode>")
        if line.get("buyerName"):
            out.append(f"      <buyerName>{esc(line['buyerName'])}</buyerName>")
        if line.get("invoiceNumber"):
            out.append(f"      <invoiceNumber>{esc(line['invoiceNumber'])}</invoiceNumber>")
        if line.get("invoiceDate"):
            out.append(f"      <invoiceDate>{esc(line['invoiceDate'])}</invoiceDate>")
        out.append(f"      <invoiceSum>{amount(line.get('invoiceSum', 0))}</invoiceSum>")
        out.append(f"      <taxRate>{esc(line.get('taxRate', ''))}</taxRate>")
        if line.get("invoiceSumForRate") not in (None, ""):
            out.append(f"      <invoiceSumForRate>{amount(line['invoiceSumForRate'])}</invoiceSumForRate>")
        if line.get("sumForRateInPeriod") not in (None, ""):
            out.append(f"      <sumForRateInPeriod>{amount(line['sumForRateInPeriod'])}</sumForRateInPeriod>")
        if line.get("comments"):
            out.append(f"      <comments>{esc(line['comments'])}</comments>")
        out.append("    </saleLine>")
    out.append("  </salesAnnex>")
    return out


def _purchases_annex_xml(annex: Optional[dict]) -> List[str]:
    """Render <purchasesAnnex> when partner lines exist, else nothing."""
    lines = (annex or {}).get("lines") or []
    if not lines:
        return []
    out = ["  <purchasesAnnex>"]
    for line in lines:
        out.append("    <purchaseLine>")
        if line.get("sellerRegCode"):
            out.append(f"      <sellerRegCode>{esc(line['sellerRegCode'])}</sellerRegCode>")
        if line.get("sellerName"):
            out.append(f"      <sellerName>{esc(line['sellerName'])}</sellerName>")
        if line.get("invoiceNumber"):
            out.append(f"      <invoiceNumber>{esc(line['invoiceNumber'])}</invoiceNumber>")
        if line.get("invoiceDate"):
            out.append(f"      <invoiceDate>{esc(line['invoiceDate'])}</invoiceDate>")
        out.append(f"      <invoiceSumVat>{amount(line.get('invoiceSumVat', 0))}</invoiceSumVat>")
        if line.get("vatSum") not in (None, ""):
            out.append(f"      <vatSum>{amount(line['vatSum'])}</vatSum>")
        out.append(f"      <vatInPeriod>{amount(line.get('vatInPeriod', 0))}</vatInPeriod>")
        if line.get("comments"):
            out.append(f"      <comments>{esc(line['comments'])}</comments>")
        out.append("    </purchaseLine>")
    out.append("  </purchasesAnnex>")
    return out


def build_xml(data: dict) -> str:
    """Build the full vatDeclaration XML document as a string."""
    regcode = str(data["regcode"])
    year = int(data["year"])
    month = int(data["month"])
    dtype = int(data.get("declaration_type", 1))
    version = compute_version(year, month)
    body = data.get("declaration_body", {}) or {}
    sales = data.get("sales_annex")
    purchases = data.get("purchases_annex")
    has_sales = bool((sales or {}).get("lines"))
    has_purchases = bool((purchases or {}).get("lines"))

    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<vatDeclaration>",
        f"  <taxPayerRegCode>{esc(regcode)}</taxPayerRegCode>",
    ]
    if data.get("submitter_person_code"):
        out.append(
            f"  <submitterPersonCode>{esc(data['submitter_person_code'])}</submitterPersonCode>"
        )
    out += [
        f"  <year>{year}</year>",
        f"  <month>{month}</month>",
        f"  <declarationType>{dtype}</declarationType>",
        f"  <version>{version}</version>",
        "  <declarationBody>",
        f"    <noSales>{xml_flag(not has_sales)}</noSales>",
        f"    <noPurchases>{xml_flag(not has_purchases)}</noPurchases>",
        f"    <sumPerPartnerSales>{xml_flag((sales or {}).get('sum_per_partner', True) if has_sales else False)}</sumPerPartnerSales>",
        f"    <sumPerPartnerPurchases>{xml_flag((purchases or {}).get('sum_per_partner', True) if has_purchases else False)}</sumPerPartnerPurchases>",
    ]
    out += _body_xml(body)
    out.append("  </declarationBody>")
    out += _sales_annex_xml(sales)
    out += _purchases_annex_xml(purchases)
    out.append("</vatDeclaration>")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------- #
# CSV generation (KMD2 machine format — the primary artifact)
# --------------------------------------------------------------------------- #
def _row(fields: List[str]) -> str:
    """Pad a field list to CSV_FIELDS and join with ';'."""
    padded = list(fields) + [""] * (CSV_FIELDS - len(fields))
    return ";".join(padded[:CSV_FIELDS])


def _csv_body_value(body: dict, key: str) -> str:
    """Render one declarationBody value for the CSV — blank when zero/absent."""
    if key not in body or body[key] in (None, ""):
        return ""
    if key in INTEGER_ELEMENTS:
        ival = int(dec(body[key]))
        return str(ival) if ival != 0 else ""
    value = q2(body[key])
    return amount(value) if value != 0 else ""


def build_csv(data: dict) -> str:
    """
    Build the KMD2 machine CSV: fixed 31-field rows, semicolon-separated, dot decimals,
    TRUE/FALSE flags, CRLF line endings, no BOM. Row types:
      header;{reg};{submitter};{year};{month};{declarationType}   — general part
      {version};{noSales};{noPurchases};{sumSales};{sumPurch};<26 body values>  — main form
      A;{buyerReg};{buyerName};{invNo};{invDate};{sum};{rate};{sumForRate};{sumInPeriod};{comments}
      B;{sellerReg};{sellerName};{invNo};{invDate};{sumVat};{vatSum};{vatInPeriod};{comments}
    """
    regcode = str(data["regcode"])
    year = int(data["year"])
    month = int(data["month"])
    dtype = int(data.get("declaration_type", 1))
    version = compute_version(year, month)
    submitter = str(data.get("submitter_person_code") or "")
    body = data.get("declaration_body", {}) or {}
    sales = data.get("sales_annex")
    purchases = data.get("purchases_annex")
    has_sales = bool((sales or {}).get("lines"))
    has_purchases = bool((purchases or {}).get("lines"))

    rows: List[str] = [
        _row(["header", regcode, submitter, str(year), str(month), str(dtype)]),
        _row(
            [
                version,
                csv_flag(not has_sales),
                csv_flag(not has_purchases),
                csv_flag((sales or {}).get("sum_per_partner", True) if has_sales else False),
                csv_flag((purchases or {}).get("sum_per_partner", True) if has_purchases else False),
            ]
            + [_csv_body_value(body, key) for key in BODY_ELEMENTS]
        ),
    ]

    for line in (sales or {}).get("lines") or []:
        rows.append(_row([
            "A",
            str(line.get("buyerRegCode", "") or ""),
            str(line.get("buyerName", "") or ""),
            str(line.get("invoiceNumber", "") or ""),
            csv_date(line.get("invoiceDate")),
            amount(line.get("invoiceSum", 0)),
            str(line.get("taxRate", "") or ""),
            amount(line["invoiceSumForRate"]) if line.get("invoiceSumForRate") not in (None, "") else "",
            amount(line["sumForRateInPeriod"]) if line.get("sumForRateInPeriod") not in (None, "") else "",
            str(line.get("comments", "") or ""),
        ]))

    for line in (purchases or {}).get("lines") or []:
        rows.append(_row([
            "B",
            str(line.get("sellerRegCode", "") or ""),
            str(line.get("sellerName", "") or ""),
            str(line.get("invoiceNumber", "") or ""),
            csv_date(line.get("invoiceDate")),
            amount(line.get("invoiceSumVat", 0)),
            amount(line["vatSum"]) if line.get("vatSum") not in (None, "") else "",
            amount(line.get("vatInPeriod", 0)),
            str(line.get("comments", "") or ""),
        ]))

    return "".join(row + "\r\n" for row in rows)


# --------------------------------------------------------------------------- #
# XSD validation
# --------------------------------------------------------------------------- #
def validate_xml_against_xsd(xml_text: str) -> Tuple[bool, str]:
    """
    Validate the XML against the bundled XSD using xmllint.

    Returns (ok, message). If xmllint is not installed, returns (True, warning) so the
    tool still runs in minimal environments. A genuine schema violation returns
    (False, errors).
    """
    if not XSD_PATH.exists():
        return False, f"bundled schema not found at {XSD_PATH}"
    with tempfile.NamedTemporaryFile(
        "w", suffix=".xml", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(xml_text)
        tmp_path = tmp.name
    try:
        proc = subprocess.run(
            ["xmllint", "--noout", "--schema", str(XSD_PATH), tmp_path],
            capture_output=True, text=True,
        )
    except FileNotFoundError:
        Path(tmp_path).unlink(missing_ok=True)
        return True, ("WARNING: xmllint not found — XSD validation skipped. "
                      "Install libxml2 (brew install libxml2) to validate output.")
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if proc.returncode == 0:
        return True, "validates against vatdeclaration.xsd"
    return False, (proc.stderr or proc.stdout or "unknown xmllint error").strip()


# --------------------------------------------------------------------------- #
# Output-format self-check (validation gate — check 1, BLOCK)
# --------------------------------------------------------------------------- #
_NUMERIC_RE = re.compile(r"^$|^\d+$|^-?\d+\.\d{2}$")  # empty | integer | 2-decimal (dot)


def _numeric_ok(value: str) -> bool:
    """A CSV monetary/count field must be empty, an integer, or a 2-decimal dot value."""
    return bool(_NUMERIC_RE.match(value))


def self_check_csv(csv_text: str, version: str) -> List[str]:
    """
    Mechanically re-validate the generated CSV against e-MTA's fixed-column spec, so a
    malformed file never leaves the desk. Returns a list of BLOCK error strings.
    """
    errors: List[str] = []

    if not csv_text.endswith("\r\n"):
        errors.append("CSV must use CRLF line endings and end with CRLF")
    if "﻿" in csv_text:
        errors.append("CSV must not contain a BOM")

    rows = [r for r in csv_text.split("\r\n") if r != ""]
    if len(rows) < 2:
        errors.append("CSV must have at least the header and declarationBody rows")
        return errors

    for i, row in enumerate(rows, start=1):
        fields = row.split(";")
        if len(fields) != CSV_FIELDS:
            errors.append(
                f"CSV row {i} has {len(fields)} fields, expected {CSV_FIELDS} "
                "(an embedded ';' in a name/number corrupts the fixed-column layout)"
            )

    header = rows[0].split(";")
    if header[0] != "header":
        errors.append(f"CSV row 1 must start with 'header', got '{header[0]}'")

    body = rows[1].split(";")
    if body and body[0] != version:
        errors.append(f"CSV row 2 version is '{body[0]}', expected '{version}'")
    for idx in range(1, 5):  # noSales, noPurchases, sumPerPartnerSales, sumPerPartnerPurchases
        if len(body) > idx and body[idx] not in ("TRUE", "FALSE"):
            errors.append(f"CSV row 2 flag {idx} is '{body[idx]}', expected TRUE/FALSE")
    for idx in range(5, len(body)):  # the 26 declarationBody values
        if not _numeric_ok(body[idx]):
            errors.append(
                f"CSV row 2 body value {idx - 4} ('{body[idx]}') is not a dot-decimal "
                "amount (a comma decimal or a stray total-VAT column would land here)"
            )

    # Annex rows: check the monetary positions use dot decimals.
    monetary_positions = {"A": (5, 7, 8), "B": (5, 6, 7)}
    for i, row in enumerate(rows[2:], start=3):
        fields = row.split(";")
        kind = fields[0]
        if kind not in monetary_positions:
            errors.append(f"CSV row {i} has unknown row type '{kind}' (expected A or B)")
            continue
        for pos in monetary_positions[kind]:
            if pos < len(fields) and not _numeric_ok(fields[pos]):
                errors.append(f"CSV row {i} field {pos + 1} ('{fields[pos]}') is not a dot-decimal amount")

    return errors


def self_check_totals(data: dict) -> List[str]:
    """
    Recompute the derived figures and, when the caller supplies an expected value,
    assert the return agrees (check 1 + check 7). Returns BLOCK error strings.
    """
    errors: List[str] = []
    totals = compute_totals(data.get("declaration_body", {}) or {})

    if totals["_line12"] > 0 and totals["_line13"] > 0:
        errors.append(
            f"line 12 (payable {totals['_line12']:.2f}) and line 13 "
            f"(overpaid {totals['_line13']:.2f}) cannot both be non-zero"
        )

    expected_payable = data.get("expected_vat_payable")
    if expected_payable is not None and abs(q2(expected_payable) - totals["_line12"]) > TOLERANCE:
        errors.append(
            f"computed VAT payable (line 12) {totals['_line12']:.2f} does not match the "
            f"expected {q2(expected_payable):.2f} — recheck the bases / inputVatTotal"
        )
    expected_overpaid = data.get("expected_vat_overpaid")
    if expected_overpaid is not None and abs(q2(expected_overpaid) - totals["_line13"]) > TOLERANCE:
        errors.append(
            f"computed VAT overpaid (line 13) {totals['_line13']:.2f} does not match the "
            f"expected {q2(expected_overpaid):.2f} — recheck the bases / inputVatTotal"
        )
    return errors


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the Estonian VAT return (KMD2 machine CSV + vatDeclaration XML)"
    )
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", default=".", help="Output directory (default: .)")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as fh:
        data = json.load(fh)

    errors = validate(data)
    if errors:
        print("VALIDATION ERRORS:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    regcode = str(data["regcode"])
    year = int(data["year"])
    month = int(data["month"])
    stem = f"{year}{month:02d}_{regcode}"

    # Build both artifacts, then run the output-format gate (check 1) BEFORE writing
    # anything. Any BLOCK error means no files are written — a malformed declaration
    # never reaches e-MTA.
    version = compute_version(year, month)
    xml_text = build_xml(data)
    csv_text = build_csv(data)

    xsd_ok, xsd_message = validate_xml_against_xsd(xml_text)
    block: List[str] = []
    if not xsd_ok:
        block.append(f"XML does not validate against vatdeclaration.xsd: {xsd_message}")
    block += self_check_csv(csv_text, version)
    block += self_check_totals(data)
    if block:
        print("OUTPUT-FORMAT GATE FAILED (BLOCK) — no files written:", file=sys.stderr)
        for err in block:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)
    message = xsd_message

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"KMD_{stem}.csv"
    xml_path = output_dir / f"vatDeclaration_{stem}.xml"
    # CSV: bytes, no BOM, CRLF already embedded. XML: UTF-8.
    csv_path.write_bytes(csv_text.encode("utf-8"))
    xml_path.write_text(xml_text, encoding="utf-8")

    body = data.get("declaration_body", {}) or {}
    totals = compute_totals(body)
    print(f"Generated (PRIMARY):   {csv_path}")
    print(f"Generated (secondary): {xml_path}")
    print(f"Format gate: PASS ({message}; CSV 31-field rows, dot decimals, TRUE/FALSE, CRLF)")
    print(f"\nKMD {year}/{month:02d} — reg code {regcode} (version {version})")
    print(f"  Total VAT   (line 4):  EUR {totals['_line4']:.2f}  [computed by e-MTA]")
    print(f"  Input VAT   (line 5):  EUR {q2(body.get('inputVatTotal', 0)):.2f}")
    if totals["_line12"] > 0:
        print(f"  VAT PAYABLE (line 12): EUR {totals['_line12']:.2f}  [computed by e-MTA]")
    elif totals["_line13"] > 0:
        print(f"  VAT OVERPAID(line 13): EUR {totals['_line13']:.2f}  [computed by e-MTA]")
    else:
        print("  Net VAT: EUR 0.00")

    for warning in reverse_charge_warnings(data):
        print(f"\nNOTE: {warning}")

    print("\nUpload the CSV at maasikas.emta.ee (or the XML). Deadline: 20th of next month.")


if __name__ == "__main__":
    main()
