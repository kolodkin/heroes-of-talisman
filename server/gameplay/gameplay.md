# Backend - GamePlay

A Pydantic-based engine for updating game state through [actions](../actions).

related specs:

- [gameplay spec](/specs/gameplay.md)
- [gameplay frontend spec](/src/components/GamePlay/gameplay.md)

## Overview

The backend manages game state using Pydantic models and processes player actions to update the game board. Game progression is controlled through stages, with actions potentially advancing or modifying the current stage.

## Game Stages and Actions

Actions may change the game stage, but not necessarily. Some actions update game state relevant to the current stage without advancing to the next stage.

**Stage Transition Rules:**

- Actions can modify `GameBoard.stage` when appropriate (e.g., completing a required task)
- Actions can modify game state within the current stage without changing it (e.g., selecting a card, moving a character)
- Stage transitions are determined by action logic, not automatically enforced
- Multiple actions may be required before a stage advances

**Example Flow:**

1. Stage: `character_select`
2. Action: `select_character` → Updates selected character, may advance to next stage
3. Action: `deselect_character` → Updates selection, stays in same stage

## Key Features
