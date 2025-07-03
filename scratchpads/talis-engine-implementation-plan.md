# Talis Engine BaseLine Implementation Plan

## Research Summary (15/15 iterations used)

**Confidence**: HIGH - Found exact patterns and comprehensive documentation for all technologies
**Key Findings**: Repository is nearly empty, requires complete implementation following detailed design guidelines

- **Dependencies**: FastAPI, SQLModel, Alembic, Redis, pytest, Lit, TailwindCSS, lit-preact-signals
- **Architecture**: FastAPI backend with PostgreSQL, Redis state management, Lit frontend
- **Tech Stack**: Python 3.12+, FastAPI, SQLModel, PostgreSQL, Redis, Lit, TypeScript, TailwindCSS
- **Patterns**: WebSocket authentication with JWT, Redis expiring locks, lit-preact-signals global state

**Questions Asked** [3/3 REQUIRED]:

1. "Should WebSocket authentication use JWT tokens passed as query parameters, headers, or cookies?" → "stick purely to JWT for both REST API and WebSocket connections"
2. "Which Redis locking approach do you prefer - simple expiring locks for speed, or robust lease locks with heartbeats?" → "Simple expiring locks for speed"
3. "Should we use lit-preact-signals as the global state store or implement reactive controllers?" → "preact-signals as the global state store that all game components subscribe to"

## POC Implementation Path Status: »» **NEXT PHASE TO IMPLEMENT**

### Unit 1: Project Foundation & Dependencies [Backend structure setup] Status: ⚪ **NOT STARTED**

**Tags**:
- [DEMOABLE] - Can verify FastAPI server starts and dependencies work

**Complexity**: SMALL (3 points)
**Purpose**: Establish basic backend structure with all required dependencies

**Changes**

- [ ] Update pyproject.toml with complete dependency list (FastAPI, SQLModel, Alembic, Redis, pytest, WebSockets)
- [ ] Create server/main.py with basic FastAPI app and health endpoints
- [ ] Create server/__init__.py and basic module structure
- [ ] Update docker-compose.yaml to include Redis service
- [ ] Create .env.example with environment variables

**Success Criteria**

- [ ] FastAPI server starts without errors
- [ ] Health check endpoint returns 200
- [ ] All dependencies install successfully
- [ ] Docker compose brings up PostgreSQL and Redis

**Testing**

- [ ] Test FastAPI server startup
- [ ] Test `/api/health` endpoint responds correctly

**Implementation Notes**

- Follow FastAPI tutorial patterns for basic setup
- Use existing docker-compose.yaml PostgreSQL configuration
- Add Redis service following same pattern

### Unit 2: Database Models & Migration Setup [SQLModel foundation] Status: ⚪ **NOT STARTED**

**Complexity**: SMALL (3 points)
**Purpose**: Create database models and migration system following design guidelines

**Changes**

- [ ] Create server/models.py with User and Game SQLModel classes
- [ ] Set up Alembic configuration in server/alembic/
- [ ] Create initial migration with users and games tables
- [ ] Create database connection and session management
- [ ] Add database URL configuration

**Success Criteria**

- [ ] Database models match design specification (users: email, password, last_log_in, created_at)
- [ ] Games table created with id, name, data (jsonb), last_updated, created
- [ ] Alembic migrations run successfully
- [ ] Database connection established

**Testing**

- [ ] Test model creation and validation
- [ ] Test migration up/down operations

**Implementation Notes**

- Follow SQLModel patterns from research
- Use PostgreSQL jsonb for game.data field
- Set up proper foreign key relationships

### Unit 3: JWT Authentication System [Security foundation] Status: ⚪ **NOT STARTED**

**Complexity**: STANDARD (4 points)
**Purpose**: Implement JWT-based authentication for both REST and WebSocket

**Changes**

- [ ] Create server/auth.py with JWT token generation and validation
- [ ] Implement password hashing with passlib
- [ ] Create login/register endpoints in server/routers/auth.py
- [ ] Add JWT dependency for protected routes
- [ ] Create WebSocket JWT authentication dependency

**Success Criteria**

- [ ] Users can register with email/password
- [ ] Login returns valid JWT token
- [ ] Protected endpoints require valid JWT
- [ ] WebSocket connections authenticate with JWT

**Testing**

- [ ] Test user registration and login
- [ ] Test JWT token validation
- [ ] Test protected endpoint access
- [ ] Test WebSocket authentication with JWT

**Implementation Notes**

- Follow FastAPI Security JWT documentation patterns
- Use JWT tokens for both REST API and WebSocket connections
- Implement secure password hashing

## 🚀 Demoable Checkpoint: Authentication Working

Users can register, login, and access protected endpoints with JWT tokens.

## MVP Implementation Path Status: ⚪ **NOT STARTED**

### Unit 4: API Router Structure [REST API foundation] Status: ⚪ **NOT STARTED**

**Complexity**: SMALL (2 points)
**Purpose**: Create API router structure following design guidelines

**Changes**

- [ ] Create server/routers/__init__.py
- [ ] Set up `/api` welcome endpoint returning text message
- [ ] Update `/api/health` endpoint
- [ ] Create router structure for future endpoints
- [ ] Integrate routers into main FastAPI app

**Success Criteria**

- [ ] `/api` returns welcome text message
- [ ] `/api/health` returns health check response
- [ ] Router structure ready for expansion

**Testing**

- [ ] Test all API endpoints respond correctly
- [ ] Test router integration with main app

**Implementation Notes**

- Use FastAPI APIRouter for modular organization
- Follow `/api/<topic>` pattern from guidelines

### Unit 5: Game Engine Core [Python class with action system] Status: ⚪ **NOT STARTED**

**Complexity**: STANDARD (5 points)
**Purpose**: Implement game engine as Python class with action execution system

**Changes**

- [ ] Create server/game_engine.py with GameEngine class
- [ ] Implement constructor: `__init__(self, game: Game, user: str)`
- [ ] Create execute method: `execute(self, action: str, **kwargs)`
- [ ] Create ACTIONS dictionary with Connect/Disconnect actions
- [ ] Implement Action base class and Connect/Disconnect action classes

**Success Criteria**

- [ ] GameEngine can be instantiated with Game model and user
- [ ] Actions can be executed via execute() method
- [ ] Connect action adds user to game.users as connected
- [ ] Disconnect action marks user as disconnected

**Testing**

- [ ] Test GameEngine instantiation
- [ ] Test Connect action execution
- [ ] Test Disconnect action execution
- [ ] Test action system extensibility

**Implementation Notes**

- Use Pydantic models for game state validation
- Design action classes for easy extension
- Store game state in PostgreSQL jsonb field

### Unit 6: WebSocket Game Endpoints [Real-time communication] Status: ⚪ **NOT STARTED**

**Complexity**: STANDARD (5 points)
**Purpose**: Implement WebSocket endpoints for real-time game communication

**Changes**

- [ ] Create server/websocket.py with WebSocket manager
- [ ] Implement `/ws/game/<gameid>/<userid>` endpoint
- [ ] Add Redis-based locking for game state updates
- [ ] Integrate JWT authentication with WebSocket connections
- [ ] Implement connect/disconnect action calls

**Success Criteria**

- [ ] WebSocket connections authenticate with JWT
- [ ] Game state updates use Redis locks
- [ ] Connect/disconnect actions called automatically
- [ ] Multiple clients can connect to same game

**Testing**

- [ ] Test WebSocket connection with JWT
- [ ] Test game state locking mechanism
- [ ] Test multiple clients in same game
- [ ] Test automatic connect/disconnect actions

**Implementation Notes**

- Use simple expiring Redis locks for speed
- Follow FastAPI WebSocket authentication patterns
- Integrate with GameEngine for action execution

## 🚀 Demoable Checkpoint: Backend Game System

Complete backend with authentication, game engine, and WebSocket communication.

## Enhancement Implementation Path Status: ⚪ **NOT STARTED**

### Unit 7: Frontend Project Setup [Lit development environment] Status: ⚪ **NOT STARTED**

**Complexity**: SMALL (3 points)
**Purpose**: Set up frontend development environment with Lit and build tools

**Changes**

- [ ] Create package.json with npm build configuration
- [ ] Install Lit, Lit Router, lit-preact-signals, TailwindCSS
- [ ] Set up TypeScript configuration
- [ ] Create Web Test Runner configuration
- [ ] Set up build scripts and dev server

**Success Criteria**

- [ ] npm install completes successfully
- [ ] TypeScript compilation works
- [ ] TailwindCSS builds correctly
- [ ] Dev server serves frontend

**Testing**

- [ ] Test build process
- [ ] Test dev server startup

**Implementation Notes**

- Follow Lit development setup patterns
- Use modern build tools and TypeScript
- Configure TailwindCSS for styling

### Unit 8: Frontend Routing & Authentication [Navigation and login] Status: ⚪ **NOT STARTED**

**Complexity**: STANDARD (4 points)
**Purpose**: Implement frontend routing and authentication flow

**Changes**

- [ ] Create src/main.ts with Lit Router setup
- [ ] Implement routes: `/`, `/login`, `/games/<game-id>`
- [ ] Create login/register components
- [ ] Set up JWT token storage and management
- [ ] Implement protected route guards

**Success Criteria**

- [ ] Home route redirects to login if not authenticated
- [ ] Login/register forms work with backend API
- [ ] JWT tokens stored and used for API calls
- [ ] Protected routes require authentication

**Testing**

- [ ] Test routing navigation
- [ ] Test authentication flow
- [ ] Test protected route access

**Implementation Notes**

- Use Lit Router for client-side routing
- Implement full screen routes (100vh, 100vw)
- Store JWT tokens securely

### Unit 9: Game State Management [WebSocket integration] Status: ⚪ **NOT STARTED**

**Complexity**: STANDARD (5 points)
**Purpose**: Implement game state management with WebSocket and lit-preact-signals

**Changes**

- [ ] Create src/game-state.ts with lit-preact-signals setup
- [ ] Implement WebSocket connection management
- [ ] Create game state signals for reactive updates
- [ ] Set up automatic UI re-rendering on state changes
- [ ] Implement game action dispatching

**Success Criteria**

- [ ] WebSocket connects with JWT authentication
- [ ] Game state updates trigger UI re-renders
- [ ] UI actions send to WebSocket
- [ ] Game state synchronized across clients

**Testing**

- [ ] Test WebSocket connection and authentication
- [ ] Test state synchronization
- [ ] Test action dispatching
- [ ] Test multi-client synchronization

**Implementation Notes**

- Use lit-preact-signals as global state store
- Follow WebSocket integration patterns from research
- Ensure all UI actions (except mouse move) send to socket

## 🚀 Demoable Checkpoint: Full Game Platform

Complete turn-based card game platform with real-time multiplayer functionality.

## Polish Implementation Path Status: ⚪ **NOT STARTED**

### Unit 10: SVG Icon System [UI component library] Status: ⚪ **NOT STARTED**

**Complexity**: SMALL (2 points)
**Purpose**: Create SVG icon system as Lit components

**Changes**

- [ ] Create src/icons/ directory structure
- [ ] Wrap SVG icons in Lit components
- [ ] Create icons.js bundle
- [ ] Implement icon usage patterns
- [ ] Add TailwindCSS styling

**Success Criteria**

- [ ] SVG icons wrapped as Lit components
- [ ] Icons bundle properly in icons.js
- [ ] Icons render correctly in UI
- [ ] Consistent styling applied

**Testing**

- [ ] Test icon component rendering
- [ ] Test icon bundle creation

**Implementation Notes**

- Follow design guidelines for SVG icon wrapping
- Use TailwindCSS for consistent styling
- Create reusable icon component patterns

### Unit 11: Testing & Documentation [Production readiness] Status: ⚪ **NOT STARTED**

**Complexity**: SMALL (3 points)  
**Purpose**: Add comprehensive testing and documentation

**Changes**

- [ ] Set up pytest with TestClient for backend testing
- [ ] Configure Web Test Runner for frontend testing
- [ ] Add API endpoint tests
- [ ] Create component tests for Lit components
- [ ] Write basic documentation

**Success Criteria**

- [ ] Backend tests cover authentication and game engine
- [ ] Frontend tests cover components and routing
- [ ] All tests pass consistently
- [ ] Basic documentation complete

**Testing**

- [ ] Run full test suite
- [ ] Test coverage meets requirements

**Implementation Notes**

- Follow FastAPI testing patterns with TestClient
- Use Web Test Runner for modern frontend testing
- Focus on critical path testing

## 🚀 Demoable Checkpoint: Production-Ready Platform

Complete turn-based card game platform with testing, documentation, and production readiness. 