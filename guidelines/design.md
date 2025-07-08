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

- Each service should include a healthcheck configuration
- Service port numbers should be defined in .env with fallback to standard ports

## API Design

- All endpoints start with `/api/<topic>`
- `/api` returns a welcome text message.
- `/api/health` returns health check response.
- Other topics use dedicated `APIRouter` in separate files.


# Frontend

## General

- all source files must include a trailing newline character

## Technology Stack

- **npm** as package manager
- **vite** as build tool and development server
- **React** for rendering
- **React Router** for routing
- **TailwindCSS** for styling: [https://tailwindcss.com](https://tailwindcss.com)
- **Web Test Runner** for testing: [Test Runner Docs](https://modern-web.dev/docs/test-runner/overview/)
