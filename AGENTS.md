# AI Agents Documentation

This file contains agent-specific documentation from .ai/ directory.

## .ai/backend/testing-guidelines.md

# Backend Testing Guidelines

## Test Function Guidelines
- Use pytest for all backend tests
- Avoid using classes for grouping tests
- Prefer function-based tests over class-based test organization
- Use descriptive function names that clearly indicate what is being tested

## Test Structure
- Each test function should be self-contained and focused on a single behavior
- Use pytest fixtures for test setup and teardown when needed
- Group related tests in the same file rather than in classes

## Examples
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

# Backend Actions

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
