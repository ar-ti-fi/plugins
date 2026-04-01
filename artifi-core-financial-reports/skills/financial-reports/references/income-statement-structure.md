# Income Statement (Profit & Loss) Structure

How to classify revenue and expense accounts into a structured P&L. Works with any chart of accounts by using `account_type` and `account_category`.

## Two Common Formats

### Format 1: By Nature of Expense (default)

Groups expenses by what they are (materials, labor, depreciation). Simpler, works for most companies.

```
Revenue                                          X,XXX,XXX.XX
Other operating income                              XX,XXX.XX
                                                ─────────────
Total Income                                     X,XXX,XXX.XX

Raw materials and consumables                     (XXX,XXX.XX)
Employee costs                                    (XXX,XXX.XX)
  - Wages and salaries              (XXX,XXX.XX)
  - Social security / benefits       (XX,XXX.XX)
Depreciation and amortization                      (XX,XXX.XX)
Other operating expenses                          (XXX,XXX.XX)
                                                ─────────────
Operating Profit (Loss)                             XXX,XXX.XX

Financial income                                      X,XXX.XX
Financial expenses                                  (XX,XXX.XX)
                                                ─────────────
Profit (Loss) Before Tax                            XXX,XXX.XX

Income tax expense                                  (XX,XXX.XX)
                                                ─────────────
Net Profit (Loss)                                   XXX,XXX.XX
```

### Format 2: By Function of Expense

Groups expenses by purpose (COGS, selling, admin). Requires cost center tracking.

```
Revenue                                          X,XXX,XXX.XX
Cost of goods sold                                (XXX,XXX.XX)
                                                ─────────────
Gross Profit                                       XXX,XXX.XX

Selling and distribution expenses                 (XXX,XXX.XX)
General and administrative expenses               (XXX,XXX.XX)
Other operating income / (expenses)                  XX,XXX.XX
                                                ─────────────
Operating Profit (Loss)                             XXX,XXX.XX

Financial income                                      X,XXX.XX
Financial expenses                                  (XX,XXX.XX)
                                                ─────────────
Profit (Loss) Before Tax                            XXX,XXX.XX

Income tax expense                                  (XX,XXX.XX)
                                                ─────────────
Net Profit (Loss)                                   XXX,XXX.XX
```

## Account Classification

| P&L Section | account_type | account_category | Notes |
|-------------|-------------|-----------------|-------|
| Revenue / Sales | revenue | sales | Primary business revenue |
| Other operating income | revenue | other_income | Gains on asset disposal, grants, misc |
| Cost of goods sold | expense | cogs | Direct materials, direct labor, manufacturing overhead |
| Raw materials | expense | materials | Purchases of raw materials and consumables |
| Employee costs | expense | payroll | Wages, salaries, social security, benefits, pensions |
| Depreciation | expense | depreciation | Depreciation of PP&E, amortization of intangibles |
| Other operating expenses | expense | operating_expense | Rent, utilities, insurance, professional fees, travel |
| Selling expenses | expense | selling_expense | Marketing, commissions, shipping, advertising |
| Administrative expenses | expense | admin_expense | Office costs, legal, audit, management fees |
| Financial income | revenue | financial_income | Interest income, FX gains, investment income |
| Financial expenses | expense | financial_expense | Interest expense, FX losses, bank charges |
| Income tax | expense | tax_expense | Corporate income tax, deferred tax |

## Format Selection Logic

Choose format based on available data:
1. If the company tracks expenses by function (COGS, selling, admin categories exist) → **Format 2**
2. If expenses are tracked by nature only → **Format 1**
3. Ask the user which format they prefer if both are possible

To detect:
```
list_entities("account", {
    "legal_entity_id": ID,
    "account_type": "expense",
    "account_category": "cogs"
})
```
If COGS accounts exist, Format 2 is available.

## Key Margins to Calculate

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Gross Margin % | (Revenue - COGS) / Revenue × 100 | Product/service profitability |
| Operating Margin % | Operating Profit / Revenue × 100 | Core business efficiency |
| Net Margin % | Net Profit / Revenue × 100 | Bottom line profitability |
| EBITDA | Operating Profit + Depreciation | Cash-generating ability |

## Comparative Analysis

When presenting comparisons:
- Show absolute change and percentage change
- Flag items with >15% variance
- Use arrows or indicators: positive changes in revenue/profit, negative changes in expenses

```
| Line Item          | Current Period | Prior Period |  Change  |   %   |
|--------------------|---------------|-------------|----------|-------|
| Revenue            |  1,200,000.00 | 1,000,000.00| 200,000 | +20.0%|
| Operating expenses |   (800,000.00)| (750,000.00)| (50,000)| +6.7% |
| Net profit         |    280,000.00 |   175,000.00| 105,000 | +60.0%|
```
