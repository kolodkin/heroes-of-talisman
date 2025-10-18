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

    // Verify player2 is connected
    const player2Card = page.locator('[data-player="player2"]').first();
    await expect(player2Card).toBeVisible();
    await expect(player2Card).toHaveAttribute("data-status", "connected");
    await screenshot(page, "both-players-connected");

    // Close player2's session to trigger disconnect
    await page2.close();

    // Wait for disconnection to propagate
    await page.waitForTimeout(500);

    // Verify player2 has disconnected status
    await expect(player2Card).toHaveAttribute("data-status", "disconnected");

    // Verify player1 is still connected
    const player1Card = page.locator('[data-player="player1"]').first();
    await expect(player1Card).toHaveAttribute("data-status", "connected");
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

    // Verify player2 appears in opponent selection and is connected
    const player2OpponentCard = page.locator('[data-player="player2"]').first();
    await expect(player2OpponentCard).toBeVisible();
    await expect(player2OpponentCard).toHaveAttribute("data-status", "connected");
    await screenshot(page, "both-players-connected");

    // Close player2's session to trigger disconnect
    await page2.close();

    // Wait for disconnection to propagate
    await page.waitForTimeout(500);

    // Verify player2 has disconnected status in opponent selection area
    await expect(player2OpponentCard).toHaveAttribute("data-status", "disconnected");

    // Verify player2 also has disconnected status in players menu on the right
    const player2MenuCard = page.locator('[data-player="player2"]').last();
    await expect(player2MenuCard).toHaveAttribute("data-status", "disconnected");
    await screenshot(page, "player2-disconnected");
  } finally {
    // Cleanup: Delete game via API
    await deleteGameViaAPI(gameName);
  }
});
