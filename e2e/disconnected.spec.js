import { test, expect } from "@playwright/test";
import { createGameViaAPI, deleteGameViaAPI } from "./api_helpers.js";
import { TIMEOUT, screenshot, setupHomePage, joinGame } from "./test-helpers.js";

test("test disconnected player overlay in players menu", async ({ page }) => {
  const testName = "disconnected-players-menu";
  const gameName = `test-${testName}`;

  // Setup: Create game via API
  await deleteGameViaAPI(gameName); // Clean up if exists
  await createGameViaAPI(gameName);

  try {
    // Player 1 joins
    await setupHomePage(page);
    await joinGame(page, "player1", gameName);

    // Wait for player1 to appear in players menu
    await page.waitForSelector('[data-player="player1"]', { timeout: TIMEOUT });
    await screenshot(page, "player1-joined");

    // Player 2 joins in a new session
    const page2 = await page.context().newPage();
    await setupHomePage(page2);
    await joinGame(page2, "player2", gameName);

    // Wait for player2 to appear in player1's players menu
    await page.waitForSelector('[data-player="player2"]', { timeout: TIMEOUT });

    // Verify player2 is connected in players menu
    const player2MenuCard = page.locator('[data-player="player2"]').first();
    await expect(player2MenuCard).toBeVisible();
    await expect(player2MenuCard).toHaveAttribute("data-status", "connected");

    // Verify no disconnected overlay initially
    const player2DisconnectedOverlay = player2MenuCard.locator('div[class*="gray-overlay"]').first();
    await expect(player2DisconnectedOverlay).not.toBeVisible();
    await screenshot(page, "both-players-connected");

    // Close player2's session to trigger disconnect
    await page2.close();

    // Wait for disconnection to propagate
    await page.waitForTimeout(500);

    // Verify player2 has disconnected status
    await expect(player2MenuCard).toHaveAttribute("data-status", "disconnected");

    // Verify disconnected overlay appears in players menu
    await expect(player2DisconnectedOverlay).toBeVisible();
    const disconnectedText = player2DisconnectedOverlay.locator('[class*="gray-overlay-text"]');
    await expect(disconnectedText).toBeVisible();

    // Verify player1 is still connected
    const player1MenuCard = page.locator('[data-player="player1"]').first();
    await expect(player1MenuCard).toHaveAttribute("data-status", "connected");
    const player1DisconnectedOverlay = player1MenuCard.locator('div[class*="gray-overlay"]').first();
    await expect(player1DisconnectedOverlay).not.toBeVisible();
    await screenshot(page, "player2-disconnected");
  } finally {
    // Cleanup: Delete game via API
    await deleteGameViaAPI(gameName);
  }
});
