# Game Play

This document outlines the gameplay architecture and component hierarchy for the card game engine, detailing main components.

- [FrontEnd GamePlay](/src/components/GamePlay/gameplay_frontend.md)
- [BackEnd GamePlay](/server/gameplay/gameplay_backend.md)

## Overview

This engine offers a fully integrated backend and frontend interaction system for card games, supporting multiple players with individual decks and a shared area.
It is built on a tightly integrated system of React components and Pydantic models, with data exchanged via JSON serialization.

The game supports internationalization via react-i18next, currently configured for Hebrew only.

### Game Requirements

- **Minimum Players**: At least 2 players are required for the game to start
- Players do not need to be connected, but at least 2 players must have joined the game

## Backend Alignment

Frontend components are designed to work seamlessly with the backend models outlined in [gameplay backend](/server/gameplay/gameplay_backend.md).

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
- Manages drawn cards deck
- Handles center pile and community cards

### Player

- The status and cards for a single player
- holds player connection status (connected \ disconncted)

### Deck

- A single deck of cards
- Supports different layouts (stack, grid)
- Handles card selection and interaction
- When a deck is marked as active, it indicates that the deck is currently involved in the playing player's turn.

### Card

- Manages card states (face up/down, selected, highlighted)
- Handles click events and animations

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

Each character has one or more abilities that can be used during their turn. When an ability is selected and applied to a target opponent character, it triggers one or more effects that modify gameplay (e.g., reduce attack, skip turn, reroll dice).

### Effect Lifecycle

- **Default Disposal**: All effects are automatically disposed at the end of battle (battle_end stage)
- **Use-Once Effects**: Some effects (like `RerollDiceEffect`) inherit from `UseOnceEffect` and can only be used once. After being used, the `used` flag is set to `True` and the effect won't be reused
- **Persistence**: Effects remain active on the character from the moment they're applied until battle ends

See [Backend GamePlay - Abilities & Effects](/server/gameplay/gameplay_backend.md#abilities--effects) for detailed implementation.

## Game Stages

The game progresses through distinct stages during each player's turn. Upon completing all stages, the turn passes to the next player.

### Turn Stages

1. **Character Select** (`character_select`) - Player chooses which character will act during this turn
2. **Ability Selection** (`ability_selection`) - Player selects which ability to use from the character's available abilities
3. **Ability Opponent Selection** (`ability_opponent_selection`) - Player selects an opponent and one of the opponent's characters to apply the ability to
4. **Opponent Selection** (`opponent_selection`) - Player selects an opponent and one of the opponent's characters for battle
5. **Battle Dice Roll** (`battle_dice_roll`) - Both players roll dice for combat
6. **Battle End** (`battle_end`) - Combat results are calculated and applied
