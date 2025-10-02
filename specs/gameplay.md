# Game Play

This document outlines the gameplay architecture and component hierarchy for the card game engine, detailing main components.

- [FrontEnd GamePlay](/src/components/GamePlay)
- [BackEnd GamePlay](/server/gameplay)

## Overview

This engine offers a fully integrated backend and frontend interaction system for card games, supporting multiple players with individual decks and a shared area.
It is built on a tightly integrated system of React components and Pydantic models, with data exchanged via JSON serialization.

The game supports internationalization via react-i18next, currently configured for Hebrew only.

## Backend Alignment

Frontend components are designed to work seamlessly with the backend models outlined in [backend gameplay](../backend/gameplay.md).

## Core Architecture

### Game Board Structure

The engine expects a JSON game board as defined in backend "server/gameplay/models.py -> GameBoard"

## Component\Models Hierarchy

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

## Game Stages

The game progresses through distinct stages during each player's turn. Upon completing all stages, the turn passes to the next player.

### Turn Stages

1. **Character Select** - Player chooses which character will act during this turn
