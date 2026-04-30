#!/usr/bin/env python3
"""generate_tsd.py — Estonian TSD (monthly tax declaration) XML generator for e-MTA.

Implements the real e-MTA XSD (tsd_schema_01.01.2025_eng.xsd):
  - Root <tsd_vorm> (NO namespace)
  - Element naming c{NNN}_{EstonianFieldName}
  - Mandatory <vorm>TSD</vorm>
  - <laadimisViis>P</laadimisViis> (default: amend existing in-progress declaration)
  - Annex 1 (<tsd_L1_0>) with <aIsikList> → <tsd_L1_A_Isik> →
      <vmList> → <tsd_L1_A_Vm> → optional <mvtList> → <tsd_L1_A_Mvt>

Scope:
  R2 — Annex 1 (resident salaries + board fees) [DONE]
  R3 — Annex 4 (fringe benefits) + Annex 5 (gifts/donations/entertainment) [DONE]
  R4 — Annex 2 (non-resident natural persons + non-resident companies) [DONE]
  R5 — Annex 7 (dividends + equity distributions) + INF1 (annual companion form) [DONE]
  Deferred:
    Annex 3 — corporate income tax / investment income carry-forward (rare)
    Annex 6 — transfer-pricing adjustments / fines / bribes (rare)
    Annex 8 — tonnage tax (shipping companies only)

Usage:
    python3 generate_tsd.py --input /tmp/tsd_data.json --output /tmp/

Input JSON format: see input_schema_tsd.json for full schema. Values may be either
pre-calculated by the caller (typical case from the ERP-driven /generate-tsd flow) or
left out, in which case this generator computes header roll-ups and Annex 1 totals
from the per-payment rows.
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

# --- Tax rates (single source of truth) ----------------------------------
SOCIAL_TAX_RATE = Decimal("0.33")  # employer 33%
INCOME_TAX_RATE = Decimal("0.22")  # employee 22%

TOLERANCE = Decimal("0.02")
ROUND_2 = Decimal("0.01")


def D(value) -> Decimal:
    """Coerce value to Decimal."""
    if value is None or value == "":
        return Decimal("0")
    return Decimal(str(value))


def fmt(value) -> str:
    """Format a numeric value as a 2-decimal string (matches XSD fractionDigits=2)."""
    if value is None:
        return ""
    return str(D(value).quantize(ROUND_2, rounding=ROUND_HALF_UP))


def esc(s: Any) -> str:
    """Escape XML special characters in a text value."""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


# --- Validation -----------------------------------------------------------

class ValidationError(Exception):
    """Aggregates validation errors so the caller can show them all at once."""

    def __init__(self, errors: List[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


def validate(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if not data.get("regcode"):
        errors.append("regcode is required")
    if not data.get("year"):
        errors.append("year is required")
    month = data.get("month")
    if not month or not (1 <= int(month) <= 12):
        errors.append("month is required and must be 1-12")

    load_mode = data.get("load_mode", "P")
    if load_mode not in ("L", "P"):
        errors.append("load_mode must be 'L' (new) or 'P' (amend, default)")

    persons = data.get("persons") or []
    non_resident_persons = data.get("non_resident_persons") or []
    if not persons and not non_resident_persons:
        errors.append("At least one person is required (in 'persons' or 'non_resident_persons')")

    for i, person in enumerate(persons):
        prefix = f"persons[{i}]({person.get('personal_id') or '?'})"

        if not person.get("personal_id"):
            errors.append(f"{prefix}: personal_id is required")
        if not person.get("full_name"):
            errors.append(f"{prefix}: full_name is required")

        payments = person.get("payments") or []
        if not payments:
            errors.append(f"{prefix}: at least one payment row is required")
            continue

        for j, p in enumerate(payments):
            ppfx = f"{prefix}.payments[{j}]"
            if not p.get("payment_type_code"):
                errors.append(f"{ppfx}: payment_type_code (c1020_ValiKood) is required")
            if D(p.get("gross")) <= 0:
                errors.append(f"{ppfx}: gross (c1030_Summa) must be > 0")

            # Cross-check: social_tax should equal social_tax_base × 33% (within tolerance)
            stb = D(p.get("social_tax_base", p.get("gross", 0)))
            st = D(p.get("social_tax", 0))
            if stb > 0 and abs(st - stb * SOCIAL_TAX_RATE) > TOLERANCE:
                errors.append(
                    f"{ppfx}: social_tax {fmt(st)} differs from {fmt(stb)} × 33% = "
                    f"{fmt(stb * SOCIAL_TAX_RATE)} by more than {TOLERANCE}"
                )

            # Cross-check: income_tax = (gross − combined_kp − Σmvt amounts) × 22%
            gross = D(p.get("gross", 0))
            kp = D(p.get("combined_kp", 0))
            exempt_total = sum((D(m.get("amount", 0)) for m in (p.get("tax_free_items") or [])), Decimal("0"))
            expected_tm = (gross - kp - exempt_total) * INCOME_TAX_RATE
            if expected_tm < 0:
                expected_tm = Decimal("0")
            it = D(p.get("income_tax", 0))
            if abs(it - expected_tm) > TOLERANCE:
                errors.append(
                    f"{ppfx}: income_tax {fmt(it)} differs from "
                    f"({fmt(gross)} − {fmt(kp)} − {fmt(exempt_total)}) × 22% = {fmt(expected_tm)} "
                    f"by more than {TOLERANCE}"
                )

    # Annex 2 — non-resident persons. Looser than Annex 1: tax-treaty rates can vary
    # (10%, 20%, 0%) so we don't enforce a fixed income-tax cross-check; we just
    # require c2020_RiikKood (residency) + payment_type_code + gross.
    for i, person in enumerate(non_resident_persons):
        prefix = f"non_resident_persons[{i}]({person.get('personal_id') or '?'})"
        if not person.get("personal_id"):
            errors.append(f"{prefix}: personal_id is required")
        if not person.get("full_name"):
            errors.append(f"{prefix}: full_name is required")

        payments = person.get("payments") or []
        if not payments:
            errors.append(f"{prefix}: at least one payment row is required")
            continue
        for j, p in enumerate(payments):
            ppfx = f"{prefix}.payments[{j}]"
            if not p.get("country_of_residence"):
                errors.append(f"{ppfx}: country_of_residence (c2020_RiikKood) is required for non-resident persons")
            if not p.get("payment_type_code"):
                errors.append(f"{ppfx}: payment_type_code (c2030_ValiKood) is required")
            if D(p.get("gross")) <= 0:
                errors.append(f"{ppfx}: gross (c2040_Summa) must be > 0")

    return errors


# --- XML rendering --------------------------------------------------------

def _emit_decimal(name: str, value, indent: str, lines: List[str], optional: bool = True,
                  emit_zero: bool = False) -> None:
    """Emit a decimal element. Skip if optional + (None/empty or zero unless emit_zero)."""
    if value is None or value == "":
        if optional:
            return
        value = 0
    if optional and not emit_zero and D(value) == 0:
        return
    lines.append(f"{indent}<{name}>{fmt(value)}</{name}>")


def _emit_string(name: str, value, indent: str, lines: List[str], optional: bool = True) -> None:
    """Emit a string element; skip if optional and value is empty."""
    if value is None or value == "":
        if optional:
            return
        return
    lines.append(f"{indent}<{name}>{esc(value)}</{name}>")


def _render_mvt(mvt: Dict[str, Any], indent: str) -> List[str]:
    """Render a single tsd_L1_A_Mvt sub-record."""
    out: List[str] = []
    out.append(f"{indent}<tsd_L1_A_Mvt>")
    _emit_string("c1150_TuliKood", mvt["code"], indent + "  ", out, optional=False)
    _emit_decimal("c1160_Summa", mvt["amount"], indent + "  ", out, optional=False)
    out.append(f"{indent}</tsd_L1_A_Mvt>")
    return out


def _render_vm(payment: Dict[str, Any], indent: str) -> List[str]:
    """Render one tsd_L1_A_Vm payment row."""
    out: List[str] = []
    out.append(f"{indent}<tsd_L1_A_Vm>")
    inner = indent + "  "

    _emit_string("c1020_ValiKood", payment["payment_type_code"], inner, out, optional=False)
    _emit_decimal("c1030_Summa", payment["gross"], inner, out, optional=False)
    _emit_string("c1050_RiikKood", payment.get("a1_certificate_country"), inner, out)

    # social tax base (defaults to gross)
    smvm = payment.get("social_tax_base", payment["gross"])
    _emit_decimal("c1060_Smvm", smvm, inner, out)
    _emit_decimal("c1070_TvpVah", payment.get("incapacity_pension_deducted"), inner, out)
    _emit_decimal("c1080_KuumVah", payment.get("monthly_rate_already_taxed"), inner, out)
    _emit_decimal("c1090_KuumSuur", payment.get("minimum_obligation_increase"), inner, out)
    _emit_decimal("c1100_Sm", payment.get("social_tax"), inner, out)
    _emit_decimal("c1110_Kp", payment.get("combined_kp"), inner, out)  # pension + unemp_employee combined
    _emit_decimal("c1120_Tkvm", payment.get("unemployment_base"), inner, out)
    _emit_decimal("c1130_Tk", payment.get("unemployment_employee"), inner, out)
    _emit_decimal("c1140_Ttk", payment.get("unemployment_employer"), inner, out)
    _emit_decimal("c1170_Tm", payment.get("income_tax"), inner, out)

    mvts = payment.get("tax_free_items") or []
    if mvts:
        out.append(f"{inner}<mvtList>")
        for mvt in mvts:
            out.extend(_render_mvt(mvt, inner + "  "))
        out.append(f"{inner}</mvtList>")

    out.append(f"{indent}</tsd_L1_A_Vm>")
    return out


def _render_isik(person: Dict[str, Any], indent: str) -> List[str]:
    out: List[str] = []
    out.append(f"{indent}<tsd_L1_A_Isik>")
    inner = indent + "  "
    _emit_string("c1000_Kood", person["personal_id"], inner, out, optional=False)
    _emit_string("c1010_Nimi", person["full_name"], inner, out, optional=False)
    out.append(f"{inner}<vmList>")
    for payment in person["payments"]:
        out.extend(_render_vm(payment, inner + "  "))
    out.append(f"{inner}</vmList>")
    out.append(f"{indent}</tsd_L1_A_Isik>")
    return out


def _sum(payments: Iterable[Dict[str, Any]], key: str) -> Decimal:
    total = Decimal("0")
    for p in payments:
        total += D(p.get(key, 0))
    return total


def _compute_annex1_totals(persons: List[Dict[str, Any]]) -> Dict[str, Decimal]:
    """Compute Annex 1 roll-ups from all payment rows under all persons."""
    all_payments = [p for person in persons for p in (person.get("payments") or [])]
    return {
        "c1200_Smvm": _sum(all_payments, "social_tax_base") or _sum(all_payments, "gross"),
        "c1210_Sm":   _sum(all_payments, "social_tax"),
        "c1220_Kp":   _sum(all_payments, "combined_kp"),
        "c1230_Tk":   _sum(all_payments, "unemployment_employee"),
        "c1240_Ttk":  _sum(all_payments, "unemployment_employer"),
        "c1250_Tm":   _sum(all_payments, "income_tax"),
    }


def _compute_header_totals(
    annex_totals: Dict[str, Decimal],
    annex2_totals: Optional[Dict[str, Decimal]] = None,
    annex4: Optional[Dict[str, Any]] = None,
    annex5: Optional[Dict[str, Any]] = None,
    annex7: Optional[Dict[str, Any]] = None,
) -> Dict[str, Decimal]:
    """Compute header c110-c119 from Annex totals across all annexes.

    Annex 6 + 8 are deferred. Current contributions:
      c110_Tm   = Annex 1 c1250 + Annex 2 c2250 + Annex 7 c7200 (income tax incl. dividend tax)
      c114_TmEj = Annex 4 c4170 + Annex 5 c5160 + c5190 (special income tax — fringe + entertainment)
      c115_Sm   = Annex 1 c1210 + Annex 2 c2210 + Annex 4 c4180 + Annex 7 c7050 (social tax incl. equity-distribution)
      c116_Tk   = Annex 1 (c1230 + c1240) + Annex 2 (c2220 + c2230) — unemployment insurance
      c117_Kp   = Annex 1 c1220 — funded pension (Annex 2 funded-pension is a separate column not in 1A subsection)
    """
    a2 = annex2_totals or {}
    a4 = annex4 or {}
    a5 = annex5 or {}
    a7 = annex7 or {}

    c110 = (
        annex_totals["c1250_Tm"]
        + D(a2.get("c2250_Tm", 0))
        + D(a7.get("payable_income_tax", 0))   # c7200_TasutavTm
    )
    # Annex input dicts use the input-key names (e.g. "special_income_tax") which are
    # mapped to c-code element names in ANNEX_4_FIELDS / ANNEX_5_FIELDS. Read by
    # input-key, not by c-code, so this stays in sync with the renderers.
    c114 = (
        D(a4.get("special_income_tax", 0))         # c4170_TmEj
        + D(a5.get("special_income_tax_payable", 0)) # c5160_TasTmEj
        + D(a5.get("other_special_income_tax", 0))   # c5190_TmEj
    )
    c115 = (
        annex_totals["c1210_Sm"]
        + D(a2.get("c2210_Sm", 0))
        + D(a4.get("social_tax", 0))
        + D(a7.get("equity_social_tax_corrected", 0))   # c7050_OmakapSmKorrig
    )
    c116 = (
        annex_totals["c1230_Tk"] + annex_totals["c1240_Ttk"]
        + D(a2.get("c2220_Tk", 0)) + D(a2.get("c2230_Ttk", 0))
    )
    c117 = annex_totals["c1220_Kp"]
    obligation = c110 + c114 + c115 + c116 + c117
    if obligation >= 0:
        c118, c119 = obligation, Decimal("0")
    else:
        c118, c119 = Decimal("0"), -obligation
    return {
        "c110_Tm":         c110,
        "c114_TmEj":       c114,
        "c115_Sm":         c115,
        "c116_Tk":         c116,
        "c117_Kp":         c117,
        "c118_KohustKokku": c118,
        "c119_TagastKokku": c119,
    }


# --- Annex 4 (fringe benefits) -------------------------------------------

# Map of input-key → c-code for Annex 4 scalars (in canonical filing order).
# Caller passes the raw amounts; generator emits one element per non-null entry.
ANNEX_4_FIELDS = [
    ("accommodation",           "c4000_ElKulu"),
    ("insurance_premium",       "c4010_KiKulu"),
    ("personal_car_above",      "c4030_Is"),
    ("company_vehicle",         "c4040_Ts"),
    ("other_property",          "c4050_Mv"),
    ("below_market_loan",       "c4060_SoLaen"),
    ("market_interest",         "c4061_TuruIntr"),
    ("loan_agreement_interest", "c4062_LaenIntr"),
    ("below_market_transfer",   "c4070_AllaTh"),
    ("market_price",            "c4071_Th"),
    ("applied_price",           "c4072_Rh"),
    ("ownership_transfer",      "c4080_OoTulu"),
    ("ownership_market_price",  "c4081_OoTh"),
    ("ownership_paid_price",    "c4082_ORh"),
    ("ownership_balance_value", "c4083_Op"),
    ("general_market_value",    "c4090_YleTh"),
    ("general_applied_price",   "c4091_Rh"),
    ("general_market_diff",     "c4092_Th"),
    ("waived_claim",            "c4100_LoobuRn"),
    ("training_expense",        "c4110_KoKulu"),
    ("other_expense",           "c4120_TeKulu"),
    ("non_specific_value",      "c4130_MEs"),
    ("representation_amount",   "c4140_EsSumma"),
    ("exempt_income_tax",       "c4150_EiTm"),
    ("exempt_social_tax",       "c4160_EiSm"),
    ("special_income_tax",      "c4170_TmEj"),
    ("social_tax",              "c4180_Sm"),
    ("social_tax_base",         "c4181_SmEs"),
]


def _render_annex4(annex4: Optional[Dict[str, Any]], indent: str) -> List[str]:
    """Emit <tsd_L4_0> if any Annex 4 fields are populated."""
    if not annex4:
        return []
    # Collect only the fields the caller provided
    populated = [(c_code, annex4.get(key)) for key, c_code in ANNEX_4_FIELDS
                 if annex4.get(key) is not None]
    if not populated:
        return []

    out: List[str] = [f"{indent}<tsd_L4_0>"]
    inner = indent + "    "
    for c_code, value in populated:
        out.append(f"{inner}<{c_code}>{fmt(value)}</{c_code}>")
    out.append(f"{indent}</tsd_L4_0>")
    return out


# --- Annex 5 (gifts/donations/entertainment) -----------------------------

# Map of input-key → c-code for Annex 5 scalars (in canonical filing order).
ANNEX_5_FIELDS = [
    ("general_gifts",                  "c5000_Ki"),
    ("listed_charity_month",           "c5010_IKiKuu"),
    ("listed_charity_year",            "c5020_IKiAasta"),
    ("personalized_distributions",     "c5030_IIsmv"),
    ("annual_profit",                  "c5040_IKasSumma"),
    ("ten_percent_threshold",          "c5050_10Prots"),
    ("listed_charity_taxable",         "c5060_IMs"),
    ("listed_charity_income_tax",      "c5070_ITm"),
    ("listed_charity_payable_tax",     "c5080_ITasTm"),
    ("listed_charity_refundable_tax",  "c5090_ITagTm"),
    ("entertainment_month",            "c5100_KyKuluKuu"),
    ("entertainment_year",             "c5110_KyKuluAasta"),
    ("entertainment_threshold",        "c5120_KyIsmv"),
    ("entertainment_income_tax",       "c5130_KyTm"),
    ("entertainment_payable_tax",      "c5140_KyTasTm"),
    ("entertainment_refundable_tax",   "c5150_KyTagTm"),
    ("special_income_tax_payable",     "c5160_TasTmEj"),
    ("special_income_tax_refundable",  "c5170_TagTmEj"),
    ("other_taxable",                  "c5180_MaKi"),
    ("other_special_income_tax",       "c5190_TmEj"),
    ("year_total_giving",              "c5220_TonnKiKokku"),
]


def _render_annex5(annex5: Optional[Dict[str, Any]], indent: str) -> List[str]:
    """Emit <tsd_L5_0> if any Annex 5 fields are populated."""
    if not annex5:
        return []
    populated = [(c_code, annex5.get(key)) for key, c_code in ANNEX_5_FIELDS
                 if annex5.get(key) is not None]
    if not populated:
        return []

    out: List[str] = [f"{indent}<tsd_L5_0>"]
    inner = indent + "    "
    for c_code, value in populated:
        out.append(f"{inner}<{c_code}>{fmt(value)}</{c_code}>")
    out.append(f"{indent}</tsd_L5_0>")
    return out


# --- Annex 2 (non-resident natural persons + non-resident companies) ----
# Mirrors Annex 1 with c2xxx codes. Per-person row supports per-country
# residency, A1/E101 social-security certificates, and tax-treaty rate.

def _render_annex2_mvt(mvt: Dict[str, Any], indent: str) -> List[str]:
    """Render a single tsd_L2_A_Mvt sub-record (tax-free amount)."""
    out: List[str] = []
    out.append(f"{indent}<tsd_L2_A_Mvt>")
    _emit_string("c2154_TuliKood", mvt["code"], indent + "  ", out, optional=False)
    _emit_decimal("c2155_Summa",   mvt["amount"], indent + "  ", out, optional=False)
    out.append(f"{indent}</tsd_L2_A_Mvt>")
    return out


def _render_annex2_vm(payment: Dict[str, Any], indent: str) -> List[str]:
    """Render one tsd_L2_A_Vm payment row."""
    out: List[str] = []
    out.append(f"{indent}<tsd_L2_A_Vm>")
    inner = indent + "  "

    # Recipient's country of residence (mandatory for non-residents)
    _emit_string("c2020_RiikKood",   payment.get("country_of_residence"), inner, out, optional=False)
    # Distribution type (e.g. 120 for non-resident service, 21 for non-resident board fee)
    _emit_string("c2030_ValiKood",   payment["payment_type_code"], inner, out, optional=False)
    _emit_decimal("c2040_Summa",     payment["gross"], inner, out, optional=False)

    # A1/E101 social-security certificate country (optional)
    _emit_string("c2060_RiikKood",   payment.get("a1_certificate_country"), inner, out)

    # Calculated bases + taxes
    _emit_decimal("c2070_Smvm",      payment.get("social_tax_base"),         inner, out)
    _emit_decimal("c2080_TvpVah",    payment.get("incapacity_pension_deducted"), inner, out)
    _emit_decimal("c2090_KuumVah",   payment.get("monthly_rate_already_taxed"),  inner, out)
    _emit_decimal("c2100_KuumSuur",  payment.get("minimum_obligation_increase"), inner, out)
    _emit_decimal("c2110_Sm",        payment.get("social_tax"),              inner, out)
    _emit_decimal("c2120_Tkvm",      payment.get("unemployment_base"),       inner, out)
    _emit_decimal("c2130_Tk",        payment.get("unemployment_employee"),   inner, out)
    _emit_decimal("c2140_Ttk",       payment.get("unemployment_employer"),   inner, out)
    _emit_decimal("c2150_Tmvm",      payment.get("income_tax_base"),         inner, out)
    # Income tax rate — Estonia standard 22%, treaty rates may apply (10%/0%)
    _emit_decimal("c2160_TmMaar",    payment.get("income_tax_rate"),         inner, out)
    _emit_decimal("c2170_Tm",        payment.get("income_tax"),              inner, out)

    mvts = payment.get("tax_free_items") or []
    if mvts:
        out.append(f"{inner}<mvtList>")
        for mvt in mvts:
            out.extend(_render_annex2_mvt(mvt, inner + "  "))
        out.append(f"{inner}</mvtList>")

    out.append(f"{indent}</tsd_L2_A_Vm>")
    return out


def _render_annex2_isik(person: Dict[str, Any], indent: str) -> List[str]:
    out: List[str] = []
    out.append(f"{indent}<tsd_L2_A_Isik>")
    inner = indent + "  "
    _emit_string("c2000_Kood", person["personal_id"], inner, out, optional=False)
    _emit_string("c2010_Nimi", person["full_name"],   inner, out, optional=False)
    out.append(f"{inner}<vmList>")
    for payment in person["payments"]:
        out.extend(_render_annex2_vm(payment, inner + "  "))
    out.append(f"{inner}</vmList>")
    out.append(f"{indent}</tsd_L2_A_Isik>")
    return out


def _compute_annex2_totals(non_resident_persons: List[Dict[str, Any]]) -> Dict[str, Decimal]:
    """Compute Annex 2 (1A subsection) roll-ups."""
    all_payments = [p for person in non_resident_persons for p in (person.get("payments") or [])]
    return {
        "c2200_Smvm": _sum(all_payments, "social_tax_base"),
        "c2210_Sm":   _sum(all_payments, "social_tax"),
        "c2220_Tk":   _sum(all_payments, "unemployment_employee"),
        "c2230_Ttk":  _sum(all_payments, "unemployment_employer"),
        "c2240_Tmvm": _sum(all_payments, "income_tax_base"),
        "c2250_Tm":   _sum(all_payments, "income_tax"),
    }


# --- Annex 7 (dividends + equity distributions) -------------------------

ANNEX_7_FIELDS = [
    ("dividends_total",                 "c7008_DivKokku"),
    ("dividends_lower_rate",            "c7009_DivMadal"),
    ("distribution_taxable",            "c7010_VmMaksust"),
    ("distribution_central_total",      "c7012_VmKeSum"),
    ("exit_tax",                        "c7014_Lahkumismaks"),
    ("cfc_income",                      "c7016_Cfc"),
    ("equity_social_tax_pre2015",       "c7020_OmakapSmEnne2015"),
    ("tonnage_dividends_total",         "c7022_TonnDivKokku"),
    ("equity_social_tax",               "c7030_OmakapSm"),
    ("equity_social_tax_total",         "c7040_OmakapSmKokku"),
    ("equity_social_tax_corrected",     "c7050_OmakapSmKorrig"),
    ("equity_distribution",             "c7060_OmakapVm"),
    ("equity_unpaid",                   "c7070_OmakapValjamaksmata"),
    ("distribution_above_st_taxable",   "c7080_VmYleSmMaksust"),
    ("foreign_tax_paid",                "c7160_VrTasutudTm"),
    ("foreign_tax_paid_corrected",      "c7170_VrTasutudTmKorrig"),
    ("foreign_tax_credit_used",         "c7180_VrVahendus"),
    ("foreign_tax_credit_unused",       "c7190_VrVmTmKasutamata"),
    ("payable_income_tax",              "c7200_TasutavTm"),
    ("dividend_equity_tax",             "c7217_DivOmakapTm"),
    ("foreign_tax_reduction",           "c7218_TmVrVahendus"),
    ("credit_method_reduction",         "c7219_TmKredasVahendus"),
    ("prior_period_distribution",       "c7290_MvVm"),
    ("prior_period_distribution_corr",  "c7300_MvVmKorrig"),
    ("prior_period_lower_rate_open",    "c7301_MvMmDivAlgus"),
    ("prior_period_lower_rate_used",    "c7302_MvMmDivYa"),
    ("prior_period_tonnage_open",       "c7303_MvTonnDivAlgus"),
    ("prior_period_tonnage_used",       "c7304_MvTonnDivYa"),
    ("prior_period_distribution_div",   "c7310_MvVmDiv"),
    ("prior_period_distribution_lower", "c7311_MvVmMmDiv"),
    ("prior_period_equity",             "c7320_MvVmOmakap"),
    ("prior_period_unused",             "c7330_MvVmKasutamata"),
]


def _render_annex7(annex7: Optional[Dict[str, Any]], indent: str) -> List[str]:
    """Emit <tsd_L7_0> if any Annex 7 fields populated."""
    if not annex7:
        return []
    populated = [(c_code, annex7.get(key)) for key, c_code in ANNEX_7_FIELDS
                 if annex7.get(key) is not None]
    if not populated:
        return []

    out: List[str] = [f"{indent}<tsd_L7_0>"]
    inner = indent + "    "
    for c_code, value in populated:
        out.append(f"{inner}<{c_code}>{fmt(value)}</{c_code}>")
    out.append(f"{indent}</tsd_L7_0>")
    return out


# --- INF1 (annual companion form for distribution recipients) -----------
# INF1 has two header scalars + a list of <tsd_Inf1_1> recipient rows.
# Each recipient: c13020_Nimi (REQUIRED), c13050_VmValiKood (REQUIRED),
# c13060_VmSumma (REQUIRED) plus optional Estonian/foreign IDs and tax fields.

INF1_RECIPIENT_FIELDS = [
    ("estonian_registry_code",  "c13000_EstRegkood"),
    ("foreign_registry_code",   "c13010_ValisRegkood"),
    ("name",                    "c13020_Nimi"),
    ("country_code",            "c13030_RiikKood"),
    ("foreign_address",         "c13040_ValisAadress"),
    ("distribution_type_code",  "c13050_VmValiKood"),
    ("distribution_amount",     "c13060_VmSumma"),
    ("taxable_amount",          "c13070_VmMaksustSumma"),
    ("exempt_amount",           "c13072_MvtSumma"),
    ("tax_rate",                "c13073_TmMaar"),
    ("withheld_tax",            "c13074_KpTmSumma"),
]


def _render_inf1_recipient(rec: Dict[str, Any], indent: str) -> List[str]:
    """Emit one <tsd_Inf1_1> recipient row."""
    out: List[str] = [f"{indent}<tsd_Inf1_1>"]
    inner = indent + "  "
    # Required fields per XSD: c13020_Nimi, c13050_VmValiKood, c13060_VmSumma
    for key, c_code in INF1_RECIPIENT_FIELDS:
        value = rec.get(key)
        if value is None or value == "":
            continue
        if c_code in ("c13060_VmSumma", "c13070_VmMaksustSumma", "c13072_MvtSumma",
                      "c13073_TmMaar", "c13074_KpTmSumma"):
            out.append(f"{inner}<{c_code}>{fmt(value)}</{c_code}>")
        else:
            out.append(f"{inner}<{c_code}>{esc(value)}</{c_code}>")
    out.append(f"{indent}</tsd_Inf1_1>")
    return out


def _render_inf1(inf1: Optional[Dict[str, Any]], indent: str) -> List[str]:
    """Emit <tsd_Inf1_0> if any INF1 fields/recipients populated."""
    if not inf1:
        return []
    recipients = inf1.get("recipients") or []
    has_scalars = any(inf1.get(k) is not None for k in ("withheld_tax_total", "taxed_proportion"))
    if not recipients and not has_scalars:
        return []

    out: List[str] = [f"{indent}<tsd_Inf1_0>"]
    inner = indent + "    "
    _emit_decimal("c13075_KpTmKokku",   inf1.get("withheld_tax_total"), inner, out)
    _emit_decimal("c13080_Osatahtsus",  inf1.get("taxed_proportion"),   inner, out)

    if recipients:
        out.append(f"{inner}<tsd_Inf1_1List>")
        for rec in recipients:
            out.extend(_render_inf1_recipient(rec, inner + "    "))
        out.append(f"{inner}</tsd_Inf1_1List>")

    out.append(f"{indent}</tsd_Inf1_0>")
    return out


def _render_annex2(non_resident_persons: Optional[List[Dict[str, Any]]], indent: str) -> List[str]:
    """Emit <tsd_L2_0> if any non-resident persons are provided."""
    if not non_resident_persons:
        return []

    out: List[str] = []
    out.append(f"{indent}<tsd_L2_0>")
    inner = indent + "    "
    out.append(f"{inner}<aIsikList>")
    for person in non_resident_persons:
        out.extend(_render_annex2_isik(person, inner + "    "))
    out.append(f"{inner}</aIsikList>")

    totals = _compute_annex2_totals(non_resident_persons)
    _emit_decimal("c2200_Smvm", totals["c2200_Smvm"], inner, out)
    _emit_decimal("c2210_Sm",   totals["c2210_Sm"],   inner, out)
    _emit_decimal("c2220_Tk",   totals["c2220_Tk"],   inner, out)
    _emit_decimal("c2230_Ttk",  totals["c2230_Ttk"],  inner, out)
    _emit_decimal("c2240_Tmvm", totals["c2240_Tmvm"], inner, out)
    _emit_decimal("c2250_Tm",   totals["c2250_Tm"],   inner, out, optional=False)
    out.append(f"{indent}</tsd_L2_0>")
    return out


def generate_tsd(data: Dict[str, Any]) -> str:
    """Render the complete TSD XML as a string (UTF-8, BOM-prefixed by writer)."""
    persons = data["persons"]
    non_resident_persons = data.get("non_resident_persons") or []
    annex4 = data.get("annex_4")
    annex5 = data.get("annex_5")
    annex7 = data.get("annex_7")
    inf1 = data.get("inf1")

    annex_totals = _compute_annex1_totals(persons)
    annex2_totals = _compute_annex2_totals(non_resident_persons) if non_resident_persons else {}
    header_totals = _compute_header_totals(
        annex_totals, annex2_totals=annex2_totals,
        annex4=annex4, annex5=annex5, annex7=annex7,
    )

    # Header overrides — let the caller pin specific values (for amended returns)
    for key, value in (data.get("header_overrides") or {}).items():
        if key in header_totals:
            header_totals[key] = D(value)

    lines: List[str] = []
    lines.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
    lines.append("<tsd_vorm>")

    # Header (xs:all — order doesn't matter for validation, but match the canonical
    # e-MTA filing order so visual diffs are minimal)
    inner = "    "
    lines.append(f'{inner}<c108_Aasta>{int(data["year"])}</c108_Aasta>')
    lines.append(f'{inner}<c109_Kuu>{int(data["month"])}</c109_Kuu>')
    _emit_decimal("c110_Tm",         header_totals["c110_Tm"],         inner, lines, optional=False)
    _emit_decimal("c114_TmEj",       header_totals["c114_TmEj"],       inner, lines, optional=False)
    _emit_decimal("c115_Sm",         header_totals["c115_Sm"],         inner, lines, optional=False)
    _emit_decimal("c116_Tk",         header_totals["c116_Tk"],         inner, lines, optional=False)
    _emit_decimal("c117_Kp",         header_totals["c117_Kp"],         inner, lines, optional=False)
    _emit_decimal("c118_KohustKokku", header_totals["c118_KohustKokku"], inner, lines, optional=False)
    _emit_decimal("c119_TagastKokku", header_totals["c119_TagastKokku"], inner, lines, optional=False)

    # Amended-return reason (optional)
    _emit_string("c121_ParPohjusKood", data.get("amend_reason_code"), inner, lines)
    _emit_string("parPohjusTekst",     data.get("amend_reason_text"), inner, lines)

    lines.append(f'{inner}<laadimisViis>{esc(data.get("load_mode", "P"))}</laadimisViis>')
    lines.append(f'{inner}<regKood>{esc(data["regcode"])}</regKood>')

    # Annex 1 — only emit if there are resident persons. Empty <aIsikList>
    # violates the XSD (Expected: tsd_L1_A_Isik).
    if persons:
        lines.append(f"{inner}<tsd_L1_0>")
        inner2 = inner + "    "
        lines.append(f"{inner2}<aIsikList>")
        for person in persons:
            lines.extend(_render_isik(person, inner2 + "    "))
        lines.append(f"{inner2}</aIsikList>")

        _emit_decimal("c1200_Smvm", annex_totals["c1200_Smvm"], inner2, lines, optional=False)
        _emit_decimal("c1210_Sm",   annex_totals["c1210_Sm"],   inner2, lines, optional=False)
        _emit_decimal("c1220_Kp",   annex_totals["c1220_Kp"],   inner2, lines, optional=False)
        _emit_decimal("c1230_Tk",   annex_totals["c1230_Tk"],   inner2, lines)
        _emit_decimal("c1240_Ttk",  annex_totals["c1240_Ttk"],  inner2, lines)
        _emit_decimal("c1250_Tm",   annex_totals["c1250_Tm"],   inner2, lines, optional=False)
        lines.append(f"{inner}</tsd_L1_0>")

    # Annex 2 (non-resident persons) — only emit if populated
    lines.extend(_render_annex2(non_resident_persons, inner))

    # Annex 4 (fringe benefits) — only emit if populated
    lines.extend(_render_annex4(annex4, inner))

    # Annex 5 (gifts/donations/entertainment) — only emit if populated
    lines.extend(_render_annex5(annex5, inner))

    # Annex 7 (dividends + equity distributions) — only emit if populated
    lines.extend(_render_annex7(annex7, inner))

    # INF1 (annual companion form) — only emit if populated
    lines.extend(_render_inf1(inf1, inner))

    lines.append(f"{inner}<vorm>TSD</vorm>")
    lines.append("</tsd_vorm>")

    return "\n".join(lines) + "\n"


def write_tsd(data: Dict[str, Any], output_dir: Path) -> Path:
    errors = validate(data)
    if errors:
        raise ValidationError(errors)

    xml = generate_tsd(data)

    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"TSD_{int(data['year']):04d}{int(data['month']):02d}_{data['regcode']}.xml"
    output_path = output_dir / filename

    # e-MTA portal accepts BOM-prefixed UTF-8; some tooling expects it.
    # Write with utf-8-sig to include the BOM.
    with open(output_path, "w", encoding="utf-8-sig", newline="\n") as f:
        f.write(xml)

    return output_path


def _print_summary(data: Dict[str, Any]) -> None:
    persons = data.get("persons") or []
    non_resident_persons = data.get("non_resident_persons") or []
    annex_totals = _compute_annex1_totals(persons)
    annex2_totals = _compute_annex2_totals(non_resident_persons) if non_resident_persons else {}
    header_totals = _compute_header_totals(
        annex_totals,
        annex2_totals=annex2_totals,
        annex4=data.get("annex_4"),
        annex5=data.get("annex_5"),
        annex7=data.get("annex_7"),
    )
    print(f"\nTSD summary ({len(persons)} person(s), "
          f"{sum(len(p.get('payments') or []) for p in persons)} payment row(s)):")
    print(f"  Total income tax (c110_Tm):       {fmt(header_totals['c110_Tm'])}")
    print(f"  Total social tax (c115_Sm):       {fmt(header_totals['c115_Sm'])}")
    print(f"  Total unemployment (c116_Tk):     {fmt(header_totals['c116_Tk'])}")
    print(f"  Total funded pension (c117_Kp):   {fmt(header_totals['c117_Kp'])}")
    print(f"  Total tax due (c118_KohustKokku): {fmt(header_totals['c118_KohustKokku'])}")
    print(f"\nReady for upload to e-MTA portal: https://maasikas.emta.ee")
    print(f"Filing deadline: 10th of the following month")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Estonian TSD XML for e-MTA")
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", default=".", help="Output directory (default: current)")
    args = parser.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    try:
        path = write_tsd(data, Path(args.output))
    except ValidationError as e:
        print("VALIDATION ERRORS:", file=sys.stderr)
        for err in e.errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print(f"Generated: {path}")
    _print_summary(data)


if __name__ == "__main__":
    main()
