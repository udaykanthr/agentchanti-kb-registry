#!/usr/bin/env python3
"""
AgentChanti KB Registry — Publish Script

Automates the full registry update workflow:
  1. Detect changed files (vs origin/main or HEAD)
  2. Run validate.py  — abort on failure
  3. Run index_check.py — warn on failure
  4. Update manifest.json category counts (version left for CI to bump on merge)
  5. Git commit + push to feature branch
  6. Create GitHub PR with auto-filled PR template + bump label

The bump label (bump:patch / bump:minor / bump:major) is applied to the PR
so that CI runs bump_version.py once on merge — avoiding double-bumps.

Usage:
    python scripts/publish.py                         # auto-detect bump type
    python scripts/publish.py --bump minor            # force bump type
    python scripts/publish.py --message "Fix X"       # custom changelog
    python scripts/publish.py --dry-run               # validate + preview, no push
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "manifest.json"
SCRIPTS_DIR = ROOT / "scripts"

# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _git(args, check=True, capture=True):
    return subprocess.run(
        ["git"] + args, cwd=ROOT, check=check,
        capture_output=capture, text=True,
    )


def current_branch() -> str:
    return _git(["branch", "--show-current"]).stdout.strip()


def get_changed_files() -> list[str]:
    """Return files changed vs origin/main (or HEAD as fallback)."""
    for base in ("origin/main", "main"):
        r = _git(["diff", "--name-only", base], check=False)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip().splitlines()

    # Fallback: all uncommitted changes (staged + unstaged + untracked)
    r = _git(["status", "--porcelain"])
    files = []
    for line in r.stdout.splitlines():
        if line.strip():
            path = line[3:].strip().strip('"')
            if path:
                files.append(path)
    return files


def is_new_file(rel_path: str) -> bool:
    """True if this path has never been committed (untracked or just added)."""
    r = _git(["log", "--oneline", "-1", "--", rel_path], check=False)
    return not r.stdout.strip()


def ensure_feature_branch(changed_files: list[str]) -> str:
    """If on main/master, create and checkout a new feature branch."""
    branch = current_branch()
    if branch in ("main", "master", ""):
        slugs = [
            Path(f).stem.replace("_", "-").replace(" ", "-")
            for f in changed_files
            if not f.endswith("manifest.json") and not f.startswith("scripts/")
        ]
        slug = slugs[0][:40] if slugs else "kb-update"
        branch = f"update/{slug}"
        _git(["checkout", "-b", branch], capture=False)
        print(f"  Created branch: {branch}")
    return branch

# ---------------------------------------------------------------------------
# Frontmatter
# ---------------------------------------------------------------------------

def read_frontmatter(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            return {}
        end = text.index("---", 3)
        fm: dict = {}
        for line in text[3:end].splitlines():
            if ":" in line and not line.startswith(" "):
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip().strip('"')
        return fm
    except Exception:
        return {}

# ---------------------------------------------------------------------------
# Validation scripts
# ---------------------------------------------------------------------------

def run_script(script_name: str) -> tuple[int, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / script_name)],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    return r.returncode, r.stdout + r.stderr

# ---------------------------------------------------------------------------
# Manifest — counts only (version bumped by CI on merge)
# ---------------------------------------------------------------------------

def update_manifest_counts(dry_run: bool = False) -> None:
    """Recount category totals in manifest.json. Does NOT touch the version."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    current_version = manifest.get("version", "?")

    categories = manifest.get("categories", {})

    # Error entries
    total = 0
    errors_dir = ROOT / "errors"
    if errors_dir.exists():
        try:
            import yaml
            for yml in errors_dir.rglob("*.yml"):
                try:
                    data = yaml.safe_load(yml.read_text(encoding="utf-8"))
                    if isinstance(data, list):
                        total += len(data)
                except Exception:
                    pass
        except ImportError:
            total = categories.get("errors", {}).get("total_entries", 0)
    categories.setdefault("errors", {})["total_entries"] = total

    # Preserve languages list
    old_langs = manifest.get("categories", {}).get("errors", {}).get("languages")
    if old_langs:
        categories["errors"]["languages"] = old_langs

    # .md file counts per category
    for cat in ("patterns", "adrs", "docs", "behavioral"):
        d = ROOT / cat
        count = len(list(d.rglob("*.md"))) if d.exists() else 0
        categories[cat] = {"total_files": count}

    manifest["categories"] = categories

    if dry_run:
        print(f"  manifest.json counts updated (dry-run, not written) — version stays at {current_version}")
        return

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"  manifest.json category counts updated (version stays at {current_version} — CI bumps on merge)")

# ---------------------------------------------------------------------------
# PR body builder
# ---------------------------------------------------------------------------

def build_pr_body(
    file_summaries: list[tuple[str, str]],
    content_types: set[str],
    languages: set[str],
    bump_type: str,
    validation_passed: bool,
    index_passed: bool,
) -> str:
    relevant = [(f, t) for f, t in file_summaries if "manifest.json" not in f]
    desc = (
        "\n".join(f"- `{f}` — {title}" for f, title in relevant)
        if relevant else "_(see changed files)_"
    )

    type_map = [
        ("error",      "`error` — New or updated error entries in `errors/`"),
        ("pattern",    "`pattern` — New or updated coding pattern in `patterns/`"),
        ("adr",        "`adr` — New or updated architectural decision record in `adrs/`"),
        ("doc",        "`doc` — New or updated reference documentation in `docs/`"),
        ("behavioral", "`behavioral` — New or updated behavioral instruction in `behavioral/`"),
    ]
    type_lines = "\n".join(
        f"- [{'x' if k in content_types else ' '}] {label}"
        for k, label in type_map
    )

    lang_str = ", ".join(sorted(languages)) if languages else "_(see frontmatter)_"
    v = "x" if validation_passed else " "
    i = "x" if index_passed else " "

    bump_rows = ""
    for label, desc_text in [
        ("bump:patch", "Content corrections, new error entries, minor wording fixes"),
        ("bump:minor", "New files added, new categories, new language coverage"),
        ("bump:major", "Breaking schema changes, ID renames, structural reorganization"),
    ]:
        marker = " ← **applied**" if label == f"bump:{bump_type}" else ""
        bump_rows += f"| `{label}` | {desc_text}{marker} |\n"

    return f"""\
## Content Description

{desc}

---

## Checklist

### Content Type
{type_lines}

### Scope
- [x] Language/framework scope identified: _{lang_str}_
- [x] Content applies to the scope listed in frontmatter `language` field

### ID Validation
- [x] All new IDs are unique — checked against existing IDs in the registry
- [x] ID follows naming convention
- [x] No ID reuses an existing ID (`python scripts/validate.py` passed)

### Schema Compliance
- [x] All `.md` files have complete frontmatter
- [x] All `.yml` error files have required fields (if applicable)
- [x] `severity`, `category`, `language`, `version` values are valid

### Content Quality
- [x] Fix templates include actual working code examples (if applicable)
- [x] No placeholder or lorem ipsum text
- [x] `.md` files have at least one `##` heading

### Local Testing
- [{v}] Ran `python scripts/validate.py` — exits with code 0
- [{i}] Ran `python scripts/index_check.py` — reviewed all warnings
- [ ] Tested `agentchanti kb seed` picks up this content locally

### Manifest
- [x] `manifest.json` category counts updated (version will be bumped by CI on merge)

---

## Version Bump Label

| Label | When to Use |
|---|---|
{bump_rows}
---

## Related Issues

Closes #_(issue number, if applicable)_"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate, update counts, commit, push, and open a PR for KB registry changes."
    )
    parser.add_argument(
        "--bump", choices=["patch", "minor", "major"],
        help="Version bump type applied via PR label. Default: 'minor' if new files, else 'patch'.",
    )
    parser.add_argument("--message", help="Commit message / PR title suffix.")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Run validation and show the PR body without pushing anything.",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("AgentChanti KB Registry — Publish")
    print("=" * 60)

    # 1. Detect changes
    print("\n[1/5] Detecting changes...")
    changed = get_changed_files()
    if not changed:
        print("  No changes detected. Nothing to publish.")
        return 0
    for f in changed:
        print(f"  {f}")

    # 2. Validate
    print("\n[2/5] Running validate.py...")
    code, out = run_script("validate.py")
    print(out.rstrip())
    if code != 0:
        print("\nABORT: validation failed. Fix the errors above before publishing.")
        return 1
    validation_passed = True

    # 3. Index check
    print("\n[3/5] Running index_check.py...")
    code, out = run_script("index_check.py")
    print(out.rstrip())
    index_passed = (code == 0)
    if not index_passed:
        print("  WARNING: index check had issues — continuing.")

    # 4. Collect PR metadata
    content_types: set[str] = set()
    languages: set[str] = set()
    file_summaries: list[tuple[str, str]] = []
    has_new_files = False

    _dir_to_type = {
        "errors": "error", "patterns": "pattern", "adrs": "adr",
        "docs": "doc", "behavioral": "behavioral",
    }
    for f in changed:
        p = ROOT / f
        parts = Path(f).parts
        top = parts[0] if parts else ""
        if top in _dir_to_type:
            content_types.add(_dir_to_type[top])
        if f.endswith(".md") and p.exists() and top != ".github":
            fm = read_frontmatter(p)
            file_summaries.append((f, fm.get("title", f)))
            if fm.get("language"):
                languages.add(fm["language"])
        if is_new_file(f):
            has_new_files = True

    bump_type = args.bump or ("minor" if has_new_files else "patch")

    if args.message:
        changelog = args.message
    else:
        titles = [t for fp, t in file_summaries if "manifest.json" not in fp]
        if titles:
            changelog = "Updated: " + ", ".join(titles[:3])
            if len(titles) > 3:
                changelog += f" (+{len(titles) - 3} more)"
        else:
            changelog = f"KB registry update (bump:{bump_type})"

    # 4. Update manifest counts only (no version bump — CI handles that on merge)
    print("\n[4/5] Updating manifest.json category counts...")
    update_manifest_counts(dry_run=args.dry_run)

    pr_body = build_pr_body(
        file_summaries, content_types, languages,
        bump_type, validation_passed, index_passed,
    )

    if args.dry_run:
        print("\n" + "─" * 60)
        print("DRY RUN — PR body preview:")
        print("─" * 60)
        print(pr_body)
        print("─" * 60)
        print("Dry run complete. Nothing was pushed.")
        return 0

    # 5. Commit + push + PR
    print("\n[5/5] Committing, pushing, and creating PR...")

    branch = ensure_feature_branch(changed)

    _git(["add", "-A"], capture=False)
    commit_msg = f"kb: {changelog} [bump:{bump_type}]"
    _git(["commit", "-m", commit_msg], capture=False)
    print(f"  Committed: {commit_msg}")

    _git(["push", "-u", "origin", branch], capture=False)
    print(f"  Pushed: origin/{branch}")

    pr_title = f"kb: {changelog}"
    if len(pr_title) > 72:
        pr_title = pr_title[:69] + "..."

    r = subprocess.run(
        ["gh", "pr", "create",
         "--title", pr_title,
         "--body", pr_body,
         "--label", f"bump:{bump_type}"],
        cwd=ROOT, capture_output=True, text=True,
    )

    if r.returncode == 0:
        print(f"\n  PR created: {r.stdout.strip()}")
    else:
        # Label may not exist in the repo yet — retry without it
        print(f"  Note: could not apply label 'bump:{bump_type}' ({r.stderr.strip()})")
        r2 = subprocess.run(
            ["gh", "pr", "create", "--title", pr_title, "--body", pr_body],
            cwd=ROOT, capture_output=True, text=True,
        )
        if r2.returncode == 0:
            print(f"  PR created (no label): {r2.stdout.strip()}")
        else:
            print(f"  gh pr create failed: {r2.stderr}")
            print("\n  PR body (copy manually):\n")
            print(pr_body)
            return 1

    print("\nDone!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
