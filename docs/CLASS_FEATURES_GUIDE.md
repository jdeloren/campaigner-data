# Class Features Schema Guide

This guide explains how to define class features, racial traits, and other game mechanics using the structured mechanic models. The schema uses **discriminated unions** — the `type` field determines which model is used and what fields are valid.

## Table of Contents

- [Core Structure](#core-structure)
- [Mechanic Types](#mechanic-types)
  - [BaseMechanic (action, passive, reaction, etc.)](#basemechanic)
  - [ResourceMechanic](#resourcemechanic)
  - [ChoiceMechanic](#choicemechanic)
  - [ProficiencyMechanic](#proficiencymechanic)
  - [GrantedSpellsMechanic](#grantedspellsmechanic)
  - [SpellcastingMechanic](#spellcastingmechanic)
  - [RetrainMechanic](#retrainmechanic)
- [Effects](#effects)
  - [Common Effect Fields](#common-effect-fields)
  - [Damage and Healing](#damage-and-healing)
  - [Advantage and Disadvantage](#advantage-and-disadvantage)
  - [Status Effects](#status-effects)
  - [Damage Response](#damage-response)
  - [Attribute Modification](#attribute-modification)
  - [Grants](#grants)
  - [Roll Modifiers](#roll-modifiers)
  - [Auras](#auras)
  - [Movement and Forced Movement](#movement-and-forced-movement)
  - [Environmental Effects](#environmental-effects)
  - [Rare Effect Types](#rare-effect-types)
- [Calculations](#calculations)
- [Requirements](#requirements)
  - [Common Requirements](#common-requirements)
  - [Combat Requirements](#combat-requirements)
  - [Perception Requirements](#perception-requirements)
  - [Other Requirements](#other-requirements)
- [Triggers](#triggers)
  - [Trigger Events](#trigger-events)
  - [Trigger Timing](#trigger-timing)
  - [Source and Target Filters](#source-and-target-filters)
  - [Complex Trigger Examples](#complex-trigger-examples)
- [Targeting](#targeting)
- [Scaling](#scaling)
- [Complex Patterns](#complex-patterns)
- [Version History](#version-history)

---

## Core Structure

A class feature has this structure:

```json
{
  "name": "Feature Name",
  "level": 1,
  "class": "Fighter",
  "description": "Plain text description of what the feature does.",
  "mechanics": [ ... ],
  "source": "phb",
  "ruleset": "dnd5e"
}
```

### Optional Top-Level Fields

| Field          | Type     | Description                                                                                            |
| -------------- | -------- | ------------------------------------------------------------------------------------------------------ |
| `triggered_by` | string   | Another feature that must be gained for this to become available (e.g., "Ability Score Improvement")   |
| `extends`      | string[] | Features this builds on — both appear in action list (e.g., Frenzy extends Rage)                       |
| `enhances`     | string   | Feature this modifies in place — only base feature appears (e.g., Destroy Undead enhances Turn Undead) |
| `subfeatures`  | array    | Sub-options within a feature (for Fighting Styles, Totem choices, etc.)                                |

### The Mechanics Array

The `mechanics` array contains one or more **Mechanic** objects. The `type` field determines the model:

```json
"mechanics": [
  { "type": "resource", ... },
  { "type": "bonus_action", ... },
  { "type": "passive", ... }
]
```

---

## Mechanic Types

### BaseMechanic

Covers most activated abilities and passive effects. The `type` field can be:

| Type           | Description                        |
| -------------- | ---------------------------------- |
| `action`       | Costs a standard action            |
| `bonus_action` | Costs a bonus action               |
| `reaction`     | Triggered response, costs reaction |
| `passive`      | Always active, no activation cost  |
| `movement`     | Movement-related ability           |
| `ritual`       | Can be cast as a ritual            |
| `critical_hit` | Triggers on critical hits          |
| `extra_attack` | Grants additional attacks          |
| `damage_bonus` | Adds damage under conditions       |
| `advantage`    | Grants advantage under conditions  |
| `resistance`   | Grants damage resistance           |
| `immunity`     | Grants immunity                    |
| `optional`     | Optional rule or variant           |
| `special`      | Doesn't fit other categories       |

#### Action Example — Second Wind

```json
{
  "type": "bonus_action",
  "name": "Second Wind",
  "uses": { "value": 1 },
  "recharge": "short_rest",
  "effects": [
    {
      "healing": {
        "dice": "1d10",
        "bonus": { "type": "class_level", "class": "Fighter" }
      },
      "target": { "type": "self" }
    }
  ]
}
```

#### Reaction Example — Uncanny Dodge

```json
{
  "type": "reaction",
  "name": "Uncanny Dodge",
  "trigger": {
    "event": ["hit"],
    "target": { "type": "self" },
    "source": {
      "perception": {
        "observer": "character",
        "subject": "attacker",
        "senses": ["sight"]
      }
    }
  },
  "effects": [
    {
      "damage_response": {
        "response": "half",
        "to": "triggering_damage"
      }
    }
  ]
}
```

#### Passive Example — Danger Sense

```json
{
  "type": "passive",
  "name": "Danger Sense",
  "effects": [
    {
      "advantage": {
        "on": "saving_throw",
        "ability": ["Dexterity"]
      },
      "requirements": [
        {
          "type": "perception",
          "observer": "character",
          "subject": "source",
          "senses": ["sight", "hearing"],
          "match": "any"
        },
        {
          "type": "status",
          "value": ["blinded", "deafened", "incapacitated"],
          "negate": true
        }
      ]
    }
  ]
}
```

#### Passive with Trigger — Sneak Attack

Passive mechanics can have triggers for "when X happens" effects:

```json
{
  "type": "passive",
  "name": "Sneak Attack",
  "uses": { "value": 1 },
  "recharge": "turn",
  "trigger": {
    "event": ["hit"],
    "source": { "type": ["weapon"] }
  },
  "effects": [
    {
      "damage_bonus": {
        "type": ["same_as_weapon"]
      },
      "scaling_key": "damage"
    }
  ],
  "requirements": [{ "type": "weapon_property", "value": ["finesse", "ranged"] }],
  "scaling": {
    "damage": {
      "1": "1d6",
      "3": "2d6",
      "5": "3d6",
      "7": "4d6",
      "9": "5d6",
      "11": "6d6",
      "13": "7d6",
      "15": "8d6",
      "17": "9d6",
      "19": "10d6"
    }
  }
}
```

#### BaseMechanic Fields Reference

| Field           | Type                  | Description                                                                   |
| --------------- | --------------------- | ----------------------------------------------------------------------------- |
| `type`          | string                | Required. One of the BaseMechanic types                                       |
| `name`          | string                | Display name                                                                  |
| `uses`          | Uses                  | Usage limits (`value`, `calculation`, `minimum`)                              |
| `limit`         | ScalingReference      | Reference to scaling for level-based limits                                   |
| `recharge`      | RechargeType          | When it recharges: `short_rest`, `long_rest`, `turn`, `round`, `dawn`, `dusk` |
| `scaling`       | Scaling               | Level-based scaling definitions                                               |
| `requirements`  | MechanicRequirement[] | Conditions for the mechanic to apply                                          |
| `concentration` | boolean               | Requires concentration                                                        |
| `activation`    | Activation            | How the mechanic activates                                                    |
| `trigger`       | Trigger               | Event that triggers this mechanic                                             |
| `grants`        | Grant                 | Action or ability granted                                                     |
| `effects`       | Effect[]              | Effects applied by this mechanic                                              |
| `target`        | Target                | Who/what is targeted                                                          |
| `area`          | Area                  | Area of effect                                                                |
| `damage`        | Damage                | Direct damage                                                                 |
| `saving_throw`  | SavingThrow           | Save required                                                                 |
| `on_failure`    | Effect                | Effect on failed save                                                         |
| `on_success`    | Effect                | Effect on successful save                                                     |
| `cost`          | Cost[]                | Resource or currency costs                                                    |
| `duration`      | Duration              | How long effects last                                                         |
| `range`         | Distance              | Range of the mechanic                                                         |
| `description`   | string                | Descriptive text                                                              |

---

### ResourceMechanic

Defines a resource pool that other mechanics spend.

```json
{
  "type": "resource",
  "id": "superiority_dice",
  "name": "Superiority Dice",
  "count": 4,
  "dice_sides": 8,
  "recharge": "short_rest",
  "scaling": {
    "count": { "7": 5, "15": 6 },
    "dice_sides": { "10": 10, "18": 12 }
  }
}
```

#### Ki Points (count from level)

```json
{
  "type": "resource",
  "id": "ki",
  "name": "Ki Points",
  "count": { "type": "class_level", "class": "Monk" },
  "recharge": "short_rest"
}
```

#### Rage (with unlimited at 20)

```json
{
  "type": "resource",
  "id": "rage",
  "name": "Rage",
  "count": 2,
  "recharge": "long_rest",
  "scaling": {
    "count": { "3": 3, "6": 4, "12": 5, "17": 6, "20": -1 }
  }
}
```

The `-1` value indicates unlimited uses.

#### ResourceMechanic Fields

| Field        | Type                     | Required | Description                                                  |
| ------------ | ------------------------ | -------- | ------------------------------------------------------------ |
| `type`       | `"resource"`             | Yes      | Must be "resource"                                           |
| `id`         | string                   | Yes      | Unique identifier for referencing (e.g., "superiority_dice") |
| `name`       | string                   | Yes      | Display name                                                 |
| `count`      | int/string/ResourceCount | No       | Pool size — static, formula, or object                       |
| `recharge`   | RechargeType             | Yes      | When pool recharges                                          |
| `dice_sides` | int                      | No       | Die size if resource uses dice (e.g., 8 for d8)              |
| `scaling`    | Scaling                  | No       | Level-based scaling for count or dice_sides                  |

---

### ChoiceMechanic

Character-building choices made at level-up.

#### Skill Choice

```json
{
  "type": "choice",
  "choice_type": "skill",
  "name": "Skill Proficiencies",
  "count": 4,
  "options": [
    "Acrobatics",
    "Athletics",
    "Deception",
    "Insight",
    "Intimidation",
    "Investigation",
    "Perception",
    "Performance",
    "Persuasion",
    "Sleight of Hand",
    "Stealth"
  ]
}
```

#### Fighting Style (reference to subfeatures)

```json
{
  "type": "choice",
  "choice_type": "fighting_style",
  "name": "Fighting Style",
  "count": 1,
  "options_ref": "subfeatures"
}
```

The `options_ref` points to a sibling `subfeatures` array on the feature.

#### Expertise (query-based)

```json
{
  "type": "choice",
  "choice_type": "query",
  "name": "Expertise",
  "count": 2,
  "query": {
    "endpoint": "character.skill_proficiencies",
    "exclude": "character.skill_expertise"
  }
}
```

#### Ability Score Improvement

```json
{
  "type": "choice",
  "choice_type": "asi",
  "name": "Ability Score Improvement",
  "count": 2
}
```

For ASI, the UI knows to present ability score options.

#### Subclass Selection

```json
{
  "type": "choice",
  "choice_type": "subclass",
  "name": "Martial Archetype"
}
```

#### ChoiceMechanic Fields

| Field          | Type                  | Description                                                                        |
| -------------- | --------------------- | ---------------------------------------------------------------------------------- |
| `type`         | `"choice"`            | Must be "choice"                                                                   |
| `choice_type`  | ChoiceType            | What kind: `skill`, `language`, `subclass`, `asi`, `fighting_style`, `query`, etc. |
| `options`      | string[]              | Inline list of choices                                                             |
| `options_ref`  | string                | Reference to sibling key containing options (e.g., "subfeatures")                  |
| `count`        | int                   | How many to pick (default: 1)                                                      |
| `name`         | string                | Display name                                                                       |
| `query`        | Query                 | Data query for dynamic options                                                     |
| `effects`      | Effect[]              | Effects applied by the choice                                                      |
| `requirements` | MechanicRequirement[] | Requirements to make this choice                                                   |
| `scaling`      | Scaling               | Level-based scaling                                                                |

---

### ProficiencyMechanic

Grants proficiencies directly.

```json
{
  "type": "proficiency",
  "category": "armor",
  "proficiencies": ["light", "medium", "shields"]
}
```

```json
{
  "type": "proficiency",
  "category": "weapon",
  "proficiencies": ["simple", "martial"]
}
```

```json
{
  "type": "proficiency",
  "category": "saving_throw",
  "proficiencies": ["Strength", "Constitution"]
}
```

```json
{
  "type": "proficiency",
  "category": "tool",
  "proficiencies": ["Thieves' Tools"]
}
```

#### ProficiencyMechanic Fields

| Field           | Type                  | Description                                                |
| --------------- | --------------------- | ---------------------------------------------------------- |
| `type`          | `"proficiency"`       | Must be "proficiency"                                      |
| `category`      | string                | One of: `skill`, `weapon`, `armor`, `saving_throw`, `tool` |
| `proficiencies` | string[]              | List of proficiency names                                  |
| `requirements`  | MechanicRequirement[] | Conditions (rare)                                          |

---

### GrantedSpellsMechanic

Grants spells from class features, domains, or similar sources.

#### Domain Spells (always prepared)

```json
{
  "type": "granted_spells",
  "spells": {
    "1": ["Bless", "Cure Wounds"],
    "3": ["Lesser Restoration", "Spiritual Weapon"],
    "5": ["Beacon of Hope", "Revivify"],
    "7": ["Death Ward", "Guardian of Faith"],
    "9": ["Mass Cure Wounds", "Raise Dead"]
  },
  "always_prepared": true
}
```

#### Ritual-Only Spells

```json
{
  "type": "granted_spells",
  "spells": ["Find Familiar"],
  "ritual_only": true
}
```

#### GrantedSpellsMechanic Fields

| Field             | Type               | Description                                                 |
| ----------------- | ------------------ | ----------------------------------------------------------- |
| `type`            | `"granted_spells"` | Must be "granted_spells"                                    |
| `spells`          | dict or list       | Spell level map `{"1": ["Bless"]}` or flat list `["Light"]` |
| `always_prepared` | boolean            | Don't count against prepared limit                          |
| `ritual_only`     | boolean            | Can only cast as rituals                                    |

---

### SpellcastingMechanic

Innate spellcasting from racial traits or features (not class spellcasting).

#### Drow Magic

```json
{
  "type": "spellcasting",
  "name": "Dancing Lights",
  "spell": "dancing lights",
  "ability": "Charisma"
}
```

#### With Uses and Requirements

```json
{
  "type": "spellcasting",
  "name": "Faerie Fire",
  "spell": "faerie fire",
  "ability": "Charisma",
  "uses": { "value": 1 },
  "recharge": "long_rest",
  "requirements": [{ "type": "level", "minimum": 3 }]
}
```

#### SpellcastingMechanic Fields

| Field          | Type                  | Description                        |
| -------------- | --------------------- | ---------------------------------- |
| `type`         | `"spellcasting"`      | Must be "spellcasting"             |
| `name`         | string                | Display name                       |
| `spell`        | string                | Spell identifier                   |
| `ability`      | string                | Spellcasting ability               |
| `components`   | string[]              | Required components                |
| `uses`         | Uses                  | Usage limits                       |
| `recharge`     | RechargeType          | When it recharges                  |
| `requirements` | MechanicRequirement[] | Requirements (often level minimum) |

---

### RetrainMechanic

Retraining options at level-up.

#### Replace a Cantrip

```json
{
  "type": "retrain",
  "name": "Cantrip Replacement",
  "attribute": "cantrips",
  "operation": "replace",
  "optional": true,
  "source": {
    "list": "spells",
    "filter": { "class": "Sorcerer", "level": 0 }
  }
}
```

#### Add a Fighting Style

```json
{
  "type": "retrain",
  "name": "Martial Versatility",
  "attribute": "fighting_styles",
  "operation": "replace",
  "optional": true,
  "source": {
    "list": "fighting_styles",
    "filter": { "class": "Fighter" }
  }
}
```

#### RetrainMechanic Fields

| Field       | Type          | Description                                   |
| ----------- | ------------- | --------------------------------------------- |
| `type`      | `"retrain"`   | Must be "retrain"                             |
| `name`      | string        | Display name                                  |
| `attribute` | string        | Character attribute being modified            |
| `operation` | string        | `"replace"` or `"add"`                        |
| `optional`  | boolean       | Whether retraining is optional (usually true) |
| `source`    | RetrainSource | Where replacement options come from           |

---

## Effects

Effects describe what happens when a mechanic activates. The `Effect` model has many optional fields — use only what's needed.

### Common Effect Fields

| Field          | Type                  | Description                                 |
| -------------- | --------------------- | ------------------------------------------- |
| `target`       | Target                | Who/what is affected                        |
| `requirements` | MechanicRequirement[] | Conditions for this specific effect         |
| `duration`     | Duration              | How long the effect lasts                   |
| `trigger`      | Trigger               | When this effect fires (for nested effects) |
| `scaling_key`  | string                | Reference to scaling property               |
| `effects`      | Effect[]              | Nested effects                              |

### Damage and Healing

#### Basic Damage

```json
{
  "damage": {
    "dice": "2d6",
    "type": ["fire"]
  }
}
```

#### Damage with Bonus

```json
{
  "damage": {
    "dice": "1d8",
    "type": ["slashing"],
    "bonus": { "type": "ability_modifier", "ability": "Strength" }
  }
}
```

#### Damage Bonus (added to existing damage)

```json
{
  "damage_bonus": {
    "dice": "1d6",
    "type": ["necrotic"]
  }
}
```

#### Damage with Same Type as Weapon

```json
{
  "damage_bonus": {
    "dice": "2d6",
    "type": ["same_as_weapon"]
  }
}
```

#### Healing

```json
{
  "healing": {
    "dice": "2d8",
    "bonus": { "type": "ability_modifier", "ability": "Wisdom" }
  }
}
```

#### Healing with Class Level

```json
{
  "healing": {
    "dice": "1d10",
    "bonus": { "type": "class_level", "class": "Fighter" }
  }
}
```

#### Recurring Damage (while status active)

```json
{
  "recurring_damage": {
    "dice": "1d6",
    "type": ["fire"]
  }
}
```

### Advantage and Disadvantage

#### Advantage on Attacks

```json
{
  "advantage": {
    "on": "attack"
  }
}
```

#### Advantage on Specific Ability Checks

```json
{
  "advantage": {
    "on": "ability_check",
    "ability": ["Strength"]
  }
}
```

#### Advantage on Saves Against Magic

```json
{
  "advantage": {
    "on": "saving_throw",
    "against": {
      "origin": "magical"
    }
  }
}
```

#### Disadvantage on Attacks Against You

```json
{
  "disadvantage": {
    "on": "attack",
    "against": {
      "target": "character"
    }
  }
}
```

#### Disadvantage on Target's Saves

```json
{
  "disadvantage": {
    "on": "saving_throw",
    "ability": ["Wisdom"],
    "against": {
      "from_source": "character"
    }
  }
}
```

#### Advantage/Disadvantage Fields

| Field         | Type     | Description                                                |
| ------------- | -------- | ---------------------------------------------------------- |
| `on`          | string   | What's affected: `attack`, `saving_throw`, `ability_check` |
| `ability`     | string[] | Specific abilities (for saves/checks)                      |
| `weapon_type` | string[] | Weapon types: `melee`, `ranged`                            |
| `against`     | Against  | Who/what the rolls are against                             |

### Status Effects

#### Apply Status

```json
{
  "apply_status": {
    "name": "frightened",
    "source": "character",
    "action": "Menacing Attack",
    "duration": { "value": 1, "unit": "rounds", "ends": "end_of_next_turn" }
  }
}
```

#### Status with Concentration

```json
{
  "apply_status": {
    "name": "charmed",
    "source": "character",
    "action": "Charm Person",
    "concentration": true,
    "duration": { "value": 1, "unit": "hours" }
  }
}
```

#### Status with Modifier (frightened OF someone)

```json
{
  "apply_status": {
    "name": "frightened",
    "source": "character",
    "modifier": "character"
  }
}
```

#### Status with Ongoing Effects

```json
{
  "apply_status": {
    "name": "hexed",
    "source": "character",
    "action": "Hex",
    "concentration": true,
    "effect": {
      "trigger": { "event": ["hit"], "source": { "type": ["character"] } },
      "damage_bonus": { "dice": "1d6", "type": ["necrotic"] }
    }
  }
}
```

#### Status with Escape Save

```json
{
  "apply_status": {
    "name": "grappled",
    "source": "character",
    "escape": {
      "ability": ["Strength", "Dexterity"],
      "dc": { "type": "ability_check", "ability": "Strength" }
    }
  }
}
```

#### Status with Constraints

```json
{
  "apply_status": {
    "name": "charmed",
    "source": "character",
    "constraints": {
      "cannot_attack": "character",
      "cannot_target_with_harmful": "character"
    }
  }
}
```

### Damage Response

Modifies how damage is received.

#### Resistance

```json
{
  "damage_response": {
    "response": "resistance",
    "to": ["bludgeoning", "piercing", "slashing"]
  }
}
```

#### Conditional Resistance

```json
{
  "damage_response": {
    "response": "resistance",
    "to": ["bludgeoning", "piercing", "slashing"],
    "source": { "origin": "nonmagical" }
  }
}
```

#### Immunity

```json
{
  "damage_response": {
    "response": "immunity",
    "to": ["poison"]
  }
}
```

#### Vulnerability

```json
{
  "damage_response": {
    "response": "vulnerability",
    "to": ["fire"]
  }
}
```

#### Half Damage (Uncanny Dodge)

```json
{
  "damage_response": {
    "response": "half",
    "to": "triggering_damage"
  }
}
```

### Attribute Modification

Modifies character attributes directly.

#### Set Critical Threshold (Improved Critical)

```json
{
  "attribute": {
    "target": "combat.critical_hit_threshold",
    "calculation": {
      "operation": "set",
      "operators": [{ "type": "integer", "value": 19 }]
    }
  }
}
```

#### Increase Movement Speed

```json
{
  "attribute": {
    "target": "movement.base",
    "calculation": {
      "operation": "add",
      "operators": [{ "type": "integer", "value": 10 }]
    }
  }
}
```

#### Set Attacks Per Action (Extra Attack)

```json
{
  "attribute": {
    "target": "combat.attacks_per_action",
    "calculation": {
      "operation": "set",
      "operators": [{ "type": "integer", "value": 2 }]
    }
  }
}
```

#### Grant All Languages (Tongues effect)

```json
{
  "attribute": {
    "target": "languages",
    "query": { "endpoint": "languages" }
  }
}
```

### Grants

Grants actions or abilities.

#### Grant Bonus Action (Cunning Action)

```json
{
  "grants": {
    "name": "Dash",
    "activation": "bonus_action"
  }
}
```

#### Grant Attack (Two-Weapon Fighting)

```json
{
  "grants": {
    "name": "Attack",
    "type": "melee_weapon",
    "activation": "bonus_action",
    "count": 1
  },
  "requirements": [
    { "type": "attack", "hand": "main_hand" },
    { "type": "weapon_property", "value": ["light"] }
  ]
}
```

#### Grant Reaction Attack (Riposte)

```json
{
  "grants": {
    "name": "Attack",
    "type": "melee_weapon",
    "activation": "reaction",
    "count": 1,
    "target": { "type": "triggering_creature" }
  }
}
```

#### Grant Movement with Immunity

```json
{
  "grants": {
    "name": "Move",
    "distance": { "value": "half_speed", "unit": "feet" },
    "immunity": {
      "to": "opportunity_attack",
      "from": { "type": "target" }
    }
  }
}
```

#### Grant Interaction (modified spell/feature activation)

```json
{
  "grants": {
    "name": "Suggestion",
    "interaction": {
      "name": "Suggestion",
      "activation": "action",
      "cost": "none",
      "save": "auto_fail",
      "ends": ["read_thoughts"]
    }
  }
}
```

### Roll Modifiers

Adds bonuses to rolls.

#### Add Charisma to Saves (Aura of Protection)

```json
{
  "roll_modifier": {
    "on": "saving_throw",
    "calculation": {
      "operation": "add",
      "operators": [{ "type": "ability_modifier", "ability": "Charisma" }]
    },
    "minimum": 1
  }
}
```

#### Add Proficiency to Initiative

```json
{
  "roll_modifier": {
    "on": "initiative",
    "calculation": {
      "operation": "add",
      "operators": [{ "type": "attribute", "value": "proficiency_bonus" }]
    }
  }
}
```

#### Bardic Inspiration Die

```json
{
  "roll_modifier": {
    "on": ["attack", "ability_check", "saving_throw"],
    "calculation": {
      "operation": "add",
      "operators": [{ "type": "resource_die", "value": "bardic_inspiration" }]
    }
  }
}
```

### Auras

Persistent area effects around a character.

#### Aura of Protection

```json
{
  "aura": {
    "radius": { "value": 10, "unit": "feet" },
    "affects": {
      "type": "creatures",
      "disposition": "friendly",
      "include_self": true
    },
    "effect": {
      "roll_modifier": {
        "on": "saving_throw",
        "calculation": {
          "operation": "add",
          "operators": [{ "type": "ability_modifier", "ability": "Charisma" }]
        },
        "minimum": 1
      }
    }
  },
  "requirements": [{ "type": "status", "value": "incapacitated", "negate": true }],
  "scaling": {
    "radius": { "18": 30 }
  }
}
```

#### Aura with Multiple Effects

```json
{
  "aura": {
    "radius": { "value": 10, "unit": "feet" },
    "affects": { "type": "creatures", "disposition": "hostile" },
    "layers": [
      {
        "name": "aura_damage",
        "trigger": { "event": ["start_turn"] },
        "damage": { "dice": "1d4", "type": ["radiant"] }
      },
      {
        "name": "aura_disadvantage",
        "effect": {
          "disadvantage": { "on": "attack" }
        }
      }
    ]
  }
}
```

### Movement and Forced Movement

#### Grant Extra Movement

```json
{
  "movement": {
    "type": "bonus",
    "distance": { "value": 10, "unit": "feet" }
  }
}
```

#### Movement Type Grant (Climb, Swim)

```json
{
  "attribute": {
    "target": "movement.climb",
    "calculation": {
      "operation": "set",
      "operators": [{ "type": "attribute", "value": "movement.base" }]
    }
  }
}
```

#### Push (Forced Movement)

```json
{
  "forced_movement": {
    "type": "push",
    "distance": { "value": 15, "unit": "feet" },
    "direction": "away"
  }
}
```

#### Pull

```json
{
  "forced_movement": {
    "type": "pull",
    "distance": { "value": 10, "unit": "feet" },
    "direction": "toward"
  }
}
```

#### Knock Prone

```json
{
  "forced_movement": {
    "type": "prone"
  }
}
```

### Environmental Effects

#### Create Light

```json
{
  "environment": {
    "type": "lighting",
    "bright_light": { "value": 20, "unit": "feet" },
    "dim_light": { "value": 20, "unit": "feet" }
  }
}
```

#### Create Difficult Terrain

```json
{
  "environment": {
    "type": "terrain",
    "difficult": true
  }
}
```

#### Create Hazard

```json
{
  "environment": {
    "type": "hazard",
    "damage": { "dice": "2d6", "type": ["fire"] },
    "trigger": { "event": ["enter_area", "start_turn_in_area"] }
  }
}
```

### Rare Effect Types

#### Projectile (Magic Missile)

```json
{
  "projectile": {
    "count": 3,
    "auto_hit": true,
    "damage": { "dice": "1d4", "bonus": 1, "type": ["force"] }
  }
}
```

#### Distribution (Sleep, Color Spray)

```json
{
  "distribution": {
    "dice": "5d8",
    "resource": "hp"
  },
  "apply_status": { "name": "unconscious" }
}
```

#### Chain (Chaos Bolt)

```json
{
  "chain": {
    "condition": { "dice_sides": 8, "check": "matching" },
    "range": { "value": 30, "unit": "feet" },
    "inherit": true
  }
}
```

#### Sustained (Witch Bolt)

```json
{
  "sustained": {
    "cost": "action",
    "damage": { "dice": "1d12", "type": ["lightning"], "auto_hit": true },
    "target": { "type": "same_target" }
  }
}
```

#### Detection (Detect Magic)

```json
{
  "detection": {
    "detects": ["magic"],
    "range": { "value": 30, "unit": "feet" },
    "blocked_by": ["total_cover"]
  }
}
```

#### Entity Creation (Summons)

```json
{
  "entity": {
    "type": "creature",
    "name": "Spectral Steed",
    "stat_block": "riding_horse",
    "modifications": {
      "speed": 100,
      "appearance": "spectral"
    }
  }
}
```

#### Recover (restore resources)

```json
{
  "recover": {
    "resource": "hit_dice",
    "amount": { "type": "integer", "value": 1 }
  }
}
```

#### Negate (removes conditions)

```json
{
  "negate": ["invisible", "hidden"]
}
```

---

## Calculations

Calculations produce values using typed operands and operations.

### Operations

| Operation  | Description                             |
| ---------- | --------------------------------------- |
| `add`      | Sum all operands                        |
| `subtract` | Subtract from first operand             |
| `multiply` | Multiply all operands                   |
| `divide`   | Divide first by second (use `rounding`) |
| `max`      | Take highest value                      |
| `min`      | Take lowest value                       |
| `set`      | Use the value directly                  |

### Operand Types

| Type               | Example                                                       | Description               |
| ------------------ | ------------------------------------------------------------- | ------------------------- |
| `integer`          | `{ "type": "integer", "value": 5 }`                           | Static number             |
| `boolean`          | `{ "type": "boolean", "value": true }`                        | True/false                |
| `string`           | `{ "type": "string", "value": "fire" }`                       | Text value                |
| `dice`             | `{ "type": "dice", "dice": "1d6" }`                           | Dice expression           |
| `attribute`        | `{ "type": "attribute", "value": "proficiency_bonus" }`       | Character attribute       |
| `ability_modifier` | `{ "type": "ability_modifier", "ability": "Wisdom" }`         | Ability mod               |
| `class_level`      | `{ "type": "class_level", "class": "Fighter" }`               | Class level               |
| `resource_die`     | `{ "type": "resource_die", "value": "superiority_dice" }`     | Resource die value        |
| `scaling`          | `{ "type": "scaling", "value": "damage" }`                    | Scaling reference         |
| `roll_result`      | `{ "type": "roll_result" }`                                   | Result of triggering roll |
| `spell_level_cast` | `{ "type": "spell_level_cast" }`                              | Spell slot level used     |
| `function`         | `{ "type": "function", "function": "...", "context": "..." }` | Function call             |

### Examples

#### Add Two Values

```json
{
  "calculation": {
    "operation": "add",
    "operators": [
      { "type": "resource_die", "value": "superiority_dice" },
      { "type": "ability_modifier", "ability": "Strength" }
    ]
  }
}
```

#### Set a Value

```json
{
  "calculation": {
    "operation": "set",
    "operators": [{ "type": "integer", "value": 19 }]
  }
}
```

#### Take Maximum

```json
{
  "calculation": {
    "operation": "max",
    "operators": [
      { "type": "integer", "value": 1 },
      { "type": "ability_modifier", "ability": "Wisdom" }
    ]
  }
}
```

#### Divide with Rounding

```json
{
  "calculation": {
    "operation": "divide",
    "operators": [
      { "type": "class_level", "class": "Monk" },
      { "type": "integer", "value": 2 }
    ],
    "rounding": "down"
  }
}
```

---

## Requirements

Requirements restrict when mechanics/effects apply. All use `type` as discriminator.

### Common Requirements

#### Status Requirement

```json
{ "type": "status", "value": "raging" }
{ "type": "status", "value": ["blinded", "deafened"], "negate": true }
```

#### Level Requirement

```json
{ "type": "level", "minimum": 5 }
{ "type": "level", "minimum": 5, "maximum": 10 }
```

#### Equipment Requirement

```json
{ "type": "equipment", "slot": "armor", "occupied": false }
{ "type": "equipment", "slot": "main_hand", "grip": "two-handed" }
{ "type": "equipment", "function": "equipment.is_wearing_heavy_armor", "negate": true }
{ "type": "equipment", "item": "shield" }
```

#### Weapon Property Requirement

```json
{ "type": "weapon_property", "value": ["finesse", "light"] }
{ "type": "weapon_property", "value": ["ranged"] }
```

#### Creature Type Requirement

```json
{ "type": "creature_type", "value": ["Undead", "Fiend"] }
{ "type": "creature_type", "value": "Humanoid", "negate": true }
```

### Combat Requirements

#### Attack Requirement

```json
{ "type": "attack", "hand": "main_hand" }
{ "type": "attack", "hand": "off_hand" }
```

#### Attack Result Requirement

```json
{ "type": "attack_result", "value": "hit" }
{ "type": "attack_result", "value": "miss" }
```

#### Combat State Requirement

```json
{ "type": "combat_state", "value": "surprised", "negate": true }
{ "type": "combat_state", "value": "hidden" }
{ "type": "combat_state", "value": "flanking" }
```

#### Hit Points Requirement

```json
{ "type": "hit_points", "attribute": "current_hp", "comparison": "less_than", "value": 50 }
{ "type": "hit_points", "comparison": "at_least", "calculation": { ... } }
```

#### Distance Requirement

```json
{ "type": "distance", "value": 5, "unit": "feet", "to": "target", "comparison": "within" }
```

### Perception Requirements

```json
{
  "type": "perception",
  "observer": "character",
  "subject": "attacker",
  "senses": ["sight"]
}
```

```json
{
  "type": "perception",
  "observer": "character",
  "subject": "source",
  "senses": ["sight", "hearing"],
  "match": "any"
}
```

```json
{
  "type": "perception",
  "observer": "character",
  "subject": "target",
  "senses": ["sight"],
  "negate": true
}
```

### Other Requirements

#### Spell Level Requirement

```json
{ "type": "spell_level", "minimum": 1 }
{ "type": "spell_level", "maximum": 5 }
```

#### Resource Requirement

```json
{ "type": "resource", "resource": "ki", "comparison": "greater_than", "value": 0 }
```

#### Size Requirement

```json
{ "type": "size", "value": ["Small", "Medium", "Large"] }
```

#### Environment Requirement

```json
{ "type": "environment", "lighting": "dim_light" }
{ "type": "environment", "lighting": "darkness" }
```

#### Immunity Requirement

```json
{ "type": "immunity", "to": "frightened", "negate": true }
```

#### Effect Target Requirement

```json
{ "type": "effect_target", "value": "not_self" }
{ "type": "effect_target", "value": "ally" }
```

#### Inventory Item Requirement

```json
{ "type": "inventory_item", "name": "Holy Symbol" }
{ "type": "inventory_item", "name_contains": ["Component Pouch", "Arcane Focus"] }
```

#### Function Requirement

For complex checks that need code:

```json
{
  "type": "function",
  "function": "resources.check_pool_remaining",
  "context": "character",
  "params": { "resource": "hit_dice", "minimum": 1 }
}
```

---

## Triggers

Triggers define when reactive mechanics activate. They're used for reactions, passive "when X happens" abilities, and status effects.

### Trigger Events

| Event            | Description                   |
| ---------------- | ----------------------------- |
| `attack`         | When an attack is made        |
| `hit`            | When an attack hits           |
| `miss`           | When an attack misses         |
| `damage`         | When damage is received       |
| `damaged_by`     | When damage is dealt          |
| `cast_spell`     | When a spell is cast          |
| `saving_throw`   | When a save is made           |
| `ability_check`  | When an ability check is made |
| `start_turn`     | At the start of a turn        |
| `end_turn`       | At the end of a turn          |
| `enter_area`     | When entering an area         |
| `leave_area`     | When leaving an area          |
| `move`           | When movement occurs          |
| `status_applied` | When a status is applied      |
| `status_removed` | When a status is removed      |
| `roll`           | When any roll is made         |
| `long_rest`      | At the end of a long rest     |
| `short_rest`     | At the end of a short rest    |

### Trigger Timing

| Timing     | Description                  |
| ---------- | ---------------------------- |
| `before`   | Before the event resolves    |
| `after`    | After the event resolves     |
| `resolved` | When event is fully resolved |

```json
{
  "trigger": {
    "event": ["attack"],
    "timing": "before"
  }
}
```

### Source and Target Filters

#### Source Filter

```json
{
  "trigger": {
    "event": ["damaged_by"],
    "source": {
      "type": ["melee", "weapon"],
      "origin": "nonmagical"
    }
  }
}
```

Source fields:

- `type` — Source types: `creature`, `spell`, `weapon`, `environment`, `melee`, `ranged`
- `origin` — `magical` or `nonmagical`
- `range` — Distance constraint
- `perception` — Perception requirements
- `disposition` — `friendly`, `hostile`, `any`

#### Target Filter

```json
{
  "trigger": {
    "event": ["hit"],
    "target": {
      "type": "self"
    }
  }
}
```

```json
{
  "trigger": {
    "event": ["damaged_by"],
    "target": {
      "type": "ally",
      "range": { "value": 30, "unit": "feet" }
    }
  }
}
```

Target fields:

- `type` — Who: `self`, `ally`, `creature`, `affected_creature`
- `size` — Creature sizes
- `range` — Distance from character
- `exclude` — Exclude specific targets

### Complex Trigger Examples

#### Reaction to Being Hit (can see attacker)

```json
{
  "trigger": {
    "event": ["hit"],
    "target": { "type": "self" },
    "source": {
      "perception": {
        "observer": "character",
        "subject": "attacker",
        "senses": ["sight"]
      }
    }
  }
}
```

#### When Ally Takes Damage Within Range

```json
{
  "trigger": {
    "event": ["damaged_by"],
    "target": {
      "type": "ally",
      "range": { "value": 30, "unit": "feet" }
    }
  }
}
```

#### On Critical Hit with Melee Weapon

Use mechanic `"type": "critical_hit"` with a trigger scoped to melee weapon hits:

```json
{
  "trigger": {
    "event": ["hit"],
    "source": { "type": ["melee", "weapon"] }
  }
}
```

#### When Spell is Cast (for Counterspell)

```json
{
  "trigger": {
    "event": ["cast_spell"],
    "timing": "before",
    "source": {
      "perception": {
        "observer": "character",
        "subject": "caster",
        "senses": ["sight"]
      },
      "range": { "value": 60, "unit": "feet" }
    }
  }
}
```

#### Start of Turn While Status Active

```json
{
  "trigger": {
    "event": ["start_turn"],
    "target": { "type": "affected_creature" }
  }
}
```

#### When Status Applied/Removed

```json
{
  "trigger": {
    "event": ["status_applied"],
    "status": { "name": "stunned" }
  }
}
```

#### Damage Type Filter

```json
{
  "trigger": {
    "event": ["damaged_by"],
    "damage_type": ["fire", "radiant"]
  }
}
```

#### Spell Level Filter

```json
{
  "trigger": {
    "event": ["cast_spell"],
    "spell_level": 1
  }
}
```

#### Action Filter

```json
{
  "trigger": {
    "event": ["hit"],
    "action": "attack"
  }
}
```

#### Result Filter

```json
{
  "trigger": {
    "event": ["saving_throw"],
    "result": "failure"
  }
}
```

---

## Targeting

The Target schema defines who/what is affected.

### Target Object

```json
{
  "target": {
    "type": "creature",
    "count": 1,
    "disposition": "hostile"
  }
}
```

### Target Types

**Selection types** (choosing targets):

- `self` — The character
- `creature` — Single creature
- `creatures` — Multiple creatures
- `object` — An object
- `point` — A point in space
- `area` — An area

**Reference types** (contextual):

- `attacker` — The attacking creature
- `triggering_creature` — Creature that triggered the effect
- `affected_creature` — Currently affected creature
- `hit_creature` — Creature that was hit
- `same_target` — Previous target

### Target Fields

| Field          | Type        | Description                             |
| -------------- | ----------- | --------------------------------------- |
| `type`         | string      | Target type (see above)                 |
| `count`        | int         | Maximum targets                         |
| `disposition`  | string      | `friendly`, `hostile`, `any`, `willing` |
| `include_self` | boolean     | Include character in area effects       |
| `status_query` | StatusQuery | Find creatures with specific status     |

### Status Query Targeting

Find creatures affected by a specific ability:

```json
{
  "target": {
    "type": "creatures",
    "status_query": {
      "name": "charmed",
      "from_action": "Charm Animals and Plants",
      "from_source": "character"
    }
  }
}
```

---

## Scaling

Scaling defines how values change with level.

### Basic Scaling

On a mechanic:

```json
{
  "type": "passive",
  "scaling": {
    "damage": {
      "1": "1d6",
      "5": "2d6",
      "11": "3d6",
      "17": "4d6"
    }
  },
  "effects": [
    {
      "damage": { "type": ["radiant"] },
      "scaling_key": "damage"
    }
  ]
}
```

### Multiple Scaling Properties

```json
{
  "scaling": {
    "damage": { "1": "1d6", "5": "2d6" },
    "radius": { "1": 10, "18": 30 },
    "uses": { "1": 1, "6": 2, "14": 3 }
  }
}
```

### Scaling Reference

Reference scaling defined elsewhere:

```json
{
  "limit": { "ref": "uses" }
}
```

---

## Complex Patterns

### Maneuver Pattern

Resource cost + triggered effect:

```json
{
  "type": "action",
  "name": "Trip Attack",
  "cost": [{ "type": "resource", "resource": "superiority_dice", "amount": 1 }],
  "trigger": { "event": ["hit"] },
  "effects": [
    {
      "damage_bonus": {
        "calculation": {
          "operation": "add",
          "operators": [{ "type": "resource_die", "value": "superiority_dice" }]
        }
      }
    },
    {
      "saving_throw": {
        "ability": "Strength",
        "dc": {
          "base": 8,
          "add": ["proficiency_bonus", { "type": "ability_modifier", "ability": "Strength" }]
        }
      },
      "on_failure": {
        "forced_movement": { "type": "prone" }
      },
      "requirements": [{ "type": "size", "value": ["Large", "Medium", "Small", "Tiny"] }]
    }
  ]
}
```

### Channel Divinity Pattern

Shared resource, multiple options:

```json
[
  {
    "type": "resource",
    "id": "channel_divinity",
    "name": "Channel Divinity",
    "count": 1,
    "recharge": "short_rest",
    "scaling": { "count": { "6": 2, "18": 3 } }
  },
  {
    "type": "action",
    "name": "Turn Undead",
    "cost": [{ "type": "resource", "resource": "channel_divinity", "amount": 1 }],
    "effects": [
      {
        "target": {
          "type": "creatures",
          "disposition": "hostile"
        },
        "area": {
          "shape": "sphere",
          "radius": { "value": 30, "unit": "feet" },
          "origin": "self"
        },
        "target_requirements": [
          { "type": "creature_type", "value": "Undead" },
          {
            "type": "perception",
            "observer": "target",
            "subject": "character",
            "senses": ["sight", "hearing"],
            "match": "any"
          }
        ],
        "saving_throw": {
          "ability": "Wisdom",
          "dc": { "type": "spell_save_dc" }
        },
        "on_failure": {
          "apply_status": {
            "name": "turned",
            "source": "character",
            "duration": { "value": 1, "unit": "minutes" }
          }
        }
      }
    ]
  }
]
```

### Aura with Scaling Radius

```json
{
  "type": "passive",
  "name": "Aura of Protection",
  "effects": [
    {
      "aura": {
        "radius": { "value": 10, "unit": "feet" },
        "affects": {
          "type": "creatures",
          "disposition": "friendly",
          "include_self": true
        },
        "effect": {
          "roll_modifier": {
            "on": "saving_throw",
            "calculation": {
              "operation": "add",
              "operators": [{ "type": "ability_modifier", "ability": "Charisma" }]
            },
            "minimum": 1
          }
        }
      }
    }
  ],
  "requirements": [{ "type": "status", "value": "incapacitated", "negate": true }],
  "scaling": {
    "radius": { "18": 30 }
  }
}
```

### Rage with Multiple Effects

```json
{
  "type": "bonus_action",
  "name": "Rage",
  "cost": [{ "type": "resource", "resource": "rage", "amount": 1 }],
  "duration": { "value": 1, "unit": "minutes" },
  "concentration": false,
  "requirements": [{ "type": "equipment", "function": "equipment.is_wearing_heavy_armor", "negate": true }],
  "effects": [
    {
      "apply_status": {
        "name": "raging",
        "source": "character"
      }
    },
    {
      "advantage": {
        "on": "ability_check",
        "ability": ["Strength"]
      }
    },
    {
      "advantage": {
        "on": "saving_throw",
        "ability": ["Strength"]
      }
    },
    {
      "damage_bonus": {
        "calculation": {
          "operation": "add",
          "operators": [{ "type": "scaling", "value": "rage_damage" }]
        }
      },
      "requirements": [
        { "type": "weapon_property", "value": ["melee"] },
        { "type": "attribute", "value": "attack.uses_strength", "equals": true }
      ]
    },
    {
      "damage_response": {
        "response": "resistance",
        "to": ["bludgeoning", "piercing", "slashing"]
      }
    }
  ],
  "scaling": {
    "rage_damage": { "1": 2, "9": 3, "16": 4 }
  }
}
```

### Nested Save Effects

```json
{
  "effects": [
    {
      "saving_throw": {
        "ability": "Constitution",
        "dc": { "type": "spell_save_dc" }
      },
      "on_failure": {
        "apply_status": {
          "name": "poisoned",
          "duration": { "value": 1, "unit": "minutes" }
        }
      },
      "on_success": {
        "damage": {
          "dice": "2d6",
          "type": ["poison"],
          "half_on_save": true
        }
      }
    }
  ]
}
```

### Conditional Feature Enhancement

```json
{
  "name": "Brutal Critical",
  "level": 9,
  "class": "Barbarian",
  "mechanics": [
    {
      "type": "critical_hit",
      "trigger": {
        "event": ["hit"],
        "source": { "type": ["melee", "weapon"] }
      },
      "effects": [
        {
          "roll_modifier": {
            "operation": "add",
            "value": "weapon_die"
          }
        }
      ],
      "scaling": {
        "extra_dice": { "13": 2, "17": 3 }
      }
    }
  ]
}
```

---

## Version History

- **v2.0** (2026) - Schema separation and strict validation
  - Data repository split from application (campaigner-data)
  - Full JSON Schema validation with strict mode
  - Discriminated unions for all mechanic and requirement types
  - Typed Calculation operands replace string-based formulas
  - AttributeModification model for character attribute changes
  - StatusEffect model for ongoing status effects
  - Grant model for action economy modifications
  - Query model for data-driven attribute population
  - Complete model documentation with examples

- **v1.4** (2026) - Unified perception schema
  - **New explicit perception format** with `observer`, `subject`, `senses`, `match`, `negate` fields
  - **Removed all legacy perception patterns**:
    - `"value": "can_see"` / `"value": "can_hear"` → explicit `observer`/`subject`/`senses`
    - `"type": "visibility"` → `"type": "perception"`
    - `"type": "condition", "value": "can_see_attacker"` → `"type": "perception"`
    - `"can_see_or_hear_character"` → explicit with `"match": "any"`
    - `"negate": true` for negation → `"negate": true`
  - **New location visibility schema** for placement/destination:
    - `"visibility": "line_of_sight"` for movement destinations
    - `"space": "unoccupied"` for placement constraints
  - Added `illusion` as valid entity reference
  - TriggerSource now accepts full Perception object
  - All data files migrated: class_features, domains, maneuvers, fighting_styles

- **v1.3** (2026) - Unified target schema
  - New structured `target` object with `type`, `count`, `disposition`, `include_self`
  - Replaced string-based targets (`friendly_creatures`, `hostile_creatures`, `allies`) with structured objects
  - Added `target_requirements` array for filtering (perception, creature_type, size, status, immunity, etc.)
  - New `against` schema for specifying advantage/disadvantage targets
  - **Removed `target_type` completely** - all usages migrated to `target` schema:
    - Class features: `target_type.include/exclude` → `target_requirements` with `creature_type`
    - Commands: `target_type.category` → `target.type`
    - Domains: `target_type.disposition/include/exclude` → `target` + `target_requirements`
  - Updated all aura and area effect examples

- **v1.2** (2026) - Targeting and save standardization
  - ~~Unified `target_type` object format with `disposition`, `include`, `exclude`~~ **(removed in v1.3)**
  - ~~Commands use `target_type.category` for target categories~~ **(removed in v1.3 - now uses `target.type`)**
  - Saving throw outcomes moved inside `saving_throw` object (`on_success`, `on_failure`)
  - Maneuver DC uses `dc` object with `base` and `add` fields
  - Feature enhancements (`enhances` field for adding to features without replacing)
  - Save outcome effects via passive triggers for conditional outcome replacement
  - Nature and Tempest domain features

- **v1.1** (2025) - Domain and spellcasting support
  - Triggers system for spells and attacks (`action: "cast"`, `action: "attack"`)
  - Feature extensions (`extends` field for feature replacement)
  - Area of effect targeting (`target: "area"` with shape configuration)
  - Player choice targeting (`player_choice: true`)
  - Auras with layers for persistent area effects
  - Granted spells (`type: "granted_spells"`)
  - Toggle actions for sustained effects
  - Dynamic uses with minimum values
  - Life and Light domain features as reference implementations

- **v1.0** (2025) - Initial unified schema
  - All Rogue class features
  - Thief subclass features
  - Core effect types: attribute, damage, advantage, status, action
  - Requirements system
  - Scaling mechanics
  - Choice mechanics
