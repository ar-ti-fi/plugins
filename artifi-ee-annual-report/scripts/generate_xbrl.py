#!/usr/bin/env python3
"""
Estonian Annual Report XBRL Generator
======================================
Generates Vormid_{REGCODE}.xsd and Aruanne_{REGCODE}.xbrl for upload to ariregister.rik.ee.
Based on the et-gaap_2026-01-01 taxonomy from xbrl.eesti.ee.

Usage:
    python generate_xbrl.py --input report_data.json --output /path/to/output/

No dependencies required — uses Python standard library only.
See input_schema.json for the required JSON format.
"""

import json
import sys
import os
import argparse
from typing import Optional

# ============================================================
# NAMESPACE CONSTANTS (hardcoded — do not modify)
# ============================================================
NS_ET_GAAP = "http://xbrl.eesti.ee/taxonomy/et-gaap_2026-01-01/"
NS_XBRLI = "http://www.xbrl.org/2003/instance"
NS_XBRLDI = "http://xbrl.org/2006/xbrldi"
NS_LINK = "http://www.xbrl.org/2003/linkbase"
NS_XLINK = "http://www.w3.org/1999/xlink"
NS_ISO4217 = "http://www.xbrl.org/2003/iso4217"
NS_ROLE_BASE = "http://xbrl.eesti.ee/role/et-gaap_2026-01-01"
NS_TEMP = "http://temporaryEntryFile"
ENTITY_SCHEME = "http://xbrl.eesti.ee/estonian_commercial_register"
TAXONOMY_DIR = "et-gaap_2026-01-01"
COR_SCHEMA = "et-gaap-cor_2026-01-01.xsd"

# ============================================================
# ROLE CATALOG  (role_code -> (form_name, has_cal_linkbase))
# ============================================================
ROLE_CATALOG: dict[str, tuple[str, bool]] = {
    "201010": ("StatementOfFinancialPosition", True),
    "201012": ("StatementOfFinancialPositionSmall", True),
    "301011": ("IncomeStatementScheme1", True),
    "301022": ("IncomeStatementScheme2", True),
    "401010": ("StatementOfCashFlowsIndirectMethod", True),
    "601010": ("StatementOfChangesInEquity", False),
    "702010": ("ProfitDistributionProposal", True),
    "702020": ("LossCoveringProposal", True),
    "801000": ("NoteAccountingPolicies", False),
    "801030": ("NoteAccountingPoliciesMicro", False),
    "802000": ("NoteCashAndCashEquivalents", False),
    "804010": ("NoteReceivablesAndPrepayments", True),
    "805000": ("NoteAccountsReceivable", False),
    "806000": ("NoteTaxPrepaymentsAndLiabilities", False),
    "811020": ("NoteLoanReceivables", False),
    "816000": ("NotePropertyPlantAndEquipment", True),
    "818000": ("NoteIntangibleAssets", True),
    "821000": ("NoteLoanCommitments", False),
    "822000": ("NotePayablesAndPrepayments", True),
    "828000": ("NoteContingentLiabilitiesAndAssets", True),
    "831010": ("NoteShareCapital", False),
    "832000": ("NoteNetSales", False),
    "839000": ("NoteLaborExpense", True),
    "842000": ("NoteIncomeTax", False),
    "843000": ("NoteRelatedParties", True),
    "844000": ("NoteEventsAfterReportingDate", False),
}

# ============================================================
# VALID ELEMENT SETS (prevents hallucination on input)
# ============================================================
VALID_MONETARY_ELEMENTS: set[str] = {
    # Balance Sheet – Assets
    "CashAndCashEquivalents", "ShortTermFinancialInvestments",
    "ShortTermReceivablesAndPrepayments", "ShortTermAccountsReceivable",
    "ShortTermReceivablesFromRelatedParties", "ShortTermTaxPrepaymentsAndReceivables",
    "ShortTermLoanReceivables", "ShortTermOtherReceivablesTotal", "ShortTermPrepaymentsTotal",
    "Inventories", "ShortTermBiologicalAssets", "CurrentAssets",
    "InvestmentsInSubsidiariesAndAssociates", "LongTermFinancialInvestments",
    "LongTermReceivablesAndPrepayments", "LongTermAccountsReceivable",
    "LongTermReceivablesFromRelatedParties", "LongTermTaxPrepaymentsAndReceivables",
    "LongTermLoanReceivables", "LongTermOtherReceivablesTotal", "LongTermPrepaymentsTotal",
    "InvestmentProperty", "PropertyPlantAndEquipment",
    "Land", "Buildings", "MachineryAndEquipment", "OtherTangibleAssets", "AssetsUnderConstruction",
    "LongTermBiologicalAssets", "IntangibleAssets", "Goodwill", "OtherIntangibleAssets",
    "NonCurrentAssets", "Assets",
    # Balance Sheet – Liabilities
    "ShortTermLoanLiabilities", "ShortTermPayablesAndPrepayments",
    "ShortTermTradePayablesTotal", "ShortTermEmployeePayablesTotal", "ShortTermTaxPayables",
    "ShortTermOtherPayablesTotal", "ShortTermDeferredIncome", "ShortTermOtherReceivedPrepayments",
    "ShortTermProvisions", "ShortTermGovernmentGrants", "CurrentLiabilities",
    "LongTermLoanLiabilities", "LongTermPayablesAndPrepayments",
    "LongTermTradePayablesTotal", "LongTermEmployeePayablesTotal", "LongTermTaxPayables",
    "LongTermOtherPayablesTotal", "LongTermDeferredIncome",
    "LongTermProvisions", "LongTermGovernmentGrants", "NonCurrentLiabilities", "Liabilities",
    # Balance Sheet – Equity
    "IssuedCapital", "UnregisteredEquity", "UnpaidCapital", "SharePremium",
    "TreasuryShares", "StatutoryReserveCapital", "OtherReserves", "OtherEquity",
    "RetainedEarningsLoss", "AnnualPeriodProfitLoss", "Equity", "LiabilitiesAndEquity",
    # Income Statement (Scheme 1)
    "Revenue", "OtherIncome", "ChangesInInventoriesOfAgriculturalProduction",
    "ProfitLossFromBiologicalAssets", "ChangesInInventoriesOfFinishedGoodsAndWorkInProgress",
    "WorkPerformedByEntityAndCapitalised", "RawMaterialsAndConsumablesUsed",
    "OtherOperatingExpense", "EmployeeExpense", "WageAndSalaryExpense",
    "SocialSecurityTaxes", "PensionExpense", "DepreciationAndImpairmentLossReversal",
    "SignificantImpairmentOfCurrentAssets", "OtherExpense", "TotalProfitLoss",
    "ProfitLossFromSubsidiaries", "ProfitLossFromAssociates",
    "GainLossFromFinancialInvestments", "InterestIncome", "InterestExpenses",
    "OtherFinancialIncomeAndExpense", "TotalProfitLossBeforeTax",
    "IncomeTaxExpense", "TotalAnnualPeriodProfitLoss",
    # Income Statement (Scheme 2)
    "CostOfGoodsSold", "GrossProfitLoss", "DistributionCosts", "AdministrativeExpenses",
    # Cash Flow
    "DepreciationAndImpairmentLossReversalNeg", "ProfitLossFromSaleOfNonCurrentAssets",
    "OtherAdjustments", "Adjustments",
    "ChangesInReceivablesAndPrepaymentsRelatedToOperatingActivities",
    "OperatingActivitiesChangesInInventories",
    "ChangesInPayablesAndPrepaymentsRelatedToOperatingActivities",
    "OperatingActivitiesIntrestReceived", "OperatingActivitiesIntrestPaid",
    "OperatingActivitiesIncomeTaxRefundPaid", "OperatingActivitiesProceedsFromGovernmentGrants",
    "OperatingActivitiesDividendsReceived", "OtherCashFlowsFromOperatingActivities",
    "CashFlowsFromOperatingActivities",
    "InvestingActivitiesPurchaseOfPropertyPlantAndEquipmentAndIntangibleAssets",
    "InvestingActivitiesProceedsFromSalesOfPropertyPlantAndEquipmentAndIntangibleAssets",
    "InvestingActivitiesLoansGiven", "InvestingActivitiesRepaymentsOfLoansGiven",
    "InvestingActivitiesIntrestReceived", "InvestingActivitiesDividendsReceived",
    "OtherCashOutflowsFromInvestingActivities", "OtherCashInflowsFromInvestingActivities",
    "CashFlowsFromInvestingActivities",
    "FinancingActivitiesLoansReceived", "FinancingActivitiesRepaymentsOfLoansReceived",
    "FinancingActivitiesProceedsFromOverdraft", "FinancingActivitiesProceedsFromFinanceLease",
    "FinancingActivitiesIntrestPaid", "FinancingActivitiesProceedsFromIssuingShares",
    "FinancingActivitiesDividendsPaid", "FinancingActivitiesIncomeTaxRefundPaid",
    "OtherCashInflowsFromFinancingActivities", "OtherCashOutflowsFromFinancingActivities",
    "CashFlowsFromFinancingActivities", "CashFlows",
    "CashAndCashEquivalentsAtBeginningOfPeriod", "ChangeInCashAndCashEquivalents",
    "EffectOnExchangeRateChangesOnCashAndCashEquivalents", "CashAndCashEquivalentsAtEndOfPeriod",
    # Equity Changes
    "ChangesInEquityIssuedCapital", "ChangesInEquityUnregisteredEquity",
    "ChangesInEquitySharePremium", "ChangesInEquityTreasuryShares",
    "ChangesInEquityStatutoryReserveCapital", "ChangesInEquityOtherReserves",
    "ChangesInEquityUnpaidCapital", "ChangesInEquityOtherEquity",
    "ChangesInEquityRetainedEarningsLoss", "ChangesInEquity",
    # Profit Allocation
    "RetainedEarningsLossWithAnnualPeriodProfitLoss",
    "ProposalStatutoryReserveCapitalIncreaseDecrease",
    "ProposalOtherReservesIncreaseDecrease", "ProposalDividends",
    "ProposalRetainedEarningsAfterDistributionCovering", "ProposalDistributionCoveringTotal",
    # Notes – Receivables
    "AccountsReceivables", "AllowanceForDoubtfulReceivables",
    "ReceivablesFromRelatedParties", "TaxPrepaymentsAndReceivables",
    "LoanReceivables", "InterestReceivables", "DividendReceivables",
    "AccruedIncome", "OtherReceivablesTotal", "DeferredExpenses",
    "OtherPaidPrepayments", "PrepaymentsTotal", "ReceivablesAndPrepayments",
    # Notes – Payables
    "TradePayablesTotal", "EmployeePayablesTotal", "RelatedPartiesPayables",
    "TaxPayables", "InterestPayables", "DividendPayables",
    "OtherAccruedExpenses", "OtherPayablesTotal", "PrepaymentsReceivedTotal",
    "PayablesAndPrepayments",
    # Notes – Contingent Liabilities
    "DistributableDividends", "IncomeTaxLiabilityOnDistributableDividends",
    "GuaranteesThatAreNotIncludedInBalanceSheet", "ContingentLiabilitiesTotal",
    # Notes – Share Capital
    "ShareCapital2", "NumberOfShares2", "NominalValueOfShares2",
    # Notes – Revenue
    "NetSalesByOperatingActivitiesValue", "NetSalesByOperatingActivitiesTotal",
    "NetSalesInEuropeanUnionTotal", "NetSalesOutsideOfEuropeanUnionTotal",
    "NetSalesByGeographicalLocation",
    # Notes – Personnel
    "LaborExpenseOther", "LaborExpense",
    "AverageNumberOfEmployeesInFullTimeEquivalentUnits",
    # Notes – Income Tax
    "DeclaredDividends", "DeclaredDividendsEstonia", "DeclaredDividendsOtherCountries",
    "IncomeTaxOnProfitForFinancialYear", "IncomeTaxExpenseComponentsTotal",
    # Notes – PP&E
    "PropertyPlantAndEquipmentAtEndOfPreviousPeriodCarriedAtCost",
    "PropertyPlantAndEquipmentAtEndOfPreviousPeriodAccumulatedDepreciation",
    "PropertyPlantAndEquipmentAtEndOfPreviousPeriodResidualCost",
    "PropertyPlantAndEquipmentAcquisitionsAndAdditions",
    "PropertyPlantAndEquipmentDepreciation", "PropertyPlantAndEquipmentDisposals",
    "PropertyPlantAndEquipmentAtEndOfPeriodCarriedAtCost",
    "PropertyPlantAndEquipmentAtEndOfPeriodAccumulatedDepreciation",
    "PropertyPlantAndEquipmentAtEndOfPeriodResidualCost",
    # Notes – Intangible Assets
    "IntangibleAssetsAtEndOfPreviousPeriodCarriedAtCost",
    "IntangibleAssetsAtEndOfPreviousPeriodAccumulatedAmortisation",
    "IntangibleAssetsAtEndOfPreviousPeriodResidualCost",
    "IntangibleAssetsAcquisitionsAndAdditions", "IntangibleAssetsAmortisation",
    "IntangibleAssetsDisposals",
    "IntangibleAssetsAtEndOfPeriodCarriedAtCost",
    "IntangibleAssetsAtEndOfPeriodAccumulatedAmortisation",
    "IntangibleAssetsAtEndOfPeriodResidualCost",
    # Notes – Related Parties
    "RelatedPartiesShortTermReceivablesAndPrepaymentsParentCompany",
    "RelatedPartiesShortTermReceivablesAndPrepaymentsSubsidiaries",
    "RelatedPartiesShortTermReceivablesAndPrepaymentsAssociates",
    "RelatedPartiesShortTermReceivablesAndPrepaymentsManagementAndHigherSupervisoryBodyAndIndividualsWithMaterialOwnershipInterest",
    "RelatedPartiesShortTermReceivablesAndPrepaymentsTotal",
    "RelatedPartiesLongTermReceivablesAndPrepaymentsParentCompany",
    "RelatedPartiesLongTermReceivablesAndPrepaymentsSubsidiaries",
    "RelatedPartiesLongTermReceivablesAndPrepaymentsAssociates",
    "RelatedPartiesLongTermReceivablesAndPrepaymentsManagementAndHigherSupervisoryBodyAndIndividualsWithMaterialOwnershipInterest",
    "RelatedPartiesLongTermReceivablesAndPrepaymentsTotal",
    "RelatedPartiesLongTermLoanLiabilitiesParentCompany",
    "RelatedPartiesLongTermLoanLiabilitiesSubsidiaries",
    "RelatedPartiesLongTermLoanLiabilitiesAssociates",
    "RelatedPartiesLongTermLoanLiabilitiesManagementAndHigherSupervisoryBodyAndIndividualsWithMaterialOwnershipInterest",
    "RelatedPartiesLongTermLoanLiabilitiesTotal",
    "Remuneration",
    # Notes – Loan Commitments
    "CurrentLoansTotal", "NonCurrentLoansTotal", "LoanCommitmentsTotal",
}

VALID_STRING_ELEMENTS: set[str] = {
    "NetSalesByOperatingActivitiesName",
}

# Elements in note_related_parties that are periodType="duration" (use D21, not I2)
# All others are periodType="instant" (use I2)
RELATED_PARTIES_DURATION_ELEMENTS: set[str] = {
    "Remuneration",
    "RelatedPartiesSalesOfParentCompany",
    "RelatedPartiesSalesOfFoundersAndMembers",
    "RelatedPartiesSalesOfSubsidiaries",
    "RelatedPartiesSalesOfAssociates",
    "RelatedPartiesSalesOfOtherEntitiesBelongingIntoSameConsolidationGroup",
    "RelatedPartiesSalesOfManagementAndHigherSupervisoryBodyAndIndividualsWithMaterialOwnershipInterest",
    "RelatedPartiesSalesTotal",
    "RelatedPartiesPurchasesOfParentCompany",
    "RelatedPartiesPurchasesOfFoundersAndMembers",
    "RelatedPartiesPurchasesOfSubsidiaries",
    "RelatedPartiesPurchasesOfAssociates",
    "RelatedPartiesPurchasesOfOtherEntitiesBelongingIntoSameConsolidationGroup",
    "RelatedPartiesPurchasesOfManagementAndHigherSupervisoryBodyAndIndividualsWithMaterialOwnershipInterest",
    "RelatedPartiesPurchasesTotal",
}

# Maturity dimension members
MATURITY_MEMBERS = {
    "total": "AllocationByRemainingMaturityTotalAbstract",
    "within_12m": "AllocationByRemainingMaturityWithin12MonthsAbstract",
    "within_1_5y": "AllocationByRemainingMaturityWithin1to5YearsAbstract",
    "over_5y": "AllocationByRemainingMaturityWithinOver5YearsAbstract",
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def major_role(role_code: str) -> str:
    """Return the major role directory code (e.g. '201010' -> '201000')."""
    return role_code[:3] + "000"


def context_instant(ctx_id: str, regcode: str, year: int) -> str:
    return (
        f'  <xbrli:context id="{ctx_id}">\n'
        f'    <xbrli:entity>\n'
        f'      <xbrli:identifier scheme="{ENTITY_SCHEME}">{regcode}</xbrli:identifier>\n'
        f'    </xbrli:entity>\n'
        f'    <xbrli:period>\n'
        f'      <xbrli:instant>{year}-12-31</xbrli:instant>\n'
        f'    </xbrli:period>\n'
        f'  </xbrli:context>'
    )


def context_duration(ctx_id: str, regcode: str, year: int) -> str:
    return (
        f'  <xbrli:context id="{ctx_id}">\n'
        f'    <xbrli:entity>\n'
        f'      <xbrli:identifier scheme="{ENTITY_SCHEME}">{regcode}</xbrli:identifier>\n'
        f'    </xbrli:entity>\n'
        f'    <xbrli:period>\n'
        f'      <xbrli:startDate>{year}-01-01</xbrli:startDate>\n'
        f'      <xbrli:endDate>{year}-12-31</xbrli:endDate>\n'
        f'    </xbrli:period>\n'
        f'  </xbrli:context>'
    )


def context_explicit_dim(ctx_id: str, regcode: str, period_type: str, year: int,
                          dim_name: str, member_name: str) -> str:
    if period_type == "instant":
        period_xml = f'      <xbrli:instant>{year}-12-31</xbrli:instant>'
    else:
        period_xml = (f'      <xbrli:startDate>{year}-01-01</xbrli:startDate>\n'
                      f'      <xbrli:endDate>{year}-12-31</xbrli:endDate>')
    return (
        f'  <xbrli:context id="{ctx_id}">\n'
        f'    <xbrli:entity>\n'
        f'      <xbrli:identifier scheme="{ENTITY_SCHEME}">{regcode}</xbrli:identifier>\n'
        f'    </xbrli:entity>\n'
        f'    <xbrli:period>\n'
        f'{period_xml}\n'
        f'    </xbrli:period>\n'
        f'    <xbrli:scenario>\n'
        f'      <xbrldi:explicitMember dimension="et-gaap:{dim_name}">et-gaap:{member_name}</xbrldi:explicitMember>\n'
        f'    </xbrli:scenario>\n'
        f'  </xbrli:context>'
    )


def monetary_fact(element: str, value, context_id: str) -> Optional[str]:
    if element not in VALID_MONETARY_ELEMENTS:
        raise ValueError(
            f"Unknown XBRL element '{element}'. "
            f"Check the element mapping tables in xbrl-generation.md."
        )
    v = int(round(float(value)))
    if v == 0:
        return None  # omit zero values
    return f'  <et-gaap:{element} decimals="0" unitRef="valuuta" contextRef="{context_id}">{v}</et-gaap:{element}>'


def string_fact(element: str, value: str, context_id: str) -> Optional[str]:
    if not value:
        return None
    return f'  <et-gaap:{element} contextRef="{context_id}">{value}</et-gaap:{element}>'


# ============================================================
# COMPANION XSD GENERATOR
# ============================================================

def generate_xsd(regcode: str, roles: list) -> str:
    """Build Vormid_{REGCODE}.xsd companion schema."""
    linkbase_refs: list[str] = []
    xsd_imports: list[str] = []

    for role_code in sorted(roles):
        if role_code not in ROLE_CATALOG:
            raise ValueError(f"Unknown role code '{role_code}'. See Role Catalog in xbrl-generation.md.")
        form_name, has_cal = ROLE_CATALOG[role_code]
        maj = major_role(role_code)
        base = f"{TAXONOMY_DIR}/role-{maj}"

        if has_cal:
            linkbase_refs.append(
                f'      <link:linkbaseRef xlink:type="simple"'
                f' xlink:href="{base}/cal_{form_name}_role-{role_code}.xml"'
                f' xlink:role="http://www.xbrl.org/2003/role/calculationLinkbaseRef"'
                f' xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>'
            )
        linkbase_refs.append(
            f'      <link:linkbaseRef xlink:type="simple"'
            f' xlink:href="{base}/def_{form_name}_role-{role_code}.xml"'
            f' xlink:role="http://www.xbrl.org/2003/role/definitionLinkbaseRef"'
            f' xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>'
        )
        linkbase_refs.append(
            f'      <link:linkbaseRef xlink:type="simple"'
            f' xlink:href="{base}/pre_{form_name}_role-{role_code}.xml"'
            f' xlink:role="http://www.xbrl.org/2003/role/presentationLinkbaseRef"'
            f' xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>'
        )
        xsd_imports.append(
            f'  <xsd:import namespace="{NS_ROLE_BASE}/role-{maj}"'
            f' schemaLocation="{TAXONOMY_DIR}/role-{maj}/role-{maj}.xsd"/>'
        )

    # Always-included linkbases (label + reference)
    linkbase_refs += [
        f'      <link:linkbaseRef xlink:type="simple"'
        f' xlink:href="{TAXONOMY_DIR}/label/et-gaap_2026-01-01-label-et.xml"'
        f' xlink:role="http://www.xbrl.org/2003/role/labelLinkbaseRef"'
        f' xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>',
        f'      <link:linkbaseRef xlink:type="simple"'
        f' xlink:href="{TAXONOMY_DIR}/label/et-gaap_2026-01-01-label-en.xml"'
        f' xlink:role="http://www.xbrl.org/2003/role/labelLinkbaseRef"'
        f' xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>',
        f'      <link:linkbaseRef xlink:type="simple"'
        f' xlink:href="{TAXONOMY_DIR}/reference/et-gaap_2026-01-01-reference.xml"'
        f' xlink:role="http://www.xbrl.org/2003/role/referenceLinkbaseRef"'
        f' xlink:arcrole="http://www.w3.org/1999/xlink/properties/linkbase"/>',
    ]

    linkbase_block = "\n".join(linkbase_refs)
    import_block = "\n".join(xsd_imports)

    return (
        f"<?xml version='1.0' encoding='UTF-8'?>\n"
        f'<xsd:schema xmlns:link="{NS_LINK}"\n'
        f'            xmlns:xlink="{NS_XLINK}"\n'
        f'            xmlns:xsd="http://www.w3.org/2001/XMLSchema"\n'
        f'            targetNamespace="{NS_TEMP}"\n'
        f'            elementFormDefault="qualified">\n'
        f'  <xsd:annotation>\n'
        f'    <xsd:appinfo>\n'
        f'{linkbase_block}\n'
        f'    </xsd:appinfo>\n'
        f'  </xsd:annotation>\n'
        f'  <xsd:import namespace="{NS_XBRLI}"'
        f' schemaLocation="http://www.xbrl.org/2003/xbrl-instance-2003-12-31.xsd"/>\n'
        f'{import_block}\n'
        f'  <xsd:import namespace="{NS_ET_GAAP}" schemaLocation="{COR_SCHEMA}"/>\n'
        f'</xsd:schema>'
    )


# ============================================================
# INSTANCE DOCUMENT GENERATOR
# ============================================================

def generate_xbrl(data: dict) -> str:
    """Build Aruanne_{REGCODE}.xbrl instance document."""
    regcode: str = data["regcode"]
    fiscal_year: int = int(data["fiscal_year"])
    prior_year: int = fiscal_year - 1

    contexts: list[str] = []
    facts: list[str] = []
    used_ctx_ids: set[str] = set()
    he_counter = [1]  # mutable counter for HE* contexts

    def add_ctx(ctx_id: str, ctx_xml: str) -> str:
        if ctx_id not in used_ctx_ids:
            contexts.append(ctx_xml)
            used_ctx_ids.add(ctx_id)
        return ctx_id

    def next_he() -> str:
        cid = f"HE{he_counter[0]}"
        he_counter[0] += 1
        return cid

    def emit(element: str, value, ctx_id: str) -> None:
        f = monetary_fact(element, value, ctx_id)
        if f:
            facts.append(f)

    def emit_map(mapping: dict, ctx_id: str) -> None:
        for element, value in mapping.items():
            emit(element, value, ctx_id)

    # Standard contexts
    ctx_i2 = add_ctx("I2", context_instant("I2", regcode, fiscal_year))
    ctx_i1 = add_ctx("I1", context_instant("I1", regcode, prior_year))
    ctx_d21 = add_ctx("D21", context_duration("D21", regcode, fiscal_year))
    ctx_d11 = add_ctx("D11", context_duration("D11", regcode, prior_year))

    # ---- Balance Sheet ----
    bs = data.get("balance_sheet", {})
    emit_map(bs.get("current", {}), ctx_i2)
    emit_map(bs.get("prior", {}), ctx_i1)

    # ---- Income Statement ----
    is_current = data.get("income_statement", {})
    is_prior = data.get("income_statement_prior", {})
    emit_map(is_current, ctx_d21)
    emit_map(is_prior, ctx_d11)
    # Auto-fill comparative zeros: if current year has a value but prior year
    # does not, emit 0 in D11 so the BTM portal shows "0" instead of blank.
    for element in is_current:
        if element not in is_prior and element in VALID_MONETARY_ELEMENTS:
            v = int(round(float(is_current[element])))
            if v != 0:
                facts.append(
                    f'  <et-gaap:{element} decimals="0" unitRef="valuuta" contextRef="{ctx_d11}">0</et-gaap:{element}>'
                )

    # ---- Cash Flow Statement ----
    cf_current = data.get("cash_flow", {})
    cf_prior = data.get("cash_flow_prior", {})
    emit_map(cf_current, ctx_d21)
    emit_map(cf_prior, ctx_d11)
    # Auto-fill comparative zeros for cash flow
    for element in cf_current:
        if element not in cf_prior and element in VALID_MONETARY_ELEMENTS:
            v = int(round(float(cf_current[element])))
            if v != 0:
                facts.append(
                    f'  <et-gaap:{element} decimals="0" unitRef="valuuta" contextRef="{ctx_d11}">0</et-gaap:{element}>'
                )

    # ---- Profit Allocation Proposal ----
    emit_map(data.get("profit_allocation", {}), ctx_i2)

    # ---- Statement of Changes in Equity ----
    # equity_changes: { row_member: { element: value } }
    for row_member, columns in data.get("equity_changes", {}).items():
        ctx_id = next_he()
        add_ctx(ctx_id, context_explicit_dim(
            ctx_id, regcode, "duration", fiscal_year,
            "ChangesInEquityDimension", row_member
        ))
        emit_map(columns, ctx_id)

    # ---- Note: Receivables (maturity breakdown) ----
    for maturity_key, maturity_member in MATURITY_MEMBERS.items():
        note_r = data.get("note_receivables", {}).get(maturity_key, {})
        if note_r:
            ctx_id = next_he()
            add_ctx(ctx_id, context_explicit_dim(
                ctx_id, regcode, "instant", fiscal_year,
                "AllocationByRemainingMaturityDimension", maturity_member
            ))
            emit_map(note_r, ctx_id)
        # Prior year receivables
        note_r_prior = data.get("note_receivables_prior", {}).get(maturity_key, {})
        if note_r_prior:
            ctx_id = next_he()
            add_ctx(ctx_id, context_explicit_dim(
                ctx_id, regcode, "instant", prior_year,
                "AllocationByRemainingMaturityDimension", maturity_member
            ))
            emit_map(note_r_prior, ctx_id)

    # ---- Note: Payables (maturity breakdown) ----
    for maturity_key, maturity_member in MATURITY_MEMBERS.items():
        note_p = data.get("note_payables", {}).get(maturity_key, {})
        if note_p:
            ctx_id = next_he()
            add_ctx(ctx_id, context_explicit_dim(
                ctx_id, regcode, "instant", fiscal_year,
                "AllocationByRemainingMaturityDimension", maturity_member
            ))
            emit_map(note_p, ctx_id)

    # ---- Note: Contingent Liabilities ----
    emit_map(data.get("note_contingent_liabilities", {}), ctx_i2)

    # ---- Note: Personnel Expenses ----
    emit_map(data.get("note_personnel", {}), ctx_d21)

    # ---- Note: Revenue ----
    note_rev = data.get("note_revenue", {})
    for elem in ["NetSalesByOperatingActivitiesTotal", "NetSalesInEuropeanUnionTotal",
                 "NetSalesOutsideOfEuropeanUnionTotal", "NetSalesByGeographicalLocation"]:
        if elem in note_rev:
            emit(elem, note_rev[elem], ctx_d21)

    # ---- Note: Income Tax (dimensional) ----
    # AllocationByIncomeTaxExpenseComponentsDimension is periodType="instant" — use instant context
    tax_dim_members = {
        "taxable_amount": "TaxableAmountAbstract",
        "tax_expense": "IncomeTaxExpenseAbstract",
        "deferred_tax": "DeferredIncomeTaxAbstract",
    }
    for comp_key, comp_member in tax_dim_members.items():
        comp_data = data.get("note_income_tax", {}).get(comp_key, {})
        if comp_data:
            ctx_id = next_he()
            add_ctx(ctx_id, context_explicit_dim(
                ctx_id, regcode, "instant", fiscal_year,
                "AllocationByIncomeTaxExpenseComponentsDimension", comp_member
            ))
            emit_map(comp_data, ctx_id)

    # ---- Note: Share Capital ----
    emit_map(data.get("note_share_capital", {}), ctx_i2)

    # ---- Note: PP&E ----
    # All PropertyPlantAndEquipment* elements are periodType="duration" — use D21
    emit_map(data.get("note_ppe", {}), ctx_d21)

    # ---- Note: Intangible Assets ----
    emit_map(data.get("note_intangibles", {}), ctx_i2)

    # ---- Note: Related Parties ----
    # Most elements are instant (balance sheet items); Remuneration and Sales/Purchases are duration
    for element, value in data.get("note_related_parties", {}).items():
        ctx = ctx_d21 if element in RELATED_PARTIES_DURATION_ELEMENTS else ctx_i2
        f = monetary_fact(element, value, ctx)
        if f:
            facts.append(f)

    # ---- Note: Loan Commitments totals ----
    emit_map(data.get("note_loan_commitments", {}), ctx_i2)

    # Assemble
    context_block = "\n".join(contexts)
    fact_block = "\n".join(facts)

    return (
        f"<?xml version='1.0' encoding='UTF-8'?>\n"
        f'<xbrli:xbrl xmlns:iso4217="{NS_ISO4217}"\n'
        f'            xmlns:et-gaap="{NS_ET_GAAP}"\n'
        f'            xmlns:xlink="{NS_XLINK}"\n'
        f'            xmlns:link="{NS_LINK}"\n'
        f'            xmlns:xbrli="{NS_XBRLI}"\n'
        f'            xmlns:xbrldi="{NS_XBRLDI}">\n'
        f'  <link:schemaRef xlink:type="simple" xlink:href="Vormid_{regcode}.xsd"/>\n'
        f'\n'
        f'{context_block}\n'
        f'\n'
        f'  <xbrli:unit id="valuuta">\n'
        f'    <xbrli:measure>iso4217:EUR</xbrli:measure>\n'
        f'  </xbrli:unit>\n'
        f'\n'
        f'{fact_block}\n'
        f'</xbrli:xbrl>'
    )


# ============================================================
# VALIDATION
# ============================================================

def validate(data: dict) -> list[str]:
    """Return list of validation error messages."""
    errors: list[str] = []

    bs_cur = data.get("balance_sheet", {}).get("current", {})
    assets = bs_cur.get("Assets")
    liabilities = bs_cur.get("Liabilities")
    equity = bs_cur.get("Equity")
    if assets is not None and liabilities is not None and equity is not None:
        diff = int(round(float(assets))) - int(round(float(liabilities))) - int(round(float(equity)))
        if abs(diff) > 1:
            errors.append(
                f"Balance sheet does not balance: Assets {assets} != Liabilities {liabilities} + Equity {equity} (diff={diff})"
            )

    is_profit = data.get("income_statement", {}).get("TotalAnnualPeriodProfitLoss")
    bs_profit = bs_cur.get("AnnualPeriodProfitLoss")
    if is_profit is not None and bs_profit is not None:
        diff = int(round(float(is_profit))) - int(round(float(bs_profit)))
        if abs(diff) > 1:
            errors.append(
                f"Net profit mismatch: IS TotalAnnualPeriodProfitLoss={is_profit} != BS AnnualPeriodProfitLoss={bs_profit}"
            )

    cf = data.get("cash_flow", {})
    cf_closing = cf.get("CashAndCashEquivalentsAtEndOfPeriod")
    bs_cash = bs_cur.get("CashAndCashEquivalents")
    if cf_closing is not None and bs_cash is not None:
        diff = int(round(float(cf_closing))) - int(round(float(bs_cash)))
        if abs(diff) > 1:
            errors.append(
                f"Cash flow closing balance {cf_closing} != BS CashAndCashEquivalents {bs_cash}"
            )

    return errors


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate XBRL files for Estonian annual report filing."
    )
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", default=".", help="Output directory (default: current dir)")
    parser.add_argument("--skip-validation", action="store_true",
                        help="Skip balance-sheet/cash-flow validation checks")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, encoding="utf-8") as fh:
        data = json.load(fh)

    regcode: str = data.get("regcode", "")
    if not regcode:
        print("ERROR: 'regcode' is required in input JSON.", file=sys.stderr)
        sys.exit(1)

    roles: list = data.get("roles", [])
    if not roles:
        print("ERROR: 'roles' list is required in input JSON.", file=sys.stderr)
        sys.exit(1)

    # Validate financial data
    if not args.skip_validation:
        errors = validate(data)
        if errors:
            print("VALIDATION ERRORS — fix before filing:", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
            sys.exit(1)

    os.makedirs(args.output, exist_ok=True)

    # Generate companion XSD
    try:
        xsd_content = generate_xsd(regcode, roles)
    except ValueError as exc:
        print(f"ERROR generating XSD: {exc}", file=sys.stderr)
        sys.exit(1)

    xsd_path = os.path.join(args.output, f"Vormid_{regcode}.xsd")
    with open(xsd_path, "w", encoding="utf-8") as fh:
        fh.write(xsd_content)
    print(f"Written: {xsd_path}")

    # Generate instance document
    try:
        xbrl_content = generate_xbrl(data)
    except ValueError as exc:
        print(f"ERROR generating XBRL: {exc}", file=sys.stderr)
        sys.exit(1)

    xbrl_path = os.path.join(args.output, f"Aruanne_{regcode}.xbrl")
    with open(xbrl_path, "w", encoding="utf-8") as fh:
        fh.write(xbrl_content)
    print(f"Written: {xbrl_path}")

    print("\nDone. Upload both files to ariregister.rik.ee:")
    print(f"  1. {xsd_path}")
    print(f"  2. {xbrl_path}")


if __name__ == "__main__":
    main()
