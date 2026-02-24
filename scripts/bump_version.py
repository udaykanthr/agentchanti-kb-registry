#!/usr/bin/env python3
"""
AgentChanti KB Registry — Version Bumper

Reads the current version from manifest.json, determines the bump type
from the latest merge commit message or PR labels, and writes the new version.

Bump type is determined by checking the git log for labels on the latest merge:
  - 'bump:major' → increment MAJOR
  - 'bump:minor' → increment MINOR
  - 'bump:patch' → increment PATCH
  - (default)   → increment PATCH
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
MANIFEST_PATH = ROOT / "manifest.json"


def get_current_version(manifest: dict) -> tuple[int, int, int]:
    version_str = manifest.get("version", "1.0.0")
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version_str)
    if not match:
        raise ValueError(f"Invalid version in manifest.json: {version_str}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def get_bump_type() -> str:
    """
    Determine bump type from the latest git commit message.
    CI sets PR labels in the merge commit message or via environment variables.
    """
    # Check environment variable first (set by CI from PR labels)
    import os
    env_bump = os.environ.get("BUMP_TYPE", "").strip().lower()
    if env_bump in ("major", "minor", "patch"):
        print(f"Using bump type from environment: {env_bump}")
        return env_bump

    # Fall back to parsing the latest commit message
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=%B"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        commit_msg = result.stdout.strip().lower()
    except Exception:
        commit_msg = ""

    if "bump:major" in commit_msg:
        return "major"
    elif "bump:minor" in commit_msg:
        return "minor"
    elif "bump:patch" in commit_msg:
        return "patch"
    else:
        print("No bump label found in commit message. Defaulting to patch.")
        return "patch"


def bump_version(major: int, minor: int, patch: int, bump_type: str) -> str:
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"


def count_files(manifest: dict) -> dict:
    """Update category counts by scanning actual files."""
    import yaml

    categories = manifest.get("categories", {})

    # Count error entries
    total_error_entries = 0
    errors_dir = ROOT / "errors"
    if errors_dir.exists():
        for yml_file in errors_dir.rglob("*.yml"):
            try:
                data = yaml.safe_load(yml_file.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    total_error_entries += len(data)
            except Exception:
                pass
    categories.setdefault("errors", {})["total_entries"] = total_error_entries

    # Count .md files per category
    for cat in ("patterns", "adrs", "docs", "behavioral"):
        cat_dir = ROOT / cat
        count = len(list(cat_dir.rglob("*.md"))) if cat_dir.exists() else 0
        categories.setdefault(cat, {})["total_files"] = count

    return categories


def main():
    print("=" * 50)
    print("AgentChanti KB Registry — Version Bump")
    print("=" * 50)

    # Load manifest
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    # Get current version
    major, minor, patch = get_current_version(manifest)
    current = f"{major}.{minor}.{patch}"
    print(f"Current version: {current}")

    # Determine bump type
    bump_type = get_bump_type()
    print(f"Bump type: {bump_type}")

    # Calculate new version
    new_version = bump_version(major, minor, patch, bump_type)
    print(f"New version: {new_version}")

    # Update manifest
    manifest["version"] = new_version
    manifest["categories"] = count_files(manifest)

    # Write back
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8"
    )

    print(f"✓ manifest.json updated to v{new_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
