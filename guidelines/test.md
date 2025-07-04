Test Guidelines
===============

# Backend Testing
- Tests should follow pytest conventions and best practices
- Use descriptive function names, or split tests across multiple files instead of using test classes
- Testing framework using **pytest** with FastAPI's `TestClient`\
  [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- For asynchronous test cases, use **pytest-asyncio**
- for websocket testing use https://fastapi.tiangolo.com/advanced/testing-websockets/
- Place test files next to implementation files for easy discovery with `pytest <package>`
- Run `docker compose up -d` before executing tests
- Use `pytest` to run backend tests
- Fix test warnings when possible

# Frontend Testing
- Execute frontend tests using `npm test`
