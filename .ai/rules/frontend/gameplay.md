# Frontend - Game Play

A React-based UI engine for visualizing and interacting with card game states represented as JSON data structures.

## Overview

This frontend engine provides a complete visualization system for card games featuring multiple players, each with their own card decks, plus a shared area. The system renders game state from JSON data and provides interactive components for gameplay.

## Backend Alignment

Frontend components are designed to work seamlessly with the backend models outlined in [backend gameplay](../backend/gameplay.md).

## Core Architecture

### Game State Structure

The engine expects a JSON game state as defined in backend "server/action/models.py -> GameBoard"

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
- When a deck is marked as active, it indicates that the deck is currently involved in the playing player's turn.

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

### Zoom, Pan and Zoom Modes

The game is presented from a top-down perspective, with the entire GameBoard always rendered and visible. Users can adjust their view by zooming in or out using the mouse scroll wheel, and can pan across the board by dragging while holding the right mouse button. Both zooming and panning are achieved through CSS3 transformations.

Store the user's current zoom and pan settings for the game board in local storage, and automatically retrieve and apply these settings when the GameHandler component initializes.

The interface provides four zoom preset modes, each accessible via a specific keyboard shortcut:

- Pressing '1' triggers Full View, resetting zoom and pan to display the entire game board (default).
- Pressing '2' activates Hand Zoom, centering and zooming in on the player's hand area.
- Pressing '3' enables Hand & Shared Zoom, adjusting the view to show both the player's hand and the shared area.
- Pressing '4' selects Active Zoom, focusing the view on the decks currently involved in the active player's turn.

### Multiplayer Layout

- **Center-focused Design**: SharedArea is always positioned in the center of the game board
- **Player Arrangement**: PlayerHands are arranged around the SharedArea as follows
  - User's PlayerHand is always positioned at the bottom
  - Second player is always positioned on top
  - Third player is always positioned on the left
  - Fourth player is always positioned on the right
  - For five or more players, continue positioning additional PlayerHands in the following repeating order: top, left, right, bottom, and so on, cycling through these positions as needed.
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

Game State and API interactions are handled within the 'src/components/GameHandler.jsx' component wrapping 'src/components/Game.jsx'
