# Frontend Testing

## Guidelines

- In `basic.spec.js` tests, capture a screenshot after every view change.

## Dom Selection

Use dedicated data attributes (e.g., `data-battle-participant`, `data-character`) or CSS class name selectors (e.g., `[class*="diceContainer"]`) to locate DOM elements in e2e tests. Avoid selecting elements by DOM type (e.g., `h2`, `div`, `span`) or text content as these are fragile and can break when refactoring markup structure or translations.

**Examples:**

- **Good**: `page.locator('[data-battle-participant="player"]')`
- **Good**: `page.locator('[data-character="knight"]')`
- **Good**: `page.locator('[class*="diceContainer"]')`
- **Avoid**: `page.locator('h2').filter({ hasText: 'player' })`
- **Avoid**: `page.locator('div.container > span')`
- **Avoid**: `page.getByText(/אביר/)` (text-based selectors break with translations)

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
- Avoid `waitForTimeout()` - use `expect(element).toBeVisible()` to wait for DOM elements.
