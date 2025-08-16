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
