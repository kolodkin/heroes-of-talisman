import { createGameViaAPI, deleteGameViaAPI } from "./api_helpers.js";
import { test, expect, setupHomePage, screenshot, waitForToast } from "./test_helpers.js";

test("should show error toast when username is empty", async ({ page, gameName }) => {
  // Setup: Create test game
  await createGameViaAPI(gameName);

  await setupHomePage(page);

  // Clear the username field
  const usernameInput = page.getByLabel("Enter your name:");
  await usernameInput.clear();

  await screenshot(page, "empty-username");

  // Try to join game with empty username
  const gameButton = page.getByRole("button", { name: gameName });
  await gameButton.click();

  // Wait for error toast to appear
  const toastMessage = await waitForToast(page, {
    type: "error",
    message: "אנא הזן שם",
  });

  await screenshot(page, "empty-username-error-toast");

  // Verify we didn't navigate away from home page
  await expect(page).toHaveURL("/");

  // Attach toast message to test report
  await test.info().attach("toast-message", {
    body: toastMessage,
    contentType: "text/plain",
  });
});

test("should show error toast when username is only whitespace", async ({ page, gameName }) => {
  // Setup: Create test game
  await createGameViaAPI(gameName);

  await setupHomePage(page);

  // Fill username with only spaces
  const usernameInput = page.getByLabel("Enter your name:");
  await usernameInput.fill("   ");

  await screenshot(page, "whitespace-username");

  // Try to join game with whitespace-only username
  const gameButton = page.getByRole("button", { name: gameName });
  await gameButton.click();

  // Wait for error toast to appear
  const toastMessage = await waitForToast(page, {
    type: "error",
    message: "אנא הזן שם",
  });

  await screenshot(page, "whitespace-username-error-toast");

  // Verify we didn't navigate away from home page
  await expect(page).toHaveURL("/");

  // Attach toast message to test report
  await test.info().attach("toast-message", {
    body: toastMessage,
    contentType: "text/plain",
  });
});

test("should allow joining game with valid username", async ({ page, gameName }) => {
  // Setup: Create test game
  await createGameViaAPI(gameName);

  await setupHomePage(page);

  // Fill in a valid username
  const usernameInput = page.getByLabel("Enter your name:");
  await usernameInput.fill("testplayer");

  await screenshot(page, "valid-username");

  // Join game with valid username
  const gameButton = page.getByRole("button", { name: gameName });
  await gameButton.click();

  // Wait for navigation to game page
  await expect(page).toHaveURL(new RegExp(`/games/${encodeURIComponent(gameName)}/`));

  await screenshot(page, "joined-game");
});

test("should trim whitespace from username when joining", async ({ page, gameName }) => {
  // Setup: Create test game
  await createGameViaAPI(gameName);

  await setupHomePage(page);

  // Fill username with leading and trailing spaces
  const usernameInput = page.getByLabel("Enter your name:");
  await usernameInput.fill("  testplayer  ");

  await screenshot(page, "username-with-spaces");

  // Join game
  const gameButton = page.getByRole("button", { name: gameName });
  await gameButton.click();

  // Wait for navigation and verify URL has trimmed username
  await expect(page).toHaveURL(new RegExp(`/games/${encodeURIComponent(gameName)}/testplayer$`));

  await screenshot(page, "joined-with-trimmed-username");
});

test("should show search dropdown when typing game name", async ({ page }) => {
  // Create multiple test games with a common prefix
  const prefix = `search-test-${Date.now()}`;
  const gameNames = [`${prefix}-alpha`, `${prefix}-beta`, `${prefix}-gamma`];

  try {
    for (const name of gameNames) {
      await createGameViaAPI(name);
    }

    await setupHomePage(page);

    // Type in the game name input
    const gameNameInput = page.locator('[data-testid="game-name-input"]');
    await gameNameInput.fill(prefix);

    // Wait for search dropdown to appear
    const dropdown = page.locator('[data-testid="search-dropdown"]');
    await expect(dropdown).toBeVisible();

    await screenshot(page, "search-dropdown-visible");

    // Verify search results are shown
    const results = page.locator('[data-testid="search-result"]');
    await expect(results).toHaveCount(3);
  } finally {
    // Cleanup
    for (const name of gameNames) {
      await deleteGameViaAPI(name);
    }
  }
});

test("should populate input when clicking search result", async ({ page }) => {
  // Create a test game
  const prefix = `click-test-${Date.now()}`;
  const gameName = `${prefix}-game`;

  try {
    await createGameViaAPI(gameName);

    await setupHomePage(page);

    // Type in the game name input
    const gameNameInput = page.locator('[data-testid="game-name-input"]');
    await gameNameInput.fill(prefix);

    // Wait for search dropdown
    const dropdown = page.locator('[data-testid="search-dropdown"]');
    await expect(dropdown).toBeVisible();

    // Click on the search result
    const result = page.locator('[data-testid="search-result"]').first();
    await result.click();

    // Verify input is populated with the game name
    await expect(gameNameInput).toHaveValue(gameName);

    // Verify dropdown is closed
    await expect(dropdown).not.toBeVisible();

    await screenshot(page, "search-result-clicked");
  } finally {
    await deleteGameViaAPI(gameName);
  }
});

test("should show load more button when more results available", async ({ page }) => {
  // Create more than 5 games (the default limit)
  const prefix = `loadmore-test-${Date.now()}`;
  const gameNames = [];
  for (let i = 1; i <= 7; i++) {
    gameNames.push(`${prefix}-game-${i}`);
  }

  try {
    for (const name of gameNames) {
      await createGameViaAPI(name);
    }

    await setupHomePage(page);

    // Type in the game name input
    const gameNameInput = page.locator('[data-testid="game-name-input"]');
    await gameNameInput.fill(prefix);

    // Wait for search dropdown
    const dropdown = page.locator('[data-testid="search-dropdown"]');
    await expect(dropdown).toBeVisible();

    // Verify only 5 results shown initially
    const results = page.locator('[data-testid="search-result"]');
    await expect(results).toHaveCount(5);

    // Verify load more button is visible
    const loadMoreButton = page.locator('[data-testid="load-more-button"]');
    await expect(loadMoreButton).toBeVisible();

    await screenshot(page, "load-more-button-visible");

    // Click load more
    await loadMoreButton.click();

    // Wait for more results to load
    await expect(results).toHaveCount(7);

    // Load more button should be hidden now (no more results)
    await expect(loadMoreButton).not.toBeVisible();

    await screenshot(page, "all-results-loaded");
  } finally {
    for (const name of gameNames) {
      await deleteGameViaAPI(name);
    }
  }
});

test("should show no results message when no games match", async ({ page }) => {
  await setupHomePage(page);

  // Type a query that won't match any games
  const gameNameInput = page.locator('[data-testid="game-name-input"]');
  await gameNameInput.fill(`nonexistent-game-${Date.now()}`);

  // Wait for dropdown to appear with no results message
  const dropdown = page.locator('[data-testid="search-dropdown"]');
  await expect(dropdown).toBeVisible();

  const noResults = page.locator('[class*="search-no-results"]');
  await expect(noResults).toBeVisible();
  await expect(noResults).toContainText("No games found");

  await screenshot(page, "no-search-results");
});

test("should reset search when query changes", async ({ page }) => {
  // Create games with different prefixes
  const prefix1 = `reset-a-${Date.now()}`;
  const prefix2 = `reset-b-${Date.now()}`;
  const game1 = `${prefix1}-game`;
  const game2 = `${prefix2}-game`;

  try {
    await createGameViaAPI(game1);
    await createGameViaAPI(game2);

    await setupHomePage(page);

    const gameNameInput = page.locator('[data-testid="game-name-input"]');

    // Search for first prefix
    await gameNameInput.fill(prefix1);
    const dropdown = page.locator('[data-testid="search-dropdown"]');
    await expect(dropdown).toBeVisible();

    let results = page.locator('[data-testid="search-result"]');
    await expect(results).toHaveCount(1);
    await expect(results.first()).toContainText(game1);

    await screenshot(page, "search-first-query");

    // Change query to second prefix
    await gameNameInput.fill(prefix2);

    // Results should update to show second game
    await expect(results).toHaveCount(1);
    await expect(results.first()).toContainText(game2);

    await screenshot(page, "search-second-query");
  } finally {
    await deleteGameViaAPI(game1);
    await deleteGameViaAPI(game2);
  }
});
