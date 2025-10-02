# FrontEnd - GamePlay

A React-based UI engine for visualizing and interacting with card game states represented as JSON data structures.

related specs:

- [gameplay spec](/specs/gameplay.md)
- [gameplay backend spec](/server/gameplay/gameplay.md)

## Overview

This frontend engine provides a complete visualization system for card games featuring multiple players, each with their own card decks, plus a shared area. The system renders game state from JSON data and provides interactive components for gameplay.

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

### Multiplayer Layout

- **GamePlay Arrangement**: Players are arranged before shared area (left for ltr, right for rtl)
- **Spatial Awareness**: Layout provides clear visual hierarchy of game elements
- **Consistent Orientation**: Maintains the same arrangement regardless of game state

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

Game State and API interactions are handled within the [GameHandler](./GameHandler.jsx) component wrapping [GamePlay](./GamePlay.jsx) Component.

# Key Compoentns

## Player

- The status and cards for a single player
- Shows player's hand, stats, and any status effects
- Highlights if it's the player's turn or if the player is disconnected
- Supports interaction with cards in hand (e.g., selection, play)
