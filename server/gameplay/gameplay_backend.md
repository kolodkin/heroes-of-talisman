# Backend - GamePlay

A Pydantic-based engine for updating game state through [actions](../actions).

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

## Key Features
