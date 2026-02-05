# Versioning & Release Process

This project uses [Semantic Versioning](https://semver.org/) with automated releases driven by commit message conventions.

## Version Format

```
MAJOR.MINOR.PATCH[-beta.N]

Examples:
  1.0.0        - Stable release
  1.2.0-beta.1 - Pre-release (beta)
  1.2.0-beta.2 - Second beta of same version
```

| Component | When to increment |
|-----------|-------------------|
| **MAJOR** | Breaking schema changes that require consumer updates |
| **MINOR** | New content (races, classes, spells, etc.), backwards compatible |
| **PATCH** | Bug fixes, data corrections, typos |
| **beta.N** | Pre-release testing before stable |

## Commit Message Conventions

Commit messages drive automatic version bumps. The format follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types

| Type | Description | Version Bump |
|------|-------------|--------------|
| `fix:` | Bug fix, data correction | PATCH |
| `feat:` | New content (races, classes, spells) | MINOR |
| `breaking:` | Schema changes, data restructuring | MAJOR |
| `docs:` | Documentation only | No release |
| `chore:` | Maintenance, dependencies | No release |
| `refactor:` | Schema/code restructuring (no data change) | No release |
| `test:` | Adding/updating tests | No release |
| `ci:` | CI/CD changes | No release |
| `style:` | Formatting, whitespace | No release |

### Beta vs Stable Releases

Add `!` before the colon to create a **beta** release instead of stable:

| Commit | Result |
|--------|--------|
| `fix: correct Fireball damage` | Stable patch release |
| `fix!: experimental data fix` | **Beta** patch release |
| `feat: add Monk class` | Stable minor release |
| `feat!: add new race (testing)` | **Beta** minor release |
| `breaking: restructure spell schema` | Stable major release |
| `breaking!: experimental schema change` | **Beta** major release |

### Promoting Beta to Stable

Use `release:` to promote the current beta version to stable:

```
release: ready for production
```

This removes the `-beta.N` suffix without changing the version number.

## Examples

### Adding New Content

```bash
# Current: 1.0.0

git commit -m "feat: add Dwarf race and subraces"
# Result: 1.1.0 (stable)

git commit -m "fix: correct Dwarf darkvision range"
# Result: 1.1.1 (stable)
```

### Beta Testing Flow

```bash
# Current: 1.0.0

git commit -m "feat!: add Dwarf race"
# Result: 1.1.0-beta.1

git commit -m "feat!: add Hill Dwarf subrace"
# Result: 1.1.0-beta.2

git commit -m "fix!: correct Dwarf traits"
# Result: 1.1.0-beta.3

git commit -m "release: Dwarf content complete"
# Result: 1.1.0 (stable)
```

### Schema Changes

```bash
# Current: 1.5.2

git commit -m "breaking!: add requirements system to equipment schema"
# Result: 2.0.0-beta.1

git commit -m "feat!: add Dwarf race with new mechanics"
# Result: 2.0.0-beta.2

git commit -m "release: schema and content ready"
# Result: 2.0.0 (stable)
```

## Scope (Optional)

You can add a scope in parentheses to indicate the affected area:

```bash
git commit -m "feat(races): add Dwarf and subraces"
git commit -m "fix(spells): correct Fireball damage"
git commit -m "breaking(equipment): restructure armor requirements"
```

Scope is informational only and doesn't affect versioning.

## What Triggers a Release?

On every push to `main`:

1. **Analyze commits** since the last tag
2. **Determine version bump** based on highest-priority commit type:
   - `breaking` > `feat` > `fix`
   - `!` suffix → beta, no `!` → stable
   - `release:` → promote existing beta
3. **Run validation** (schema + data validation)
4. **If validation passes**:
   - Update `manifest.json` with new version
   - Create git tag (`dnd5e-v1.2.0` or `dnd5e-v1.2.0-beta.1`)
   - Create GitHub Release with changelog

### No Release Triggered

These commit types alone will **not** trigger a release:
- `docs:`, `chore:`, `refactor:`, `test:`, `ci:`, `style:`

You can accumulate these commits and they'll be included in the changelog of the next release.

## Version in Data Files

The authoritative version for each ruleset is stored in its `manifest.json`:

```json
{
  "name": "dnd5e",
  "version": "1.2.0",
  "description": "D&D 5th Edition (2014) SRD Data"
}
```

## Quick Reference

```bash
# Bug fix / data correction (stable)
git commit -m "fix: description"

# Bug fix (beta)
git commit -m "fix!: description"

# New content (stable)
git commit -m "feat: description"

# New content (beta)
git commit -m "feat!: description"

# Breaking schema change (stable)
git commit -m "breaking: description"

# Breaking schema change (beta)
git commit -m "breaking!: description"

# Promote beta to stable
git commit -m "release: description"

# No release
git commit -m "docs: description"
git commit -m "chore: description"
git commit -m "refactor: description"
```
