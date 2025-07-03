# Test Guidelines

## Backend Testing
- Run `docker compose up -d` before executing tests
- Use `pytest` to run backend tests
- Handle test warnings when possible
- Place test files next to implementation files for easy discovery with `pytest <package>`
- Include a migration test file that:
  - creates a temporary test database during test module initialization
  - executes all database migrations forward and backward on the temporary database
  - removes the temporary test database during test module cleanup

## Frontend Testing
- Execute frontend tests using `npm test`
