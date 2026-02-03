#!/usr/bin/env python3
"""
Create GitHub releases for newly created tags.

Uses the gh CLI to create releases with auto-generated notes.
"""

import json
import subprocess
from pathlib import Path


def get_previous_tag(tag: str) -> str | None:
    """Get the previous tag for release notes generation."""
    if "-v" in tag:
        # Dataset tag like dnd5e-v1.2.3
        dataset = tag.rsplit("-v", 1)[0]
        pattern = f"{dataset}-v*"
    else:
        # Repo tag like v1.2.3
        pattern = "v*"

    try:
        result = subprocess.run(
            ["git", "tag", "-l", pattern, "--sort=-v:refname"],
            capture_output=True,
            text=True,
            check=True,
        )
        tags = result.stdout.strip().split("\n")
        tags = [t for t in tags if t and t != tag]

        # Filter out dataset tags when looking for repo tags
        if "-v" not in tag:
            tags = [t for t in tags if "-" not in t]

        return tags[0] if tags else None
    except subprocess.CalledProcessError:
        return None


def package_dataset(dataset: str) -> Path | None:
    """Package a dataset and return the tarball path."""
    try:
        subprocess.run(
            ["python", "scripts/package.py", "--ruleset", dataset],
            check=True,
        )
        # Find the created tarball
        dist_dir = Path("dist")
        tarballs = list(dist_dir.glob(f"{dataset}-*.tar.gz"))
        return tarballs[0] if tarballs else None
    except subprocess.CalledProcessError:
        return None


def create_release(tag: str, previous_tag: str | None, asset: Path | None):
    """Create a GitHub release."""
    cmd = [
        "gh", "release", "create", tag,
        "--title", tag,
        "--generate-notes",
    ]

    if previous_tag:
        cmd.extend(["--notes-start-tag", previous_tag])

    if asset and asset.exists():
        cmd.append(str(asset))

    try:
        subprocess.run(cmd, check=True)
        print(f"Created release: {tag}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create release {tag}: {e}")


def main():
    # Load created tags
    tags_file = Path("tags_created.json")
    if not tags_file.exists():
        print("No tags_created.json found")
        return

    tags = json.loads(tags_file.read_text())

    for tag in tags:
        previous_tag = get_previous_tag(tag)

        # Package dataset if this is a dataset tag
        asset = None
        if "-v" in tag:
            dataset = tag.rsplit("-v", 1)[0]
            asset = package_dataset(dataset)

        create_release(tag, previous_tag, asset)


if __name__ == "__main__":
    main()
