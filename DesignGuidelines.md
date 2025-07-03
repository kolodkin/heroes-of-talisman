# Turn Based Card Games – Webservice Design Guidelines

## Backend

### Technology Stack

- Python with **FastAPI**
- **PostgreSQL** using **SQLModel** and **Alembic** for migrations
- Tested with **pytest** and `TestClient`\
  [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)

---

## Database

### Tables & Models

1. **users**

   - `email`: str
   - `password`: str
   - `last_log_in`: datetime
   - `created_at`: datetime

2. **games**

   - `id`: str
   - `name`: str
   - `data`: jsonb
   - `last_updated`: datetime
   - `created`: datetime

---

## Game Engine

- Implemented as a Python class that manages game logic.

- Constructor:

  ```python
  def __init__(self, game: Game, user: str)
  ```

  where `Game` is a **Pydantic** model.

- Execution method:

  ```python
  def execute(self, action: str, **kwargs)
  ```

  Logic:

  ```python
  action_cls = ACTIONS[action]
  self.game = action_cls(game, user).execute(**kwargs)
  ```

  where `ACTIONS` is a dictionary of available action classes (e.g., `Connect(Action)`).

---

## API Design

- All endpoints start with `/api/<topic>`
- `/api` returns a welcome text message.
- `/api/health` returns health check response.
- Other topics use dedicated `APIRouter` in separate files.

### Auth API

- JWT-based auth per [FastAPI Security JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

---

## WebSocket

- Endpoint: `/ws/game/<gameid>/<userid>`
- Each logged-in user uses a separate WebSocket connection.
- Workflow:
  - Receive actions from UI.
  - Acquire Redis-based lock.
  - Update the `games` table in DB.
  - Call `connect` on socket open.
  - Call `disconnect` on socket close.

---

## Frontend

### Design Principles

- **npm** as build tool
- **Lit** for rendering: [https://lit.dev](https://lit.dev)
- **Lit Router** for routing
- **lit preact-signals** for state management
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

