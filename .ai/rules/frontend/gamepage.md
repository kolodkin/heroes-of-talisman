# Frontend - Game Page

A React-based UI engine for visualizing and interacting with card game states represented as JSON data structures.

## Overview

This frontend engine provides a complete visualization system for card games featuring multiple players, each with their own card decks, plus a shared area. The system renders game state from JSON data and provides interactive components for gameplay.

## Core Architecture

### Game State Structure

The engine expects a JSON game state as defined in backend "server/action/models.py -> GameModel"

## Component Hierarchy

### GameBoard (Root Component)

- Manages overall game state
- Handles player turns and game flow
- Coordinates between all child components
- Manages SharedArea and PlayerHands

### SharedArea

- Displays common game elements
- Manages drawn cards deck
- Handles center pile and community cards

### PlayerHand

- Renders the cards and character(s) for a single player
- Shows player's hand, character stats, and any status effects
- Highlights if it's the player's turn or if the player is disconnected
- Supports interaction with cards in hand (e.g., selection, play)

### DeckComponent

- Renders a single deck of cards
- Supports different layouts (stack, grid)
- Handles card selection and interaction

### CardComponent

- Renders individual card visuals
- Manages card states (face up/down, selected, highlighted)
- Handles click events and animations

## Key Features

### Deck Management

- **Flexible Layouts**: Stack, grid arrangement
- **Visibility Controls**: Face-up/face-down rendering

### Card Interactions

- **Selection System**: Single and multi-card selection
- **Hover Effects**: Visual feedback for interactive elements
- **Animation Support**: Smooth transitions for card movements

### Player Management

- **Multi-Player Support**: 2-8 players with configurable layouts
- **Turn Indicators**: Visual cues for active player
- **Player Statistics**: Score, remaining cards, status

### Responsive Design

- **Adaptive Layouts**: Adjusts to different screen sizes
- **Scalable Components**: Cards and decks resize appropriately
- **Mobile Support**: Touch-friendly interactions
- **Accessibility**: Screen reader support and keyboard navigation

## Implementation Details

### Deck Layout Algorithms

- **Stack Layout**: Cards positioned with slight offsets
- **Grid Layout**: Cards in rows/columns with consistent spacing

## State and API Integration

Game State and API interactions are handled within the 'src/components/Game.jsx' component.
