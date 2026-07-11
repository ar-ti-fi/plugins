#!/usr/bin/env python3
"""
plugin_versions.py — plugin version discipline for the Artifi marketplace.

Claude.ai's plugin marketplace caches installed plugins BY VERSION: pushing new
content under an unchanged version means users keep the stale cached copy even
after reinstalling. Every content change must therefore bump the plugin version
in BOTH plugins/<name>/.claude-plugin/plugin.json and
plugins/.claude-plugin/marketplace.json.

This script makes that mechanical:

  # bump (use when you changed a plugin's content):
  python3 plugins/scripts/plugin_versions.py --bump artifi-ee-vat-declaration minor

  # verify (CI runs this in publish-plugins.yml before syncing to ar-ti-fi/plugins):
  python3 plugins/scripts/plugin_versions.py --check

The lock file plugins/.claude-plugin/versions.lock.json stores, per plugin, the
version and a content hash at the moment of the last bump. --check fails when a
plugin's content hash changed but its version did not, or when plugin.json and
marketplace.json disagree.

Bump levels: major = breaking (commands removed/renamed, output format changed),
minor = new features/commands, patch = fixes and doc/text updates.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

PLUGINS_DIR = Path(__file__).resolve().parent.parent
MARKETPLACE = PLUGINS_DIR / ".claude-plugin" / "marketplace.json"
LOCK = PLUGINS_DIR / ".claude-plugin" / "versions.lock.json"

# Files that never affect published behavior.
IGNORED_NAMES = {".DS_Store"}


def plugin_dirs():
    for p in sorted(PLUGINS_DIR.iterdir()):
        if p.is_dir() and (p / ".claude-plugin" / "plugin.json").exists():
            yield p


def content_hash(plugin_dir: Path) -> str:
    """Deterministic hash over every file in the plugin (path + bytes)."""
    h = hashlib.sha256()
    for f in sorted(plugin_dir.rglob("*")):
        if not f.is_file() or f.name in IGNORED_NAMES or "__pycache__" in f.parts:
            continue
        h.update(str(f.relative_to(plugin_dir)).encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def marketplace_entry(marketplace: dict, name: str):
    for entry in marketplace["plugins"]:
        if entry["name"] == name:
            return entry
    return None


def next_version(version: str, level: str) -> str:
    try:
        major, minor, patch = (int(x) for x in version.split("."))
    except ValueError:
        raise SystemExit(f"Cannot parse version '{version}' — expected MAJOR.MINOR.PATCH")
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def cmd_check() -> int:
    lock = load(LOCK) if LOCK.exists() else {}
    marketplace = load(MARKETPLACE)
    errors = []

    for pdir in plugin_dirs():
        name = pdir.name
        plugin = load(pdir / ".claude-plugin" / "plugin.json")
        version = plugin.get("version", "")
        entry = marketplace_entry(marketplace, name)

        if entry is None:
            errors.append(f"{name}: missing from marketplace.json")
        elif entry.get("version") != version:
            errors.append(
                f"{name}: version mismatch — plugin.json={version}, "
                f"marketplace.json={entry.get('version')}"
            )

        current = content_hash(pdir)
        locked = lock.get(name)
        if locked is None:
            errors.append(
                f"{name}: not in versions.lock.json — run "
                f"'plugin_versions.py --bump {name} patch' (or --init once)"
            )
        elif locked["content_hash"] != current and locked["version"] == version:
            errors.append(
                f"{name}: CONTENT CHANGED but version is still {version} — "
                f"Claude.ai will keep serving the cached old copy. Run "
                f"'python3 plugins/scripts/plugin_versions.py --bump {name} "
                f"<major|minor|patch>'"
            )

    if errors:
        print("Plugin version check FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"Plugin version check OK ({len(list(plugin_dirs()))} plugins)")
    return 0


def cmd_bump(name: str, level: str) -> int:
    pdir = PLUGINS_DIR / name
    pjson_path = pdir / ".claude-plugin" / "plugin.json"
    if not pjson_path.exists():
        raise SystemExit(f"No such plugin: {name}")

    plugin = load(pjson_path)
    old = plugin.get("version", "0.0.0")
    new = next_version(old, level)
    plugin["version"] = new
    save(pjson_path, plugin)

    marketplace = load(MARKETPLACE)
    entry = marketplace_entry(marketplace, name)
    if entry is None:
        raise SystemExit(f"{name} missing from marketplace.json — add it first")
    entry["version"] = new
    save(MARKETPLACE, marketplace)

    lock = load(LOCK) if LOCK.exists() else {}
    lock[name] = {"version": new, "content_hash": content_hash(pdir)}
    save(LOCK, dict(sorted(lock.items())))

    print(f"{name}: {old} → {new} (plugin.json + marketplace.json + lock updated)")
    return 0


def cmd_init() -> int:
    """Initialize the lock from current state (first adoption only)."""
    lock = {}
    for pdir in plugin_dirs():
        plugin = load(pdir / ".claude-plugin" / "plugin.json")
        lock[pdir.name] = {
            "version": plugin.get("version", "0.0.0"),
            "content_hash": content_hash(pdir),
        }
    save(LOCK, dict(sorted(lock.items())))
    print(f"Initialized {LOCK} with {len(lock)} plugins")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="verify versions (CI)")
    g.add_argument("--bump", nargs=2, metavar=("PLUGIN", "LEVEL"),
                   help="bump a plugin: LEVEL is major|minor|patch")
    g.add_argument("--init", action="store_true",
                   help="initialize the lock from current state")
    args = ap.parse_args()

    if args.check:
        return cmd_check()
    if args.init:
        return cmd_init()
    name, level = args.bump
    if level not in ("major", "minor", "patch"):
        raise SystemExit("LEVEL must be major, minor or patch")
    return cmd_bump(name, level)


if __name__ == "__main__":
    sys.exit(main())
