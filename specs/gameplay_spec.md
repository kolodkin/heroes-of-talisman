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

## Game Stages

The game progresses through distinct stages during each player's turn. Upon completing all stages, the turn passes to the next player.

### Turn Stages

1. **Character Select** - Player chooses which character will act during this turn
2. **Opponent Selection** - Player selects an opponent and one of their characters for battle
3. **Battle** - Combat between selected character and opponent's character
