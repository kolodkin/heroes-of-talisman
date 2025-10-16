# FrontEnd - GamePlay

A React-based UI engine for visualizing and interacting with card game states represented as JSON data structures.

related specs:

- [gameplay spec](/specs/gameplay_spec.md)
- [gameplay backend spec](/server/gameplay/gameplay_backend.md)

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

### RTL/LTR Layout

The application supports both RTL (Hebrew) and LTR layouts using CSS logical properties:

- **Avoid**: `left`, `right`, `margin-left`, `margin-right`, `padding-left`, `padding-right`
- **Use Instead**:
  - `inline-start` / `inline-end` for horizontal positioning
  - `margin-inline-start` / `margin-inline-end` for margins
  - `padding-inline-start` / `padding-inline-end` for padding
  - `inset-inline-start` / `inset-inline-end` for absolute positioning
- **Naming Convention**: Use `start` and `end` in class/variable names (e.g., `startGroup`, `endGroup`) instead of `left` and `right`
- **Flexbox**: Automatically handles direction - items flow according to text direction
- **Why**: Logical properties automatically adapt to text direction, making the code direction-agnostic

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
3. SharedArea renders the appropriate stage component (e.g., StageCharacterSelect, StageOpponentSelection, Battle)
4. Stage component handles user interactions and sends actions to backend

**Current Stage Components:**

- **StageCharacterSelect** (`character_select` stage): Player selects their character
  - Displays player's characters
  - Actions: `character_press` (highlight), `character_select` (confirm)
  - Transitions to: `opponent_selection`

- **StageOpponentSelection** (`opponent_selection` stage): Player selects opponent and their character
  - Displays all opponents with their characters (starting minimized)
  - **Opponent Filtering**: Opponents are filtered based on `gamePlay.active.player` (the active player), not the viewer
    - All players see the same opponent selection menu
    - The active player (whose turn it is) is excluded from the opponents list
  - Players can be expanded to see full character details
  - Actions: `opponent_press` (highlight selection), `opponent_select` (confirm selection)
  - Transitions to: `battle`

- **StageBattle** (`battle` stage): Displays the battle between current player and opponent
  - **Layout**: Two vertically aligned sections
    - **Player section**: Shows current player (`gamePlay.active.player`), their selected character (`gamePlay.active.character`), and dice/roll button
    - **Opponent section**: Shows opponent player (`gamePlay.opponent.player`), their character (`gamePlay.opponent.character`), and dice/roll button
  - **Dice Roll Flow**:
    - Initially, dice values are not set; roll buttons displayed instead of dice
    - Active player clicks roll → `active_player_roll` action → sets `gamePlay.active.dice_roll` (list) → dice shown after re-render
    - Opponent clicks roll → `opponent_roll` action → sets `gamePlay.opponent.dice_roll` (list) → dice shown after re-render
    - **Note**: Opponent roll button has `pointer-events` enabled (non-active players can interact)
    - Number of dice rolled is based on character's `dice` value
  - **Score Display**:
    - After both players roll, scores are calculated: `sum(dice_roll) + (character.attack || 0)`
    - Score displayed next to dice for each participant
  - **Winner Effect**:
    - Winner (higher score) gets golden badge with pulsing animation
    - Winner's row has highlighted background
  - **Draw Handling**:
    - When both players roll and scores are equal (draw), no winner badge is shown
    - **Reroll Button** appears instead of continue button
    - Only active player can click reroll button
    - Invokes `action_reroll` action → resets both players' dice rolls → returns to initial battle state
    - Players can re-roll until there is a winner
  - **Continue Button**:
    - Appears after both players have rolled AND there is a winner
    - Only active player can click
    - Invokes `battle_end` action → reduces loser's health by 1 → transitions to `character_select` stage with next player (circular rotation) as new active player
  - All connected players see synchronized battle state
  - Actions: `active_player_roll`, `opponent_roll`, `action_reroll`, `battle_end`

# Key Components

## Navbar

- Home button (routes to '/')
- Game name
- Username
- Current stage name (translated)
- Current playing player
- Game title (at end)
- **Active Player Indicator**: White outline around navbar when current user is the active player

## Player

- The status and cards for a single player
- Shows player's hand, stats, and any status effects
- Highlights if it's the player's turn or if the player is disconnected
- Supports interaction with cards in hand (e.g., selection, play)
- **Minimizable**: Each player card can be collapsed using +/- toggle button
  - When expanded: Shows full character cards with all details
  - When minimized: Shows only character names and levels in a compact list

### Dead Characters

Characters with `is_alive=false` (health = 0) should be visually distinguished and non-interactive:

- **Visual State**: Dead characters should be grayed out to indicate they are no longer available
- **Disabled State**: Dead characters should be disabled and non-clickable
- **Applies To**:
  - Character selection stage (player's own characters)
  - Opponent selection stage (opponent's characters)

## SharedArea

- Dynamically renders stage-specific components based on `gamePlay.stage`
- Acts as the central game area where turn actions occur
- Contains stage components: CharacterSelect, OpponentSelection, Battle, etc.
- **Scrolling**: Uses `overflow-y: auto` to prevent content from escaping the SharedArea bounds
  - Content that exceeds the SharedArea height will be scrollable
  - Ensures the layout remains constrained within the viewport
- **Active Player Interaction**:
  - Only the active player (`gamePlay.active.player`) can interact with UI elements in SharedArea
  - Non-active players see the SharedArea with `pointer-events: none` to prevent all interactions
  - Stage components also receive `active` prop as defensive coding for programmatic checks
