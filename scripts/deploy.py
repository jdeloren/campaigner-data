#!/usr/bin/env python3
"""
Deploy game data to a target location.

Usage:
    python scripts/deploy.py --target local --path /path/to/destination
    python scripts/deploy.py --target local --path ../campaigner/data

This script copies the data files (not packages) directly to a target location,
useful for local development where you want the raw files rather than a tarball.
"""

import argparse
import shutil
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"


def discover_rulesets() -> list[str]:
    """Find all ruleset directories under data/."""
    if not DATA_DIR.exists():
        return []
    return [d.name for d in DATA_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]


def deploy_local(destination: Path, rulesets: list[str]) -> bool:
    """Deploy data files to a local directory."""
    destination = destination.resolve()

    print(f"Deploying to: {destination}")

    # Create destination if it doesn't exist
    destination.mkdir(parents=True, exist_ok=True)

    for ruleset in rulesets:
        source = DATA_DIR / ruleset
        target = destination / ruleset

        print(f"\n{ruleset}:")

        # Remove existing target if it exists
        if target.exists():
            print(f"  Removing existing {target}")
            shutil.rmtree(target)

        # Copy the ruleset directory
        print(f"  Copying {source} -> {target}")
        shutil.copytree(source, target)

        # Count files
        file_count = len(list(target.rglob("*.json")))
        print(f"  Copied {file_count} files")

    return True


def main():
    parser = argparse.ArgumentParser(description="Deploy game data")
    parser.add_argument(
        "--target",
        type=str,
        required=True,
        choices=["local"],
        help="Deployment target (currently only 'local' supported)"
    )
    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Destination path for deployment"
    )
    parser.add_argument(
        "--ruleset",
        type=str,
        help="Deploy specific ruleset (default: all)"
    )

    args = parser.parse_args()

    # Determine rulesets to deploy
    if args.ruleset:
        rulesets = [args.ruleset]
        if not (DATA_DIR / args.ruleset).exists():
            print(f"Error: Ruleset not found: {args.ruleset}")
            sys.exit(1)
    else:
        rulesets = discover_rulesets()
        if not rulesets:
            print("Error: No rulesets found in data/")
            sys.exit(1)

    print(f"Rulesets: {', '.join(rulesets)}")

    # Deploy
    if args.target == "local":
        success = deploy_local(Path(args.path), rulesets)
    else:
        print(f"Error: Unknown target: {args.target}")
        sys.exit(1)

    if success:
        print("\nDeployment complete!")
    else:
        print("\nDeployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
