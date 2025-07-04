Design Guidelines
=================

# Backend

## General
- remove unused imports to keep code clean
- organize imports in the following groups, separated by a blank line:
  1. Python standard library imports (e.g. os, datetime, typing)
  2. Third-party package imports (e.g. fastapi, sqlmodel, redis)
  3. Local application imports (e.g. from server.models)
  4. Module-level imports (e.g. from .utils)


## Technology Stack

- Backend built with **FastAPI** framework in Python
- Database using **PostgreSQL** with **SQLModel** ORM and **Alembic** migration tool
- Service orchestration with docker compose
- JWT-based auth per [FastAPI Security JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- pre-commit used for keeping code clean

### Docker Compose
ˆˆ
- Each service should include a healthcheck configuration
- Service port numbers should be defined in .env with fallback to standard ports

## API Design

- All endpoints start with `/api/<topic>`
- `/api` returns a welcome text message.
- `/api/health` returns health check response.
- Other topics use dedicated `APIRouter` in separate files.

---

## WebSocket

- Endpoint: `/ws/game/<gameid>/<userid>`
- Each logged-in user uses a separate WebSocket connection.
- Workflow:
  - Client sends action via WebSocket
  - Server gets game with for_update flag to avoid mutex on game update.
  - Game engine processes action and returns updated game state
  - Server persists new game state to database
  - Server broadcasts state change to connected clients

# Frontend

## Technology Stack

- **npm** as package manager
- **vite** as build tool and development server
- **Lit** for rendering: [https://lit.dev](https://lit.dev)
- **Lit Router** for routing
- **lit preact-signals** for state management [@lit-labs/preact-signals](https://www.npmjs.com/package/@lit-labs/preact-signals)
- **TailwindCSS** for styling: [https://tailwindcss.com](https://tailwindcss.com)
- **Web Test Runner** for testing: [Test Runner Docs](https://modern-web.dev/docs/test-runner/overview/)
- Each SVG icon is wrapped in a Lit component and bundled in `icons.js`

---

## Routes

- `/`: Home page

  - Redirects to `/login` if user not logged in
  - Full screen (`100vh`, `100vw`)

- `/login`: Login / Create Account

  - Email & password form

- `/games/<game-id>`: Game Page

  - Full screen (`100vh`, `100vw`)
  - On load, connect via WebSocket
  - Any UI action (except mouse move) sends action to socket
  - Game state is updated and UI is re-rendered

---

## Actions Example

- `connect`: Adds user to `game.users` as connected
- `disconnect`: Marks user as disconnected in `game.users`
