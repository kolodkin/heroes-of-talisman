# Homepage

Entry point for the game at `/`. Allows users to create, search, and join games.

## Features

- **Username input** - Persisted to localStorage
- **Game search** - Filters games list by prefix match (debounced 300ms)
- **Pagination** - Shows 5 results, "Load more" button for additional results
- **Create game** - Add new game via input + button
- **Join game** - Click game name to navigate to `/games/{gameName}/{username}`
- **Delete game** - Remove games from list

## API Endpoints

| Endpoint            | Method | Description                  |
| ------------------- | ------ | ---------------------------- |
| `/api/games/`       | GET    | List all games               |
| `/api/games/`       | POST   | Create new game              |
| `/api/games/{name}` | DELETE | Delete game                  |
| `/api/games/search` | GET    | Search games with pagination |

### Search Parameters

- `q` - Search query (prefix match, whitespace trimmed)
- `offset` - Skip N results (default: 0)
- `limit` - Max results (default: 5, max: 50)

## Component

`src/components/HomePage.jsx` with `HomePage.module.css`

## Tests

E2E tests in `e2e/home.spec.js` cover:

- Username validation (empty, whitespace, valid)
- Game filtering and load more
- No results message
- Query reset behavior
- Clear search
