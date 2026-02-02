# Agent Guidelines

## Related Documentation

- [Gameplay Spec](docs/gameplay_spec.md) - Game mechanics and rules
- [Gameplay Frontend](docs/gameplay_frontend.md) - Frontend implementation details
- [Gameplay Backend](docs/gameplay_backend.md) - Backend implementation details

## Git Workflow

After each `git push`, use the `check-pr` skill to verify GitHub Actions workflows are successful.

If any workflows fail, analyze the error logs and fix issues automatically.

## General Guidelines

- Whenever a file is referenced, always verify if a corresponding <filename>.md or <foldername>.md file exists in the same directory to gather additional context.
- Always run Python scripts using the following command to ensure correct module resolution:
  `PYTHONPATH=. uv run <script path>`
- When coding, check if a file named test\_<filename>.py exists in the same folder as the file you are working on. If it exists, use it for testing. If it does not exist, recommend creating one following the Testing Guidelines.

# Development Services

- **postgres** - PostgreSQL database - Port ${POSTGRES_PORT:-5432}
- **redis** - Redis cache and message broker - Port ${REDIS_PORT:-6379}
- **server** - FastAPI backend server - Port 8000
- **www** - Vite React frontend development server - Port 5173
- **playwright-report** - Playwright test report viewer - Port 9323

# Backend

## Import Organization

All imports must be at the top of the file, organized in the following order:

1. **Native/built-in modules** (e.g., `import copy`, `import random`)
2. **Third-party packages** (e.g., `from pydantic import BaseModel`)
3. **Local/relative imports** (e.g., `from .action import Action`, `from ..common import ...`)

Separate each group with a blank line.

**Good:**

```python
import copy
import random

from pydantic import BaseModel

from .action import Action
from ..common import GameException
from ..gameplay import GamePlay
```

**Avoid:**

```python
from .action import Action
import copy  # Wrong: native import after local
from ..gameplay import GamePlay

def my_function():
    from ..cards import CARDS_MAP  # Wrong: import inside function
    ...
```

## String Literals and Type Safety

When working with string constants in Python code:

- **Use Literal types** from `typing.Literal` to define valid string values for variables and function parameters
- **Use topic prefix** for constant names (e.g., `FRUIT_`, `STATUS_`, `MODE_`)
- **Combine multiple Literal types** when a variable can accept values from different string sets

**Implementation pattern:**

```python
from typing import Literal

# Define literals with topic prefix
FRUIT_APPLE = "apple"
FRUIT_BANANA = "banana"
FRUIT_TYPES = [FRUIT_APPLE, FRUIT_BANANA]
FruitType = Literal[*FRUIT_TYPES]

def eat_fruit(fruit: FruitType) -> None:
    """Accept only validated string values with compile-time checking."""
    pass
```

## Backend Testing

- Use pytest for all backend tests
- Avoid using classes for grouping tests
- Prefer function-based tests over class-based test organization
- Use descriptive function names that clearly indicate what is being tested

### Test Structure

- Each test function should be self-contained and focused on a single behavior
- Use pytest fixtures for test setup and teardown when needed
- Group related tests in the same file rather than in classes

### Examples

```python
# Good: Function-based test
def test_character_creation_with_valid_data():
    character = create_character("Knight", 100)
    assert character.name == "Knight"
    assert character.health == 100

# Avoid: Class-based grouping
class TestCharacter:  # Don't do this
    def test_creation(self):
        pass
```

### Action Testing Guidelines

When testing action classes (subclasses of `Action`):

**Use Action Properties**

- **Always use action properties** where appropriate instead of accessing game state directly
- See the `Action` base class for available properties and their usage

**Suggest New Properties**

- If you find yourself repeatedly accessing nested game state, suggest adding a new property to the `Action` base class
- Properties should encapsulate common access patterns and provide validation

**Use presets.py for Game State**

- Use `get_debug_preset()` from `server/gameplay/presets.py` to create preset game states for testing
- Example:

  ```python
  from ..presets import get_debug_preset

  def test_battle_action():
      game = get_debug_preset("battle_player_1_win")
      action = BattleEndAction("player1", game)
      updated_game = action.run()
      # assertions...
  ```

**Validate Against Character State**

- Always validate that dice counts match character dice values
- Use character properties (attack, dice, health) for calculations
- Don't hardcode character stats in tests

**Example**

```python
def test_action_with_properties():
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE,
        active=ActivePlayer3(player="player1", character=KNIGHT, dice_roll=[6]),
        opponent=Opponent3(player="player2", character=MAGE, dice_roll=[3]),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = MyAction("player1", game)

    # Good: Use properties
    active_char = action.active_character
    opponent_char = action.opponent_character

    # Avoid: Direct access
    # active_char = game.players[game.active.player].characters[game.active.character]

    updated_game = action.run()
    assert updated_game.active.winner is True
```

# Frontend

## Import Organization

All imports must be at the top of the file, organized in the following order:

**Non-components first:**

1. **React** (e.g., `import React, { useState } from "react"`)
2. **Third-party packages** (e.g., `import { useParams } from "react-router-dom"`)
3. **Local utilities** (e.g., `import { formatDate } from "./utils"`)

**Then components with their CSS (utility components first):** 4. **Utility components** with CSS immediately after 5. **Feature components** with CSS immediately after 6. **Current component's CSS** last

**Good:**

```javascript
import React, { useState, useEffect } from "react";

import { useParams } from "react-router-dom";

import { formatScore } from "./utils";

import { Button } from "./Button";
import buttonStyles from "./Button.module.css";

import { CharacterCard } from "./CharacterCard";
import characterStyles from "./CharacterCard.module.css";

import styles from "./GamePlay.module.css";
```

**Avoid:**

```javascript
import styles from "./GamePlay.module.css"; // Wrong: CSS before React
import { CharacterCard } from "./CharacterCard";
import React from "react";
```

## Coding Standards

### React Imports

Always use destructured imports for React hooks and features instead of accessing them from the React object.

**Good:**

```javascript
import React, { useState, useEffect, useCallback } from "react";

function MyComponent() {
  const [count, setCount] = useState(0);
  // ...
}
```

**Avoid:**

```javascript
import React from "react";

function MyComponent() {
  const [count, setCount] = React.useState(0); // Don't do this
  // ...
}
```

## Routing

The GamePlay component uses **React Router** for client-side navigation:

- **Navigation**: Use `Link` component from `react-router-dom` for internal links
- **Route Parameters**: Access game and player info via `useParams()` hook
- **Programmatic Navigation**: Use `useNavigate()` hook for redirects
- **Pattern**: All routes use React Router for SPA behavior (no full page reloads)

## Styling

### Primary: Use CSS Modules

**CSS Modules should be the default choice for component styling.** Use `.module.css` files for better organization and maintainability.

### Secondary: Tailwind CSS for Simple Styling

**Use Tailwind CSS only for simple styling with ≤3 utility classes.**

**Good (simple):**

```jsx
<button className="px-4 py-2 rounded">Click</button>
```

**Bad (too many classes):**

```jsx
<button className="px-6 py-3 rounded-lg font-semibold bg-blue-600 text-white hover:bg-blue-700 transition-colors shadow-md">
  Click
</button>
```

**Better (use CSS Module instead):**

```css
/* Button.module.css */
.primary {
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 600;
  background-color: #2563eb;
  color: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: background-color 0.2s;
}
.primary:hover {
  background-color: #1d4ed8;
}
```

```jsx
import styles from "./Button.module.css";
<button className={styles.primary}>Click</button>;
```

### CSS Module Usage

CSS Modules in Vite work automatically for any CSS file ending with `.module.css`.

**Create a CSS Module File:**

```css
/* styles.module.css */
.red {
  color: red;
}

.container {
  padding: 20px;
  border: 1px solid #ccc;
}

.button {
  background-color: blue;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
}
```

**Import and Use in JavaScript:**

```javascript
import classes from "./styles.module.css";

document.getElementById("foo").className = classes.red;
document.getElementById("container").className = classes.container;
document.getElementById("btn").className = classes.button;
```

**React Component Example:**

```css
/* Button.module.css */
.button {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.button:hover {
  background-color: #0056b3;
}

.button--large {
  padding: 16px 32px;
  font-size: 18px;
}

.button--disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
```

```jsx
import styles from "./Button.module.css";

function Button({ children, large, disabled, onClick }) {
  const buttonClass = [styles.button, large && styles["button--large"], disabled && styles["button--disabled"]]
    .filter(Boolean)
    .join(" ");

  return (
    <button className={buttonClass} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}

export default Button;
```

### CSS Architecture

- **BEM Methodology**: Block-Element-Modifier naming
- **CSS Custom Properties**: Theme variables for easy customization
- **Responsive Breakpoints**: Mobile-first responsive design
- **Animation Classes**: Reusable transition effects

## Frontend Testing

- In `basic.spec.js` tests, capture a screenshot after every UI update.
- Skip screenshot capture when only backend state changes occur without visible UI updates.
- Use `api_helpers.js` to call backend APIs directly in e2e tests for test setup or by demand. This allows faster test execution and more reliable state management compared to UI-only interactions.

### DOM Selection

Use dedicated data attributes (e.g., `data-battle-participant`, `data-character`) or CSS class name selectors (e.g., `[class*="diceContainer"]`) to locate DOM elements in e2e tests. Avoid selecting elements by DOM type (e.g., `h2`, `div`, `span`) or text content as these are fragile and can break when refactoring markup structure or translations.

**Examples:**

- **Good**: `page.locator('[data-battle-participant="player"]')`
- **Good**: `page.locator('[data-character="knight"]')`
- **Good**: `page.locator('[class*="diceContainer"]')`
- **Avoid**: `page.locator('h2').filter({ hasText: 'player' })`
- **Avoid**: `page.locator('div.container > span')`
- **Avoid**: `page.getByText(/אביר/)` (text-based selectors break with translations)

### Best Practices

- Write tests in a flat structure using function-based test definitions (avoid class-based grouping).
- Use descriptive test names that clearly indicate the user flow or feature being tested.
- Prefer colocating test files with the components or features they cover, or group related tests in the same directory.
- Avoid `waitForTimeout()` - use `expect(element).toBeVisible()` to wait for DOM elements.
