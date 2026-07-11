# Arfiti Plugins

AI-powered plugins that give finance and accounting teams superpowers inside Claude, Cursor, and other AI tools. Each plugin packages domain knowledge — reporting formats, tax rules, compliance workflows — so your AI assistant handles the details correctly.

## Available Plugins

### Core

Universal plugins that work with any chart of accounts and any country.

| Plugin | What it does | Commands |
|--------|-------------|----------|
| [artifi-core-financial-reports](./artifi-core-financial-reports) | Financial reporting suite: Balance Sheet, P&L, Cash Flow, Trial Balance, Aging Analysis, and Dimension Analysis. Discovers account properties dynamically — works with any COA. | `/balance-sheet` `/profit-and-loss` `/cash-flow` `/trial-balance` `/aged-receivables` `/aged-payables` `/dimension-analysis` `/financial-summary` |
| [artifi-core-budget-planning](./artifi-core-budget-planning) | Budget planning: annual/quarterly budgets, forecasting from actuals, employee cost budgeting with burden rates, and project budgeting. | `/create-budget` `/forecast-budget` `/preview-budget` `/review-variance` |
| [artifi-core-cost-allocation](./artifi-core-cost-allocation) | Cost allocation across departments, projects, or dimensions. Standalone mode (from GL balances) and document-linked mode (from a specific bill/invoice with full traceability). | `/run-allocation` `/preview-allocation` |
| [artifi-core-implementation-consultant](./artifi-core-implementation-consultant) | ERP migration consultant. Guides customers through the full migration journey: chart of accounts setup, opening balances with open transactions (individual AR invoices, AP bills, fixed assets), master data import, gap period transaction processing, and go-live verification. Supports 4 migration paths — Connector (Merit/QBO/SmartAccounts), CSV/Manual, Greenfield, and Hybrid. Features advisory intelligence that scans the balance sheet to detect what additional data is needed. | `/start-migration` `/migration-status` `/import-data` `/verify-migration` `/close-migration` |
| [artifi-core-reconciliation](./artifi-core-reconciliation) | Payment-to-invoice reconciliation. Automated 6-pass matching via reconciliation agent, then guided manual matching for complex cases — N:N splits, partial payments, rounding write-offs. Supports AR and AP. | `/reconcile` `/match-payment` `/reconciliation-status` |
| [artifi-core-country-setup](./artifi-core-country-setup) | Generates country-specific tax and payroll configuration templates. Researches VAT/GST rates, tax authorities, withholding taxes, and payroll rules to produce structured JSON for onboarding. | `/generate-country-template` |
| [artifi-credit-intelligence](./artifi-credit-intelligence) | Credit intelligence on a borrower's live general ledger. Produces real-time credit memos with DSCR, leverage, working-capital cycle, concentration risk, and early-warning signals — with citations back to specific GL transactions. Designed for banks, alt lenders, and PE credit teams monitoring portfolio borrowers. | `/credit-read` `/covenant-monitor` `/cash-runway` `/borrower-watchlist` |
| [artifi-fund-servicing](./artifi-fund-servicing) | Fund-servicing back office on an AI-native ledger. Strikes NAV, accrues management/performance fees, processes investor subscriptions and redemptions, maintains the cap table, and produces investor statements. The accounting layer behind tokenized funds, FoFs, and private-market vehicles. | `/nav-strike` `/investor-statement` `/cap-table` |

### Estonia (EE)

| Plugin | What it does | Commands |
|--------|-------------|----------|
| [artifi-ee-year-end-bookkeeping](./artifi-ee-year-end-bookkeeping) | Builds a full year's accounting from scratch for Estonian companies (OÜ/AS). Guides through chart of accounts setup, opening balances, bank statement processing (month by month), source document posting, reconciliation, and period close — preparing the entity for annual report filing. | `/setup-entity` `/upload-opening-balance` `/process-bank-statements` `/fill-gaps` `/reconcile-and-close` `/check-progress` |
| [artifi-ee-annual-report](./artifi-ee-annual-report) | Prepares the full annual report (balance sheet, income statement, notes, management report) and generates XBRL for e-Business Register filing. Uses the et-gaap-2026 taxonomy. | `/prepare-annual-report` `/check-prerequisites` `/generate-xbrl-file` |
| [artifi-ee-payroll-calculator](./artifi-ee-payroll-calculator) | Calculates gross-to-net payroll with Estonian tax formulas (social tax, income tax, unemployment insurance, funded pension) and generates TSD declarations for EMTA. | `/calculate-payroll` `/generate-tsd` |
| [artifi-ee-vat-declaration](./artifi-ee-vat-declaration) | Prepares & validates VAT returns (KMD2 machine CSV + XML) and KMD INF annexes. Runs a pre-close validation gate, then generates. The EC Sales List (Form VD) is a separate filing. Dynamically discovers tax codes and maps to KMD lines. | `/prepare-vat-declaration` (add `validate` to run the gate only) `/prepare-ec-sales-list` |

More countries coming soon.

## Getting Started

### Option 1: Clone the repository

```bash
git clone https://github.com/ar-ti-fi/plugins.git
```

Add the plugin directory to your Claude Desktop project or Cursor workspace.

### Option 2: Download ZIP

[Download latest ZIP](https://github.com/ar-ti-fi/plugins/archive/refs/heads/main.zip)

### Option 3: Via Arfiti admin dashboard

If you use [Arfiti](https://ar-ti-fi.com), plugins are available directly from the admin dashboard under **Administration > Plugins** with one-click download.

## How Plugins Work

Each plugin is a self-contained package that extends your AI assistant with domain-specific knowledge:

```
plugin-name/
  .claude-plugin/plugin.json    # Plugin manifest (name, version, description)
  .mcp.json                     # MCP server connection (links to Arfiti backend)
  commands/                     # Slash commands (e.g. /prepare-annual-report)
  skills/                       # Detailed workflow instructions + reference data
    skill-name/
      SKILL.md                  # Step-by-step workflow with checkpoints
      references/               # Tax tables, form structures, filing guides
  scripts/                      # Deterministic generators (XML, XBRL, etc.)
```

**Commands** are entry points — the user types `/prepare-vat-declaration` and the AI follows the workflow defined in the skill.

**Skills** contain the actual knowledge — multi-step workflows with mandatory checkpoints, validation rules, and reference data.

**References** are the source of truth — tax formulas, XBRL element mappings, regulatory form structures. The AI reads these instead of guessing.

**Scripts** generate deterministic output (XBRL, XML declarations) where AI generation would be unreliable. Claude builds compact JSON, the script produces valid XML with hardcoded namespaces and validated structure.

## Contributing a Country Plugin

We welcome contributions for new countries. A typical compliance plugin needs:

1. **Annual report** — Balance sheet and income statement formats, local GAAP taxonomy, filing portal instructions
2. **VAT/GST/Sales tax** — Return form structure, tax codes and rates, filing format
3. **Payroll** — Tax formulas (income tax, social contributions, pension), payslip format, declaration forms

See any existing country plugin for the structure. Open an issue or PR to get started.

## Versioning (required on every content change)

Claude.ai caches installed plugins **by version** — shipping changed content under an
unchanged version means users keep the stale cached copy even after reinstalling.
Whenever you change anything inside a plugin, bump its version:

```bash
python3 plugins/scripts/plugin_versions.py --bump <plugin-name> <major|minor|patch>
```

- **major** — breaking: commands removed/renamed, output format changed
- **minor** — new commands or features
- **patch** — fixes, doc/text updates

The bump updates `plugin.json`, `marketplace.json`, and `versions.lock.json` together.
CI (`publish-plugins.yml`) runs `plugin_versions.py --check` before syncing to the
public marketplace repo and **fails the publish** if content changed without a bump.

Why this exists (per the official plugin-marketplace docs): when `version` is set,
clients pin the cached plugin to that exact string — *"you must bump it every time you
want users to receive changes; pushing new commits alone is not enough."* The docs also
advise against setting `version` in both `plugin.json` and the marketplace entry
(plugin.json silently wins); we deliberately keep both **because the CI check enforces
they are identical**, which removes the masking risk while every client surface sees
the same version. Do not remove one of them without updating the checker.

## License

[MIT](./LICENSE) - Arfiti Technologies OU
