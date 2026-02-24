#!/usr/bin/env python3
"""
AgentChanti KB Registry — Index Quality Check

Performs content quality analysis. Warnings do not fail CI.
Checks:
  a. No .md file exceeds 5000 words (warn, not fail)
  b. All .md files have at least one ## heading section
  c. All .yml files are valid YAML (parseable)
  d. No error entry has empty fix_template
  e. Count total errors per language, warn if < 5 for any language
  f. Report summary: total files, total errors, coverage per language

Exit code is always 0 (warnings only, no hard failures from this script).
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

import yaml

ROOT = Path(__file__).parent.parent

EXPECTED_LANGUAGES = ["python", "javascript", "typescript", "java", "go", "rust", "csharp"]
MIN_ERRORS_PER_LANGUAGE = 5


class Report:
    def __init__(self):
        self.warnings = []
        self.infos = []
        self.errors_found = []

    def warn(self, msg: str):
        self.warnings.append(msg)

    def info(self, msg: str):
        self.infos.append(msg)

    def error(self, msg: str):
        self.errors_found.append(msg)


report = Report()


def count_words(text: str) -> int:
    # Remove frontmatter
    if text.startswith("---"):
        try:
            end = text.index("\n---", 3)
            text = text[end + 4:]
        except ValueError:
            pass
    # Remove code blocks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    return len(text.split())


def has_h2_heading(text: str) -> bool:
    return bool(re.search(r"^## .+", text, re.MULTILINE))


def check_md_files():
    """Check a, b for all .md files in patterns/, adrs/, docs/, behavioral/."""
    dirs = ["patterns", "adrs", "docs", "behavioral"]
    md_files = []
    for d in dirs:
        dir_path = ROOT / d
        if dir_path.exists():
            md_files.extend(dir_path.rglob("*.md"))

    over_limit = 0
    missing_heading = 0
    total = len(md_files)

    for path in md_files:
        rel = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")

        # Check a: word count
        word_count = count_words(text)
        if word_count > 5000:
            report.warn(f"  ⚠ WARN [word-count] {rel}: {word_count} words (exceeds 5000 limit)")
            over_limit += 1

        # Check b: ## heading
        if not has_h2_heading(text):
            report.error(f"  ✗ FAIL [headings] {rel}: No ## heading section found")
            missing_heading += 1

    report.info(f"  ✓ INFO [md-files] Checked {total} .md files")
    if over_limit == 0:
        report.info(f"  ✓ INFO [word-count] All .md files within 5000 word limit")
    if missing_heading == 0:
        report.info(f"  ✓ INFO [headings] All .md files have at least one ## heading")

    return total


def check_yml_files() -> tuple[int, dict[str, int]]:
    """Check c, d, e for all .yml files in errors/."""
    errors_dir = ROOT / "errors"
    if not errors_dir.exists():
        report.warn("  ⚠ WARN [yml-files] No errors/ directory found")
        return 0, {}

    yml_files = list(errors_dir.rglob("*.yml"))
    invalid_yaml = 0
    empty_fix = 0
    lang_counts: dict[str, int] = defaultdict(int)
    total_entries = 0

    for path in yml_files:
        rel = path.relative_to(ROOT)

        # Check c: valid YAML
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            report.error(f"  ✗ FAIL [valid-yaml] {rel}: YAML parse error: {e}")
            invalid_yaml += 1
            continue

        if not isinstance(data, list):
            report.warn(f"  ⚠ WARN [valid-yaml] {rel}: Not a list — expected list of error entries")
            continue

        # Determine language from path
        # errors/{language}/... or errors/{language}/frameworks/...
        parts = path.relative_to(errors_dir).parts
        if parts:
            lang = parts[0]
        else:
            lang = "unknown"

        for entry in data:
            if not isinstance(entry, dict):
                continue
            total_entries += 1
            lang_counts[lang] += 1

            # Check d: empty fix_template
            fix = entry.get("fix_template", "")
            if not fix or str(fix).strip() == "":
                report.error(f"  ✗ FAIL [fix-template] {rel}: Entry \"{entry.get('id', '?')}\" has empty fix_template")
                empty_fix += 1

    report.info(f"  ✓ INFO [yml-files] Checked {len(yml_files)} .yml files, {total_entries} total entries")

    if invalid_yaml == 0:
        report.info(f"  ✓ INFO [valid-yaml] All .yml files are valid YAML")
    if empty_fix == 0:
        report.info(f"  ✓ INFO [fix-template] No error entries have empty fix_template")

    # Check e: coverage per language
    for lang in EXPECTED_LANGUAGES:
        count = lang_counts.get(lang, 0)
        if count < MIN_ERRORS_PER_LANGUAGE:
            report.warn(f"  ⚠ WARN [coverage] Language '{lang}': only {count} error entries (minimum {MIN_ERRORS_PER_LANGUAGE} recommended)")

    return total_entries, dict(lang_counts)


def main():
    print("=" * 60)
    print("AgentChanti KB Registry — Index Quality Check")
    print("=" * 60)
    print()

    total_md = check_md_files()
    total_errors, lang_counts = check_yml_files()

    print()
    print("─" * 60)
    print("SUMMARY REPORT")
    print("─" * 60)
    print()

    # Print infos
    for msg in report.infos:
        print(msg)

    # Print errors (hard failures)
    if report.errors_found:
        print()
        print("FAILURES (must fix):")
        for msg in report.errors_found:
            print(msg)

    # Print warnings
    if report.warnings:
        print()
        print("WARNINGS (review recommended):")
        for msg in report.warnings:
            print(msg)

    print()
    print("─" * 60)
    print(f"Total .md files checked: {total_md}")
    print(f"Total error entries: {total_errors}")
    print()
    print("Error coverage per language:")
    for lang in EXPECTED_LANGUAGES:
        count = lang_counts.get(lang, 0)
        bar = "█" * min(count, 20)
        status = "✓" if count >= MIN_ERRORS_PER_LANGUAGE else "⚠"
        print(f"  {status} {lang:<14} {count:>3} entries  {bar}")

    other_langs = {k: v for k, v in lang_counts.items() if k not in EXPECTED_LANGUAGES}
    for lang, count in sorted(other_langs.items()):
        bar = "█" * min(count, 20)
        print(f"    {lang:<14} {count:>3} entries  {bar}")

    print("─" * 60)

    if report.errors_found:
        print(f"✗ {len(report.errors_found)} hard failure(s) found — must be fixed")
        print(f"  {len(report.warnings)} warning(s) (advisory only)")
    elif report.warnings:
        print(f"✓ No hard failures")
        print(f"  {len(report.warnings)} warning(s) — review recommended but not blocking")
    else:
        print("✓ All checks passed, no warnings")
    print("─" * 60)

    # Index check does not fail CI — exit 0 always
    # Hard failures from this script are advisory; validate.py handles blocking failures
    return 0


if __name__ == "__main__":
    sys.exit(main())
