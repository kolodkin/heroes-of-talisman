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

- **Multiple Deck Types**: Hand, draw pile, discard pile, custom decks
- **Flexible Layouts**: Stack, fan spread, grid arrangement
- **Visibility Controls**: Face-up/face-down rendering
- **Size Limits**: Configurable maximum deck sizes

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

### State Management

```javascript
// Using React Context for global game state
const GameStateContext = createContext();

// Custom hook for accessing game state
const useGameState = () => {
  const context = useContext(GameStateContext);
  if (!context) {
    throw new Error("useGameState must be used within GameStateProvider");
  }
  return context;
};
```

### Card Rendering Logic

```javascript
// Card component with conditional rendering
const Card = ({ card, onClick }) => {
  const cardClass = `card ${card.faceUp ? "face-up" : "face-down"}
                     ${card.selected ? "selected" : ""}
                     ${card.metadata?.highlighted ? "highlighted" : ""}`;

  return (
    <div className={cardClass} onClick={() => onClick(card)}>
      {card.faceUp ? <CardFace card={card} /> : <CardBack />}
    </div>
  );
};
```

### Deck Layout Algorithms

- **Stack Layout**: Cards positioned with slight offsets
- **Grid Layout**: Cards in rows/columns with consistent spacing

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
    drawCard: (playerId) => sendAction({ type: "DRAW_CARD", playerId }),
    playCard: (playerId, cardId, targetDeck) => sendAction({ type: "PLAY_CARD", playerId, cardId, targetDeck }),
    selectCard: (playerId, cardId) => sendAction({ type: "SELECT_CARD", playerId, cardId }),
  };
};
```

### Development Dependencies

- Playwright for end-to-end testing
