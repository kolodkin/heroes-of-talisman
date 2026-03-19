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
  // Register listener before click so we never miss the event
  const gameButton = page.getByRole("button", { name: gameName });
  const toastPromise = waitForToast(page, { type: "error", message: "אנא הזן שם" });
  await gameButton.click();
  const toastMessage = await toastPromise;

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
  // Register listener before click so we never miss the event
  const gameButton = page.getByRole("button", { name: gameName });
  const toastPromise = waitForToast(page, { type: "error", message: "אנא הזן שם" });
  await gameButton.click();
  const toastMessage = await toastPromise;

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

test("should filter games list when typing game name and load more twice", async ({ page }) => {
  // Create 15 games to test load more twice (5 -> 10 -> 15)
  const prefix = `search-test-${Date.now()}`;
  const gameNames = [];
  for (let i = 1; i <= 15; i++) {
    gameNames.push(`${prefix}-game-${String(i).padStart(2, "0")}`);
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

    // Scroll to load more button before screenshot
    await loadMoreButton.scrollIntoViewIfNeeded();
    await screenshot(page, "games-list-filtered-5-games");

    // Click load more first time - should show 10 games
    await loadMoreButton.click();
    await expect(gameItems).toHaveCount(10);
    await expect(loadMoreButton).toBeVisible();

    // Click load more second time - should show all 15 games
    await loadMoreButton.click();
    await expect(gameItems).toHaveCount(15);

    // Load more button should be hidden now
    await expect(loadMoreButton).not.toBeVisible();

    // Scroll to last game item before final screenshot
    await gameItems.last().scrollIntoViewIfNeeded();
    await screenshot(page, "games-list-all-15-games-loaded");
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
  // Create games with two different prefixes
  const timestamp = Date.now();
  const prefixA = `clear-test-a-${timestamp}`;
  const prefixB = `clear-test-b-${timestamp}`;
  const gamesA = [`${prefixA}-game-1`, `${prefixA}-game-2`, `${prefixA}-game-3`];
  const gamesB = [`${prefixB}-game-1`, `${prefixB}-game-2`];
  const allGames = [...gamesA, ...gamesB];

  try {
    for (const name of allGames) {
      await createGameViaAPI(name);
    }

    await setupHomePage(page);

    const gameNameInput = page.locator('[data-testid="game-name-input"]');
    const gameItems = page.locator('[data-testid="game-list-item"]');

    // Search for prefix A - should only show A games
    await gameNameInput.fill(prefixA);
    await expect(gameItems).toHaveCount(3);

    await screenshot(page, "games-list-prefix-a-filtered");

    // Clear search - should show both A and B games
    await gameNameInput.fill("");

    // Wait for debounce and verify both prefixes are visible
    await expect(async () => {
      const count = await gameItems.count();
      expect(count).toBeGreaterThanOrEqual(5);
    }).toPass({ timeout: 5000 });

    // Verify we can see games from both prefixes
    await expect(page.locator(`[data-testid="game-list-item"]:has-text("${prefixA}")`).first()).toBeVisible();
    await expect(page.locator(`[data-testid="game-list-item"]:has-text("${prefixB}")`).first()).toBeVisible();

    await screenshot(page, "games-list-search-cleared-shows-both");
  } finally {
    for (const name of allGames) {
      await deleteGameViaAPI(name);
    }
  }
});
