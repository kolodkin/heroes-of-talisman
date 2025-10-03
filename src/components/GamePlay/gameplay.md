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

### Multi-Language Support

- **i18next Integration**: All UI text is managed via `react-i18next`
- **Current Languages**: Hebrew only (for development simplicity)
- **Configuration**: Centralized in `src/i18n.js` with translation resources
- **Usage Pattern**:
  - Components use the `useTranslation` hook to access translations
  - Translation keys use dot notation (e.g., `t('errors.connection_failed')`)
  - Interpolation supported for dynamic values (e.g., `t('errors.game_not_found', { gamename })`)
- **Direction Support**: RTL handled via `t('direction')`

## Implementation Details

### Deck Layout Algorithms

- **Stack Layout**: Cards positioned with slight offsets
- **Grid Layout**: Cards in rows/columns with consistent spacing

## State and API Integration

Game State and API interactions are handled within the [GameHandler](./GameHandler.jsx) component wrapping [GamePlay](./GamePlay.jsx) Component.

## Interactive

Any player action that updates the gameplay state triggers a re-render for all connected players, ensuring synchronized game state across all clients.

**Re-render Flow (onmessage in GameHandler.jsx):**

1. WebSocket receives `game_update` event in `onmessage()` callback
2. Game state is updated via `setGamePlay(data.game)`
3. React automatically re-renders all components that depend on `gamePlay` state
4. All connected players see the updated game state simultaneously

## Stage Components

Each game stage has its own dedicated component that renders the appropriate UI for that stage. The SharedArea uses a switch/case statement to render the relevant stage component based on the current game stage.

**Stage Rendering Flow:**

1. GamePlay receives the game state including current stage
2. SharedArea evaluates `gamePlay.stage`
3. SharedArea renders the appropriate stage component (e.g., CharacterSelect, Movement, Combat)
4. Stage component handles user interactions and sends actions to backend

# Key Components

## Player

- The status and cards for a single player
- Shows player's hand, stats, and any status effects
- Highlights if it's the player's turn or if the player is disconnected
- Supports interaction with cards in hand (e.g., selection, play)

## SharedArea

- Dynamically renders stage-specific components based on `gamePlay.stage`
- Acts as the central game area where turn actions occur
- Contains stage components: CharacterSelect, Movement, Combat, etc.
