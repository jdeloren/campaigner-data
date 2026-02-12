#!/usr/bin/env python3
"""
Validate game data files against JSON schemas.

Usage:
    python scripts/validate.py --all              # Validate all rulesets
    python scripts/validate.py --ruleset dnd5e    # Validate specific ruleset
    python scripts/validate.py --syntax-only      # JSON syntax check only (no schema)

Exit codes:
    0 = All files valid
    1 = Validation errors found
"""

import argparse
import json
import sys
from pathlib import Path

# Optional jsonschema import - only needed for schema validation
try:
    import jsonschema
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


# Repository paths
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
SCHEMAS_DIR = REPO_ROOT / "schemas" / "json"

# Mapping from data file names to schema file names
# Keys are the base filename (without .json), values are schema filenames
SCHEMA_MAP = {
    "races": "race.schema.json",
    "classes": "class.schema.json",
    "equipment": "equipment.schema.json",
    "spells": "spell.schema.json",  # For files in spells/ subdirectory
    "class_features": "class_feature.schema.json",  # For files in class_features/
    "backgrounds": "background.schema.json",
    "deities": "deity.schema.json",
    "domains": "domain.schema.json",
    "tools": "tool.schema.json",
    "fighting_styles": "fighting_style.schema.json",
    "maneuvers": "maneuver.schema.json",
    "statuses": "status.schema.json",
    "commands": "command.schema.json",
}


def discover_rulesets() -> list[str]:
    """Find all ruleset directories under data/."""
    if not DATA_DIR.exists():
        return []
    return [d.name for d in DATA_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]


def discover_data_files(ruleset: str) -> list[Path]:
    """Find all JSON files for a ruleset."""
    ruleset_dir = DATA_DIR / ruleset
    if not ruleset_dir.exists():
        return []
    return list(ruleset_dir.rglob("*.json"))


def get_schema_for_file(file_path: Path) -> Path | None:
    """Determine which schema applies to a data file."""
    # Check if file is in a subdirectory (spells/, class_features/)
    relative = file_path.relative_to(DATA_DIR)
    parts = relative.parts  # e.g., ('dnd5e', 'spells', 'level_0.json')

    if len(parts) >= 3:
        # File is in a subdirectory like spells/ or class_features/
        subdir = parts[1]  # 'spells' or 'class_features'
        schema_name = SCHEMA_MAP.get(subdir)
    else:
        # Top-level file like races.json
        base_name = file_path.stem  # 'races' from 'races.json'
        schema_name = SCHEMA_MAP.get(base_name)

    if schema_name:
        schema_path = SCHEMAS_DIR / schema_name
        if schema_path.exists():
            return schema_path

    return None


def validate_json_syntax(file_path: Path) -> tuple[bool, str | None]:
    """Validate that a file contains valid JSON."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json.load(f)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"JSON syntax error: {e}"
    except Exception as e:
        return False, f"Error reading file: {e}"


def build_schema_registry() -> "Registry":
    """Build a registry of all schemas for reference resolution."""
    registry = Registry()

    # Load all schema files and register them
    for schema_file in SCHEMAS_DIR.glob("*.schema.json"):
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_content = json.load(f)

        # Use the filename as the URI
        uri = schema_file.name
        resource = Resource.from_contents(schema_content, default_specification=DRAFT202012)
        registry = registry.with_resource(uri, resource)

    return registry


# Cache the registry
_schema_registry = None


def get_schema_registry() -> "Registry":
    """Get or create the schema registry."""
    global _schema_registry
    if _schema_registry is None:
        _schema_registry = build_schema_registry()
    return _schema_registry


def validate_against_schema(file_path: Path, schema_path: Path) -> tuple[bool, str | None]:
    """Validate a JSON file against a JSON Schema."""
    if not HAS_JSONSCHEMA:
        return True, None  # Skip schema validation if jsonschema not installed

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        # Use registry for resolving $ref to common.schema.json
        registry = get_schema_registry()
        validator = jsonschema.Draft202012Validator(schema, registry=registry)
        validator.validate(data)
        return True, None
    except jsonschema.ValidationError as e:
        # Provide a concise error message
        path = " -> ".join(str(p) for p in e.absolute_path) if e.absolute_path else "root"
        return False, f"Schema validation error at '{path}': {e.message}"
    except Exception as e:
        return False, f"Validation error: {e}"


def validate_file(file_path: Path, syntax_only: bool = False) -> tuple[bool, list[str]]:
    """Validate a single data file. Returns (success, list of error messages)."""
    errors = []

    # Always validate JSON syntax
    valid, error = validate_json_syntax(file_path)
    if not valid:
        errors.append(error)
        return False, errors

    if syntax_only:
        return True, errors

    # Try schema validation if schema exists
    schema_path = get_schema_for_file(file_path)
    if schema_path:
        valid, error = validate_against_schema(file_path, schema_path)
        if not valid:
            errors.append(error)
            return False, errors

    return True, errors


def validate_ruleset(ruleset: str, syntax_only: bool = False) -> tuple[int, int, list[tuple[Path, str]]]:
    """
    Validate all files in a ruleset.

    Returns: (total_files, valid_files, list of (file_path, error_message))
    """
    files = discover_data_files(ruleset)
    total = len(files)
    valid = 0
    errors = []

    for file_path in sorted(files):
        success, file_errors = validate_file(file_path, syntax_only)
        if success:
            valid += 1
        else:
            for error in file_errors:
                errors.append((file_path, error))

    return total, valid, errors


def main():
    parser = argparse.ArgumentParser(description="Validate game data files")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all rulesets"
    )
    parser.add_argument(
        "--ruleset",
        type=str,
        help="Validate specific ruleset (e.g., dnd5e)"
    )
    parser.add_argument(
        "--syntax-only",
        action="store_true",
        help="Only check JSON syntax, skip schema validation"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show all files, not just errors"
    )

    args = parser.parse_args()

    if not args.all and not args.ruleset:
        parser.error("Must specify --all or --ruleset")

    # Determine which rulesets to validate
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

    # Check if schemas are available
    schemas_available = SCHEMAS_DIR.exists() and any(SCHEMAS_DIR.glob("*.json"))
    if not args.syntax_only and not schemas_available:
        print("Note: No schemas found in schemas/json/ - running syntax validation only")
        print("      Run schema generation (Phase 2) to enable full validation\n")
        args.syntax_only = True

    if not args.syntax_only and not HAS_JSONSCHEMA:
        print("Note: jsonschema package not installed - running syntax validation only")
        print("      Install with: pip install jsonschema\n")
        args.syntax_only = True

    # Validate each ruleset
    total_files = 0
    total_valid = 0
    all_errors = []

    for ruleset in sorted(rulesets):
        print(f"Validating {ruleset}...")
        count, valid, errors = validate_ruleset(ruleset, args.syntax_only)
        total_files += count
        total_valid += valid
        all_errors.extend(errors)

        if args.verbose:
            print(f"  {valid}/{count} files valid")

    # Print results
    print()
    if all_errors:
        print("Errors found:")
        for file_path, error in all_errors:
            rel_path = file_path.relative_to(REPO_ROOT)
            print(f"  {rel_path}: {error}")
        print()

    mode = "syntax" if args.syntax_only else "schema"
    print(f"Validation complete ({mode}): {total_valid}/{total_files} files valid")

    sys.exit(0 if not all_errors else 1)


if __name__ == "__main__":
    main()
