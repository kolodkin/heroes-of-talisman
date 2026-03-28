## Backend - GamePlay

A Pydantic-based engine for updating game state through [actions](#actions).

related specs:

- [gameplay spec](/docs/gameplay.md)
- [gameplay frontend spec](/docs/frontend.md)

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

Abilities and cards are stored as **string literal names** on the character (`active_abilities`, `cards`, `effects`). The `effect` computed property aggregates these into an `EffectTotal` with hardcoded values per name. Self-targeted abilities (`apply_to = "self"`) are applied directly; opponent-targeted (`apply_to = "selected_opponent"`) require `ability_opponent_selection` stage.

Each character level has exactly one set of abilities — higher-level abilities **replace** lower-level ones, they do not stack. A character only has the abilities for their current level (e.g., a level 2 Mage has `storm` and `dragon_breath`, not `freeze`).

See [Abilities & Effects](/docs/gameplay.md#abilities--effects) for the full ability list with character, level, and descriptions.

| Ability             | Effect                                                              | `apply_to`          | When Applied                  | When Cleared                                       |
| ------------------- | ------------------------------------------------------------------- | ------------------- | ----------------------------- | -------------------------------------------------- |
| `BATTLE_HOWL`       | `AttackBonusEffect(+2)`                                             | `self`              | `AbilitySelectAction`         | `BattleEndAction`                                  |
| `DISARM`            | `DrawCardEffect` — routes to `card_draw` stage; after card drawn, turn ends (rotates to next player, skips battle entirely) | `self` | `AbilitySelectAction` | `CardSelectAction` (turn rotation, no `BattleEndAction`) |
| `BOUNCING_ARROW`    | `RerollDiceEffect`                                                  | `self`              | `AbilitySelectAction`         | `BattleEndAction`                                  |
| `BOUNCING_ARROW_L2` | `RerollDiceEffect` (×2)                                             | `self`              | `AbilitySelectAction`         | `BattleEndAction`                                  |
| `BOUNCING_ARROW_L3` | `RerollDiceEffect`                                                  | `self`              | `AbilitySelectAction`         | `BattleEndAction`                                  |
| `BURNING_ARROW`     | `BurningArrowEffect` — on win, appends `burning_arrow:2` to opponent's effects; `CharacterSelectAction` decrements countdown and applies 2 damage when it reaches 0 | `self` | `AbilitySelectAction` | countdown auto-removed by `CharacterSelectAction` |
| `FREEZE`            | `SkipTurnEffect`                                                    | `selected_opponent` | `AbilityOpponentSelectAction` | `CharacterSelectAction` / `SkipTurnAction`         |
| `STORM`             | `AttackNegBonusEffect(-2)`                                          | `battle_opponent`   | `AbilitySelectAction`         | `BattleEndAction`                                  |
| `DRAGON_BREATH`     | `NeutralizeItemEffect`                                              | `selected_opponent` | `AbilityItemSelectAction`     | instant (no persist)                               |

# Cards

Generic `Deck[T]` with `draw()` method that auto-resets with shuffled cards when empty. Instant cards are applied immediately. Persistent cards are stored in `character.cards`. Restricted characters skip the card.

See [Cards](/docs/gameplay.md#cards) for the full card list with types, descriptions, and restrictions.

| Card            | Implementation Effect                                                                 |
| --------------- | ------------------------------------------------------------------------------------- |
| `metal_armor`   | `defense_bonus += 2`                                                                  |
| `sacred_sword`  | `attack_bonus += 3`                                                                   |
| `golden_apple`  | `health += 1` (capped at max)                                                         |
| `magic_ball`    | Level up (+1 level, heal to max)                                                      |
| `devils_fork`   | Level down (-1 level), no effect at L1                                                |
| `darkness_rise` | Skip turn for all alive chars above L1                                                |
| `talisman`      | `has_talisman = True`                                                                 |
| `fog`           | Skip active player's turn unless ALL their alive chars are level 3+ (they resist fog) |

# Action Cleanup

Actions clean up abilities and effects from characters inline when they're no longer relevant. Each action clears the specific list directly:

| Action                  | What is cleared                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------ |
| `BattleEndAction`       | `active_abilities = []` on both active and opponent; `no_damage_on_win` from `effects` on active |
| `CharacterSelectAction` | `effects = []` on all active player's characters                                                 |
| `SkipTurnAction`        | `effects = []` on all active player's characters                                                 |

**Note:** Persistent cards (`metal_armor`, `sacred_sword`, `talisman`) are never disposed.

# Stages

## Stage: Character Select

The character selection stage allows players to choose which character will act during their turn. Dead characters (`is_alive=False`) and characters with `SkipTurnEffect` cannot be selected. The `Character.is_available` computed field encapsulates this check (`is_alive and not skip_turn`).

- **`CharacterPressAction`**: Sets `stage_meta['selected']` to the character name pressed by the active player. Validates that the player is active, the stage is `character_select`, the character exists for this player, and the character is alive (`is_alive=True`).
- **`CharacterSelectAction`**: Confirms the character selection by setting `selected_character` to the chosen character name, **clears `effects`** from all active player's characters, and transitioning the game stage from `character_select` to `ability_selection`. Validates that the selected character is alive. **Auto-selects ability**: If the selected character has only one ability, `stage_meta.selected` is automatically set to that ability's name for the ability selection stage; otherwise `stage_meta` is cleared.
- **`SkipTurnAction`**: Skips the current player's turn when no character is available for selection (all characters are either dead or have `skip_turn` effect). **Clears `effects`** from all active player's characters, rotates to the next player (circular rotation), and stays in `character_select` stage for the next player's turn.

**Actions:**

- [x] `character_press` – highlight selected character (`CharacterPressAction`)
- [x] `character_select` – confirm character selection, dispose skip_turn effects, and transition to card_draw (`CharacterSelectAction`)
- [x] `skip_turn` – skip turn when no character available, dispose skip_turn effects, and rotate to next player (`SkipTurnAction`)

## Stage: Card Draw

The card draw stage allows players to draw a card from the deck and add it to their character.

- **`CardDrawAction`**: Draws a random card from the deck and stores it in `stage_meta.drawn_card`. The deck auto-resets when empty.
- **`CardSelectAction`**: Confirms the card selection. Instant cards are applied immediately (see [Available Cards](#available-cards)). Persistent cards are stored in `character.cards`. Restricted characters skip the card. Transitions to `ability_selection` stage.

**Card Restrictions:**

- Some cards have `restricted_characters` that cannot use them
- Restricted cards are skipped when drawn by excluded characters

**Actions:**

- [x] `card_draw` – draw a random card from deck, store in stage_meta (`CardDrawAction`)
- [x] `card_select` – apply card effects and transition to ability_selection (`CardSelectAction`)

## Stage: Ability Selection

The ability selection stage allows players to choose which ability to use from their selected character's available abilities.

- **`AbilityPressAction`**: Sets `stage_meta['selected']` to the ability name pressed by the active player. Validates that the player is active, the stage is `ability_selection`, and the ability is available for the selected character.
- **`AbilitySelectAction`**: Confirms the ability selection by storing the selected ability name in `GamePlay.ability`. Self-targeted abilities (`apply_to = "self"`) are appended to `character.active_abilities`. Transitions to `ability_opponent_selection` if any effect has `apply_to = "selected_opponent"` (e.g., `FREEZE`), otherwise transitions directly to `opponent_selection`. Clears `stage_meta` after confirmation. Validates that the ability is available for the character.

**Actions:**

- [x] `ability_press` – highlight selected ability in stage_meta (`AbilityPressAction`)
- [x] `ability_select` – confirm ability selection, store in GamePlay.ability, transition to ability_opponent_selection or opponent_selection based on ability effects (`AbilitySelectAction`)

## Stage: Ability Opponent Selection

The ability opponent selection stage allows players to choose which opponent character to apply the selected ability's effects to. **This stage is only used for abilities with effects that require target selection (e.g., `SkipTurnEffect`).** Other abilities skip this stage entirely.

- **`AbilityOpponentPressAction`**: Sets `stage_meta` to an `Opponent2` object with the selected opponent player name and character. Validates that the player is active, the stage is `ability_opponent_selection`, the opponent exists, is not the current player, has the selected character, and the character is alive (`is_alive=True`).
- **`AbilityOpponentSelectAction`**: Confirms the ability target selection by reading from `stage_meta`, storing the target in `GamePlay.ability_opponent`, and transitioning based on the ability's effects:
  - If the ability has a `NeutralizeItemEffect` (e.g., `DRAGON_BREATH`) **and** the target character has active item cards → transitions to `ability_item_selection` stage with `AbilityItemMeta` set.
  - Otherwise → applies effects to the target character (e.g., `FREEZE` appends `skip_turn` to target's `effects`) and transitions directly to `opponent_selection`.
    Validates that the opponent character is still alive.

**Actions:**

- [x] `ability_opponent_press` – highlight selected opponent and character in stage_meta (`AbilityOpponentPressAction`)
- [x] `ability_opponent_select` – confirm ability target, apply effects to target character, store in GamePlay.ability_opponent, and transition to ability_item_selection or opponent_selection (`AbilityOpponentSelectAction`)

## Stage: Ability Item Selection

The ability item selection stage allows the active player to choose which of the target character's item cards to neutralize. **This stage is only used for abilities with `NeutralizeItemEffect` (e.g., `DRAGON_BREATH`) when the target character has active item cards.**

- **`AbilityItemPressAction`**: Sets `stage_meta.selected_item` to the item card name pressed by the active player. Validates that the player is active, the stage is `ability_item_selection`, and the item is in the target character's `active_cards`.
- **`AbilityItemSelectAction`**: Confirms the item selection by removing `selected_item` from the target character's `active_cards`, clearing `stage_meta`, and transitioning to `opponent_selection`.

**Actions:**

- [x] `ability_item_press` – highlight selected item card in stage_meta (`AbilityItemPressAction`)
- [x] `ability_item_select` – confirm item selection, remove from target's active_cards, transition to opponent_selection (`AbilityItemSelectAction`)

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

  When both players have rolled, scores are calculated using the [battle score formula](/docs/gameplay.md#turn-stages) and stored in `active.result.score` / `opponent.result.score`.

- **`RerollAction`**: Resets dice rolls when both players rolled and the result is a draw. Downgrades `ActivePlayer4`/`Opponent4` back to `ActivePlayer2`/`Opponent2` for re-rolling.
- **`RerollEffectAction`**: Allows the active player to use a reroll ability after losing a battle. Only available in `battle_dice_roll` stage when the loser has `reroll_dice_available`. Handles two variants:
  - **`BOUNCING_ARROW` (L1)**: Removes the ability from `active_abilities` and resets dice for one reroll.
  - **`BOUNCING_ARROW_L2` (first reroll)**: Removes the ability from `active_abilities`, appends `EFFECT_REROLL_DICE` and `EFFECT_NO_DAMAGE_ON_WIN` to `character.effects`, and resets dice. The second reroll is now available.
  - **`EFFECT_REROLL_DICE` in effects (second reroll for L2)**: Removes `EFFECT_REROLL_DICE` from `character.effects` (keeps `EFFECT_NO_DAMAGE_ON_WIN`) and resets dice.
- **`BattleEndAction`**: Ends the battle after both players have rolled. Uses the pre-calculated scores to determine the winner, reduces the loser's health by 1 with level-based death handling:
  - **Winner has talisman and opponent at 0 health**: Opponent dies regardless of level (`is_alive=False`)
  - **Level 2+ character at 0 health** (no talisman): Reduces level by 1 and restores health to new level's max_health (character survives)
  - **Level 1 character at 0 health**: Character dies (`is_alive=False`)
  - **Active player wins with `no_damage_on_win` effect**: Damage to opponent is skipped entirely (Archer L2 second reroll)

  Also clears `active_abilities` from both active and opponent characters, clears `EFFECT_NO_DAMAGE_ON_WIN` from active character's `effects`, sets the next player (circular rotation) as the new active player, and transitions back to `character_select` stage.

**Stage Transition Logic:**

When both players have rolled, the game calculates the winner and determines the next stage:

- **Draw**: Stay in `battle_dice_roll` stage (players can reroll via `RerollAction`)
- **Winner with loser having `reroll_dice_available`**: Stay in `battle_dice_roll` stage (loser can use `RerollEffectAction`)
- **Winner with no reroll available**: Transition to `battle_end` stage

**Actions:**

- [x] `active_player_roll` – roll dice for active player, sets `active.dice_roll` list (`ActivePlayerRollAction`)
- [x] `opponent_roll` – roll dice for opponent, sets `opponent.dice_roll` list (`OpponentRollAction`)
- [x] `action_reroll` – reset dice rolls on draw (`RerollAction`)
- [x] `action_reroll_effect` – use reroll ability after losing, dispose BOUNCING_ARROW (`RerollEffectAction`)
- [x] `battle_end` – end battle, reduce loser's health, dispose battle abilities, transition to next turn (`BattleEndAction`)
