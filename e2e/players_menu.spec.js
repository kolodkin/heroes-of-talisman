import { createGameViaAPI } from "./api_helpers.js";
import { test, expect, TIMEOUT, screenshot, setupHomePage, joinGame } from "./test_helpers.js";

test("players menu minified by default with global toggle", async ({ page, gameName }) => {
  // Setup: Create game via API
  const createdGame = await createGameViaAPI(gameName);

  // Navigate to home and join game
  await setupHomePage(page);

  // Verify the game button is available before trying to join
  await page.waitForSelector(`button:has-text("${gameName}")`, { timeout: TIMEOUT });

  await joinGame(page, "player", gameName);

  // Wait for player div to be visible
  const playerDiv = page.locator('[data-player="player"]');
  await expect(playerDiv).toBeVisible();

  // Find the global toggle button in the players header
  const playersHeader = page.locator('[class*="players-header"]');
  const toggleButton = playersHeader.getByRole("button", { name: /minimize|expand/i });
  await expect(toggleButton).toBeVisible();

  // Verify initial state - player menu is MINIFIED by default (toggle shows "+")
  await expect(toggleButton).toHaveText("+");
  await screenshot(page, "player-minimized-by-default");

  // Character cards (images) should not be visible in minified state
  await expect(playerDiv.getByAltText("knight")).not.toBeVisible();
  await expect(playerDiv.getByAltText("archer")).not.toBeVisible();
  await expect(playerDiv.getByAltText("mage")).not.toBeVisible();

  // Character names and levels should be visible (in minimized format)
  await expect(playerDiv.getByText(/אביר/)).toBeVisible(); // knight in Hebrew
  await expect(playerDiv.getByText(/קשת/)).toBeVisible(); // archer in Hebrew
  await expect(playerDiv.getByText(/קוסם/)).toBeVisible(); // mage in Hebrew
  await expect(playerDiv.getByText(/דרגה 1/).first()).toBeVisible(); // level 1

  // Click toggle button to expand all players
  await toggleButton.click();

  // Verify expanded state
  await expect(toggleButton).toHaveText("−");
  await expect(playerDiv.getByAltText("knight")).toBeVisible();
  await expect(playerDiv.getByAltText("archer")).toBeVisible();
  await expect(playerDiv.getByAltText("mage")).toBeVisible();
  await screenshot(page, "player-expanded");

  // Add a second player to test global toggle affects all players
  const page2 = await page.context().newPage();
  await setupHomePage(page2);
  await joinGame(page2, "player2", gameName);

  // Wait for player2's div to be visible on both pages
  await page.waitForSelector('[data-player="player2"]', { timeout: TIMEOUT });
  await page2.waitForSelector('[data-player="player2"]', { timeout: TIMEOUT });
  await screenshot(page, "player2-joined-page1");
  await screenshot(page2, "player2-joined-page2");

  // Verify both players are expanded (toggle still shows "−" since we expanded earlier)
  const player2Div = page.locator('[data-player="player2"]');
  await expect(player2Div.getByAltText("knight")).toBeVisible();
  await expect(playerDiv.getByAltText("knight")).toBeVisible();

  // Click toggle to minimize ALL players globally
  await toggleButton.click();
  await screenshot(page, "all-players-minimized");

  // Verify BOTH players are now minimized
  await expect(toggleButton).toHaveText("+");
  await expect(playerDiv.getByAltText("knight")).not.toBeVisible();
  await expect(player2Div.getByAltText("knight")).not.toBeVisible();

  // Character names should still be visible for both players
  await expect(playerDiv.getByText(/אביר/)).toBeVisible();
  await expect(player2Div.getByText(/אביר/)).toBeVisible();

  // Click toggle again to expand ALL players
  await toggleButton.click();
  await screenshot(page, "all-players-expanded");

  // Verify BOTH players are now expanded
  await expect(toggleButton).toHaveText("−");
  await expect(playerDiv.getByAltText("knight")).toBeVisible();
  await expect(player2Div.getByAltText("knight")).toBeVisible();

  // Clean up
  await page2.close();
});
