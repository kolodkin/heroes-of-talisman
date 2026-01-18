# Game Play

This document outlines the gameplay architecture and component hierarchy for the game engine, detailing main components.

- [FrontEnd GamePlay](/docs/gameplay_frontend.md)
- [BackEnd GamePlay](/docs/gameplay_backend.md)

## Overview

This engine offers a fully integrated backend and frontend interaction system, supporting multiple players with their characters and a shared area.
It is built on a tightly integrated system of React components and Pydantic models, with data exchanged via JSON serialization.

The game supports internationalization via react-i18next, currently configured for Hebrew only.

### Game Requirements

- **Minimum Players**: At least 2 players are required for the game to start
- Players do not need to be connected, but at least 2 players must have joined the game

## Backend Alignment

Frontend components are designed to work seamlessly with the backend models outlined in [gameplay backend](/docs/gameplay_backend.md).

## Core Architecture

### Game Board Structure

The engine expects a JSON game board as defined in backend "server/gameplay/models.py -> GameBoard"

## Component\Models Hierarchy

### Navbar

- Game name
- Username
- Current stage name (translated)
- Current playing player

### GameBoard

- Manages overall game state
- Handles player turns and game flow
- Coordinates between all child components
- Manages SharedArea and Players

### SharedArea

- Common game elements
- Displays stage-specific UI components

### Player

- The status and characters for a single player
- Holds player connection status (connected/disconnected)

## Interactive

Any player action that updates the gameplay state will trigger an update for all players in the game via the WebSocket connection. This update implicitly causes a re-render of the game UI for all connected players, ensuring synchronized game state across all clients.

## Characters

The game features three distinct character types:

- **Knight**: Has the strongest attack skills and health
- **Archer**: Has the highest health
- **Mage**: Has the strongest special skills

### Lifespan

Once a character's health hits 0, it dies. A dead character can no longer be selected neither as an active player character nor as an opponent.

## Abilities & Effects

Each character has one or more abilities that can be used during their turn. When an ability is selected, it triggers one or more effects that modify gameplay (e.g., reduce attack, skip turn, reroll dice).

Effects are applied to different targets depending on their type: the active player's character, the battle opponent, or a selected opponent. Effects persist until disposed by specific game actions (e.g., battle end, character select).

See [Backend GamePlay - Abilities & Effects](/docs/gameplay_backend.md#abilities--effects) for detailed implementation.

## Game Stages

The game progresses through distinct stages during each player's turn. Upon completing all stages, the turn passes to the next player.

### Turn Stages

1. **Character Select** (`character_select`) - Player chooses which character will act during this turn
2. **Ability Selection** (`ability_selection`) - Player selects which ability to use from the character's available abilities
3. **Ability Opponent Selection** (`ability_opponent_selection`) - _(Only for effects requiring target selection, e.g., SkipTurnEffect)_ Player selects an opponent character to apply the ability to
4. **Opponent Selection** (`opponent_selection`) - Player selects an opponent and one of the opponent's characters for battle
5. **Battle Dice Roll** (`battle_dice_roll`) - Both players roll dice for combat
6. **Battle End** (`battle_end`) - Combat results are calculated and applied
