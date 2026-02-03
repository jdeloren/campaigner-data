#!/usr/bin/env python3
"""
Package game data for deployment.

Usage:
    python scripts/package.py --ruleset dnd5e           # Package specific ruleset
    python scripts/package.py --all                     # Package all rulesets
    python scripts/package.py --ruleset dnd5e --version 1.0.0  # With explicit version

Output:
    dist/{ruleset}-data-{version}.tar.gz

The package includes:
    - All JSON data files for the ruleset
    - A manifest.json with version and file checksums
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path


# Repository paths
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
DIST_DIR = REPO_ROOT / "dist"


def discover_rulesets() -> list[str]:
    """Find all ruleset directories under data/."""
    if not DATA_DIR.exists():
        return []
    return [d.name for d in DATA_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]


def get_version() -> str:
    """Get version from git tag or generate timestamp-based version."""
    try:
        # Try to get the latest git tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode == 0:
            return result.stdout.strip().lstrip("v")
    except Exception:
        pass

    # Fall back to timestamp-based version
    return datetime.now(timezone.utc).strftime("%Y%m%d.%H%M%S")


def compute_checksum(file_path: Path) -> str:
    """Compute SHA256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def create_manifest(ruleset: str, version: str, files: list[Path]) -> dict:
    """Create a manifest with version and file checksums."""
    manifest = {
        "ruleset": ruleset,
        "version": version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": {},
    }

    ruleset_dir = DATA_DIR / ruleset
    for file_path in sorted(files):
        relative_path = str(file_path.relative_to(ruleset_dir))
        manifest["files"][relative_path] = {
            "checksum": compute_checksum(file_path),
            "size": file_path.stat().st_size,
        }

    return manifest


def package_ruleset(ruleset: str, version: str) -> Path | None:
    """
    Package a ruleset into a tarball.

    Returns the path to the created tarball, or None on error.
    """
    ruleset_dir = DATA_DIR / ruleset
    if not ruleset_dir.exists():
        print(f"Error: Ruleset directory not found: {ruleset_dir}")
        return None

    # Find all JSON files
    files = list(ruleset_dir.rglob("*.json"))
    if not files:
        print(f"Error: No JSON files found in {ruleset_dir}")
        return None

    # Create dist directory
    DIST_DIR.mkdir(exist_ok=True)

    # Create manifest
    manifest = create_manifest(ruleset, version, files)

    # Create tarball
    tarball_name = f"{ruleset}-data-{version}.tar.gz"
    tarball_path = DIST_DIR / tarball_name

    print(f"Creating {tarball_name}...")

    with tarfile.open(tarball_path, "w:gz") as tar:
        # Add data files
        for file_path in sorted(files):
            arcname = str(file_path.relative_to(ruleset_dir))
            tar.add(file_path, arcname=arcname)
            print(f"  + {arcname}")

        # Add manifest
        manifest_json = json.dumps(manifest, indent=2)
        manifest_bytes = manifest_json.encode("utf-8")

        import io
        manifest_info = tarfile.TarInfo(name="manifest.json")
        manifest_info.size = len(manifest_bytes)
        tar.addfile(manifest_info, io.BytesIO(manifest_bytes))
        print("  + manifest.json")

    print(f"Created: {tarball_path}")
    print(f"  Files: {len(files)}")
    print(f"  Size: {tarball_path.stat().st_size:,} bytes")

    return tarball_path


def main():
    parser = argparse.ArgumentParser(description="Package game data for deployment")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Package all rulesets"
    )
    parser.add_argument(
        "--ruleset",
        type=str,
        help="Package specific ruleset (e.g., dnd5e)"
    )
    parser.add_argument(
        "--version",
        type=str,
        help="Version string (default: from git tag or timestamp)"
    )

    args = parser.parse_args()

    if not args.all and not args.ruleset:
        parser.error("Must specify --all or --ruleset")

    # Determine version
    version = args.version or get_version()
    print(f"Version: {version}\n")

    # Determine which rulesets to package
    if args.all:
        rulesets = discover_rulesets()
        if not rulesets:
            print("No rulesets found in data/")
            sys.exit(1)
    else:
        rulesets = [args.ruleset]
        if not (DATA_DIR / args.ruleset).exists():
            print(f"Ruleset not found: {args.ruleset}")
            sys.exit(1)

    # Package each ruleset
    created = []
    failed = []

    for ruleset in sorted(rulesets):
        result = package_ruleset(ruleset, version)
        if result:
            created.append(result)
        else:
            failed.append(ruleset)
        print()

    # Summary
    print("=" * 50)
    print(f"Packaged: {len(created)} ruleset(s)")
    if failed:
        print(f"Failed: {len(failed)} ruleset(s): {', '.join(failed)}")
        sys.exit(1)

    for path in created:
        print(f"  {path}")


if __name__ == "__main__":
    main()
