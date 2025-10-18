import { test, expect } from "@playwright/test";
import { createPresetGameViaAPI, deleteGameViaAPI } from "./api_helpers.js";
import { TIMEOUT, screenshot, setupHomePage, joinGame } from "./test-helpers.js";

test("test disconnected player overlay in battle stage", async ({ page }) => {
  const testName = "disconnected-battle";
  const gameName = `test-${testName}`;

  // Setup: Create battle preset game via API
  await deleteGameViaAPI(gameName); // Clean up if exists
  await createPresetGameViaAPI(gameName, "battle_player_1_win");

  try {
    // Player 1 joins
    await setupHomePage(page);
    await joinGame(page, "player1", gameName);

    // Wait for battle stage to load
    await page.waitForSelector('[data-battle-participant="player1"]', { timeout: TIMEOUT });

    // Player 2 joins in a new session
    const page2 = await page.context().newPage();
    await setupHomePage(page2);
    await joinGame(page2, "player2", gameName);

    // Wait for player2 to appear in player1's players menu
    await page.waitForSelector('[data-player="player2"]', { timeout: TIMEOUT });

    // Verify player2 does not have disconnected indicator
    const player2Wrapper = page.locator('[data-player-disconnected="player2"]');
    await expect(player2Wrapper).toBeVisible();
    await expect(player2Wrapper.locator("[data-disconnected-indicator]")).not.toBeVisible();
    await screenshot(page, "both-players-connected");

    // Close player2's session to trigger disconnect
    await page2.close();

    // Wait for disconnection to propagate
    await page.waitForTimeout(500);

    // Verify disconnected overlay appears on player2's card
    const disconnectedIndicator = player2Wrapper.locator("[data-disconnected-indicator]");
    await expect(disconnectedIndicator).toBeVisible();

    // Verify player1 does not have disconnected indicator (still connected)
    const player1Wrapper = page.locator('[data-player-disconnected="player1"]');
    await expect(player1Wrapper.locator("[data-disconnected-indicator]")).not.toBeVisible();
    await screenshot(page, "player2-disconnected");
  } finally {
    // Cleanup: Delete game via API
    await deleteGameViaAPI(gameName);
  }
});

test("test disconnected player overlay in opponent selection stage", async ({ page }) => {
  const testName = "disconnected-opponent-selection";
  const gameName = `test-${testName}`;

  // Setup: Create game via API
  await deleteGameViaAPI(gameName); // Clean up if exists
  await createPresetGameViaAPI(gameName, "battle_player_1_win", "opponent_selection");

  try {
    // Player 1 joins
    await setupHomePage(page);
    await joinGame(page, "player1", gameName);

    // Wait for opponent selection stage
    await page.waitForSelector('[data-player="player2"]', { timeout: TIMEOUT });

    // Player 2 joins in a new session
    const page2 = await page.context().newPage();
    await setupHomePage(page2);
    await joinGame(page2, "player2", gameName);

    // Verify player2 appears in opponent selection without disconnected indicator
    const player2OpponentWrapper = page.locator('[data-player-disconnected="player2"]').first();
    await expect(player2OpponentWrapper).toBeVisible();
    await expect(player2OpponentWrapper.locator("[data-disconnected-indicator]")).not.toBeVisible();
    await screenshot(page, "both-players-connected");

    // Close player2's session to trigger disconnect
    await page2.close();

    // Wait for disconnection to propagate
    await page.waitForTimeout(500);

    // Verify disconnected overlay appears in opponent selection area
    const disconnectedIndicator = player2OpponentWrapper.locator("[data-disconnected-indicator]");
    await expect(disconnectedIndicator).toBeVisible();

    // Verify overlay also appears in players menu on the right
    const player2MenuWrapper = page.locator('[data-player-disconnected="player2"]').last();
    const menuDisconnectedIndicator = player2MenuWrapper.locator("[data-disconnected-indicator]");
    await expect(menuDisconnectedIndicator).toBeVisible();
    await screenshot(page, "player2-disconnected");
  } finally {
    // Cleanup: Delete game via API
    await deleteGameViaAPI(gameName);
  }
});
