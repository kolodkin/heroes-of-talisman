# Backend Tests

## Guidelines

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

## Action Testing Guidelines

When testing action classes (subclasses of `Action`):

### Use Action Properties

- **Always use action properties** where appropriate instead of accessing game state directly
- See the `Action` base class for available properties and their usage

### Suggest New Properties

- If you find yourself repeatedly accessing nested game state, suggest adding a new property to the `Action` base class
- Properties should encapsulate common access patterns and provide validation

### Use debug_presets.py for Game State

- Use `get_debug_preset()` from `server/gameplay/debug_presets.py` to create preset game states for testing
- Available presets: `battle_player_1_win`, `battle_player_2_win`, `battle_draw`, `knight_not_alive`, etc.
- Example:

  ```python
  from ..debug_presets import get_debug_preset

  def test_battle_action():
      game = get_debug_preset("battle_player_1_win")
      action = BattleEndAction("player1", game)
      updated_game = action.run()
      # assertions...
  ```

### Validate Against Character State

- Always validate that dice counts match character dice values
- Use character properties (attack, dice, health) for calculations
- Don't hardcode character stats in tests

### Example

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

## Running Tests

- To run all tests, use:
  ```
  uv run pytest
  ```
- To run tests in a specific file, use:
  ```
  uv run pytest <filename>
  ```
- To run a specific test function in a file, use:
  ```
  uv run pytest <filename>::<testname>
  ```
