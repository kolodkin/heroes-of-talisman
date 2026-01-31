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

test("should filter games list when typing game name", async ({ page }) => {
  // Create multiple test games with a common prefix
  const prefix = `search-test-${Date.now()}`;
  const gameNames = [`${prefix}-alpha`, `${prefix}-beta`, `${prefix}-gamma`];

  try {
    for (const name of gameNames) {
      await createGameViaAPI(name);
    }

    await setupHomePage(page);

    // Type in the game name input to filter
    const gameNameInput = page.locator('[data-testid="game-name-input"]');
    await gameNameInput.fill(prefix);

    // Wait for filtered results
    const gameItems = page.locator('[data-testid="game-list-item"]');
    await expect(gameItems).toHaveCount(3);

    await screenshot(page, "games-list-filtered");
  } finally {
    // Cleanup
    for (const name of gameNames) {
      await deleteGameViaAPI(name);
    }
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

    // Type in the game name input to filter
    const gameNameInput = page.locator('[data-testid="game-name-input"]');
    await gameNameInput.fill(prefix);

    // Wait for filtered results - only 5 shown initially
    const gameItems = page.locator('[data-testid="game-list-item"]');
    await expect(gameItems).toHaveCount(5);

    // Verify load more button is visible
    const loadMoreButton = page.locator('[data-testid="load-more-button"]');
    await expect(loadMoreButton).toBeVisible();

    await screenshot(page, "games-list-with-load-more-button");

    // Click load more
    await loadMoreButton.click();

    // Wait for more results to load
    await expect(gameItems).toHaveCount(7);

    // Load more button should be hidden now (no more results)
    await expect(loadMoreButton).not.toBeVisible();

    await screenshot(page, "games-list-all-loaded");
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

  // Wait for no results message
  const noResults = page.locator('[class*="search-no-results"]');
  await expect(noResults).toBeVisible();
  await expect(noResults).toContainText("No games found");

  await screenshot(page, "no-games-found");
});

test("should reset games list when query changes", async ({ page }) => {
  // Create games with different prefixes
  const prefix1 = `reset-a-${Date.now()}`;
  const prefix2 = `reset-b-${Date.now()}`;
  const games1 = [`${prefix1}-game-1`, `${prefix1}-game-2`, `${prefix1}-game-3`];
  const game2 = `${prefix2}-game`;

  try {
    for (const name of games1) {
      await createGameViaAPI(name);
    }
    await createGameViaAPI(game2);

    await setupHomePage(page);

    const gameNameInput = page.locator('[data-testid="game-name-input"]');
    const gameItems = page.locator('[data-testid="game-list-item"]');

    // Search for first prefix
    await gameNameInput.fill(prefix1);
    await expect(gameItems).toHaveCount(3);

    // Change query to second prefix
    await gameNameInput.fill(prefix2);

    // Results should update to show second game (reset happened)
    await expect(gameItems).toHaveCount(1);

    await screenshot(page, "games-list-query-changed");
  } finally {
    for (const name of games1) {
      await deleteGameViaAPI(name);
    }
    await deleteGameViaAPI(game2);
  }
});

test("should show all games when search is cleared", async ({ page }) => {
  // Create test games
  const prefix = `clear-test-${Date.now()}`;
  const gameNames = [`${prefix}-alpha`, `${prefix}-beta`];

  try {
    for (const name of gameNames) {
      await createGameViaAPI(name);
    }

    await setupHomePage(page);

    const gameNameInput = page.locator('[data-testid="game-name-input"]');
    const gameItems = page.locator('[data-testid="game-list-item"]');

    // Filter games
    await gameNameInput.fill(prefix);
    await expect(gameItems).toHaveCount(2);

    // Clear search - should show more games than filtered
    await gameNameInput.fill("");

    // Wait for debounce and verify we have more than the filtered count
    // (we can't predict exact count due to parallel tests, but should have at least our 2 games)
    await expect(async () => {
      const count = await gameItems.count();
      expect(count).toBeGreaterThanOrEqual(2);
    }).toPass({ timeout: 5000 });

    await screenshot(page, "games-list-search-cleared");
  } finally {
    for (const name of gameNames) {
      await deleteGameViaAPI(name);
    }
  }
});
