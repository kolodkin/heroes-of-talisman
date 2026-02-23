# Refactor Plan: Simplify to String Literals on Character

## Overview

Radically simplify by storing only **string literal names** on Character instead of full Effect/Ability/Card objects. Effect values are looked up from `ABILITIES_MAP` / `CARDS_MAP` at computation time. Each Action declares what it disposes as string literal lists, and disposal logic is written **once** in the base Action class.

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
  ├── active_cards: list[CardName]       # applied persistent cards (string names)
  ├── effects: list[EffectName]          # only SkipTurnEffect (string name)
  ├── effect: EffectTotal (computed)     # aggregated by looking up ABILITIES_MAP/CARDS_MAP
  └── card_names: list[str] (computed)   # derived from active_cards for frontend
```

- When ability is used → append ability **name string** to `character.active_abilities`
- Exception: FREEZE → append `"skip_turn"` to target `character.effects`
- When persistent card is selected → append card **name string** to `character.active_cards`
- Instant cards (golden_apple, magic_ball) → applied immediately, not stored
- No more deep-copying of Effect objects
- Disposal: each Action declares `dispose_abilities`, `dispose_cards`, `dispose_effects` as string lists; base Action class handles removal

## Detailed Changes

### 1. `Character` model — `server/gameplay/gameplay.py`

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
    active_cards: list[CardName] = Field(default_factory=list)         # persistent cards (string names)
    effects: list[str] = Field(default_factory=list)                   # only SkipTurnEffect

    @computed_field
    @property
    def effect(self) -> EffectTotal:
        total = EffectTotal()
        # From active abilities — lookup from ABILITIES_MAP
        for ability_name in self.active_abilities:
            ability = ABILITIES_MAP[ability_name]
            for eff in ability.effects:
                if isinstance(eff, AttackBonusEffect):
                    total.attack_bonus += eff.attack_bonus
                elif isinstance(eff, AttackNegBonusEffect):
                    total.attack_neg_bonus += eff.attack_neg_bonus
                elif isinstance(eff, RerollDiceEffect):
                    total.reroll_dice_available = True
                elif isinstance(eff, DrawCardEffect):
                    total.draw_card_count += eff.draw_count
        # From active cards — lookup from CARDS_MAP
        for card_name in self.active_cards:
            card = CARDS_MAP[card_name]
            for eff in card.effects:
                if isinstance(eff, DefenseBonusEffect):
                    total.defense_bonus += eff.defense_bonus
                elif isinstance(eff, AttackBonusEffect):
                    total.attack_bonus += eff.attack_bonus
                elif isinstance(eff, TalismanEffect):
                    total.has_talisman = True
        # From effects (only SkipTurnEffect)
        if EFFECT_SKIP_TURN in self.effects:
            total.skip_next_turn = True
        return total

    @computed_field
    @property
    def is_available(self) -> bool:
        return self.is_alive and not self.effect.skip_next_turn

    @computed_field
    @property
    def card_names(self) -> list[str]:
        """Card names for frontend display (replaces old cards field)"""
        return list(self.active_cards)
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

### 2. `GamePlay` model — `server/gameplay/gameplay.py`

Simplify `ability` field from Ability object to string name:

```python
class GamePlay(StrictModel):
    # ...
    ability: Optional[AbilityName] = None     # was: Optional[Ability]
    # ...
    stage_meta: Optional[CharacterSelectMeta | CardDrawMeta | AbilitySelectMeta | Opponent2] = None
    # (remove Ability from stage_meta union — it was unused)
```

### 3. Base `Action` class — `server/gameplay/actions/action.py`

Add disposal declaration and generic disposal method:

```python
class Action(ABC):
    # Each action declares what it disposes (override in subclasses)
    dispose_abilities: list[AbilityName] = []
    dispose_cards: list[CardName] = []
    dispose_effects: list[str] = []

    def dispose_character(self, character: Character) -> None:
        """Generic disposal — written once, used by all actions."""
        if self.dispose_abilities:
            character.active_abilities = [
                a for a in character.active_abilities
                if a not in self.dispose_abilities
            ]
        if self.dispose_cards:
            character.active_cards = [
                c for c in character.active_cards
                if c not in self.dispose_cards
            ]
        if self.dispose_effects:
            character.effects = [
                e for e in character.effects
                if e not in self.dispose_effects
            ]
```

### 4. Action dispose declarations

Each action specifies what it disposes:

| Action | dispose_abilities | dispose_cards | dispose_effects |
| ------ | ----------------- | ------------- | --------------- |
| `BattleEndAction` | `[BATTLE_HOWL, BOUNCING_ARROW]` | `[]` | `[]` |
| `RerollEffectAction` | `[BOUNCING_ARROW]` | `[]` | `[]` |
| `CharacterSelectAction` | `[]` | `[]` | `[EFFECT_SKIP_TURN]` |
| `SkipTurnAction` | `[]` | `[]` | `[EFFECT_SKIP_TURN]` |

Note: Persistent cards (metal_armor, sacred_sword, talisman) have empty dispose lists everywhere — they're never disposed.

### 5. `AbilitySelectAction` — `server/gameplay/actions/stage_ability_selection.py`

Massively simplified — just append ability name string:

```python
def _run(self, ability: AbilityName) -> GamePlay:
    # ... validation unchanged ...

    # Store ability name in GamePlay (was: ability_obj)
    self.game.ability = ability

    # Apply self-targeted abilities to active character
    ability_obj = ABILITIES_MAP[ability]
    has_self_effects = any(e.apply_to == APPLY_TO_SELF for e in ability_obj.effects)
    if has_self_effects:
        character.active_abilities.append(ability)

    # ... transition logic unchanged ...
    if ability_obj.requires_opponent_selection:
        self.game.stage = STAGE_ABILITY_OPPONENT_SELECTION
    else:
        self.game.stage = STAGE_OPPONENT_SELECTION
```

### 6. `AbilityOpponentSelectAction` — `server/gameplay/actions/stage_ability_opponent_selection.py`

SkipTurnEffect exception — append effect name string to target:

```python
def _run(self) -> GamePlay:
    # ... validation unchanged ...

    # Apply ability effects to target character
    ability_obj = ABILITIES_MAP[self.game.ability]
    for effect in ability_obj.effects:
        if isinstance(effect, SkipTurnEffect):
            target_character.effects.append(EFFECT_SKIP_TURN)
        # Future non-skip-turn selected_opponent effects:
        # would append to target_character.active_abilities
```

### 7. `CardSelectAction` — `server/gameplay/actions/stage_card_draw.py`

Simplified — instant effects applied immediately, persistent cards stored as name:

```python
def _run(self) -> GamePlay:
    # ... validation unchanged ...

    if not is_restricted:
        card_obj = CARDS_MAP[drawn_card_name]
        is_instant = False

        for effect in card_obj.effects:
            if isinstance(effect, HealEffect):
                character.health = min(character.max_health, character.health + effect.heal_amount)
                is_instant = True
            elif isinstance(effect, LevelUpEffect):
                # ... level up logic unchanged ...
                is_instant = True

        # Store persistent/equipment cards
        if not is_instant:
            character.active_cards.append(drawn_card_name)

    # ... transition unchanged ...
```

### 8. `OpponentSelectAction` — `server/gameplay/actions/stage_opponent_selection.py`

Card/ability effects applied to opponent via name strings:

```python
def _run(self) -> GamePlay:
    # ... validation unchanged ...

    # Apply card's battle_opponent effects
    if self.game.card:
        card_obj = CARDS_MAP.get(self.game.card)
        if card_obj:
            has_opponent_effects = any(e.apply_to == APPLY_TO_BATTLE_OPPONENT for e in card_obj.effects)
            if has_opponent_effects:
                opponent_character.active_cards.append(self.game.card)

    # Apply ability's battle_opponent effects
    if self.game.ability:
        ability_obj = ABILITIES_MAP[self.game.ability]
        has_opponent_effects = any(e.apply_to == APPLY_TO_BATTLE_OPPONENT for e in ability_obj.effects)
        if has_opponent_effects:
            opponent_character.active_abilities.append(self.game.ability)
```

### 9. `BattleEndAction` — `server/gameplay/actions/battle_end.py`

Uses generic disposal:

```python
class BattleEndAction(Action):
    dispose_abilities = [ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW]

    def _run(self) -> GamePlay:
        # ... battle logic unchanged ...

        # Dispose — one line each
        self.dispose_character(active_character)
        self.dispose_character(opponent_character)

        rotate_to_next_player(self.game)
        return self.game
```

### 10. `RerollEffectAction` — `server/gameplay/actions/stage_battle.py`

```python
class RerollEffectAction(Action):
    dispose_abilities = [ABILITY_BOUNCING_ARROW]

    def _run(self) -> GamePlay:
        # ... validation unchanged ...

        # Dispose reroll ability
        self.dispose_character(self.active_character)

        return validate_and_reset_reroll(self.game, self.user)
```

### 11. `CharacterSelectAction` / `SkipTurnAction` — `server/gameplay/actions/stage_character_select.py`

```python
class CharacterSelectAction(Action):
    dispose_effects = [EFFECT_SKIP_TURN]

    def _run(self, character: str) -> GamePlay:
        # ... validation unchanged ...

        # Dispose skip_turn from all active player's characters
        for char in player.characters.values():
            self.dispose_character(char)

        # ... transition unchanged ...

class SkipTurnAction(Action):
    dispose_effects = [EFFECT_SKIP_TURN]

    def _run(self) -> GamePlay:
        # ... validation unchanged ...

        # Dispose skip_turn from all active player's characters
        for char in player.characters.values():
            self.dispose_character(char)

        rotate_to_next_player(self.game)
        return self.game
```

### 12. `Ability` / `Card` models — `server/gameplay/abilities.py`, `server/gameplay/cards.py`

**Ability and Card class definitions stay as-is** — they're still used as lookup templates in `ABILITIES_MAP` / `CARDS_MAP`. They just no longer get stored on Character.

The `Effect` classes also stay as definitions inside ABILITIES_MAP/CARDS_MAP — they're used for value lookup (attack_bonus=2, defense_bonus=2, etc.) and for EffectTotal computation.

Remove `dispose_actions` and `source` from Effect classes — no longer needed since disposal is handled by Action declarations, and effects aren't stored as objects on Character.

### 13. Frontend — `src/components/CharacterCard.jsx`

```javascript
// Card presence — use active_cards (already string names)
const hasArmor = character.active_cards?.includes("metal_armor") || false;
const hasSword = character.active_cards?.includes("sacred_sord") || false;
const hasTalisman = character.active_cards?.includes("talisman") || false;

// SkipTurn — check effects (string names)
const hasSkipTurn = character.effects?.includes("skip_turn") || false;

// Effect names for data attribute — combine all sources
const effectNames = [
    ...(character.active_abilities || []),
    ...(character.active_cards || []),
    ...(character.effects || []),
].join(",");

// EffectTotal — unchanged (computed server-side)
const attackBonus = character.effect?.attack_bonus || 0;
const hasReroll = character.effect?.reroll_dice_available || false;
```

### 14. Presets — `server/gameplay/presets.py`

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
character.active_cards = [CARD_METAL_ARMOR]
```

### 15. Tests

All tests that set/assert `character.effects` with Effect objects → use string names:

| Test File | Changes |
| --------- | ------- |
| `test_stage_battle_end.py` | `character.active_abilities = [ABILITY_BATTLE_HOWL]` instead of `character.effects = [AttackBonusEffect(...)]`. Assert `len(active_abilities) == 0` after disposal. Keep SkipTurnEffect as `effects = [EFFECT_SKIP_TURN]` |
| `test_stage_battle_dice_roll.py` | Same pattern — string names for abilities, assert EffectTotal values via `character.effect` |
| `test_stage_ability_selection.py` | Assert `ABILITY_BATTLE_HOWL in character.active_abilities` instead of `isinstance(effects[0], RerollDiceEffect)` |
| `test_stage_character_select.py` | `effects = [EFFECT_SKIP_TURN]` instead of `SkipTurnEffect(...)` |
| `test_stage_card_draw.py` | Assert `CARD_METAL_ARMOR in character.active_cards` instead of `isinstance(effects[0], DefenseBonusEffect)` |
| `test_stage_opponent_selection.py` | String names for card/ability assertions |
| `test_stage_ability_opponent_selection.py` | Assert `EFFECT_SKIP_TURN in target.effects` |

## What Gets Removed / Simplified

- **`Effect.dispose_actions`** — removed (disposal logic moved to Action declarations)
- **`Effect.source`** — removed (no longer stored on Character, source is implicit from ABILITIES_MAP/CARDS_MAP)
- **`Effect.apply_to`** — stays on Effect class (still needed for application logic in actions)
- **`character.cards: list[str]`** — replaced by `active_cards`
- **Deep copying of Effect objects** — eliminated entirely
- **`EffectUnion` discriminated union on Character** — no longer needed for Character storage
- **`Effect.model_validator` for source validation** — removed (source field removed)

## What Stays Unchanged

- **`Ability` class** — stays as lookup definition in `ABILITIES_MAP`
- **`Card` class** — stays as lookup definition in `CARDS_MAP`
- **`Effect` subclasses** — stay as definitions inside ability/card effects lists (for value lookup)
- **`EffectTotal` class** — fields unchanged
- **`is_available` computed property** — unchanged
- **Battle score calculation** — unchanged (reads from `character.effect`)
- **Instant card effects** (heal, level up) — still applied immediately

## Key Files to Modify

**Backend:**
1. `server/gameplay/gameplay.py` — Character model (string lists), EffectTotal computation, CHARACTER_STATS_BY_LEVEL, GamePlay.ability type
2. `server/gameplay/effects.py` — remove `dispose_actions`, `source` from Effect classes
3. `server/gameplay/abilities.py` — no structural change (just remove source validation dependency)
4. `server/gameplay/cards.py` — no structural change
5. `server/gameplay/actions/action.py` — add dispose declarations + `dispose_character()` method
6. `server/gameplay/actions/stage_ability_selection.py` — store ability name string
7. `server/gameplay/actions/stage_ability_opponent_selection.py` — store effect name string
8. `server/gameplay/actions/stage_card_draw.py` — store card name string
9. `server/gameplay/actions/stage_opponent_selection.py` — store card/ability name strings
10. `server/gameplay/actions/battle_end.py` — use `dispose_character()`
11. `server/gameplay/actions/stage_battle.py` — use `dispose_character()`
12. `server/gameplay/actions/stage_character_select.py` — use `dispose_character()`
13. `server/gameplay/presets.py` — string names everywhere

**Frontend:**
14. `src/components/CharacterCard.jsx` — `active_cards`, string-based checks
