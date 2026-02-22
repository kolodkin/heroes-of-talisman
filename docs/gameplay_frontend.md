## FrontEnd - GamePlay

A React-based UI engine for visualizing and interacting with game states represented as JSON data structures.

related specs:

- [gameplay spec](/docs/gameplay_spec.md)
- [gameplay backend spec](/docs/gameplay_backend.md)

# Overview

This frontend engine provides a complete visualization system for the game, featuring multiple players with their characters, plus a shared area. The system renders game state from JSON data and provides interactive components for gameplay.

# Key Features

## Player Management

- **Multi-Player Support**: 2-8 players with configurable layouts
- **Minimum Players**: At least 2 players required for the game to start
- **Turn Indicators**: Visual cues for active player
- **Player Statistics**: Characters, status

## Multiplayer Layout

- **GamePlay Arrangement**: Players are arranged before shared area (left for ltr, right for rtl)
- **Spatial Awareness**: Layout provides clear visual hierarchy of game elements
- **Consistent Orientation**: Maintains the same arrangement regardless of game state

## Responsive Design

- **Adaptive Layouts**: Adjusts to different screen sizes
- **Scalable Components**: Components resize appropriately
- **Mobile Support**: Touch-friendly interactions
- **Accessibility**: Screen reader support and keyboard navigation

## Multi-Language Support

- **i18next Integration**: All UI text is managed via `react-i18next`
- **Current Languages**: Hebrew only (for development simplicity)
- **Configuration**: Centralized in `src/i18n.js` with translation resources
- **Usage Pattern**:
  - Components use the `useTranslation` hook to access translations
  - Translation keys use dot notation (e.g., `t('errors.connection_failed')`)
  - Interpolation supported for dynamic values (e.g., `t('errors.game_not_found', { gamename })`)
- **Direction Support**: Layout direction is determined by the i18n `direction` translation key (e.g., `t('direction')`), which is language-specific (`"rtl"` for Hebrew, `"ltr"` for English). Defaults to `"ltr"` when not specified.

## RTL/LTR Layout

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

# State and API Integration

Game State and API interactions are handled within the [GameHandler](./GameHandler.jsx) component wrapping [GamePlay](./GamePlay.jsx) Component.

# Interactive

Any player action that updates the gameplay state triggers a re-render for all connected players, ensuring synchronized game state across all clients.

**Re-render Flow (onmessage in GameHandler.jsx):**

1. WebSocket receives `game_update` event in `onmessage()` callback
2. Game state is updated via `setGamePlay(data.game)`
3. React automatically re-renders all components that depend on `gamePlay` state
4. All connected players see the updated game state simultaneously

# Stage Components

Each game stage has its own dedicated component that renders the appropriate UI for that stage. The SharedArea uses a switch/case statement to render the relevant stage component based on the current game stage.

**Stage Rendering Flow:**

1. GamePlay receives the game state including current stage
2. SharedArea evaluates `gamePlay.stage`
3. SharedArea renders the appropriate stage component (e.g., StageCharacterSelect, StageOpponentSelection, Battle)
4. Stage component handles user interactions and sends actions to backend

**Current Stage Components:**

- **StageCharacterSelect** (`character_select` stage): Player selects their character
  - Displays player's characters
  - Arrow keys cycle through available characters (alive, no skip_turn)
  - Actions: `character_press` (highlight), `character_select` (confirm)
  - Transitions to: `card_draw`

- **StageCardDraw** (`card_draw` stage): Player draws a card from the deck
  - Initially displays face-down `DeckCard` component
  - After draw action, displays `GameplayCard` with card details
  - Actions: `card_draw` (draw from deck), `card_select` (confirm selection)
  - Non-active players see disabled interactions
  - Transitions to: `ability_selection`

- **StageOpponentSelection** (`opponent_selection` stage): Player selects opponent and their character
  - Displays all opponents with their characters (starting minimized)
  - **Opponent Filtering**: Opponents are filtered based on `gamePlay.active.player` (the active player), not the viewer
    - All players see the same opponent selection menu
    - The active player (whose turn it is) is excluded from the opponents list
  - Players can be expanded to see full character details
  - Arrow keys cycle through all alive opponent characters across all opponents
  - Actions: `opponent_press` (highlight selection), `opponent_select` (confirm selection)
  - Transitions to: `battle`

- **StageBattle** (`battle` stage): Displays the battle between current player and opponent
  - **Layout**: Two vertically aligned sections
    - **Player section**: Shows current player (`gamePlay.active.player`), their selected character (`gamePlay.active.character`), and dice
    - **Opponent section**: Shows opponent player (`gamePlay.opponent.player`), their character (`gamePlay.opponent.character`), and dice
  - **Dice Roll Flow**:
    - Rolling is done via the main **action button** (not inline buttons), which shows "Roll Dice" text
    - The action button is enabled for the player who needs to roll next
    - Active player clicks roll → `active_player_roll` action → sets `gamePlay.active.dice_roll` (list) → dice shown after re-render
    - Opponent clicks roll → `opponent_roll` action → sets `gamePlay.opponent.dice_roll` (list) → dice shown after re-render
    - **Note**: Opponent roll button has `pointer-events: auto` override, allowing non-active players to click the action button when it's their turn to roll
    - Number of dice rolled is based on character's `dice` value
  - **Score Display**:
    - After both players roll, scores are displayed from `active.result.score` / `opponent.result.score` (calculated by backend)
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

- The status and characters for a single player
- Shows player's characters with stats and any status effects
- Highlights if it's the player's turn or if the player is disconnected
- **Three-state menu** (`playersMenuState`):
  - **Collapsed**: Entire players container hidden. A small expand arrow button appears as overlay in the shared area, below StatusIndicator. Default on mobile landscape.
  - **Minimized**: Header + compact player list (names and levels). Default on desktop.
  - **Expanded**: Header + full character cards with all details.
- **Header buttons** (when not collapsed): Collapse arrow (`<` in LTR / `>` in RTL) on the start side, expand/minimize toggle (`+`/`−`) on the end side.
- **Expand overlay button** (when collapsed): Arrow button (`>` in LTR / `<` in RTL) positioned in the shared area. Clicking it restores the menu to minimized state.

**Data Attributes:**

- `data-players-menu-state`: Current menu state on the game-play container - values: `"collapsed"`, `"minimized"`, `"expanded"`
- `data-player`: Player name identifier (used for selecting player cards in tests)
- `data-status`: Connection status - values: `"connected"`, `"disconnected"`

### Disconnected Players

When a player is disconnected (`player.status === "disconnected"`), a dark overlay with disconnected text can appear over their player card:

- **Visual Display**: Dark semi-transparent overlay (rgba(0, 0, 0, 0.7)) with centered disconnected text
- **Implementation**: Uses the reusable `Player` component that wraps player cards
- **Styling**: Overlay covers entire card content with centered muted text (#999)
- **Visibility Control**: The `Player` component accepts a `showDisconnected` prop (defaults to `false`)
  - **Players Menu**: `showDisconnected={true}` - overlay appears in both minimized and expanded views
  - **Other contexts** (e.g., opponent selection, battle view): `showDisconnected={false}` (default) - no overlay shown

## CharacterCard

Character cards represent individual characters belonging to players. Each character has stats (health, attack, dice) and can have abilities and effects applied to them.

**Data Model** (from backend):

- `level`: Character level (1 or 2). Higher levels have improved stats. See [Character Levels](/docs/gameplay_spec.md#character-levels) for stats per level.
- `health`: Current health points
- `max_health`: Maximum health points (varies by level)
- `dice`: Number of dice to roll in battle (varies by level)
- `attack`: Attack bonus value (varies by level)
- `effects`: List of active effects applied to this character (each effect has `source` ability name)
- `cards`: List of card names held by this character (e.g., `["metal_armor", "talisman"]`)
- `is_alive`: Stored boolean field (defaults to `true`, set to `false` when character dies in battle)
- `is_available`: Computed boolean field — `true` when character is alive and has no skip_turn effect. Used by frontend to determine selectable characters without recomputing availability logic

**Level Display:**

- Character level should be displayed prominently on the card
- Level changes (up or down) should be visually reflected immediately after state update

### Dead Characters

Characters with `is_alive=false` (health = 0) should be visually distinguished and non-interactive:

- **Visual State**: Dead characters should be grayed out to indicate they are no longer available
- **Disabled State**: Dead characters should be disabled and non-clickable
- **Applies To**:
  - Character selection stage (player's own characters)
  - Opponent selection stage (opponent's characters)

### Effects

Active effects applied to characters should be displayed visually on character cards. A 'has_effect' icon should be displayed in card top left as overlay (position: absolute, inset-inline-start: 0, top: 0 with some margin).

**Effect Visual Indicators:**

- **SkipTurnEffect**: Display skip/freeze icon
- **AttackBonusEffect**: Value added to attack stat, make attack text color blue
- **AttackNegBonusEffect**: Value subtracted from attack stat, make attack text color red
- **RerollDiceEffect**: Display reroll icon
- **DefenseBonusEffect**: Defense value applied (no separate icon, armor icon shown via card)

### Card Icons

Characters that hold cards display small icons in their stats row, based on `character.cards` list:

- **metal_armor**: ArmorIcon (shield image)
- **sacred_sord**: SwordIcon (sword image)
- **talisman**: TalismanIcon (dragon medallion image)

## AbilityCard

Displays a character ability with image, name, and description (`src/components/AbilityCard.jsx`).

**Props:**

- `ability` (object): Ability data with `name` property
- `isSelected` (boolean): Whether the ability is currently selected
- `onClick` (function): Click handler for selection
- `size` (string, default: `"normal"`): Card size - `"normal"` or `"small"`

**Data Attributes:**

- `data-ability`: Ability name (used for testing)

**Features:**

- Uses common card styles from `Card.module.css`
- Displays ability image from `/images/effects/{ability.name}.jpg`
- Shows translated ability name and description via i18next

## GameplayCard

Displays a game card with image, name, and description (`src/components/GameplayCard.jsx`).

**Props:**

- `cardName` (string): Card identifier
- `isSelected` (boolean): Whether the card is currently selected
- `onClick` (function): Click handler for selection
- `size` (string, default: `"normal"`): Card size - `"normal"` or `"small"`

**Data Attributes:**

- `data-card`: Card name (used for testing)

**Features:**

- Uses common card styles from `Card.module.css`
- Displays card image from `/images/cards/{cardName}.png`
- Shows translated card name and description via i18next

## DeckCard

Displays a face-down deck card for drawing (`src/components/DeckCard.jsx`).

**Props:**

- `onClick` (function): Click handler for drawing
- `size` (string, default: `"normal"`): Card size

**Data Attributes:**

- `data-deck-card`: Presence attribute for testing

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
- **Keyboard Shortcuts (Desktop)**:
  - Pressing **Enter** triggers the action button in the shared area, equivalent to clicking it
  - Pressing **Left/Right Arrow** keys navigates between selectable items in selection stages (character select, opponent select, ability opponent select)
    - **RTL-aware**: Arrow direction is flipped based on the i18n `direction` key. In RTL, ArrowLeft moves to the next item and ArrowRight moves to the previous item (opposite of LTR)
    - If no item is selected, pressing either arrow selects the first available item
    - Selection wraps around (last item → first, first item → last)
    - Only cycles through available (alive, no skip_turn) items
  - Only active on desktop viewports (min-width: 1024px) — disabled on mobile/tablet
  - Respects disabled state: does nothing when the action button is disabled or not rendered
- **Minimum Player Requirement**:
  - When there are less than 2 players in the game (regardless of connection status), SharedArea displays a grayed overlay
  - Overlay prevents any interaction until the minimum player count is reached

# Common Components

Reusable UI components shared across different parts of the game.

## Card

Common card styling (`Card.module.css`) used by `CharacterCard` and `AbilityCard` components for consistent visual appearance and selection states.

# Mobile Layout Considerations

The game is designed for landscape orientation on mobile devices. The horizontal row layout (players menu + shared area) is maintained across all screen sizes.

## Portrait Orientation Overlay

When a mobile device is in portrait mode (width < height), a full-screen overlay appears prompting the user to rotate their device to landscape mode:

- **Trigger**: `@media (max-width: 915px) and (orientation: portrait)`
- **Display**: Fixed overlay covering the entire viewport with dark background
- **Content**: Rotating phone icon with "rotate to play" message (translated)
- **Location**: `GamePlay.module.css` - `.portrait-overlay` class

## Landscape Mobile Adjustments

For mobile devices in landscape mode, the following adjustments are applied via media queries:

- **Trigger**: `@media (max-height: 500px) and (orientation: landscape)`
- **GamePlay Layout**:
  - Reduced padding and gaps
  - Smaller players container min-width
  - Smaller toggle buttons
- **Character Cards** (in `CharacterCard.module.css`):
  - Normal size cards (SharedArea): 80px images instead of 160px
  - Small size cards (Players menu): 50px images instead of 80px
  - Reduced font sizes and padding throughout

## Breakpoints Summary

| Condition                                      | Behavior                           |
| ---------------------------------------------- | ---------------------------------- |
| Portrait + mobile (max-width: 915px)           | Show "rotate to landscape" overlay |
| Landscape + short viewport (max-height: 500px) | Apply mobile-optimized sizes       |
| Desktop/Large screens                          | Standard desktop layout            |
