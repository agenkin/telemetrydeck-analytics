#!/usr/bin/env python3
"""Pre-release test harness for telemetrydeck-analytics.

Run before tagging a release:

    python3 scripts/test_release.py            # all offline checks
    python3 scripts/test_release.py --with-claude   # also exercise `claude plugin ...`

Exits non-zero if any check fails. Stdlib-only.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN_JSON = ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = ROOT / ".claude-plugin" / "marketplace.json"
SKILLS_DIR = ROOT / "skills"
TDQ_PY = SKILLS_DIR / "analytics" / "tdq.py"
TDQ_WRAPPER = ROOT / "bin" / "tdq"
MAIN_SKILL = SKILLS_DIR / "analytics" / "SKILL.md"

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"

failures: list[str] = []
warnings: list[str] = []


def ok(msg: str) -> None:
    print(f"{GREEN}PASS{RESET} {msg}")


def fail(msg: str) -> None:
    print(f"{RED}FAIL{RESET} {msg}")
    failures.append(msg)


def warn(msg: str) -> None:
    print(f"{YELLOW}WARN{RESET} {msg}")
    warnings.append(msg)


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Tiny flat-YAML frontmatter parser. Only handles `key: value` lines."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{path}: no frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError(f"{path}: unterminated frontmatter")
    out: dict[str, str] = {}
    for line in text[3:end].splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip()
    return out


def check_plugin_marketplace_sync() -> None:
    plugin = json.loads(PLUGIN_JSON.read_text())
    market = json.loads(MARKETPLACE_JSON.read_text())

    for k in ("name", "version", "description"):
        if k not in plugin:
            fail(f"plugin.json missing `{k}`")
    for k in ("name", "plugins"):
        if k not in market:
            fail(f"marketplace.json missing `{k}`")

    plugins = market.get("plugins") or []
    if not plugins:
        fail("marketplace.json `plugins` is empty")
        return

    entry = next((p for p in plugins if p.get("name") == plugin.get("name")), None)
    if entry is None:
        fail(f"marketplace.json has no entry for `{plugin.get('name')}`")
        return

    if entry.get("version") != plugin.get("version"):
        fail(
            f"version drift: plugin.json={plugin.get('version')} "
            f"marketplace.json={entry.get('version')}"
        )
    else:
        ok(f"version sync: {plugin['version']}")

    for k in ("source", "description"):
        if k not in entry:
            fail(f"marketplace.json plugin entry missing `{k}`")


def check_skill_frontmatter() -> None:
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    if not skill_files:
        fail("no SKILL.md files found")
        return

    plugin_version = json.loads(PLUGIN_JSON.read_text()).get("version")

    for path in skill_files:
        try:
            fm = parse_frontmatter(path)
        except ValueError as e:
            fail(str(e))
            continue

        if "description" not in fm:
            fail(f"{path.relative_to(ROOT)}: missing `description`")
        elif len(fm["description"]) < 20:
            warn(f"{path.relative_to(ROOT)}: description suspiciously short")

        # Main analytics skill must have `name` (skills.sh + model invocation).
        if path.parent.name == "analytics" and "name" not in fm:
            fail(f"{path.relative_to(ROOT)}: missing `name`")

        # Version drift inside SKILL.md frontmatter.
        if "version" not in fm:
            warn(f"{path.relative_to(ROOT)}: missing `version` (expected {plugin_version})")
        elif fm["version"] != plugin_version:
            fail(
                f"{path.relative_to(ROOT)}: version `{fm['version']}` "
                f"!= plugin.json `{plugin_version}`"
            )

    ok(f"frontmatter parsed for {len(skill_files)} SKILL.md files")


def check_python_syntax() -> None:
    if not TDQ_PY.is_file():
        fail(f"{TDQ_PY.relative_to(ROOT)} not found")
        return
    src = TDQ_PY.read_text(encoding="utf-8")
    try:
        ast.parse(src, filename=str(TDQ_PY))
    except SyntaxError as e:
        fail(f"{TDQ_PY.relative_to(ROOT)}: {e}")
        return
    ok(f"{TDQ_PY.relative_to(ROOT)} parses")


def check_bash_syntax() -> None:
    if not TDQ_WRAPPER.is_file():
        fail(f"{TDQ_WRAPPER.relative_to(ROOT)} not found")
        return
    r = subprocess.run(
        ["bash", "-n", str(TDQ_WRAPPER)],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        fail(f"{TDQ_WRAPPER.relative_to(ROOT)}: {r.stderr.strip()}")
    else:
        ok(f"{TDQ_WRAPPER.relative_to(ROOT)} parses")


def check_cli_help() -> None:
    if not TDQ_PY.is_file():
        fail(f"{TDQ_PY.relative_to(ROOT)} not found")
        return
    try:
        r = subprocess.run(
            [sys.executable, str(TDQ_PY), "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except FileNotFoundError as e:
        fail(f"`tdq.py --help` could not run: {e}")
        return
    if r.returncode != 0:
        fail(f"`tdq.py --help` exit {r.returncode}: {r.stderr.strip()[:200]}")
        return
    if "usage" not in r.stdout.lower():
        fail("`tdq.py --help` output missing `usage`")
        return
    ok("`tdq.py --help` works")


def check_wrapper_help() -> None:
    if not TDQ_WRAPPER.is_file():
        fail(f"{TDQ_WRAPPER.relative_to(ROOT)} not found")
        return
    try:
        r = subprocess.run(
            [str(TDQ_WRAPPER), "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except FileNotFoundError as e:
        fail(f"`bin/tdq --help` could not run: {e}")
        return
    if r.returncode != 0:
        fail(f"`bin/tdq --help` exit {r.returncode}: {r.stderr.strip()[:200]}")
        return
    ok("`bin/tdq --help` works")


def check_slash_command_refs() -> None:
    """Every `/telemetrydeck-analytics:<cmd>` mentioned in the main SKILL.md
    must have a matching `skills/<cmd>/SKILL.md`."""
    text = MAIN_SKILL.read_text(encoding="utf-8")
    refs = set(re.findall(r"/telemetrydeck-analytics:([a-z][a-z0-9_-]*)", text))
    if not refs:
        warn("main SKILL.md references no slash commands — skipping ref check")
        return
    missing = []
    for cmd in sorted(refs):
        if not (SKILLS_DIR / cmd / "SKILL.md").is_file():
            missing.append(cmd)
    if missing:
        fail(f"slash commands referenced but no SKILL.md: {', '.join(missing)}")
    else:
        ok(f"all {len(refs)} slash command references resolve")


def check_with_claude_cli() -> None:
    """Optional: end-to-end `claude plugin` smoke test."""
    if not _have("claude"):
        warn("`claude` CLI not on PATH — skipping --with-claude checks")
        return

    r = subprocess.run(
        ["claude", "plugin", "validate", "."],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if r.returncode != 0:
        fail(f"`claude plugin validate .` failed: {r.stderr.strip()[:300]}")
    else:
        ok("`claude plugin validate .`")

    plugin_data = json.loads(PLUGIN_JSON.read_text())
    market_data = json.loads(MARKETPLACE_JSON.read_text())
    plugin_name = plugin_data["name"]
    market_name = market_data.get("name", plugin_name)

    # add → install → list → uninstall → remove. Best-effort cleanup.
    added = installed = False
    try:
        r = subprocess.run(
            ["claude", "plugin", "marketplace", "add", "./"],
            cwd=ROOT, capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0:
            fail(f"`marketplace add` failed: {r.stderr.strip()[:300]}")
            # `added` is still False here so finally skips cleanup — correct
            return
        added = True

        r = subprocess.run(
            ["claude", "plugin", "install", f"{plugin_name}@{market_name}"],
            cwd=ROOT, capture_output=True, text=True, timeout=120,
        )
        if r.returncode != 0:
            fail(f"`plugin install` failed: {r.stderr.strip()[:300]}")
            return
        installed = True

        r = subprocess.run(
            ["claude", "plugin", "list"],
            capture_output=True, text=True, timeout=30,
        )
        if plugin_name not in r.stdout:
            fail(f"`plugin list` does not show `{plugin_name}` after install")
        else:
            ok(f"installed `{plugin_name}` via local marketplace")
    finally:
        if installed:
            subprocess.run(
                ["claude", "plugin", "uninstall", f"{plugin_name}@{market_name}"],
                capture_output=True, text=True, timeout=60,
            )
        if added:
            subprocess.run(
                ["claude", "plugin", "marketplace", "remove", market_name],
                capture_output=True, text=True, timeout=60,
            )


def _have(cmd: str) -> bool:
    return subprocess.run(
        ["which", cmd], capture_output=True, text=True
    ).returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--with-claude",
        action="store_true",
        help="Also run `claude plugin validate / install / uninstall` end-to-end.",
    )
    args = ap.parse_args()

    print(f"Running pre-release checks in {ROOT}\n")

    check_plugin_marketplace_sync()
    check_skill_frontmatter()
    check_python_syntax()
    check_bash_syntax()
    check_cli_help()
    check_wrapper_help()
    check_slash_command_refs()
    if args.with_claude:
        print()
        check_with_claude_cli()

    print()
    if failures:
        print(f"{RED}{len(failures)} check(s) failed{RESET}")
        for f in failures:
            print(f"  - {f}")
        return 1
    if warnings:
        print(f"{YELLOW}{len(warnings)} warning(s){RESET}")
    print(f"{GREEN}all checks passed{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
