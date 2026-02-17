## Backend - GamePlay

A Pydantic-based engine for updating game state through [actions](#actions).

related specs:

- [gameplay spec](/docs/gameplay_spec.md)
- [gameplay frontend spec](/docs/gameplay_frontend.md)

# Overview

The backend manages game state using Pydantic models and processes player actions to update the game board. Game progression is controlled through stages, with actions potentially advancing or modifying the current stage.

# Interactive

Any player action that updates the gameplay state will trigger a WebSocket broadcast to all players in the game, ensuring synchronized game state across all clients.

**WebSocket Broadcast Flow (actions_loop, game_update_loop in server/main.py):**

1. Player action is received via `actions_loop()`
2. Action is processed and game state is updated
3. Updated state is saved to database
4. Redis pub/sub broadcasts `game_update` event to all connected clients
5. All clients receive the update via `game_update_loop()`

# Game Stages and Actions

Actions may change the game stage, but not necessarily. Some actions update game state relevant to the current stage without advancing to the next stage.

**Stage Transition Rules:**

- Actions can modify `GamePlay.stage` when appropriate (e.g., completing a required task)
- Actions can modify game state within the current stage without changing it (e.g., selecting a card, moving a character)
- Stage transitions are determined by action logic, not automatically enforced
- Multiple actions may be required before a stage advances

**Example Flow:**

1. Stage: `character_select`
   - `active` contains `ActivePlayer1` with the active player name
2. Action: `character_press` → Updates selected character in stage_meta, stays in same stage
3. Action: `character_select` → Confirms character selection, updates `active` to `ActivePlayer2` with player and character, advances to `opponent_selection` stage
4. Stage: `opponent_selection`
   - `active` contains `ActivePlayer2` with player and selected character
5. Action: `opponent_press` → Updates selected opponent and character in stage_meta (as `Opponent2`), stays in same stage
6. Action: `opponent_select` → Confirms opponent selection, sets `opponent` field with `Opponent2`, advances to `battle` stage

# Actions

The backend action layer organizes game mutations into small, focused classes. Each action is invoked with the current user and `GamePlay` state and returns the updated game after running.

## Core Components

- **`Action` base class** (`server/gameplay/action.py`): provides convenience accessors for game properties (players, stage, deck) and the `assert_stage` helper to validate that an action is executed in the correct phase.
- **Connection actions** (`ConnectAction`, `LeaveAction`, `DisconnectAction`): manage player lifecycle by connecting players, removing them from the game, or marking them as disconnected.
- **Models**: Pydantic models (`GamePlay`, `Player`, `Character`) describe the game state and enforce structure and types.

## Action Workflow

1. An action instance is created with a user identifier and the current `GamePlay`.
2. The client-provided parameters are passed to the action's `run` method.
3. The action updates the `GamePlay` and returns it for broadcasting to other players.

## Error Handling

- `GameException` represents general server-side errors.
- `ReportedException` indicates errors that should be surfaced to the client, such as invalid stages or missing resources.

## Extending Actions

To implement a new action, subclass `Action` and implement the `run` method. Use `assert_stage` to ensure the action only executes during the appropriate game phase and update the `GamePlay` as needed.

## General Actions

- [x] `connect` – add a player to the game (`ConnectAction`)
- [x] `leave` – remove a player from the game (`LeaveAction`)
- [x] `disconnect` – mark a player as disconnected (`DisconnectAction`)

# Abilities & Effects

Each character has one or more abilities that can be used during their turn. When an ability is selected, it triggers one or more effects.

## Effect Base Class

All effects inherit from `Effect` base class (`server/gameplay/models.py`) with:

- `name`: Discriminator field for polymorphic serialization
- `source`: The ability that created this effect
- `dispose_actions`: List of action names when this effect should be disposed
- `apply_to`: Target type (`'self'`, `'battle_opponent'`, or `'selected_opponent'`)

## Effect Application Types

- **Self** (`apply_to='self'`): Applied to active player's character in `AbilitySelectAction`
- **Battle Opponent** (`apply_to='battle_opponent'`): Applied to battle opponent in `OpponentSelectAction`
- **Selected Opponent** (`apply_to='selected_opponent'`): Requires `ability_opponent_selection` stage, applied in `AbilityOpponentSelectAction`

## Effect Types

| Effect                 | Description                                 | `dispose_actions` (default)              | `apply_to`          |
| ---------------------- | ------------------------------------------- | ---------------------------------------- | ------------------- |
| `SkipTurnEffect`       | Character skips next turn                   | `['character_select']`                   | `selected_opponent` |
| `AttackBonusEffect`    | Increases attack by value                   | `['battle_end']`                         | `self`              |
| `AttackNegBonusEffect` | Decreases attack by value                   | `['battle_end']`                         | `battle_opponent`   |
| `RerollDiceEffect`     | Allows dice reroll on loss                  | `['battle_end', 'action_reroll_effect']` | `self`              |
| `DrawCardEffect`       | Draws cards                                 | `['battle_end']`                         | `self`              |
| `DefenseBonusEffect`   | Increases defense by value                  | `['battle_end']`                         | `self`              |
| `HealEffect`           | Heals character instantly                   | `['card_select']`                        | `self`              |
| `LevelUpEffect`        | Levels up character, restores health        | `['card_select']`                        | `self`              |
| `TalismanEffect`       | Kills defeated opponent regardless of level | `[]` (persistent)                        | `self`              |

**Note:** `dispose_actions` can be overridden per instance. Card-sourced equipment effects (e.g., `metal_armor`, `sacred_sword`) override `dispose_actions=[]` to make them persistent, while ability-sourced effects use the defaults shown above.

# Cards

Cards provide bonuses and effects to characters. Cards are drawn from a shared deck during the `card_draw` stage.

## Card Model

- `name`: Unique card identifier
- `effects`: List of effects applied when card is selected
- `restricted_characters`: Characters that cannot use this card

## Deck Model

Generic `Deck[T]` with `draw()` method that auto-resets with shuffled cards when empty.

## Available Cards

| Card           | Effects                                      | Restrictions |
| -------------- | -------------------------------------------- | ------------ |
| `metal_armor`  | `DefenseBonusEffect(+2, dispose_actions=[])` | None         |
| `sacred_sword` | `AttackBonusEffect(+3, dispose_actions=[])`  | Archer       |
| `golden_apple` | `HealEffect(+1)` (instant)                   | None         |
| `magic_ball`   | `LevelUpEffect(+1)` (instant)                | None         |
| `talisman`     | `TalismanEffect` (persistent)                | None         |

**Note:** Equipment cards (`metal_armor`, `sacred_sword`) override `dispose_actions=[]` making their effects persistent (never disposed). The `talisman` effect is also persistent. Card names are tracked in `character.cards` list.

## Available Abilities

| Character | Ability          | Effect                                       |
| --------- | ---------------- | -------------------------------------------- |
| Knight L1 | `BATTLE_HOWL`    | `AttackBonusEffect(attack_bonus=2)`          |
| Archer L1 | `BOUNCING_ARROW` | `RerollDiceEffect`                           |
| Mage L1   | `FREEZE`         | `SkipTurnEffect` (requires target selection) |

# Stages

## Stage: Character Select

The character selection stage allows players to choose which character will act during their turn. Dead characters (`is_alive=False`) and characters with `SkipTurnEffect` cannot be selected. The `Character.is_available` computed field encapsulates this check (`is_alive and not skip_turn`).

- **`CharacterPressAction`**: Sets `stage_meta['selected']` to the character name pressed by the active player. Validates that the player is active, the stage is `character_select`, the character exists for this player, and the character is alive (`is_alive=True`).
- **`CharacterSelectAction`**: Confirms the character selection by setting `selected_character` to the chosen character name, **disposes all effects with `dispose_action='character_select'`** from the active player's characters (e.g., all SkipTurnEffects), and transitioning the game stage from `character_select` to `ability_selection`. Validates that the selected character is alive. **Auto-selects ability**: If the selected character has only one ability, `stage_meta.selected` is automatically set to that ability's name for the ability selection stage; otherwise `stage_meta` is cleared.
- **`SkipTurnAction`**: Skips the current player's turn when no character is available for selection (all characters are either dead or have `SkipTurnEffect`). **Disposes all effects with `dispose_action='character_select'`** from the active player's characters, rotates to the next player (circular rotation), and stays in `character_select` stage for the next player's turn.

**Actions:**

- [x] `character_press` – highlight selected character (`CharacterPressAction`)
- [x] `character_select` – confirm character selection, dispose character_select effects, and transition to card_draw (`CharacterSelectAction`)
- [x] `skip_turn` – skip turn when no character available, dispose character_select effects, and rotate to next player (`SkipTurnAction`)

## Stage: Card Draw

The card draw stage allows players to draw a card from the deck and add it to their character.

- **`CardDrawAction`**: Draws a random card from the deck and stores it in `stage_meta.drawn_card`. The deck auto-resets when empty.
- **`CardSelectAction`**: Confirms the card selection by applying instant effects and adding persistent effects to the character. Instant effects are applied immediately:
  - **`HealEffect`**: Heals character (capped at max_health)
  - **`LevelUpEffect`**: Increases character level, updates stats to new level, and restores health to new max_health

  Cards are tracked in `character.cards`. Transitions to `ability_selection` stage.

**Card Restrictions:**

- Some cards have `restricted_characters` that cannot use them
- Restricted cards are skipped when drawn by excluded characters

**Actions:**

- [x] `card_draw` – draw a random card from deck, store in stage_meta (`CardDrawAction`)
- [x] `card_select` – apply card effects and transition to ability_selection (`CardSelectAction`)

## Stage: Ability Selection

The ability selection stage allows players to choose which ability to use from their selected character's available abilities.

- **`AbilityPressAction`**: Sets `stage_meta['selected']` to the ability name pressed by the active player. Validates that the player is active, the stage is `ability_selection`, and the ability is available for the selected character.
- **`AbilitySelectAction`**: Confirms the ability selection by storing the selected ability object in `GamePlay.ability`. Transitions to `ability_opponent_selection` if the ability has effects requiring target selection (e.g., `SkipTurnEffect`), otherwise transitions directly to `opponent_selection`. Clears `stage_meta` after confirmation. Validates that the ability is available for the character.

**Actions:**

- [x] `ability_press` – highlight selected ability in stage_meta (`AbilityPressAction`)
- [x] `ability_select` – confirm ability selection, store in GamePlay.ability, transition to ability_opponent_selection or opponent_selection based on ability effects (`AbilitySelectAction`)

## Stage: Ability Opponent Selection

The ability opponent selection stage allows players to choose which opponent character to apply the selected ability's effects to. **This stage is only used for abilities with effects that require target selection (e.g., `SkipTurnEffect`).** Other abilities skip this stage entirely.

- **`AbilityOpponentPressAction`**: Sets `stage_meta` to an `Opponent2` object with the selected opponent player name and character. Validates that the player is active, the stage is `ability_opponent_selection`, the opponent exists, is not the current player, has the selected character, and the character is alive (`is_alive=True`).
- **`AbilityOpponentSelectAction`**: Confirms the ability target selection by reading from `stage_meta`, applying the ability's effects to the target character, storing the target in `GamePlay.ability_opponent`, clearing `stage_meta`, and transitioning the game stage from `ability_opponent_selection` to `opponent_selection`. Validates that the opponent character is still alive.

**Actions:**

- [x] `ability_opponent_press` – highlight selected opponent and character in stage_meta (`AbilityOpponentPressAction`)
- [x] `ability_opponent_select` – confirm ability target, apply effects to target character, store in GamePlay.ability_opponent, and transition to opponent_selection (`AbilityOpponentSelectAction`)

## Stage: Opponent Selection

The opponent selection stage allows players to choose an opponent and one of their characters for battle.

- **`OpponentPressAction`**: Sets `stage_meta` to an `Opponent` object with the selected opponent player name and character. Validates that the player is active, the stage is `opponent_selection`, the opponent exists, is not the current player, has the selected character, and the character is alive (`is_alive=True`).
- **`OpponentSelectAction`**: Confirms the opponent selection by reading from `stage_meta`, setting `opponent` to the selected opponent, and transitioning the game stage from `opponent_selection` to `battle`. Validates that the opponent character is alive. Clears `stage_meta` after transition.

**Actions:**

- [x] `opponent_press` – highlight selected opponent and character (`OpponentPressAction`)
- [x] `opponent_select` – confirm opponent selection and transition to battle (`OpponentSelectAction`)

## Stage: Battle

The battle stage handles dice rolling for both the active player and opponent, followed by resolving the battle outcome.

- **`ActivePlayerRollAction`**: Rolls dice for the active player based on their character's dice value and sets `active.dice_roll` to a list of rolled values. Validates that the player is active and the stage is `battle_dice_roll`.
- **`OpponentRollAction`**: Rolls dice for the opponent based on their character's dice value and sets `opponent.dice_roll` to a list of rolled values. Validates that the stage is `battle_dice_roll`. Note: This action can be invoked by the opponent player (not the active player), as the opponent needs to roll their own dice.
- **`RerollAction`**: Resets dice rolls when both players rolled and the result is a draw. Downgrades `ActivePlayer4`/`Opponent4` back to `ActivePlayer2`/`Opponent2` for re-rolling.
- **`RerollEffectAction`**: Allows the active player to use a `RerollDiceEffect` after losing a battle. Removes the effect and resets dice for re-rolling. Only available in `battle_dice_roll` stage when the loser has a reroll effect.
- **`BattleEndAction`**: Ends the battle after both players have rolled. Calculates scores (`sum(dice_roll) + attack`), reduces the loser's health by 1 with level-based death handling:
  - **Winner has talisman and opponent at 0 health**: Opponent dies regardless of level (`is_alive=False`)
  - **Level 2+ character at 0 health** (no talisman): Reduces level by 1 and restores health to new level's max_health (character survives)
  - **Level 1 character at 0 health**: Character dies (`is_alive=False`)

  Also disposes effects with `'battle_end'` in `dispose_actions`, clears battle state, sets the next player (circular rotation) as the new active player, and transitions back to `character_select` stage.

**Stage Transition Logic:**

When both players have rolled, the game calculates the winner and determines the next stage:

- **Draw**: Stay in `battle_dice_roll` stage (players can reroll via `RerollAction`)
- **Winner with loser having reroll effect**: Stay in `battle_dice_roll` stage (loser can use `RerollEffectAction`)
- **Winner with no reroll available**: Transition to `battle_end` stage

**Actions:**

- [x] `active_player_roll` – roll dice for active player, sets `active.dice_roll` list (`ActivePlayerRollAction`)
- [x] `opponent_roll` – roll dice for opponent, sets `opponent.dice_roll` list (`OpponentRollAction`)
- [x] `action_reroll` – reset dice rolls on draw (`RerollAction`)
- [x] `action_reroll_effect` – use reroll effect after losing, mark effect as used (`RerollEffectAction`)
- [x] `battle_end` – end battle, reduce loser's health, dispose battle effects, transition to next turn (`BattleEndAction`)
