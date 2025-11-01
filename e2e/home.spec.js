import { test, expect } from "@playwright/test";
import { createGameViaAPI, deleteGameViaAPI } from "./api_helpers.js";
import { setupHomePage, screenshot, waitForToast } from "./test_helpers.js";

test("should show error toast when username is empty", async ({ page }) => {
  const gameName = "test-empty-username";

  // Setup: Create test game
  await deleteGameViaAPI(gameName);
  await createGameViaAPI(gameName);

  try {
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
  } finally {
    await deleteGameViaAPI(gameName);
  }
});

test("should show error toast when username is only whitespace", async ({ page }) => {
  const gameName = "test-whitespace-username";

  // Setup: Create test game
  await deleteGameViaAPI(gameName);
  await createGameViaAPI(gameName);

  try {
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
  } finally {
    await deleteGameViaAPI(gameName);
  }
});

test("should allow joining game with valid username", async ({ page }) => {
  const gameName = "test-valid-username";

  // Setup: Create test game
  await deleteGameViaAPI(gameName);
  await createGameViaAPI(gameName);

  try {
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
  } finally {
    await deleteGameViaAPI(gameName);
  }
});

test("should trim whitespace from username when joining", async ({ page }) => {
  const gameName = "test-trim-username";

  // Setup: Create test game
  await deleteGameViaAPI(gameName);
  await createGameViaAPI(gameName);

  try {
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
  } finally {
    await deleteGameViaAPI(gameName);
  }
});
