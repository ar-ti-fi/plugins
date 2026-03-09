# Arfiti Plugins

AI-powered plugins that give finance and accounting teams superpowers inside Claude, Cursor, and other AI tools. Each plugin packages country-specific compliance knowledge, tax rules, and reporting formats so your AI assistant handles the details correctly.

## Why plugins?

Accounting rules differ by country. A VAT return in Estonia looks nothing like one in Germany or the UK. These plugins encode that knowledge — tax formulas, filing formats, regulatory deadlines, XBRL taxonomies — so your AI assistant produces compliant output without hallucinating rules.

## Available Plugins

### Estonia (EE)

| Plugin | What it does |
|--------|-------------|
| [arfiti-ee-annual-report](./arfiti-ee-annual-report) | Prepares the full annual report (balance sheet, income statement, notes, management report) and generates XBRL mapping for e-Business Register filing. Uses the et-gaap-2026 taxonomy. |
| [arfiti-ee-payroll-calculator](./arfiti-ee-payroll-calculator) | Calculates gross-to-net payroll with Estonian tax formulas (social tax, income tax, unemployment insurance, funded pension) and generates TSD declarations for EMTA. |
| [arfiti-ee-vat-declaration](./arfiti-ee-vat-declaration) | Prepares VAT returns (KMD form), KMD INF annexes, and EC Sales Lists. Validates against Estonian tax codes and VAT rates. |

More countries coming soon.

## Getting Started

### Option 1: Clone the repository

```bash
git clone https://github.com/porydchik/ar-ti-fi.git
```

Add the plugin directory to your Claude Desktop project or Cursor workspace.

### Option 2: Download ZIP

[Download latest ZIP](https://github.com/porydchik/ar-ti-fi/archive/refs/heads/main.zip)

### Option 3: Via Arfiti admin dashboard

If you use [Arfiti](https://arfiti.com), plugins are available directly from the admin dashboard under **Administration > Plugins** with one-click download.

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
```

**Commands** are entry points — the user types `/prepare-vat-declaration` and the AI follows the workflow defined in the skill.

**Skills** contain the actual knowledge — multi-step workflows with mandatory checkpoints, validation rules, and reference data (tax rates, form field mappings, filing instructions).

**References** are the source of truth — tax formulas, XBRL element mappings, regulatory form structures. The AI reads these instead of guessing.

## Contributing a Country Plugin

We welcome contributions for new countries. A typical compliance plugin needs:

1. **Annual report** — Balance sheet and income statement formats, local GAAP taxonomy, filing portal instructions
2. **VAT/GST/Sales tax** — Return form structure, tax codes and rates, filing format
3. **Payroll** — Tax formulas (income tax, social contributions, pension), payslip format, declaration forms

See any existing country plugin for the structure. Open an issue or PR to get started.

## License

[MIT](./LICENSE) - Arfiti Technologies OU
