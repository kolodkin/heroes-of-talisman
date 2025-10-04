import { test, expect } from "@playwright/test";
import { createGameViaAPI, deleteGameViaAPI } from "./api_helpers.js";
import { TIMEOUT, screenshot, setupHomePage, joinGame } from "./test-helpers.js";

test("test players menu minified", async ({ page }) => {
  const testName = "players-menu-minified";
  const gameName = `test-${testName}`;

  // Setup: Create game via API
  await deleteGameViaAPI(gameName); // Clean up if exists
  await createGameViaAPI(gameName);

  try {
    // Navigate to home and join game
    await setupHomePage(page);
    await joinGame(page, "player", gameName);
    await screenshot(page, "001-joined-game");

    // Wait for player div to be visible
    const playerDiv = page.locator('[data-player="player"]');
    await expect(playerDiv).toBeVisible();

    // Verify initial state - player menu is expanded (character cards visible)
    await expect(playerDiv.getByAltText("knight")).toBeVisible();
    await expect(playerDiv.getByAltText("archer")).toBeVisible();
    await expect(playerDiv.getByAltText("mage")).toBeVisible();
    await screenshot(page, "002-player-expanded");

    // Find and verify the toggle button exists and shows "−" (expanded state)
    const toggleButton = playerDiv.getByRole("button", { name: /minimize|expand/i });
    await expect(toggleButton).toBeVisible();
    await expect(toggleButton).toHaveText("−");
    await screenshot(page, "003-toggle-button-visible");

    // Click toggle button to minimize
    await toggleButton.click();
    await screenshot(page, "004-after-minimize-click");

    // Verify minimized state
    // Toggle button should now show "+"
    await expect(toggleButton).toHaveText("+");

    // Character cards (images) should not be visible
    await expect(playerDiv.getByAltText("knight")).not.toBeVisible();
    await expect(playerDiv.getByAltText("archer")).not.toBeVisible();
    await expect(playerDiv.getByAltText("mage")).not.toBeVisible();

    // Character names and levels should still be visible (in minimized format)
    await expect(playerDiv.getByText(/אביר/)).toBeVisible(); // knight in Hebrew
    await expect(playerDiv.getByText(/קשת/)).toBeVisible(); // archer in Hebrew
    await expect(playerDiv.getByText(/קוסם/)).toBeVisible(); // mage in Hebrew
    await expect(playerDiv.getByText(/דרגה 1/).first()).toBeVisible(); // level 1
    await screenshot(page, "005-player-minimized");

    // Click toggle button again to expand
    await toggleButton.click();
    await screenshot(page, "006-after-expand-click");

    // Verify expanded state again
    await expect(toggleButton).toHaveText("−");
    await expect(playerDiv.getByAltText("knight")).toBeVisible();
    await expect(playerDiv.getByAltText("archer")).toBeVisible();
    await expect(playerDiv.getByAltText("mage")).toBeVisible();
    await screenshot(page, "007-player-expanded-again");

    // Add a second player to test multiple players
    const page2 = await page.context().newPage();
    await setupHomePage(page2);
    await joinGame(page2, "player2", gameName);

    // Wait for player2's div to be visible on both pages
    await page.waitForSelector('[data-player="player2"]', { timeout: TIMEOUT });
    await page2.waitForSelector('[data-player="player2"]', { timeout: TIMEOUT });
    await screenshot(page, "008-player2-joined-page1");
    await screenshot(page2, "009-player2-joined-page2");

    // Test minimizing/expanding player2's menu independently
    const player2Div = page.locator('[data-player="player2"]');
    const toggleButton2 = player2Div.getByRole("button", { name: /minimize|expand/i });

    await expect(toggleButton2).toHaveText("−");
    await toggleButton2.click();
    await screenshot(page, "010-player2-minimized");

    // Verify player2 is minimized but player1 is still expanded
    await expect(toggleButton2).toHaveText("+");
    await expect(player2Div.getByAltText("knight")).not.toBeVisible();
    await expect(playerDiv.getByAltText("knight")).toBeVisible(); // player1 still expanded
    await screenshot(page, "011-mixed-states");

    // Clean up
    await page2.close();
  } finally {
    // Cleanup: Delete game via API
    await deleteGameViaAPI(gameName);
  }
});
