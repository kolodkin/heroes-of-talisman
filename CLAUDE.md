# Claude AI Documentation

This file contains concatenated documentation from .ai/ directory.

## .ai/frontend/engine.md

# Card Game Frontend Engine

A React-based UI engine for visualizing and interacting with card game states represented as JSON data structures.

## Overview

This frontend engine provides a complete visualization system for card games featuring multiple players, each with their own card decks, plus a shared drawn cards area. The system renders game state from JSON data and provides interactive components for gameplay.

## Core Architecture

### Game State Structure

The engine expects a JSON game state with the following structure:

```json
{
  "gameId": "string",
  "currentTurn": "playerId",
  "status": "waiting|playing|finished",
  "players": [
    {
      "id": "string",
      "name": "string",
      "position": "number",
      "decks": {
        "hand": {
          "cards": [],
          "maxSize": "number",
          "visible": "boolean"
        },
        "draw": {
          "cards": [],
          "faceDown": "boolean"
        },
        "discard": {
          "cards": []
        }
      }
    }
  ],
  "sharedArea": {
    "drawnCards": {
      "cards": []
    },
    "centerPile": {
      "cards": []
    }
  },
  "gameSettings": {
    "maxPlayers": "number",
    "deckSize": "number",
    "handLimit": "number"
  }
}
```

### Card Data Structure

```json
{
  "id": "string",
  "suit": "hearts|diamonds|clubs|spades",
  "rank": "A|2|3|4|5|6|7|8|9|10|J|Q|K",
  "value": "number",
  "faceUp": "boolean",
  "selected": "boolean",
  "metadata": {
    "playable": "boolean",
    "highlighted": "boolean",
    "customProperties": {}
  }
}
```

## Component Hierarchy

### GameBoard (Root Component)
- Manages overall game state
- Handles player turns and game flow
- Coordinates between all child components

### PlayerArea
- Renders individual player's game space
- Contains multiple DeckComponent instances
- Displays player information and status

### DeckComponent
- Renders a single deck of cards
- Handles card selection and interaction

### CardComponent
- Renders individual card visuals
- Manages card states (face up/down, selected, highlighted)
- Handles click events and animations

### SharedArea
- Displays common game elements
- Manages drawn cards deck
- Handles center pile and community cards

## Key Features

### Deck Management
- **Multiple Deck Types**: Hand, draw pile, discard pile, custom decks
- **Visibility Controls**: Face-up/face-down rendering
- **Size Limits**: Configurable maximum deck sizes

### Card Interactions
- **Selection System**: Single and multi-card selection
- **Hover Effects**: Visual feedback for interactive elements
- **Animation Support**: Smooth transitions for card movements

### Player Management
- **Multi-Player Support**: 2-8 players with configurable layouts
- **Turn Indicators**: Visual cues for active player
- **Individual Deck Areas**: Separated player spaces
- **Player Statistics**: Score, remaining cards, status

### Responsive Design
- **Adaptive Layouts**: Adjusts to different screen sizes
- **Scalable Components**: Cards and decks resize appropriately
- **Mobile Support**: Touch-friendly interactions
- **Accessibility**: Screen reader support

## Implementation Details

### State Management
```javascript
// Using React Context for global game state
const GameStateContext = createContext();

// Custom hook for accessing game state
const useGameState = () => {
  const context = useContext(GameStateContext);
  if (!context) {
    throw new Error('useGameState must be used within GameStateProvider');
  }
  return context;
};
```

### Card Rendering Logic
```javascript
// Card component with conditional rendering
const Card = ({ card, onClick }) => {
  const cardClass = `card ${card.faceUp ? 'face-up' : 'face-down'}
                     ${card.selected ? 'selected' : ''}
                     ${card.metadata?.highlighted ? 'highlighted' : ''}`;

  return (
    <div
      className={cardClass}
      onClick={() => onClick(card)}
    >
      {card.faceUp ? <CardFace card={card} /> : <CardBack />}
    </div>
  );
};
```

## Styling System

### CSS Architecture
- **BEM Methodology**: Block-Element-Modifier naming
- **CSS Custom Properties**: Theme variables for easy customization
- **Responsive Breakpoints**: Mobile-first responsive design
- **Animation Classes**: Reusable transition effects

### Theme Configuration
```css
:root {
  --card-width: 80px;
  --card-height: 112px;
  --card-border-radius: 8px;
  --deck-spacing: 16px;
  --player-area-padding: 24px;
  --primary-color: #2563eb;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --warning-color: #f59e0b;
}
```

## API Integration

### Game State Updates
```javascript
// WebSocket connection for real-time updates
const useGameSocket = (gameId) => {
  const [socket, setSocket] = useState(null);
  const [gameState, setGameState] = useState(null);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:3001/game/${gameId}`);

    ws.onmessage = (event) => {
      const update = JSON.parse(event.data);
      setGameState(update);
    };

    setSocket(ws);
    return () => ws.close();
  }, [gameId]);

  return { socket, gameState };
};
```

### Action Dispatching
```javascript
// Send player actions to game server
const useGameActions = (socket) => {
  const sendAction = (action) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(action));
    }
  };

  return {
    drawCard: (playerId) => sendAction({ type: 'DRAW_CARD', playerId }),
    playCard: (playerId, cardId, targetDeck) =>
      sendAction({ type: 'PLAY_CARD', playerId, cardId, targetDeck }),
    selectCard: (playerId, cardId) =>
      sendAction({ type: 'SELECT_CARD', playerId, cardId })
  };
};
```

## Performance Optimizations

### Rendering Optimizations
- **React.memo**: Prevent unnecessary re-renders
- **useMemo**: Cache expensive calculations
- **Virtual Scrolling**: Handle large numbers of cards
- **Lazy Loading**: Load card assets on demand

### Animation Performance
- **CSS Transforms**: Hardware-accelerated animations

## Testing Strategy

### End-to-End Tests (Playwright)
- Complete game flow from start to finish
- Multi-player interactions and turn-based gameplay
- Card selection and click functionality
- WebSocket connection handling and real-time updates
- Cross-browser compatibility testing
- Mobile device interaction testing
- Visual regression testing with screenshots
- Accessibility compliance validation
- Error scenarios and recovery flows

## Deployment Considerations

### Build Configuration
- **Code Splitting**: Lazy load non-critical components
- **Asset Optimization**: Compress card images and icons
- **Bundle Analysis**: Monitor and optimize bundle size
- **Progressive Loading**: Critical CSS inline, defer non-critical

## Dependencies

### Core Dependencies
- React 18+
- Styled Components or CSS Modules
- WebSocket client library
- Animation library (Framer Motion recommended)

### Development Dependencies
- Playwright for end-to-end testing
- ESLint and Prettier for code quality

---

## .ai/backend/actions.md

# Server Action Design

The server's action layer organizes game mutations into small, focused
classes. Each action is invoked with the current user and `GameModel`
state and returns the updated game after running.

## Core Components

- **`Action` base class**: provides convenience accessors for game
  properties (players, stage, deck) and the `assert_stage` helper to
  validate that an action is executed in the correct phase.
- **Connection actions** (`ConnectAction`, `LeaveAction`,
  `DisconnectAction`): manage player lifecycle by connecting players,
  removing them from the game, or marking them as disconnected.
- **Character actions** (`CharacterSelectAction`, `CharacterSelectedAction`):
  handle the character selection phase and transition the game into the
  card draw phase once a character is chosen.
- **Card actions** (`CardDrawAction`, `CardSelectAction`): control drawing
  and selecting cards, maintaining the deck and moving play into the
  skill usage stage.
- **Models**: Pydantic models (`GameModel`, `PlayerModel`, `CharacterModel`)
  describe the game state and enforce structure and types.

## Workflow

1. An action instance is created with a user identifier and the current
   `GameModel`.
2. The client-provided parameters are passed to the action's `run`
   method.
3. The action updates the `GameModel` and returns it for broadcasting to
   other players.

## Error Handling

- `GameException` represents general server-side errors.
- `ReportedException` indicates errors that should be surfaced to the
  client, such as invalid stages or missing resources.

## Extending Actions

To implement a new action, subclass `Action` and implement the `run`
method. Use `assert_stage` to ensure the action only executes during the
appropriate game phase and update the `GameModel` as needed.


# Server Actions

Checklist of actions implemented in the server's action layer and the
class responsible for handling each action.

- [x] `connect` – add a player to the game (`ConnectAction`)
- [x] `leave` – remove a player from the game (`LeaveAction`)
- [x] `disconnect` – mark a player as disconnected (`DisconnectAction`)
- [x] `character_select` – stage where the player chooses a character (`CharacterSelectAction`)
- [x] `character_selected` – confirm character selection and move to card draw (`CharacterSelectedAction`)
- [x] `card_draw` – prompt the player to draw a card (`CardDrawAction`)
- [x] `card_select` – resolve the drawn card and advance to skill use (`CardSelectAction`)


---
