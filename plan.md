# Refactor Plan: Simplify to String Literals + Hardcoded Logic

## Overview

Radically simplify by storing only **string literal names** on Character. Drop all Effect subclasses, Ability class, and Card class. Effect values are **hardcoded** in `EffectTotal` computation and action logic. Each Action declares what it disposes as immutable tuples, and disposal logic is written **once** in the base Action class.

## Current Architecture

```
Character
  ├── abilities: list[Ability]           # innate abilities (full objects)
  ├── effects: list[EffectUnion]         # ALL applied effects (full objects, from abilities + cards)
  ├── effect: EffectTotal (computed)     # aggregated by iterating effect objects
  └── cards: list[str]                   # card names
```

- Abilities/cards → deep-copy individual Effect objects → append to `character.effects`
- Each Effect object carries `dispose_actions`, `apply_to`, `source`, and value fields
- Disposal: filter `character.effects` by `effect.dispose_actions` matching action name

## Target Architecture

```
Character
  ├── abilities: list[AbilityName]       # innate abilities (string names)
  ├── active_abilities: list[AbilityName]# applied abilities (string names)
  ├── cards: list[CardName]              # applied persistent cards (string names)
  ├── effects: list[EffectName]          # only SkipTurnEffect (string name)
  └── effect: EffectTotal (computed)     # hardcoded per ability/card name
```

- When ability is used → append ability **name string** to `character.active_abilities`
- Exception: FREEZE → append `"skip_turn"` to target `character.effects`
- When persistent card is selected → append card **name string** to `character.cards`
- Instant cards (golden_apple, magic_ball) → applied immediately, not stored
- No more deep-copying of Effect objects
- Disposal: each Action declares `dispose_abilities`, `dispose_cards`, `dispose_effects` as tuples; base Action class handles removal

## Detailed Changes

### 1. `effects.py` — Gut to constants only

Remove all 9 Effect subclasses, `EffectUnion`, base `Effect` class, `model_validator`, `dispose_actions`, `source`, `apply_to`. Keep only:

```python
# server/gameplay/effects.py

########################################################
# Effect name constants
########################################################
EFFECT_SKIP_TURN = "skip_turn"
EFFECT_NAMES = [EFFECT_SKIP_TURN]
EffectName = Literal[*EFFECT_NAMES]
```

### 2. `abilities.py` — Constants + minimal metadata

Remove `Ability` class and `ABILITIES_MAP` with Effect objects. Replace with:

```python
# server/gameplay/abilities.py

########################################################
# Ability names
########################################################
ABILITY_BATTLE_HOWL = "battle_howl"
ABILITY_BOUNCING_ARROW = "bouncing_arrow"
ABILITY_FREEZE = "freeze"
ABILITIES_NAMES: list[str] = [ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW, ABILITY_FREEZE]
AbilityName = Literal[*ABILITIES_NAMES]

########################################################
# Ability metadata
########################################################
# Abilities that apply effects to self when selected
SELF_TARGETED_ABILITIES = (ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW)

# Abilities that require opponent selection stage
OPPONENT_TARGETED_ABILITIES = (ABILITY_FREEZE,)
```

### 3. `cards.py` — Constants + minimal metadata

Remove `Card` class and `CARDS_MAP` with Effect objects. Replace with:

```python
# server/gameplay/cards.py

########################################################
# Card names
########################################################
CARD_METAL_ARMOR = "metal_armor"
CARD_SACRED_SWORD = "sacred_sord"
CARD_GOLDEN_APPLE = "golden_apple"
CARD_MAGIC_BALL = "magic_ball"
CARD_TALISMAN = "talisman"
CARD_NAMES: list[str] = [CARD_METAL_ARMOR, CARD_SACRED_SWORD, CARD_GOLDEN_APPLE, CARD_MAGIC_BALL, CARD_TALISMAN]
CardName = Literal[*CARD_NAMES]

########################################################
# Card metadata
########################################################
# Cards that cannot be used by certain characters
CARD_RESTRICTED_CHARACTERS: dict[str, tuple[str, ...]] = {
    CARD_SACRED_SWORD: ("archer",),
}

# Instant cards — applied immediately, not stored on character
INSTANT_CARDS = (CARD_GOLDEN_APPLE, CARD_MAGIC_BALL)
```

### 4. `Character` model — `server/gameplay/gameplay.py`

```python
class Character(StrictModel):
    level: int
    health: int
    max_health: int
    dice: int
    attack: int
    is_alive: bool = True
    abilities: list[AbilityName] = Field(default_factory=list)         # innate (string names)
    active_abilities: list[AbilityName] = Field(default_factory=list)  # applied (string names)
    cards: list[CardName] = Field(default_factory=list)                # persistent cards (string names)
    effects: list[str] = Field(default_factory=list)                   # only SkipTurnEffect

    @computed_field
    @property
    def effect(self) -> EffectTotal:
        total = EffectTotal()
        # Abilities — hardcoded values
        if ABILITY_BATTLE_HOWL in self.active_abilities:
            total.attack_bonus += 2
        if ABILITY_BOUNCING_ARROW in self.active_abilities:
            total.reroll_dice_available = True
        # Cards — hardcoded values
        if CARD_METAL_ARMOR in self.cards:
            total.defense_bonus += 2
        if CARD_SACRED_SWORD in self.cards:
            total.attack_bonus += 3
        if CARD_TALISMAN in self.cards:
            total.has_talisman = True
        # Effects
        if EFFECT_SKIP_TURN in self.effects:
            total.skip_next_turn = True
        return total

    @computed_field
    @property
    def is_available(self) -> bool:
        return self.is_alive and not self.effect.skip_next_turn
```

Update `CHARACTER_STATS_BY_LEVEL` — abilities as string names:

```python
CHARACTER_STATS_BY_LEVEL = {
    1: {
        "knight": {
            ...,
            "abilities": [ABILITY_BATTLE_HOWL],      # was: [ABILITIES_MAP[...]]
        },
        "archer": {
            ...,
            "abilities": [ABILITY_BOUNCING_ARROW],
        },
        "mage": {
            ...,
            "abilities": [ABILITY_FREEZE],
        },
    },
    # ... same for levels 2-4
}
```

### 5. `GamePlay` model — `server/gameplay/gameplay.py`

Simplify `ability` field from Ability object to string name:

```python
class GamePlay(StrictModel):
    # ...
    ability: Optional[AbilityName] = None     # was: Optional[Ability]
    # ...
    stage_meta: Optional[CharacterSelectMeta | CardDrawMeta | AbilitySelectMeta | Opponent2] = None
    # (remove Ability from stage_meta union — it was unused)
```

### 6. Base `Action` class — `server/gameplay/actions/action.py`

Add disposal declaration and generic disposal method:

```python
class Action(ABC):
    # Each action declares what it disposes (override in subclasses, tuples for immutability)
    dispose_abilities: tuple[AbilityName, ...] = ()
    dispose_cards: tuple[CardName, ...] = ()
    dispose_effects: tuple[str, ...] = ()

    def dispose_character(self, character: Character) -> None:
        """Generic disposal — written once, used by all actions."""
        if self.dispose_abilities:
            character.active_abilities = [
                a for a in character.active_abilities
                if a not in self.dispose_abilities
            ]
        if self.dispose_cards:
            character.cards = [
                c for c in character.cards
                if c not in self.dispose_cards
            ]
        if self.dispose_effects:
            character.effects = [
                e for e in character.effects
                if e not in self.dispose_effects
            ]
```

### 7. Action dispose declarations

Each action specifies what it disposes:

| Action | dispose_abilities | dispose_cards | dispose_effects |
| ------ | ----------------- | ------------- | --------------- |
| `BattleEndAction` | `(BATTLE_HOWL, BOUNCING_ARROW)` | `()` | `()` |
| `RerollEffectAction` | `(BOUNCING_ARROW,)` | `()` | `()` |
| `CharacterSelectAction` | `()` | `()` | `(EFFECT_SKIP_TURN,)` |
| `SkipTurnAction` | `()` | `()` | `(EFFECT_SKIP_TURN,)` |

Note: Persistent cards (metal_armor, sacred_sword, talisman) have empty dispose lists everywhere — they're never disposed.

### 8. `AbilitySelectAction` — `server/gameplay/actions/stage_ability_selection.py`

Hardcoded routing — no Ability class lookups:

```python
def _run(self, ability: AbilityName) -> GamePlay:
    # ... validation unchanged ...

    # Store ability name in GamePlay
    self.game.ability = ability

    # Apply self-targeted abilities
    if ability in SELF_TARGETED_ABILITIES:
        character.active_abilities.append(ability)

    # Route to correct stage
    if ability in OPPONENT_TARGETED_ABILITIES:
        self.game.stage = STAGE_ABILITY_OPPONENT_SELECTION
    else:
        self.game.stage = STAGE_OPPONENT_SELECTION
```

### 9. `AbilityOpponentSelectAction` — `server/gameplay/actions/stage_ability_opponent_selection.py`

Hardcoded — FREEZE adds skip_turn to target:

```python
def _run(self) -> GamePlay:
    # ... validation unchanged ...

    # Apply ability effects to target character
    if self.game.ability == ABILITY_FREEZE:
        target_character.effects.append(EFFECT_SKIP_TURN)
```

### 10. `CardSelectAction` — `server/gameplay/actions/stage_card_draw.py`

Hardcoded instant card effects, persistent cards stored as name:

```python
def _run(self) -> GamePlay:
    # ... validation unchanged ...

    is_restricted = drawn_card_name in CARD_RESTRICTED_CHARACTERS and \
        character_type in CARD_RESTRICTED_CHARACTERS[drawn_card_name]

    if not is_restricted:
        if drawn_card_name == CARD_GOLDEN_APPLE:
            character.health = min(character.max_health, character.health + 1)
        elif drawn_card_name == CARD_MAGIC_BALL:
            # ... level up logic unchanged ...
            pass
        else:
            # Persistent/equipment card
            character.cards.append(drawn_card_name)

    # ... transition unchanged ...
```

### 11. `OpponentSelectAction` — `server/gameplay/actions/stage_opponent_selection.py`

No card/ability effects currently apply to battle_opponent, so this simplifies significantly. The BATTLE_HOWL applies to self (already in active_abilities). No current ability or card has `apply_to=BATTLE_OPPONENT`, so the opponent-effect application logic can be removed or kept as a no-op placeholder:

```python
def _run(self) -> GamePlay:
    # ... validation unchanged ...

    # Currently no abilities/cards apply effects to battle opponent
    # (BATTLE_HOWL applies to self, FREEZE targets selected_opponent)
    # Future: add hardcoded opponent-effect logic here if needed
```

### 12. `BattleEndAction` — `server/gameplay/actions/battle_end.py`

Uses generic disposal:

```python
class BattleEndAction(Action):
    dispose_abilities = (ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW)

    def _run(self) -> GamePlay:
        # ... battle logic unchanged ...

        # Dispose — one line each
        self.dispose_character(active_character)
        self.dispose_character(opponent_character)

        rotate_to_next_player(self.game)
        return self.game
```

### 13. `RerollEffectAction` — `server/gameplay/actions/stage_battle.py`

```python
class RerollEffectAction(Action):
    dispose_abilities = (ABILITY_BOUNCING_ARROW,)

    def _run(self) -> GamePlay:
        # ... validation unchanged ...

        # Dispose reroll ability
        self.dispose_character(self.active_character)

        return validate_and_reset_reroll(self.game, self.user)
```

### 14. `CharacterSelectAction` / `SkipTurnAction` — `server/gameplay/actions/stage_character_select.py`

```python
class CharacterSelectAction(Action):
    dispose_effects = (EFFECT_SKIP_TURN,)

    def _run(self, character: str) -> GamePlay:
        # ... validation unchanged ...

        # Dispose skip_turn from all active player's characters
        for char in player.characters.values():
            self.dispose_character(char)

        # ... transition unchanged ...

class SkipTurnAction(Action):
    dispose_effects = (EFFECT_SKIP_TURN,)

    def _run(self) -> GamePlay:
        # ... validation unchanged ...

        # Dispose skip_turn from all active player's characters
        for char in player.characters.values():
            self.dispose_character(char)

        rotate_to_next_player(self.game)
        return self.game
```

### 15. Frontend — `src/components/CharacterCard.jsx`

```javascript
// Card presence — use character.cards (string names, same field name as before)
const hasArmor = character.cards?.includes("metal_armor") || false;
const hasSword = character.cards?.includes("sacred_sord") || false;
const hasTalisman = character.cards?.includes("talisman") || false;

// SkipTurn — check effects (string names)
const hasSkipTurn = character.effects?.includes("skip_turn") || false;

// Effect names for data attribute — combine all sources
const effectNames = [
    ...(character.active_abilities || []),
    ...(character.cards || []),
    ...(character.effects || []),
].join(",");

// EffectTotal — unchanged (computed server-side)
const attackBonus = character.effect?.attack_bonus || 0;
const hasReroll = character.effect?.reroll_dice_available || false;
```

### 16. Presets — `server/gameplay/presets.py`

Update all presets to use string names:

```python
# Before:
characters[CHARACTER_KNIGHT].effects = [
    AttackBonusEffect(source=ABILITY_BATTLE_HOWL, attack_bonus=2),
]

# After:
characters[CHARACTER_KNIGHT].active_abilities = [ABILITY_BATTLE_HOWL]
```

```python
# Before:
characters[CHARACTER_MAGE].effects = [SkipTurnEffect(source=ABILITY_FREEZE)]

# After:
characters[CHARACTER_MAGE].effects = [EFFECT_SKIP_TURN]
```

```python
# Before:
character.cards = ["metal_armor"]
character.effects = [DefenseBonusEffect(source=CARD_METAL_ARMOR, defense_bonus=2)]

# After:
character.cards = [CARD_METAL_ARMOR]
```

### 17. Tests

All tests that set/assert `character.effects` with Effect objects → use string names:

| Test File | Changes |
| --------- | ------- |
| `test_stage_battle_end.py` | `character.active_abilities = [ABILITY_BATTLE_HOWL]` instead of `character.effects = [AttackBonusEffect(...)]`. Assert `len(active_abilities) == 0` after disposal. Keep SkipTurnEffect as `effects = [EFFECT_SKIP_TURN]` |
| `test_stage_battle_dice_roll.py` | Same pattern — string names for abilities, assert EffectTotal values via `character.effect` |
| `test_stage_ability_selection.py` | Assert `ABILITY_BATTLE_HOWL in character.active_abilities` instead of `isinstance(effects[0], RerollDiceEffect)` |
| `test_stage_character_select.py` | `effects = [EFFECT_SKIP_TURN]` instead of `SkipTurnEffect(...)` |
| `test_stage_card_draw.py` | Assert `CARD_METAL_ARMOR in character.cards` instead of `isinstance(effects[0], DefenseBonusEffect)` |
| `test_stage_opponent_selection.py` | String names for card/ability assertions |
| `test_stage_ability_opponent_selection.py` | Assert `EFFECT_SKIP_TURN in target.effects` |
| `test_effect_source_validation.py` | **Delete entirely** — source validation no longer exists |

## What Gets Deleted

- **All 9 Effect subclasses** (`AttackBonusEffect`, `DefenseBonusEffect`, `RerollDiceEffect`, `SkipTurnEffect`, `HealEffect`, `LevelUpEffect`, `DrawCardEffect`, `AttackNegBonusEffect`, `TalismanEffect`)
- **Base `Effect` class** with `source`, `dispose_actions`, `apply_to`, `model_validator`
- **`EffectUnion` discriminated union**
- **`Ability` class** + `ABILITIES_MAP` (replaced by constants + tuples)
- **`Card` class** + `CARDS_MAP` (replaced by constants + tuples)
- **`EFFECTS_SOURCE_ABILITY_MAP`** + **`EFFECTS_SOURCE_CARD_MAP`** (source validation gone)
- **`test_effect_source_validation.py`** (entire file)
- **Deep copying of Effect objects** — eliminated entirely
- **`effects.py`** shrinks from ~190 lines to ~10 lines (just constants)
- **`abilities.py`** shrinks from ~80 lines to ~20 lines (constants + metadata tuples)
- **`cards.py`** shrinks from ~95 lines to ~25 lines (constants + metadata dict + tuple)

## What Stays Unchanged

- **`EffectTotal` class** — fields unchanged (just computed differently)
- **`is_available` computed property** — unchanged
- **Battle score calculation** — unchanged (reads from `character.effect`)
- **Instant card effects** (heal, level up) — still applied immediately (now hardcoded per card name)

## Key Files to Modify

**Backend:**
1. `server/gameplay/effects.py` — gut to constants only
2. `server/gameplay/abilities.py` — gut to constants + metadata tuples
3. `server/gameplay/cards.py` — gut to constants + metadata dict/tuple
4. `server/gameplay/gameplay.py` — Character model (string lists), hardcoded EffectTotal, CHARACTER_STATS_BY_LEVEL, GamePlay.ability type
5. `server/gameplay/actions/action.py` — add dispose tuples + `dispose_character()` method
6. `server/gameplay/actions/stage_ability_selection.py` — hardcoded routing
7. `server/gameplay/actions/stage_ability_opponent_selection.py` — hardcoded FREEZE logic
8. `server/gameplay/actions/stage_card_draw.py` — hardcoded instant cards
9. `server/gameplay/actions/stage_opponent_selection.py` — simplify (no current opponent effects)
10. `server/gameplay/actions/battle_end.py` — use `dispose_character()`
11. `server/gameplay/actions/stage_battle.py` — use `dispose_character()`
12. `server/gameplay/actions/stage_character_select.py` — use `dispose_character()`
13. `server/gameplay/presets.py` — string names everywhere
14. `server/gameplay/test_effect_source_validation.py` — delete

**Frontend:**
15. `src/components/CharacterCard.jsx` — `cards`, string-based checks
