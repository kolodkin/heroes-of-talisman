# Frontend Implementation Plan

## Research Summary (8/15 iterations used)

**Confidence**: HIGH - Found clear patterns for Vite + Lit + TailwindCSS setup and Preact Signals integration
**Key Findings**: Modern frontend stack with FastAPI backend integration

- **Dependencies**: Vite, Lit 3.x, @preact/signals, @preact/signals-core, TailwindCSS v4, Vaadin Router
- **Architecture**: Vite dev server with native ES modules, Lit web components, centralized signals state
- **Tech Stack**: Vite + JavaScript + Lit + @preact/signals + TailwindCSS v4 + Vaadin Router
- **Patterns**: SignalWatcher mixin for component reactivity, centralized auth service with signals, sessionStorage for JWT tokens

**Questions Asked** [1/3]:
1. "I now understand your FastAPI backend with JWT auth at `/api/auth` endpoints. For the authentication service with signals, should I store the JWT token in localStorage, sessionStorage, or use a different approach?" → "sessionStorage"

## POC Implementation Path Status: »» **NEXT PHASE TO IMPLEMENT**

### Unit 1: Basic Frontend Setup [Initialize Vite project with Lit] Status: ✅ **COMPLETE**

**Tags**:
- [DEMOABLE] - Can run development server and see basic Lit component

**Complexity**: MICRO (1 point)
**Purpose**: Establish the foundational frontend development environment

**Changes**

- [x] Create package.json with Vite, Lit, and development dependencies
- [x] Set up Vite configuration for Lit development
- [x] Create basic index.html entry point
- [x] Add main.js with simple "Hello World" Lit component

**Success Criteria**

- [x] `npm run dev` starts Vite development server successfully
- [x] Browser displays basic Lit component at localhost:5173
- [x] Hot module replacement works for component changes

**Testing**

- [x] Verify Vite dev server starts without errors
- [x] Confirm basic Lit component renders in browser

**Implementation Notes**

- Use latest Vite 5.x with native ES module development
- Follow Lit 3.x component patterns from documentation
- Set up proper file structure: src/components/, src/pages/, src/services/

## 🚀 Demoable Checkpoint: Basic Development Environment

Run `npm run dev` and see a working Lit component with Vite hot reload.

## MVP Implementation Path Status: ⚪ **NOT STARTED**

### Unit 2: Add TailwindCSS v4 [Style system integration] Status: ✅ **COMPLETE**

**Complexity**: SMALL (2 points)
**Purpose**: Integrate modern styling system with Vite and Lit

**Changes**

- [x] Install TailwindCSS v4 and @tailwindcss/postcss plugin
- [x] Configure Vite to use TailwindCSS with PostCSS
- [x] Create src/styles/index.css with @tailwind directives
- [x] Set up CSS reset and base styles using @layer base
- [x] Update main.js to import CSS
- [x] Update HelloWorld component to use TailwindCSS classes

**Success Criteria**

- [x] TailwindCSS classes work in Lit components
- [x] Development build includes only used CSS classes
- [x] Styling updates trigger hot reload
- [x] Modern card-based UI with TailwindCSS utilities

**Testing**

- [x] Apply TailwindCSS classes to test component and verify styling
- [x] Check browser dev tools shows compiled TailwindCSS output
- [x] Verify server runs without errors and styles compile correctly

**Implementation Notes**

- Use TailwindCSS v4 with Vite plugin integration pattern
- Import CSS in main.js for proper loading order
- Configure content paths for class detection

### Unit 3: Signals Integration [Add @preact/signals state management] Status: ⚪ **NOT STARTED**

**Complexity**: SMALL (3 points)
**Purpose**: Enable reactive state management across components

**Changes**

- [ ] Install @preact/signals and @preact/signals-core packages
- [ ] Create src/services/auth.js with signal-based auth service
- [ ] Implement SignalWatcher pattern for Lit component reactivity
- [ ] Set up API client with signal-based state management

**Success Criteria**

- [ ] Components automatically re-render when signals change
- [ ] Signal state persists across component mounts/unmounts
- [ ] Auth signals work with sessionStorage persistence

**Testing**

- [ ] Create test signal and verify component updates
- [ ] Test signal persistence across page refreshes
- [ ] Verify SignalWatcher mixin functionality

**Implementation Notes**

- Follow @preact/signals integration patterns from research
- Use signal() for auth state, computed() for derived values
- Implement effect() for sessionStorage synchronization

### Unit 4: Routing System [Add Vaadin Router for navigation] Status: ⚪ **NOT STARTED**

**Complexity**: SMALL (2 points)
**Purpose**: Enable client-side navigation between login and homepage

**Changes**

- [ ] Install @vaadin/router package
- [ ] Create src/router.js with route definitions
- [ ] Set up protected route middleware using auth signals
- [ ] Configure routes for /login and /home paths

**Success Criteria**

- [ ] Navigation between routes works without page refresh
- [ ] Protected routes redirect to login when not authenticated
- [ ] Browser back/forward buttons work correctly

**Testing**

- [ ] Test navigation to /login and /home routes
- [ ] Verify protected route redirects work

**Implementation Notes**

- Use Vaadin Router based on research showing better Lit integration
- Implement route guards using auth signals for automatic redirects
- Set up lazy loading for route components

## 🚀 Demoable Checkpoint: Complete Development Stack

Full development environment with styling, state management, and routing ready for authentication implementation.

## Enhancement Implementation Path Status: ⚪ **NOT STARTED**

### Unit 5: Auth Service Implementation [Centralized JWT authentication] Status: ⚪ **NOT STARTED**

**Complexity**: STANDARD (4 points)
**Purpose**: Implement complete authentication system with FastAPI backend

**Changes**

- [ ] Create comprehensive auth service with login/register/logout functions
- [ ] Implement automatic JWT token injection for API requests
- [ ] Add auth state signals (isAuthenticated, currentUser, authError)
- [ ] Set up sessionStorage persistence with expiration handling

**Success Criteria**

- [ ] Login/register API calls work with FastAPI backend
- [ ] JWT tokens automatically added to authenticated requests
- [ ] Auth state persists across browser sessions
- [ ] Token expiration triggers automatic logout

**Testing**

- [ ] Test login with valid/invalid credentials
- [ ] Verify JWT token storage and retrieval
- [ ] Test automatic token injection in API calls
- [ ] Confirm session persistence across page refreshes

**Implementation Notes**

- Connect to existing FastAPI endpoints: /api/auth/login, /api/auth/register, /api/auth/me
- Use signals for reactive auth state management
- Implement fetch wrapper with automatic Bearer token injection

### Unit 6: Login Page Component [Email/password authentication form] Status: ⚪ **NOT STARTED**

**Complexity**: STANDARD (4 points)
**Purpose**: Create user interface for authentication

**Changes**

- [ ] Create login-page Lit component with email/password form
- [ ] Implement form validation and error handling
- [ ] Add loading states and user feedback
- [ ] Style with TailwindCSS for modern appearance

**Success Criteria**

- [ ] Form validates email format and password requirements
- [ ] Successful login redirects to homepage
- [ ] Error messages display for failed authentication
- [ ] Loading spinner shows during API requests

**Testing**

- [ ] Test form validation with invalid inputs
- [ ] Verify successful login flow and redirect
- [ ] Test error handling for API failures
- [ ] Confirm loading states display correctly

**Implementation Notes**

- Use reactive forms with signal-based state management
- Implement client-side validation with server-side verification
- Follow modern UX patterns for authentication flows

### Unit 7: Homepage Component [Welcome page with auth status] Status: ⚪ **NOT STARTED**

**Complexity**: MICRO (1 point)
**Purpose**: Create authenticated landing page

**Changes**

- [ ] Create home-page Lit component
- [ ] Display "Welcome to Talis Card Game" title
- [ ] Add logout functionality
- [ ] Show current user information

**Success Criteria**

- [ ] Page displays welcome message
- [ ] Logout button clears auth state and redirects
- [ ] User email/info displayed correctly

**Testing**

- [ ] Verify welcome message displays
- [ ] Test logout functionality and redirect

**Implementation Notes**

- Keep simple as requested - just title and basic auth controls
- Use auth signals to display user information
- Implement logout with signal state clearing

## Polish Implementation Path Status: ⚪ **NOT STARTED**

### Unit 8: Error Handling & UX Polish [Production-ready authentication] Status: ⚪ **NOT STARTED**

**Complexity**: SMALL (3 points)
**Purpose**: Enhance user experience and error handling

**Changes**

- [ ] Add comprehensive error boundaries and fallbacks
- [ ] Implement toast notifications for user feedback
- [ ] Add password strength indicators and form improvements
- [ ] Optimize bundle size and implement code splitting

**Success Criteria**

- [ ] Graceful error handling for network failures
- [ ] User-friendly feedback for all actions
- [ ] Fast initial page load and optimized bundles

**Testing**

- [ ] Test error scenarios and recovery
- [ ] Verify performance improvements

**Implementation Notes**

- Focus on production readiness and user experience
- Add monitoring for auth failures and performance
- Implement proper error logging and recovery

## 🚀 Demoable Checkpoint: Production-Ready Authentication System

Complete frontend application with secure authentication, modern UI, and excellent user experience.

---

## CHECKPOINT: Talis Engine Frontend - TailwindCSS Integration - Unit 2 Complete

### MASTER PLAN STATUS
**Implementation Progress**:
1. POC Implementation
   - [x] Unit 1: Basic Frontend Setup [Initialize Vite project with Lit] ✓
   - [x] Unit 2: Add TailwindCSS v4 [Style system integration] ✓
   - [ ] Unit 3: Signals Integration [Add @preact/signals state management] ← NEXT UNIT
   - [ ] Unit 4: Routing System [Add Vaadin Router for navigation]
2. Enhancement Implementation
   - [ ] Unit 5: Auth Service Implementation [Centralized JWT authentication]
   - [ ] Unit 6: Login Page Component [Email/password authentication form]
   - [ ] Unit 7: Homepage Component [Welcome page with auth status]
3. Polish Implementation
   - [ ] Unit 8: Error Handling & UX Polish [Production-ready authentication]

### TECHNICAL CONTEXT
**Established Patterns**:
- Frontend Structure: Files in project root (not separate frontend/ directory)
- Lit Components: ES6 classes extending LitElement with TailwindCSS classes in templates
- Vite Config: PostCSS with TailwindCSS and Autoprefixer plugins
- Package Management: NPM with package.json in project root
- Styling: TailwindCSS v4 with @tailwindcss/postcss plugin

**Architecture**:
- Vite 5.x dev server with native ES modules
- Lit 3.x web components using TailwindCSS classes
- TailwindCSS v4 with PostCSS integration
- Project structure: src/components/, src/pages/, src/services/, src/styles/
- FastAPI backend with JWT auth at /api/auth endpoints

### COMPLETED UNITS
**Unit 1**: Basic Frontend Setup - Initialize Vite project with Lit
**Unit 2**: Add TailwindCSS v4 - Style system integration
**Files Modified**:
- package.json - Added TailwindCSS and PostCSS dependencies
- vite.config.js - PostCSS configuration with TailwindCSS plugin
- tailwind.config.js - TailwindCSS configuration
- src/styles/index.css - TailwindCSS imports and base styles
- src/main.js - Updated with CSS imports and TailwindCSS-styled component
- Directory structure: src/styles/ added

**Verification**:
- Vite dev server starts successfully with `npm run dev`
- TailwindCSS classes compile correctly
- Modern card-based UI with TailwindCSS utilities
- Hot module replacement functional with styling updates

### NEXT UNIT SPECIFICATION
**Task**: Add @preact/signals for reactive state management
**Steps**:
1. Install @preact/signals and @preact/signals-core packages
2. Create src/services/auth.js with signal-based auth service
3. Implement SignalWatcher pattern for Lit component reactivity
4. Set up API client with signal-based state management
5. Create test signals and verify component updates

**Success Criteria**:
- Components automatically re-render when signals change
- Signal state persists across component mounts/unmounts
- Auth signals work with sessionStorage persistence

**Pattern to Follow**: @preact/signals integration patterns from research

---
Units: 2 completed | Next: Medium complexity
