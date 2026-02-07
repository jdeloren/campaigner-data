#!/usr/bin/env python3
"""
Analyze commits since last tag to determine version bumps needed.

Version bump logic:
- Each dataset gets bumped based on changes to files in data/{dataset}/
- The repo version (version.json) gets bumped if ANY dataset changes OR if
  repo-level files (schemas, scripts) change
- The repo bump type is the max of all dataset bumps and repo-only bumps

Outputs GitHub Actions outputs:
- has_changes: 'true' if any bumps needed
- datasets: JSON list of datasets to bump with bump type
- repo_bump: bump type for repo (or 'none')
"""

import json
import subprocess
from pathlib import Path


def get_last_tag_for_dataset(dataset: str) -> str | None:
    """Get the last tag for a dataset (e.g., dnd5e-v1.2.3)."""
    try:
        result = subprocess.run(
            ["git", "tag", "-l", f"{dataset}-v*", "--sort=-v:refname"],
            capture_output=True,
            text=True,
            check=True,
        )
        tags = result.stdout.strip().split("\n")
        return tags[0] if tags and tags[0] else None
    except subprocess.CalledProcessError:
        return None


def get_last_repo_tag() -> str | None:
    """Get the last repo tag (e.g., v1.2.3, not dataset-prefixed)."""
    try:
        result = subprocess.run(
            ["git", "tag", "-l", "v*", "--sort=-v:refname"],
            capture_output=True,
            text=True,
            check=True,
        )
        tags = [t for t in result.stdout.strip().split("\n") if t and "-" not in t]
        return tags[0] if tags else None
    except subprocess.CalledProcessError:
        return None


def get_commits_since(ref: str | None) -> list[dict]:
    """Get commits since a ref (or all commits if ref is None)."""
    if ref:
        cmd = ["git", "log", f"{ref}..HEAD", "--pretty=format:%H|%s"]
    else:
        cmd = ["git", "log", "--pretty=format:%H|%s"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        commits = []
        for line in result.stdout.strip().split("\n"):
            if "|" in line:
                sha, message = line.split("|", 1)
                commits.append({"sha": sha, "message": message})
        return commits
    except subprocess.CalledProcessError:
        return []


def get_changed_files(sha: str) -> list[str]:
    """Get files changed in a commit."""
    try:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", sha],
            capture_output=True,
            text=True,
            check=True,
        )
        return [f for f in result.stdout.strip().split("\n") if f]
    except subprocess.CalledProcessError:
        return []


def parse_bump_type(message: str) -> str:
    """Parse commit message to determine bump type."""
    message_lower = message.lower()

    # Extract the type prefix before the colon or parenthesis, stripping "!"
    for sep in ("(", ":"):
        if sep in message_lower:
            prefix = message_lower.split(sep, 1)[0].rstrip("!")
            break
    else:
        return "patch"

    if prefix == "breaking":
        return "major"
    elif prefix == "feat":
        return "minor"
    elif prefix == "fix":
        return "patch"
    else:
        return "patch"  # Default fallback


def get_affected_datasets(files: list[str]) -> set[str]:
    """Determine which datasets are affected by changed files."""
    datasets = set()
    for f in files:
        if f.startswith("data/"):
            parts = f.split("/")
            if len(parts) >= 2:
                datasets.add(parts[1])
    return datasets


def is_repo_change(files: list[str]) -> bool:
    """Check if any files are repo-level (not data)."""
    for f in files:
        if not f.startswith("data/"):
            return True
    return False


def max_bump(bumps: list[str]) -> str:
    """Return the highest bump type."""
    if "major" in bumps:
        return "major"
    elif "minor" in bumps:
        return "minor"
    elif "patch" in bumps:
        return "patch"
    return "none"


def main():
    # Discover all datasets
    data_dir = Path("data")
    all_datasets = [d.name for d in data_dir.iterdir() if d.is_dir()] if data_dir.exists() else []

    dataset_bumps: dict[str, list[str]] = {ds: [] for ds in all_datasets}
    repo_bumps: list[str] = []

    # Analyze commits for each dataset
    for dataset in all_datasets:
        last_tag = get_last_tag_for_dataset(dataset)
        commits = get_commits_since(last_tag)

        for commit in commits:
            files = get_changed_files(commit["sha"])
            affected = get_affected_datasets(files)

            if dataset in affected:
                bump_type = parse_bump_type(commit["message"])
                dataset_bumps[dataset].append(bump_type)

    # Analyze commits for repo
    last_repo_tag = get_last_repo_tag()
    repo_commits = get_commits_since(last_repo_tag)

    for commit in repo_commits:
        files = get_changed_files(commit["sha"])
        if is_repo_change(files):
            bump_type = parse_bump_type(commit["message"])
            repo_bumps.append(bump_type)

    # Determine final bumps for datasets
    results = []
    dataset_bump_types = []
    for dataset, bumps in dataset_bumps.items():
        if bumps:
            bump_type = max_bump(bumps)
            results.append({"dataset": dataset, "bump": bump_type})
            dataset_bump_types.append(bump_type)

    # Repo version bumps if ANY dataset changes OR if repo-only files change
    # Take the max bump type from all sources
    all_bump_types = dataset_bump_types + repo_bumps
    repo_bump = max_bump(all_bump_types)
    has_changes = bool(results) or repo_bump != "none"

    # Output for GitHub Actions
    print(f"has_changes={str(has_changes).lower()}")
    print(f"datasets={json.dumps(results)}")
    print(f"repo_bump={repo_bump}")

    # Also write to a file for other scripts
    output = {
        "has_changes": has_changes,
        "datasets": results,
        "repo_bump": repo_bump,
    }
    Path("bump_plan.json").write_text(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()