#!/usr/bin/env python3
"""
AgentChanti KB Registry — Validation Script

Validates all content in the registry against the required schemas.
Checks:
  a. All .md files have required frontmatter fields
  b. All .yml error files have required fields per entry
  c. No duplicate IDs across entire registry
  d. All related_errors references in .yml point to existing IDs
  e. severity values are only: critical | warning | info
  f. category values are only: pattern | adr | doc | behavioral | error
  g. language values are only: all | python | javascript | typescript | java | go | rust | csharp
  h. version follows semver format X.Y.Z

Exit code 0 if all checks pass, 1 if any check fails.
"""

import sys
import re
import json
from pathlib import Path

import yaml

# ─── Constants ────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent

VALID_SEVERITIES = {"critical", "warning", "info"}
VALID_CATEGORIES = {"pattern", "adr", "doc", "behavioral", "error"}
VALID_LANGUAGES = {"all", "python", "javascript", "typescript", "java", "go", "rust", "csharp"}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

MD_REQUIRED_FIELDS = {"id", "title", "category", "language", "version", "created_at"}
YML_REQUIRED_FIELDS = {"id", "error_type", "severity", "pattern", "fix_template", "tags"}

# ─── Result tracking ──────────────────────────────────────────────────────────

class CheckResult:
    def __init__(self):
        self.errors = []
        self.passes = []

    def fail(self, check: str, message: str):
        self.errors.append((check, message))

    def ok(self, check: str, message: str):
        self.passes.append((check, message))

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0


results = CheckResult()

# ─── Helpers ──────────────────────────────────────────────────────────────────

def parse_md_frontmatter(path: Path) -> dict | None:
    """Parse YAML frontmatter from a .md file. Returns None on failure."""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None
    try:
        end = content.index("\n---", 3)
        yaml_text = content[3:end]
        return yaml.safe_load(yaml_text) or {}
    except (ValueError, yaml.YAMLError):
        return None


def parse_yml_file(path: Path) -> list | None:
    """Parse a .yml error file. Returns None on failure."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
        return None
    except yaml.YAMLError:
        return None


def find_md_files() -> list[Path]:
    dirs = ["patterns", "adrs", "docs", "behavioral"]
    files = []
    for d in dirs:
        files.extend((ROOT / d).rglob("*.md"))
    return files


def find_yml_files() -> list[Path]:
    return list((ROOT / "errors").rglob("*.yml"))


# ─── Check A: MD frontmatter fields ───────────────────────────────────────────

def check_md_frontmatter(md_files: list[Path]) -> dict[str, dict]:
    """Returns a dict of {str(path): frontmatter} for valid files."""
    valid = {}
    fail_count = 0

    for path in md_files:
        fm = parse_md_frontmatter(path)
        rel = path.relative_to(ROOT)

        if fm is None:
            results.fail("frontmatter", f"  ✗ {rel}: Missing or malformed frontmatter")
            fail_count += 1
            continue

        missing = MD_REQUIRED_FIELDS - set(fm.keys())
        if missing:
            results.fail("frontmatter", f"  ✗ {rel}: Missing fields: {', '.join(sorted(missing))}")
            fail_count += 1
        else:
            valid[str(path)] = fm

    if fail_count == 0:
        results.ok("frontmatter", f"  ✓ PASS [frontmatter] All {len(md_files)} .md files have valid frontmatter")
    else:
        results.fail("frontmatter", f"  ✗ FAIL [frontmatter] {fail_count}/{len(md_files)} .md files have frontmatter issues")

    return valid


# ─── Check B: YML error entry fields ──────────────────────────────────────────

def check_yml_entries(yml_files: list[Path]) -> dict[str, list]:
    """Returns a dict of {str(path): entries} for valid files."""
    valid = {}
    fail_count = 0
    total_entries = 0

    for path in yml_files:
        entries = parse_yml_file(path)
        rel = path.relative_to(ROOT)

        if entries is None:
            results.fail("yml-schema", f"  ✗ {rel}: Not a valid YAML list or parse error")
            fail_count += 1
            continue

        file_errors = []
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                file_errors.append(f"    Entry {i}: Not a dict")
                continue
            missing = YML_REQUIRED_FIELDS - set(entry.keys())
            if missing:
                file_errors.append(f"    Entry {i} (id={entry.get('id', '?')}): Missing fields: {', '.join(sorted(missing))}")

        if file_errors:
            results.fail("yml-schema", f"  ✗ {rel}:\n" + "\n".join(file_errors))
            fail_count += 1
        else:
            valid[str(path)] = entries
            total_entries += len(entries)

    if fail_count == 0:
        results.ok("yml-schema", f"  ✓ PASS [yml-schema] All {len(yml_files)} .yml files have valid entry schemas ({total_entries} total entries)")
    else:
        results.fail("yml-schema", f"  ✗ FAIL [yml-schema] {fail_count}/{len(yml_files)} .yml files have schema issues")

    return valid


# ─── Check C: No duplicate IDs ────────────────────────────────────────────────

def check_no_duplicate_ids(
    md_frontmatters: dict[str, dict],
    yml_entries: dict[str, list]
) -> set[str]:
    """Returns set of all known IDs."""
    id_locations: dict[str, list[str]] = {}

    for path_str, fm in md_frontmatters.items():
        id_val = str(fm.get("id", "")).strip()
        if id_val:
            id_locations.setdefault(id_val, []).append(f"{Path(path_str).relative_to(ROOT)} (frontmatter)")

    for path_str, entries in yml_entries.items():
        for entry in entries:
            id_val = str(entry.get("id", "")).strip()
            if id_val:
                id_locations.setdefault(id_val, []).append(f"{Path(path_str).relative_to(ROOT)}")

    duplicates = {id_val: locs for id_val, locs in id_locations.items() if len(locs) > 1}

    if duplicates:
        for id_val, locs in duplicates.items():
            loc_str = "\n      ".join(locs)
            results.fail("duplicate-id", f"  ✗ FAIL [duplicate-id] ID \"{id_val}\" found in:\n      {loc_str}")
    else:
        total = len(id_locations)
        results.ok("duplicate-id", f"  ✓ PASS [duplicate-id] All {total} IDs are unique")

    return set(id_locations.keys())


# ─── Check D: related_errors references exist ─────────────────────────────────

def check_related_errors(yml_entries: dict[str, list], all_ids: set[str]):
    fail_count = 0

    for path_str, entries in yml_entries.items():
        rel = Path(path_str).relative_to(ROOT)
        for entry in entries:
            related = entry.get("related_errors", []) or []
            for ref_id in related:
                if str(ref_id) not in all_ids:
                    results.fail("related-errors", f"  ✗ {rel}: Entry \"{entry.get('id', '?')}\" references unknown ID \"{ref_id}\"")
                    fail_count += 1

    if fail_count == 0:
        results.ok("related-errors", "  ✓ PASS [related-errors] All related_errors references point to existing IDs")
    else:
        results.fail("related-errors", f"  ✗ FAIL [related-errors] {fail_count} broken related_errors reference(s)")


# ─── Check E: severity values ─────────────────────────────────────────────────

def check_severity_values(yml_entries: dict[str, list]):
    fail_count = 0

    for path_str, entries in yml_entries.items():
        rel = Path(path_str).relative_to(ROOT)
        for entry in entries:
            sev = entry.get("severity", "")
            if sev not in VALID_SEVERITIES:
                results.fail("severity", f"  ✗ {rel}: Entry \"{entry.get('id', '?')}\" has invalid severity \"{sev}\" (must be: {', '.join(sorted(VALID_SEVERITIES))})")
                fail_count += 1

    if fail_count == 0:
        results.ok("severity", "  ✓ PASS [severity] All severity values are valid")
    else:
        results.fail("severity", f"  ✗ FAIL [severity] {fail_count} invalid severity value(s)")


# ─── Check F: category values ─────────────────────────────────────────────────

def check_category_values(md_frontmatters: dict[str, dict]):
    fail_count = 0

    for path_str, fm in md_frontmatters.items():
        rel = Path(path_str).relative_to(ROOT)
        cat = str(fm.get("category", "")).strip()
        if cat not in VALID_CATEGORIES:
            results.fail("category", f"  ✗ {rel}: Invalid category \"{cat}\" (must be: {', '.join(sorted(VALID_CATEGORIES))})")
            fail_count += 1

    if fail_count == 0:
        results.ok("category", f"  ✓ PASS [category] All category values are valid")
    else:
        results.fail("category", f"  ✗ FAIL [category] {fail_count} invalid category value(s)")


# ─── Check G: language values ─────────────────────────────────────────────────

def check_language_values(md_frontmatters: dict[str, dict]):
    fail_count = 0

    for path_str, fm in md_frontmatters.items():
        rel = Path(path_str).relative_to(ROOT)
        lang = str(fm.get("language", "")).strip()
        if lang not in VALID_LANGUAGES:
            results.fail("language", f"  ✗ {rel}: Invalid language \"{lang}\" (must be: {', '.join(sorted(VALID_LANGUAGES))})")
            fail_count += 1

    if fail_count == 0:
        results.ok("language", f"  ✓ PASS [language] All language values are valid")
    else:
        results.fail("language", f"  ✗ FAIL [language] {fail_count} invalid language value(s)")


# ─── Check H: version follows semver ──────────────────────────────────────────

def check_semver(md_frontmatters: dict[str, dict]):
    fail_count = 0

    for path_str, fm in md_frontmatters.items():
        rel = Path(path_str).relative_to(ROOT)
        ver = str(fm.get("version", "")).strip()
        if not SEMVER_RE.match(ver):
            results.fail("semver", f"  ✗ {rel}: Invalid version \"{ver}\" (must be X.Y.Z semver format)")
            fail_count += 1

    if fail_count == 0:
        results.ok("semver", f"  ✓ PASS [semver] All version fields follow semver format")
    else:
        results.fail("semver", f"  ✗ FAIL [semver] {fail_count} invalid version value(s)")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("AgentChanti KB Registry — Validation")
    print("=" * 60)
    print()

    md_files = find_md_files()
    yml_files = find_yml_files()

    print(f"Found {len(md_files)} .md files and {len(yml_files)} .yml files")
    print()

    # Run all checks
    md_frontmatters = check_md_frontmatter(md_files)
    yml_entries = check_yml_entries(yml_files)
    all_ids = check_no_duplicate_ids(md_frontmatters, yml_entries)
    check_related_errors(yml_entries, all_ids)
    check_severity_values(yml_entries)
    check_category_values(md_frontmatters)
    check_language_values(md_frontmatters)
    check_semver(md_frontmatters)

    # Print summary
    print()
    print("─" * 60)
    print("RESULTS")
    print("─" * 60)

    for check, msg in results.passes:
        print(msg)

    if results.errors:
        print()
        for check, msg in results.errors:
            print(msg)

    print()
    print("─" * 60)

    if results.passed:
        print(f"✓ ALL CHECKS PASSED ({len(results.passes)} checks)")
        print("─" * 60)
        return 0
    else:
        print(f"✗ {len(results.errors)} CHECK(S) FAILED")
        print("─" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
