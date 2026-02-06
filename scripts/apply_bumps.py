#!/usr/bin/env python3
"""
Apply version bumps from bump_plan.json.

Updates manifest.json files and creates git tags.
"""

import json
import subprocess
from pathlib import Path


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse semver string to tuple."""
    parts = version.split(".")
    return (
        int(parts[0]) if len(parts) > 0 else 0,
        int(parts[1]) if len(parts) > 1 else 0,
        int(parts[2]) if len(parts) > 2 else 0,
    )


def bump_version(version: str, bump_type: str) -> str:
    """Bump a semver version."""
    major, minor, patch = parse_version(version)

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"


def get_repo_version() -> str:
    """Get current repo version from version.json, git tag, or default."""
    # First check version.json
    version_file = Path("version.json")
    if version_file.exists():
        try:
            version_data = json.loads(version_file.read_text())
            if "version" in version_data:
                return version_data["version"]
        except (json.JSONDecodeError, KeyError):
            pass

    # Fall back to git tags
    try:
        result = subprocess.run(
            ["git", "tag", "-l", "v*", "--sort=-v:refname"],
            capture_output=True,
            text=True,
            check=True,
        )
        tags = [t for t in result.stdout.strip().split("\n") if t and "-" not in t]
        if tags:
            return tags[0].lstrip("v")
    except subprocess.CalledProcessError:
        pass
    return "0.0.0"


def create_tag(tag_name: str, message: str):
    """Create a git tag."""
    subprocess.run(
        ["git", "tag", "-a", tag_name, "-m", message],
        check=True,
    )
    print(f"Created tag: {tag_name}")


def main():
    # Load bump plan
    plan_file = Path("bump_plan.json")
    if not plan_file.exists():
        print("No bump_plan.json found")
        return

    plan = json.loads(plan_file.read_text())

    if not plan.get("has_changes"):
        print("No changes to apply")
        return

    tags_created = []

    # Apply dataset bumps
    for item in plan.get("datasets", []):
        dataset = item["dataset"]
        bump_type = item["bump"]

        manifest_path = Path(f"data/{dataset}/manifest.json")
        if not manifest_path.exists():
            print(f"Warning: No manifest for {dataset}, skipping")
            continue

        manifest = json.loads(manifest_path.read_text())
        old_version = manifest.get("version", "0.0.0")
        new_version = bump_version(old_version, bump_type)

        manifest["version"] = new_version
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

        print(f"{dataset}: {old_version} -> {new_version} ({bump_type})")

        tag_name = f"{dataset}-v{new_version}"
        create_tag(tag_name, f"Release {dataset} v{new_version}")
        tags_created.append(tag_name)

    # Apply repo bump
    repo_bump = plan.get("repo_bump", "none")
    if repo_bump != "none":
        # Read current version from version.json (or fall back to git tag)
        version_file = Path("version.json")
        if version_file.exists():
            version_data = json.loads(version_file.read_text())
            old_version = version_data.get("version", "0.0.0")
        else:
            old_version = get_repo_version()
            version_data = {"version": old_version, "name": "campaigner-data", "description": "Game data repository for the Campaigner project"}

        new_version = bump_version(old_version, repo_bump)

        # Update version.json
        version_data["version"] = new_version
        version_file.write_text(json.dumps(version_data, indent=2) + "\n")

        print(f"repo: {old_version} -> {new_version} ({repo_bump})")

        tag_name = f"v{new_version}"
        create_tag(tag_name, f"Release v{new_version}")
        tags_created.append(tag_name)

    # Write tags for release step
    Path("tags_created.json").write_text(json.dumps(tags_created))


if __name__ == "__main__":
    main()
