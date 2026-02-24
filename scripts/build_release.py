#!/usr/bin/env python3
"""
AgentChanti KB Registry — Release Builder

Builds the release zip artifact containing all KB content.
Also updates total_entries and total_files counts in manifest.json
by scanning actual files before zipping.

Usage:
    python scripts/build_release.py [version]

If version is not provided, reads from manifest.json.
"""

import json
import sys
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent
MANIFEST_PATH = ROOT / "manifest.json"


CONTENT_DIRS = ["errors", "patterns", "adrs", "docs", "behavioral"]


def count_and_update_manifest(manifest: dict) -> dict:
    """Scan actual files and update manifest counts."""
    categories = manifest.get("categories", {})

    # Count error entries across all .yml files
    total_error_entries = 0
    errors_dir = ROOT / "errors"
    if errors_dir.exists():
        for yml_file in errors_dir.rglob("*.yml"):
            try:
                data = yaml.safe_load(yml_file.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    total_error_entries += len(data)
            except Exception as e:
                print(f"  WARN: Could not parse {yml_file.relative_to(ROOT)}: {e}")

    categories.setdefault("errors", {})["total_entries"] = total_error_entries
    print(f"  Counted {total_error_entries} error entries")

    # Count .md files per non-error category
    for cat in ("patterns", "adrs", "docs", "behavioral"):
        cat_dir = ROOT / cat
        if cat_dir.exists():
            count = len(list(cat_dir.rglob("*.md")))
        else:
            count = 0
        categories.setdefault(cat, {})["total_files"] = count
        print(f"  Counted {count} files in {cat}/")

    manifest["categories"] = categories
    return manifest


def collect_files() -> list[Path]:
    """Collect all content files to include in the zip."""
    files = []
    for dir_name in CONTENT_DIRS:
        dir_path = ROOT / dir_name
        if dir_path.exists():
            # Include .yml and .md files
            files.extend(dir_path.rglob("*.yml"))
            files.extend(dir_path.rglob("*.md"))
    # Always include manifest.json
    files.append(MANIFEST_PATH)
    return files


def build_zip(version: str, files: list[Path]) -> Path:
    """Create the release zip file."""
    zip_path = ROOT / f"kb-registry-v{version}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in files:
            arcname = file_path.relative_to(ROOT)
            zf.write(file_path, arcname)
            print(f"  Added: {arcname}")

    return zip_path


def verify_zip(zip_path: Path) -> bool:
    """Verify the zip can be opened and manifest is readable."""
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            # Check manifest is present
            if "manifest.json" not in zf.namelist():
                print("  ERROR: manifest.json not found in zip")
                return False
            # Try reading manifest
            manifest_data = json.loads(zf.read("manifest.json").decode("utf-8"))
            if "version" not in manifest_data:
                print("  ERROR: manifest.json in zip is missing 'version' field")
                return False
            print(f"  Verified: zip contains {len(zf.namelist())} files")
            print(f"  Verified: manifest version = {manifest_data['version']}")
            return True
    except Exception as e:
        print(f"  ERROR: Could not verify zip: {e}")
        return False


def main():
    print("=" * 50)
    print("AgentChanti KB Registry — Build Release")
    print("=" * 50)
    print()

    # Load manifest
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    # Determine version
    if len(sys.argv) > 1:
        version = sys.argv[1].lstrip("v")
    else:
        version = manifest.get("version", "1.0.0")

    print(f"Building release: v{version}")
    print()

    # Update manifest counts
    print("Counting content files...")
    manifest = count_and_update_manifest(manifest)

    # Write updated manifest
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8"
    )
    print(f"✓ manifest.json counts updated")
    print()

    # Collect files
    print("Collecting files for zip...")
    files = collect_files()
    print(f"  Found {len(files)} files to package")
    print()

    # Build zip
    print("Building zip...")
    zip_path = build_zip(version, files)
    zip_size_kb = zip_path.stat().st_size / 1024
    print()
    print(f"✓ Created: {zip_path.name} ({zip_size_kb:.1f} KB)")
    print()

    # Verify zip
    print("Verifying zip integrity...")
    if verify_zip(zip_path):
        print("✓ Zip integrity verified")
    else:
        print("✗ Zip verification failed")
        return 1

    print()
    print(f"Release v{version} ready: {zip_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
