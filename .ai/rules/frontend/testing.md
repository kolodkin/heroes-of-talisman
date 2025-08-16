# Frontend Testing

## Running tests

- All frontend end-to-end and integration tests are run using [Playwright](https://playwright.dev/).
- To run all Playwright tests locally, use:
  ```
  npm run e2e
  ```
- To run a specific test file:
  ```
  npx playwright test <filename>
  ```
- Test reports are generated in the `playwright-report/` directory after each run.

**Best Practices:**
- Write tests in a flat structure using function-based test definitions (avoid class-based grouping).
- Use descriptive test names that clearly indicate the user flow or feature being tested.
- Prefer colocating test files with the components or features they cover, or group related tests in the same directory.
