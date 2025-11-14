# Backend - GamePlay

A Pydantic-based engine for updating game state through [actions](#actions).

related specs:

- [gameplay spec](/docs/gameplay_spec.md)
- [gameplay frontend spec](/src/components/GamePlay/gameplay_frontend.md)

## Overview

The backend manages game state using Pydantic models and processes player actions to update the game board. Game progression is controlled through stages, with actions potentially advancing or modifying the current stage.

## Interactive

Any player action that updates the gameplay state will trigger a WebSocket broadcast to all players in the game, ensuring synchronized game state across all clients.

**WebSocket Broadcast Flow (actions_loop, game_update_loop in server/main.py):**

1. Player action is received via `actions_loop()`
2. Action is processed and game state is updated
3. Updated state is saved to database
4. Redis pub/sub broadcasts `game_update` event to all connected clients
5. All clients receive the update via `game_update_loop()`

## Game Stages and Actions

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

## Actions

The backend action layer organizes game mutations into small, focused classes. Each action is invoked with the current user and `GamePlay` state and returns the updated game after running.

### Core Components

- **`Action` base class** (`server/gameplay/action.py`): provides convenience accessors for game properties (players, stage, deck) and the `assert_stage` helper to validate that an action is executed in the correct phase.
- **Connection actions** (`ConnectAction`, `LeaveAction`, `DisconnectAction`): manage player lifecycle by connecting players, removing them from the game, or marking them as disconnected.
- **Models**: Pydantic models (`GamePlay`, `Player`, `CharacterCard`) describe the game state and enforce structure and types.

### Action Workflow

1. An action instance is created with a user identifier and the current `GamePlay`.
2. The client-provided parameters are passed to the action's `run` method.
3. The action updates the `GamePlay` and returns it for broadcasting to other players.

### Error Handling

- `GameException` represents general server-side errors.
- `ReportedException` indicates errors that should be surfaced to the client, such as invalid stages or missing resources.

### Extending Actions

To implement a new action, subclass `Action` and implement the `run` method. Use `assert_stage` to ensure the action only executes during the appropriate game phase and update the `GamePlay` as needed.

### General Actions

- [x] `connect` – add a player to the game (`ConnectAction`)
- [x] `leave` – remove a player from the game (`LeaveAction`)
- [x] `disconnect` – mark a player as disconnected (`DisconnectAction`)

## Abilities & Effects

Each character has one or more abilities that can be used during their turn. When an ability is selected and applied to a target opponent character, it triggers one or more effects.

### Ability System

- **Ability**: Contains a name and a list of effects to apply (description is managed via i18n)
- **Effects**: Applied to the target character when the ability is used
- **Effect Lifecycle**: All effects are automatically disposed at the end of battle (battle_end stage) by default

### Effect Types

All effect classes are defined in `server/gameplay/models.py`:

- **`Effect`** (base class, lines 148-155): All effects have a `source: AbilityName` field indicating which ability created them
- **`UseOnceEffect`** (extends Effect, lines 158-165): Effects that can only be used once. After being used, the `used` flag is set to `True` and the effect won't be reused
- **`SkipTurnEffect`** (extends Effect, lines 168-174): Character cannot participate in the next turn
- **`AttackBonusEffect`** (extends Effect, lines 177-183): Increases character's attack by a specified value (`attack_bonus: int`)
- **`AttackNegBonusEffect`** (extends Effect, lines 196-202): Decreases character's attack by a specified value (`attack_neg_bonus: int`, negative value)
- **`RerollDiceEffect`** (extends UseOnceEffect, lines 186-193): Character can reroll dice if they lose the battle, but only once (`reroll_dice: bool = True`)

### Available Abilities

Ability definitions with their effects (defined in `server/gameplay/models.py:230-248`):

- **Knight L1**: `BATTLE_HOWL`
  - Activates: `AttackNegBonusEffect(attack_neg_bonus=-2)`
  - Effect: Reduces opponent's attack by 2

- **Archer L1**: `BOUNCING_ARROW`
  - Activates: `RerollDiceEffect`
  - Effect: Allows the target to reroll dice if they lose the battle (use-once)

- **Mage L1**: `FREEZE`
  - Activates: `SkipTurnEffect`
  - Effect: Opponent skips their next turn

### Character Effects

Characters have an `effects` list that stores all active effects applied to them. Each effect includes:

- `source`: The ability that created this effect (required)

## Stages

### Stage: Character Select

The character selection stage allows players to choose which character will act during their turn. Dead characters (`is_alive=False`) cannot be selected.

- **`CharacterPressAction`**: Sets `stage_meta['selected']` to the character name pressed by the active player. Validates that the player is active, the stage is `character_select`, the character exists for this player, and the character is alive (`is_alive=True`).
- **`CharacterSelectAction`**: Confirms the character selection by setting `selected_character` to the chosen character name and transitioning the game stage from `character_select` to `opponent_selection`. Validates that the selected character is alive. Clears `stage_meta` after transition.

**Actions:**

- [x] `character_press` – highlight selected character (`CharacterPressAction`)
- [x] `character_select` – confirm character selection and transition to ability_selection (`CharacterSelectAction`)

### Stage: Ability Selection

The ability selection stage allows players to choose which ability to use from their selected character's available abilities.

- **`AbilityPressAction`**: Sets `stage_meta['selected']` to the ability name pressed by the active player. Validates that the player is active, the stage is `ability_selection`, and the ability is available for the selected character.
- **`AbilitySelectAction`**: Confirms the ability selection by storing the selected ability object in `GamePlay.ability` and transitioning the game stage from `ability_selection` to `ability_opponent_selection`. Clears `stage_meta` after confirmation. Validates that the ability is available for the character.

**Actions:**

- [x] `ability_press` – highlight selected ability in stage_meta (`AbilityPressAction`)
- [x] `ability_select` – confirm ability selection, store in GamePlay.ability, and transition to ability_opponent_selection (`AbilitySelectAction`)

### Stage: Ability Opponent Selection

The ability opponent selection stage allows players to choose which opponent and opponent character to apply the selected ability to.

- **`AbilityOpponentPressAction`**: Sets `stage_meta` to an `Opponent2` object with the selected opponent player name and character. Validates that the player is active, the stage is `ability_opponent_selection`, the opponent exists, is not the current player, has the selected character, and the character is alive (`is_alive=True`).
- **`AbilityOpponentSelectAction`**: Confirms the ability target selection by reading from `stage_meta`, applying the ability's effects to the target character, storing the target in `GamePlay.ability_opponent`, clearing `stage_meta`, and transitioning the game stage from `ability_opponent_selection` to `opponent_selection`. Validates that the opponent character is still alive.

**Actions:**

- [x] `ability_opponent_press` – highlight selected opponent and character in stage_meta (`AbilityOpponentPressAction`)
- [x] `ability_opponent_select` – confirm ability target, apply effects to target character, store in GamePlay.ability_opponent, and transition to opponent_selection (`AbilityOpponentSelectAction`)

### Stage: Opponent Selection

The opponent selection stage allows players to choose an opponent and one of their characters for battle.

- **`OpponentPressAction`**: Sets `stage_meta` to an `Opponent` object with the selected opponent player name and character. Validates that the player is active, the stage is `opponent_selection`, the opponent exists, is not the current player, has the selected character, and the character is alive (`is_alive=True`).
- **`OpponentSelectAction`**: Confirms the opponent selection by reading from `stage_meta`, setting `opponent` to the selected opponent, and transitioning the game stage from `opponent_selection` to `battle`. Validates that the opponent character is alive. Clears `stage_meta` after transition.

**Actions:**

- [x] `opponent_press` – highlight selected opponent and character (`OpponentPressAction`)
- [x] `opponent_select` – confirm opponent selection and transition to battle (`OpponentSelectAction`)

### Stage: Battle

The battle stage handles dice rolling for both the active player and opponent, followed by resolving the battle outcome.

- **`ActivePlayerRollAction`**: Rolls dice for the active player based on their character's dice value and sets `active.dice_roll` to a list of rolled values. Validates that the player is active and the stage is `battle`.
- **`OpponentRollAction`**: Rolls dice for the opponent based on their character's dice value and sets `opponent.dice_roll` to a list of rolled values. Validates that the stage is `battle`. Note: This action can be invoked by the opponent player (not the active player), as the opponent needs to roll their own dice.
- **`BattleEndAction`**: Ends the battle after both players have rolled. Calculates scores (`sum(dice_roll) + attack`), reduces the loser's health by 1 (which may set `is_alive=False` if health reaches 0), clears battle state, sets the next player (circular rotation) as the new active player, and transitions back to `character_select` stage.

**Actions:**

- [x] `active_player_roll` – roll dice for active player, sets `active.dice_roll` list (`ActivePlayerRollAction`)
- [x] `opponent_roll` – roll dice for opponent, sets `opponent.dice_roll` list (`OpponentRollAction`)
- [x] `battle_end` – end battle, reduce loser's health, transition to next turn (`BattleEndAction`)
