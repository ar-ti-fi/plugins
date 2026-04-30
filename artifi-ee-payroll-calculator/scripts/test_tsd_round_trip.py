#!/usr/bin/env python3
"""Golden-master round-trip test for generate_tsd.py.

Builds the JSON input that should reproduce the canonical April 2026 filing
(`~/Downloads/TSD 2026 4.xml`), runs the generator, and verifies the output
is **semantically identical** to the canonical (zero element diffs, zero
value diffs after numeric normalization).

Run:
    python3 scripts/test_tsd_round_trip.py

Exit code 0 = pass; non-zero = fail.

This test pins the generator's correctness against a real e-MTA filing.
Any future change to generate_tsd.py that breaks this test means the change
would produce an XML the e-MTA portal would reject.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path
from typing import Iterable, Tuple

# Path to the canonical golden master. Override with TSD_GOLDEN_MASTER env var if needed.
GOLDEN = Path(os.environ.get(
    "TSD_GOLDEN_MASTER",
    str(Path.home() / "Downloads" / "TSD 2026 4.xml"),
))

# The exact JSON input that should reproduce the canonical filing.
# Source: April 2026 filing for ANDRII RUDCHUK (board fee, basic exemption applied).
GOLDEN_INPUT = {
    "regcode": "17266831",
    "year": 2026,
    "month": 4,
    "load_mode": "P",
    "persons": [
        {
            "personal_id": "38704290190",
            "full_name": "ANDRII RUDCHUK",
            "payments": [
                {
                    "payment_type_code": "21",
                    "gross": 1500.00,
                    "social_tax_base": 1500.00,
                    "social_tax": 495.00,
                    "combined_kp": 30.00,
                    "income_tax": 169.40,
                    "tax_free_items": [
                        {"code": "610", "amount": 700.00}
                    ]
                }
            ]
        }
    ]
}


def _normalize_text(s: str | None) -> str:
    """Normalize numeric text for comparison (1500 == 1500.00 == 1500.000)."""
    s = (s or "").strip()
    if not s:
        return ""
    try:
        d = Decimal(s)
        return str(d.normalize())
    except Exception:
        return s


def _collect(elem, path: str = "") -> Iterable[Tuple[str, str]]:
    p = f"{path}/{elem.tag}"
    yield p, _normalize_text(elem.text)
    for child in elem:
        yield from _collect(child, p)


def _build_xml(input_dict, tmp_dir):
    """Generate XML for an input and return the parsed root."""
    sys.path.insert(0, str(Path(__file__).parent))
    from generate_tsd import write_tsd
    p = write_tsd(input_dict, Path(tmp_dir))
    return ET.parse(p).getroot(), p


def _diff(gen_root, canon_root):
    gen = {p: t for p, t in _collect(gen_root) if t}
    canon = {p: t for p, t in _collect(canon_root) if t}
    only_gen = sorted(set(gen) - set(canon))
    only_canon = sorted(set(canon) - set(gen))
    diffs = [(p, gen[p], canon[p]) for p in sorted(set(gen) & set(canon)) if gen[p] != canon[p]]
    return gen, canon, only_gen, only_canon, diffs


def _print_diff(label, only_gen, only_canon, diffs):
    if only_gen:
        print(f"\n  Elements only in generated ({len(only_gen)}):")
        for p in only_gen:
            print(f"    + {p}")
    if only_canon:
        print(f"\n  Elements only in canonical ({len(only_canon)}):")
        for p in only_canon:
            print(f"    - {p}")
    if diffs:
        print(f"\n  Value differences ({len(diffs)}):")
        for p, gv, cv in diffs:
            print(f"    ~ {p}: gen={gv!r} canon={cv!r}")


def _check_xpath_value(root, xpath, expected, label):
    """Find an element by tag name (no namespace) and confirm its text matches expected."""
    elem = root.find(xpath)
    if elem is None:
        return False, f"{label}: element {xpath} not found"
    actual = (elem.text or "").strip()
    if Decimal(actual) == Decimal(str(expected)):
        return True, ""
    return False, f"{label}: {xpath} = {actual} (expected {expected})"


def test_r2_golden_master(tmp):
    """R2 — generated XML is semantically identical to the canonical filing."""
    canon_root = ET.parse(GOLDEN).getroot()
    gen_root, _ = _build_xml(GOLDEN_INPUT, tmp)
    gen, canon, only_gen, only_canon, diffs = _diff(gen_root, canon_root)
    if not only_gen and not only_canon and not diffs:
        print(f"  PASS: {len(gen)} elements match canonical filing exactly")
        return True
    print(f"  FAIL: {len(diffs)} value diffs, {len(only_gen)} extra gen, {len(only_canon)} extra canon")
    _print_diff("R2", only_gen, only_canon, diffs)
    return False


def test_r3_annex4_emit(tmp):
    """R3 — Annex 4 fringe-benefit values flow through to <tsd_L4_0> + header c114/c115."""
    inp = {
        **GOLDEN_INPUT,
        "annex_4": {
            "company_vehicle": 300.00,
            "representation_amount": 300.00,
            "social_tax_base": 379.62,
            "special_income_tax": 84.62,
            "social_tax": 125.27,
        },
    }
    gen_root, p = _build_xml(inp, tmp)

    checks = [
        ("Annex 4 emitted", "tsd_L4_0/c4040_Ts", 300.00),
        ("c4170 special income tax", "tsd_L4_0/c4170_TmEj", 84.62),
        ("c4180 social tax", "tsd_L4_0/c4180_Sm", 125.27),
        ("Header c114 includes Annex 4 c4170", "c114_TmEj", 84.62),
        ("Header c115 includes Annex 1 + Annex 4 c4180", "c115_Sm", 620.27),
        ("Header c118 = c110+c114+c115+c116+c117", "c118_KohustKokku", 904.29),
    ]
    all_ok = True
    for label, xpath, expected in checks:
        ok, msg = _check_xpath_value(gen_root, xpath, expected, label)
        if ok:
            print(f"  ✓ {label} = {expected}")
        else:
            print(f"  ✗ {msg}")
            all_ok = False
    return all_ok


def test_r4_annex2_only(tmp):
    """R4 — non-resident-only filing (no Annex 1, only Annex 2). Header c110/c115 roll-up correct."""
    inp = {
        "regcode": "17266831",
        "year": 2026,
        "month": 4,
        "load_mode": "P",
        "persons": [],
        "non_resident_persons": [
            {
                "personal_id": "FI-12345-67890",
                "full_name": "MIKKO VIRTANEN",
                "payments": [
                    {
                        "country_of_residence": "FI",
                        "payment_type_code": "120",
                        "gross": 1000.00,
                        "income_tax_base": 1000.00,
                        "income_tax_rate": 22.00,
                        "income_tax": 220.00,
                    }
                ],
            }
        ],
    }
    gen_root, _ = _build_xml(inp, tmp)

    checks = [
        ("Annex 2 emitted", "tsd_L2_0/aIsikList/tsd_L2_A_Isik/c2000_Kood", None),  # presence-only check
        ("c2030 payment_type_code", "tsd_L2_0/aIsikList/tsd_L2_A_Isik/vmList/tsd_L2_A_Vm/c2030_ValiKood", "120"),
        ("c2170 income tax",        "tsd_L2_0/aIsikList/tsd_L2_A_Isik/vmList/tsd_L2_A_Vm/c2170_Tm", 220.00),
        ("Annex 2 total c2250_Tm",  "tsd_L2_0/c2250_Tm", 220.00),
        ("Header c110 includes Annex 2 c2250", "c110_Tm", 220.00),
        ("No Annex 1 emitted (no resident persons)", "tsd_L1_0", None),  # absence check below
    ]
    all_ok = True
    for label, xpath, expected in checks:
        elem = gen_root.find(xpath)
        if expected is None:
            if "No Annex 1" in label:
                if elem is None:
                    print(f"  ✓ {label}")
                else:
                    print(f"  ✗ {label}: <tsd_L1_0> should NOT be present")
                    all_ok = False
            else:
                if elem is not None:
                    print(f"  ✓ {label}")
                else:
                    print(f"  ✗ {label}: element not found")
                    all_ok = False
            continue
        if isinstance(expected, str):
            actual = (elem.text or "").strip() if elem is not None else None
            if actual == expected:
                print(f"  ✓ {label} = {expected!r}")
            else:
                print(f"  ✗ {label}: actual={actual!r} expected={expected!r}")
                all_ok = False
        else:
            ok, msg = _check_xpath_value(gen_root, xpath, expected, label)
            if ok:
                print(f"  ✓ {label} = {expected}")
            else:
                print(f"  ✗ {msg}")
                all_ok = False
    return all_ok


def test_r4_mixed_residency(tmp):
    """R4 — mixed: 1 resident in Annex 1 + 1 non-resident in Annex 2. Header c110 sums both."""
    inp = {
        **GOLDEN_INPUT,
        "non_resident_persons": [
            {
                "personal_id": "FI-99999-99999",
                "full_name": "ANNA KORHONEN",
                "payments": [
                    {
                        "country_of_residence": "FI",
                        "payment_type_code": "122",
                        "gross": 500.00,
                        "income_tax_base": 500.00,
                        "income_tax_rate": 10.00,
                        "income_tax": 50.00,
                    }
                ],
            }
        ],
    }
    gen_root, _ = _build_xml(inp, tmp)
    checks = [
        ("Annex 1 still emits c1250_Tm", "tsd_L1_0/c1250_Tm", 169.40),
        ("Annex 2 emits c2250_Tm",       "tsd_L2_0/c2250_Tm", 50.00),
        ("Header c110 = 169.40 + 50.00", "c110_Tm", 219.40),
    ]
    all_ok = True
    for label, xpath, expected in checks:
        ok, msg = _check_xpath_value(gen_root, xpath, expected, label)
        if ok:
            print(f"  ✓ {label} = {expected}")
        else:
            print(f"  ✗ {msg}")
            all_ok = False
    return all_ok


def test_r5_annex7_dividends(tmp):
    """R5 — Annex 7 dividend distribution + header roll-up (c7200 → c110, c7050 → c115)."""
    inp = {
        **GOLDEN_INPUT,
        "annex_7": {
            "dividends_total": 5000.00,
            "equity_social_tax_corrected": 1090.00,
            "payable_income_tax": 1410.26,
        },
    }
    gen_root, _ = _build_xml(inp, tmp)
    checks = [
        ("Annex 7 emitted",                           "tsd_L7_0/c7008_DivKokku", 5000.00),
        ("c7050 equity ST corrected",                 "tsd_L7_0/c7050_OmakapSmKorrig", 1090.00),
        ("c7200 payable income tax",                  "tsd_L7_0/c7200_TasutavTm", 1410.26),
        ("Header c110 = Annex 1 (169.40) + c7200",    "c110_Tm", 169.40 + 1410.26),
        ("Header c115 = Annex 1 (495.00) + c7050",    "c115_Sm", 495.00 + 1090.00),
    ]
    all_ok = True
    for label, xpath, expected in checks:
        ok, msg = _check_xpath_value(gen_root, xpath, expected, label)
        if ok:
            print(f"  ✓ {label} = {expected}")
        else:
            print(f"  ✗ {msg}")
            all_ok = False
    return all_ok


def test_r5_inf1_recipient_list(tmp):
    """R5 — INF1 emit with header scalars + recipient list (resident + non-resident)."""
    inp = {
        **GOLDEN_INPUT,
        "inf1": {
            "withheld_tax_total": 2200.00,
            "taxed_proportion": 1.000000000,
            "recipients": [
                {
                    "estonian_registry_code": "38704290190",
                    "name": "ANDRII RUDCHUK",
                    "distribution_type_code": "DK",
                    "distribution_amount": 5000.00,
                    "tax_rate": 22.00,
                    "withheld_tax": 1100.00,
                },
                {
                    "foreign_registry_code": "FI-99999",
                    "name": "ANNA KORHONEN",
                    "country_code": "FI",
                    "foreign_address": "HELSINKI MANNERHEIMINTIE 10",
                    "distribution_type_code": "DK",
                    "distribution_amount": 5000.00,
                    "tax_rate": 22.00,
                    "withheld_tax": 1100.00,
                },
            ],
        },
    }
    gen_root, _ = _build_xml(inp, tmp)

    inf1 = gen_root.find("tsd_Inf1_0")
    if inf1 is None:
        print("  ✗ tsd_Inf1_0 not emitted")
        return False
    recipients = inf1.findall("tsd_Inf1_1List/tsd_Inf1_1")
    if len(recipients) != 2:
        print(f"  ✗ expected 2 recipient rows, got {len(recipients)}")
        return False
    print(f"  ✓ 2 recipient rows emitted")

    # Resident first (has c13000_EstRegkood, no c13030_RiikKood)
    r0 = recipients[0]
    if r0.find("c13000_EstRegkood") is None or r0.find("c13030_RiikKood") is not None:
        print(f"  ✗ resident recipient should have c13000 but no c13030")
        return False
    print(f"  ✓ resident recipient has c13000_EstRegkood, no c13030_RiikKood")

    # Non-resident second (has c13030_RiikKood + c13040_ValisAadress)
    r1 = recipients[1]
    if r1.find("c13030_RiikKood") is None or r1.find("c13030_RiikKood").text != "FI":
        print(f"  ✗ non-resident recipient should have c13030_RiikKood='FI'")
        return False
    print(f"  ✓ non-resident recipient has c13030_RiikKood=FI")

    # Header scalars
    if (inf1.find("c13075_KpTmKokku").text or "").strip() != "2200.00":
        print(f"  ✗ c13075_KpTmKokku should be 2200.00")
        return False
    print(f"  ✓ c13075_KpTmKokku = 2200.00")
    return True


def test_r3_annex5_emit(tmp):
    """R3 — Annex 5 gifts/donations/entertainment flow through to <tsd_L5_0> + header c114."""
    inp = {
        **GOLDEN_INPUT,
        "annex_5": {
            "general_gifts": 200.00,
            "entertainment_month": 100.00,
            "entertainment_year": 100.00,
            "entertainment_threshold": 50.00,
            "special_income_tax_payable": 12.82,
        },
    }
    gen_root, p = _build_xml(inp, tmp)

    checks = [
        ("Annex 5 emitted", "tsd_L5_0/c5000_Ki", 200.00),
        ("c5100 entertainment month", "tsd_L5_0/c5100_KyKuluKuu", 100.00),
        ("c5160 special income tax", "tsd_L5_0/c5160_TasTmEj", 12.82),
        ("Header c114 includes Annex 5 c5160", "c114_TmEj", 12.82),
    ]
    all_ok = True
    for label, xpath, expected in checks:
        ok, msg = _check_xpath_value(gen_root, xpath, expected, label)
        if ok:
            print(f"  ✓ {label} = {expected}")
        else:
            print(f"  ✗ {msg}")
            all_ok = False
    return all_ok


def main() -> int:
    if not GOLDEN.exists():
        print(f"FAIL: golden master not found at {GOLDEN}", file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        results = []

        print("Test 1: R2 golden-master (Annex 1 only)")
        results.append(("R2 golden-master", test_r2_golden_master(tmp)))

        print("\nTest 2: R3 Annex 4 emit + header roll-up")
        results.append(("R3 Annex 4", test_r3_annex4_emit(tmp)))

        print("\nTest 3: R3 Annex 5 emit + header roll-up")
        results.append(("R3 Annex 5", test_r3_annex5_emit(tmp)))

        print("\nTest 4: R4 Annex 2 only (no resident persons)")
        results.append(("R4 Annex 2 only", test_r4_annex2_only(tmp)))

        print("\nTest 5: R4 mixed residency (Annex 1 + Annex 2)")
        results.append(("R4 mixed residency", test_r4_mixed_residency(tmp)))

        print("\nTest 6: R5 Annex 7 dividends + header roll-ups")
        results.append(("R5 Annex 7", test_r5_annex7_dividends(tmp)))

        print("\nTest 7: R5 INF1 recipient list (resident + non-resident)")
        results.append(("R5 INF1", test_r5_inf1_recipient_list(tmp)))

    print("\n" + "=" * 60)
    failed = [name for name, ok in results if not ok]
    if not failed:
        print(f"PASS — all {len(results)} test(s) green")
        return 0
    print(f"FAIL — {len(failed)} of {len(results)} failed: {', '.join(failed)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
