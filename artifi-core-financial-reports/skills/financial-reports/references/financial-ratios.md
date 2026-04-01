# Financial Ratios Reference

Key ratios for the `/financial-summary` command. All ratios are calculated from balance sheet and income statement data.

## Liquidity Ratios

Measure the company's ability to meet short-term obligations.

| Ratio | Formula | Good Range | Interpretation |
|-------|---------|-----------|----------------|
| Current Ratio | Current Assets / Current Liabilities | 1.5 - 3.0 | >1 means can cover short-term debts. <1 is a warning sign. >3 may indicate idle assets. |
| Quick Ratio | (Current Assets - Inventory) / Current Liabilities | 1.0 - 2.0 | More conservative — excludes inventory which may not be quickly liquidated. |
| Cash Ratio | Cash / Current Liabilities | 0.2 - 0.5 | Most conservative — only liquid cash. Very low = potential cash crunch. |

## Profitability Ratios

Measure how efficiently the company generates profit.

| Ratio | Formula | Notes |
|-------|---------|-------|
| Gross Margin % | (Revenue - COGS) / Revenue × 100 | Product/service profitability. Industry-specific benchmarks. |
| Operating Margin % | Operating Profit / Revenue × 100 | Core business profitability after all operating costs. |
| Net Margin % | Net Profit / Revenue × 100 | Bottom line profitability after all costs including tax. |
| EBITDA Margin % | (Operating Profit + Depreciation) / Revenue × 100 | Cash-generating ability independent of asset base. |
| Return on Equity (ROE) | Net Profit / Average Total Equity × 100 | Return generated on shareholder investment. |
| Return on Assets (ROA) | Net Profit / Average Total Assets × 100 | How efficiently assets generate profit. |

## Leverage Ratios

Measure the company's debt position and financial risk.

| Ratio | Formula | Good Range | Interpretation |
|-------|---------|-----------|----------------|
| Debt-to-Equity | Total Liabilities / Total Equity | 0.5 - 2.0 | Higher = more leveraged. Industry-dependent. |
| Debt-to-Assets | Total Liabilities / Total Assets | 0.3 - 0.6 | What proportion of assets is financed by debt. |
| Interest Coverage | Operating Profit / Interest Expense | >3.0 | Ability to pay interest. <1.5 is risky. |
| Equity Ratio | Total Equity / Total Assets | 0.4 - 0.7 | Owner-financed proportion of assets. |

## Efficiency Ratios

Measure how effectively the company uses its resources.

| Ratio | Formula | Notes |
|-------|---------|-------|
| Days Sales Outstanding (DSO) | (Trade Receivables / Revenue) × 365 | Average days to collect payment. Lower is better. |
| Days Payable Outstanding (DPO) | (Trade Payables / COGS) × 365 | Average days to pay vendors. Higher preserves cash but watch relationships. |
| Inventory Days | (Inventory / COGS) × 365 | Days of inventory on hand. Lower = efficient (but watch stockouts). |
| Cash Conversion Cycle | DSO + Inventory Days - DPO | Days between paying suppliers and collecting from customers. Lower is better. |
| Asset Turnover | Revenue / Average Total Assets | How efficiently assets generate revenue. |

## Presentation Format

```
FINANCIAL RATIOS SUMMARY
═══════════════════════════════════════════════════
                              Current    Prior     Change
LIQUIDITY
  Current Ratio               2.15       1.89      +0.26
  Quick Ratio                 1.42       1.21      +0.21

PROFITABILITY
  Gross Margin %              45.2%      42.8%     +2.4pp
  Operating Margin %          18.5%      15.2%     +3.3pp
  Net Margin %                14.1%      11.8%     +2.3pp
  ROE                         22.3%      18.7%     +3.6pp

LEVERAGE
  Debt-to-Equity              0.85       0.92      -0.07
  Interest Coverage           8.2x       6.5x      +1.7x

EFFICIENCY
  DSO                         38 days    42 days   -4 days
  DPO                         31 days    28 days   +3 days
  Cash Conversion Cycle       22 days    29 days   -7 days
═══════════════════════════════════════════════════
```

## Interpretation Guidelines

When analyzing ratios:
1. **Trend matters more than absolute value** — is the ratio improving or deteriorating?
2. **Industry context** — a 2% net margin is excellent for grocery, poor for SaaS
3. **Interrelationships** — high growth may temporarily hurt margins; high DSO with rising revenue may be acceptable
4. **Avoid standalone conclusions** — always consider multiple ratios together
