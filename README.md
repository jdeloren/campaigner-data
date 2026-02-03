# Campaigner Game Data

Game reference data for the [Campaigner](https://github.com/jdeloren/campaigner) application.

## Overview

This repository contains structured game data in JSON format. The data is organized by game system (ruleset) and can be used by any compatible application.

## Structure

```
data/
├── dnd5e/                    # D&D 5th Edition
│   ├── manifest.json         # Version and schema info
│   ├── races.json
│   ├── classes.json
│   ├── equipment.json
│   ├── spells/
│   │   └── level_N.json
│   ├── class_features/
│   │   └── {class}/{subclass}.json
│   └── ...
└── {other-system}/           # Future game systems

schemas/
├── versions.json             # Current schema versions
└── json/                     # JSON Schema files
    ├── class.schema.json
    ├── race.schema.json
    └── ...
```

## Usage

### For Developers

1. Clone this repository
2. Run validation: `python scripts/validate.py --all`
3. Package for deployment: `python scripts/package.py --ruleset dnd5e`

### For the Campaigner App

Set the `DATA_DIR` environment variable to point to the `data/` folder, or use the setup script in the main Campaigner repository.

## Versioning

This repository uses semantic versioning with three levels:

### Dataset Versions

Each ruleset (e.g., `dnd5e`) has its own version in `data/{ruleset}/manifest.json`:

```json
{
  "name": "dnd5e",
  "version": "1.2.3",
  "schema_versions": {
    "class": "1.0",
    "race": "1.0"
  }
}
```

### Schema Versions

Schema versions are tracked in `schemas/versions.json`. Each data type (class, race, spell, etc.) has its own version. When a schema changes in a breaking way, its version is bumped.

Dataset manifests declare which schema versions they're compatible with via `schema_versions`.

### Repository Version

Infrastructure changes (scripts, workflows, configs) are versioned separately from datasets.

## Commit Convention

Version bumps are determined by commit message prefixes:

| Prefix | Bump | Use for |
|--------|------|---------|
| `fix:` | patch | Bug fixes, typos, data corrections |
| `feat:` | minor | New content (spells, classes, races, etc.) |
| `breaking:` | major | Schema changes, data restructuring |
| *(no prefix)* | patch | Fallback default |

### Examples

```bash
# Patch bump - fixing a typo
git commit -m "fix: correct Fireball damage from 8d6 to 8d6"

# Minor bump - adding new content
git commit -m "feat: add Monk class features"

# Major bump - breaking schema change
git commit -m "breaking: restructure spell components format"
```

### What Gets Bumped

- Commits touching `data/{ruleset}/*` → bump that dataset's version
- Commits touching `scripts/`, `.github/`, root configs → bump repo version
- Commits touching `schemas/` → requires manual schema version bump

### Schema Changes

Schema changes require a **manual version bump** in `schemas/versions.json`. CI will fail if a schema file changes but its version doesn't.

## Releases

Releases are created automatically on merge to main:

- Dataset releases are tagged as `{ruleset}-v{version}` (e.g., `dnd5e-v1.2.3`)
- Repo releases are tagged as `v{version}` (e.g., `v1.0.0`)

Each release includes a packaged tarball of the affected dataset(s).

## Contributing

Contributions are welcome! Please ensure your data:

1. Contains only **mechanical information** (stats, rules, formulas)
2. Does NOT include copyrighted flavor text or lore
3. Passes validation: `python scripts/validate.py --all`
4. Uses appropriate commit prefixes (see Commit Convention above)

See [docs/CLASS_FEATURES_GUIDE.md](docs/CLASS_FEATURES_GUIDE.md) for the data format specification.

## License

This data is licensed under [CC BY-SA 4.0](LICENSE). You are free to use, modify, and distribute this data with attribution.

**Note:** Game system names and trademarks are property of their respective owners. This repository contains game mechanics only, which are not subject to copyright.
