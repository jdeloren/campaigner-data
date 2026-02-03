#!/usr/bin/env python3
"""
Check that schema file changes include corresponding version bumps.

Compares current schema files against the base branch to detect changes,
then verifies that schemas/versions.json was updated accordingly.

Usage:
    python scripts/check_schema_versions.py [--base main]

Exit codes:
    0 = All schema changes have version bumps
    1 = Schema changed without version bump
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas" / "json"
VERSIONS_FILE = REPO_ROOT / "schemas" / "versions.json"


def get_changed_files(base: str) -> list[str]:
    """Get files changed compared to base branch."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base],
            capture_output=True,
            text=True,
            check=True,
        )
        return [f for f in result.stdout.strip().split("\n") if f]
    except subprocess.CalledProcessError:
        return []


def get_file_content_at_ref(file_path: str, ref: str) -> str | None:
    """Get content of a file at a specific git ref."""
    try:
        result = subprocess.run(
            ["git", "show", f"{ref}:{file_path}"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def extract_schema_name(file_path: str) -> str | None:
    """Extract schema name from file path like schemas/json/class.schema.json."""
    if not file_path.startswith("schemas/json/"):
        return None
    filename = Path(file_path).name
    if filename.endswith(".schema.json"):
        return filename.replace(".schema.json", "")
    return None


def main():
    parser = argparse.ArgumentParser(description="Check schema version bumps")
    parser.add_argument(
        "--base",
        type=str,
        default="origin/main",
        help="Base branch/ref to compare against (default: origin/main)"
    )
    args = parser.parse_args()

    # Get changed files
    changed_files = get_changed_files(args.base)

    # Find changed schema files
    changed_schemas = []
    for f in changed_files:
        schema_name = extract_schema_name(f)
        if schema_name:
            changed_schemas.append(schema_name)

    if not changed_schemas:
        print("No schema files changed")
        sys.exit(0)

    print(f"Changed schemas: {', '.join(changed_schemas)}")

    # Check if versions.json was also changed
    if "schemas/versions.json" not in changed_files:
        print("\nError: Schema files changed but schemas/versions.json was not updated")
        print("Please bump the version for changed schemas in schemas/versions.json")
        sys.exit(1)

    # Get old and new versions
    old_versions_content = get_file_content_at_ref("schemas/versions.json", args.base)
    if old_versions_content:
        old_versions = json.loads(old_versions_content)
    else:
        old_versions = {}

    if VERSIONS_FILE.exists():
        new_versions = json.loads(VERSIONS_FILE.read_text())
    else:
        print("Error: schemas/versions.json does not exist")
        sys.exit(1)

    # Check each changed schema has a version bump
    errors = []
    for schema_name in changed_schemas:
        old_version = old_versions.get(schema_name, "0.0")
        new_version = new_versions.get(schema_name)

        if new_version is None:
            errors.append(f"  {schema_name}: not found in versions.json")
        elif new_version == old_version:
            errors.append(f"  {schema_name}: version unchanged ({old_version})")
        else:
            print(f"  {schema_name}: {old_version} -> {new_version} ✓")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(error)
        print("\nPlease bump versions for all changed schemas")
        sys.exit(1)

    print("\nAll changed schemas have version bumps ✓")
    sys.exit(0)


if __name__ == "__main__":
    main()
