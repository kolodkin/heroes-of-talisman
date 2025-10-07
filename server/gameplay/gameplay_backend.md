# Backend - GamePlay

A Pydantic-based engine for updating game state through [actions](#actions).

related specs:

- [gameplay spec](/specs/gameplay_spec.md)
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

### Stage: Character Select

The character selection stage allows players to choose which character will act during their turn.

- **`CharacterPressAction`**: Sets `stage_meta['selected']` to the character name pressed by the active player. Validates that the player is active, the stage is `character_select`, and the character exists for this player.
- **`CharacterSelectAction`**: Confirms the character selection by setting `selected_character` to the chosen character name and transitioning the game stage from `character_select` to `opponent_selection`. Clears `stage_meta` after transition.

### Stage: Opponent Selection

The opponent selection stage allows players to choose an opponent and one of their characters for battle.

- **`OpponentPressAction`**: Sets `stage_meta` to an `Opponent` object with the selected opponent player name and character. Validates that the player is active, the stage is `opponent_selection`, the opponent exists, is not the current player, and has the selected character.
- **`OpponentSelectAction`**: Confirms the opponent selection by reading from `stage_meta`, setting `opponent` to the selected opponent, and transitioning the game stage from `opponent_selection` to `battle`. Clears `stage_meta` after transition.

### Action Workflow

1. An action instance is created with a user identifier and the current `GamePlay`.
2. The client-provided parameters are passed to the action's `run` method.
3. The action updates the `GamePlay` and returns it for broadcasting to other players.

### Error Handling

- `GameException` represents general server-side errors.
- `ReportedException` indicates errors that should be surfaced to the client, such as invalid stages or missing resources.

### Extending Actions

To implement a new action, subclass `Action` and implement the `run` method. Use `assert_stage` to ensure the action only executes during the appropriate game phase and update the `GamePlay` as needed.

### Implemented Actions

Checklist of actions implemented in `server/gameplay/actions/`:

**General:**

- [x] `connect` – add a player to the game (`ConnectAction`)
- [x] `leave` – remove a player from the game (`LeaveAction`)
- [x] `disconnect` – mark a player as disconnected (`DisconnectAction`)

**Character Select Stage:**

- [x] `character_press` – highlight selected character (`CharacterPressAction`)
- [x] `character_select` – confirm character selection and transition to opponent_selection (`CharacterSelectAction`)

**Opponent Selection Stage:**

- [x] `opponent_press` – highlight selected opponent and character (`OpponentPressAction`)
- [x] `opponent_select` – confirm opponent selection and transition to battle (`OpponentSelectAction`)

## Key Features
