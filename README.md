# Arfiti Plugins

Plugins for Claude, Cursor and other tools for running the accounting and finance system.

## Available Plugins

| Plugin | Description | Country |
|--------|-------------|---------|
| [arfiti-ee-annual-report](./arfiti-ee-annual-report) | Estonian annual report preparation & XBRL filing | EE |
| [arfiti-ee-payroll-calculator](./arfiti-ee-payroll-calculator) | Estonian payroll calculation & TSD declaration | EE |
| [arfiti-ee-vat-declaration](./arfiti-ee-vat-declaration) | Estonian VAT declaration & EC sales list | EE |

## Installation

### Claude Desktop / Claude Code

Clone or download and add the plugin directory to your Claude project:

```bash
git clone https://github.com/porydchik/ar-ti-fi.git
```

Then add the plugin directory path to your Claude project settings.

### Download ZIP

Download the latest release as a ZIP file from [Releases](https://github.com/porydchik/ar-ti-fi/archive/refs/heads/main.zip).

## Plugin Structure

Each plugin follows the Claude plugin format:

```
plugin-name/
  .claude-plugin/plugin.json   # Plugin manifest
  .mcp.json                    # MCP server configuration
  commands/                    # Slash commands
  skills/                      # Skill definitions + references
```

## License

Proprietary - Arfiti OÜ
