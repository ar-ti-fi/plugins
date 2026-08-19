#!/usr/bin/env python3
"""Validate every plugin's .mcp.json transport config.

Why this exists: from April to 2026-08-19 all 12 plugins shipped
`{"type": "url", "url": "https://mcp.ar-ti-fi.com/mcp"}`. There is no `url`
transport — the valid values are stdio, http (alias streamable-http), sse and
ws. Claude Code tolerated it (marketplace added fine, commands worked), but
Cowork's stricter plugin sync rejected the ENTIRE repo with a generic
"Marketplace sync failed", so every plugin was invisible in Cowork for five
weeks.

Nothing caught it: `claude plugin validate` inspects plugin.json, skill/agent/
command frontmatter and hooks/hooks.json — it never reads .mcp.json. Hence
this check, wired into the publish workflow ahead of the marketplace sync.

Usage: python3 plugins/scripts/check_mcp_configs.py [plugins_dir]
Exit 0 = all good, 1 = at least one invalid config.
"""
import json
import pathlib
import sys

# https://code.claude.com/docs/en/mcp — .mcp.json transport types
URL_TRANSPORTS = {"http", "streamable-http", "sse", "ws"}
ALL_TRANSPORTS = URL_TRANSPORTS | {"stdio"}


def check_file(path: pathlib.Path) -> list:
    """Return a list of human-readable problems for one .mcp.json."""
    problems = []
    try:
        data = json.load(path.open(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        return [f"{path}: unreadable/invalid JSON: {exc}"]

    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        return [f"{path}: missing or non-object 'mcpServers'"]

    for name, cfg in servers.items():
        if not isinstance(cfg, dict):
            problems.append(f"{path} [{name}]: server config must be an object")
            continue

        transport = cfg.get("type")
        has_url = bool(cfg.get("url"))
        has_command = bool(cfg.get("command"))

        if transport is not None and transport not in ALL_TRANSPORTS:
            problems.append(
                f"{path} [{name}]: invalid transport {transport!r} — "
                f"use one of {sorted(ALL_TRANSPORTS)}"
                + (' (a url endpoint wants "http")' if has_url else "")
            )
            continue

        if has_url:
            # A url entry with no type is read as stdio and fails at load.
            if transport is None:
                problems.append(
                    f'{path} [{name}]: has "url" but no "type" — add "type": "http" '
                    f"(or sse/ws); an entry with no type is read as stdio"
                )
            elif transport not in URL_TRANSPORTS:
                problems.append(
                    f"{path} [{name}]: transport {transport!r} cannot be used with "
                    f'"url" — use one of {sorted(URL_TRANSPORTS)}'
                )
        elif has_command:
            if transport not in (None, "stdio"):
                problems.append(
                    f"{path} [{name}]: transport {transport!r} needs a \"url\", "
                    f'not "command"'
                )
        else:
            problems.append(f'{path} [{name}]: needs either "url" or "command"')

    return problems


def main() -> int:
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "plugins")
    files = sorted(root.glob("*/.mcp.json"))
    if not files:
        print(f"No .mcp.json files found under {root} — nothing to check")
        return 0

    problems = [p for f in files for p in check_file(f)]
    if problems:
        print(f"MCP config check FAILED ({len(problems)} problem(s)):")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print(f"MCP config check OK ({len(files)} plugin(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
