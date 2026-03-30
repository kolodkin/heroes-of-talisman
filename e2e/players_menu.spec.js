import { createGameViaAPI } from "./api_helpers.js";
import { test, expect, TIMEOUT, screenshot, setupHomePage, joinGame, dismissToasts } from "./test_helpers.js";

test("players menu minimized by default on desktop with expand minimize and collapse", async ({
  page,
  gameName,
}, testInfo) => {
  // Skip on mobile - desktop-only test
  if (testInfo.project.name === "mobile-landscape") {
    test.skip();
    return;
  }
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

  // Find the header buttons
  const playersHeader = page.locator('[class*="players-header"]');
  const expandMinimizeButton = playersHeader.getByRole("button", { name: /minimize|expand/i });
  const collapseButton = playersHeader.getByRole("button", { name: /collapse/i });
  await expect(expandMinimizeButton).toBeVisible();
  await expect(collapseButton).toBeVisible();

  // Verify initial state - player menu is MINIMIZED by default on desktop (toggle shows "+")
  await expect(expandMinimizeButton).toHaveText("+");
  await screenshot(page, "player-minimized-by-default");

  // Character cards (images) should not be visible in minimized state
  await expect(playerDiv.getByAltText("knight")).not.toBeVisible();
  await expect(playerDiv.getByAltText("archer")).not.toBeVisible();
  await expect(playerDiv.getByAltText("mage")).not.toBeVisible();

  // Character names and levels should be visible (in minimized format)
  await expect(playerDiv.getByText(/אביר/)).toBeVisible(); // knight in Hebrew
  await expect(playerDiv.getByText(/קשת/)).toBeVisible(); // archer in Hebrew
  await expect(playerDiv.getByText(/קוסם/)).toBeVisible(); // mage in Hebrew
  await expect(playerDiv.getByText(/דרגה 1/).first()).toBeVisible(); // level 1

  // Dismiss any lingering connection toast before clicking
  await dismissToasts(page);

  // Click expand/minimize button to expand all players
  await expandMinimizeButton.click();

  // Verify expanded state
  await expect(expandMinimizeButton).toHaveText("−");
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
  await expandMinimizeButton.click();
  await screenshot(page, "all-players-minimized");

  // Verify BOTH players are now minimized
  await expect(expandMinimizeButton).toHaveText("+");
  await expect(playerDiv.getByAltText("knight")).not.toBeVisible();
  await expect(player2Div.getByAltText("knight")).not.toBeVisible();

  // Character names should still be visible for both players
  await expect(playerDiv.getByText(/אביר/)).toBeVisible();
  await expect(player2Div.getByText(/אביר/)).toBeVisible();

  // Click toggle again to expand ALL players
  await expandMinimizeButton.click();
  await screenshot(page, "all-players-expanded");

  // Verify BOTH players are now expanded
  await expect(expandMinimizeButton).toHaveText("−");
  await expect(playerDiv.getByAltText("knight")).toBeVisible();
  await expect(player2Div.getByAltText("knight")).toBeVisible();

  // Test collapse: click the collapse arrow button
  await collapseButton.click();

  // Players container should be hidden
  await expect(page.locator('[class*="players-container"]')).not.toBeVisible();

  // Expand overlay button should appear in the shared area
  const expandOverlay = page.locator("[data-expand-button]");
  await expect(expandOverlay).toBeVisible();
  await screenshot(page, "players-collapsed");

  // Click expand overlay to restore menu
  await expandOverlay.click();

  // Players container should be visible again in minimized state
  await expect(page.locator('[class*="players-container"]')).toBeVisible();
  await expect(expandOverlay).not.toBeVisible();
  await screenshot(page, "players-restored-from-collapse");

  // Clean up
  await page2.close();
});

test("players menu collapsed by default on mobile landscape", async ({ page, gameName, browserName }, testInfo) => {
  // Skip this test for non-mobile projects
  if (testInfo.project.name !== "mobile-landscape") {
    test.skip();
    return;
  }

  // Setup: Create game via API
  const createdGame = await createGameViaAPI(gameName);

  // Navigate to home and join game
  await setupHomePage(page);
  await page.waitForSelector(`button:has-text("${gameName}")`, { timeout: TIMEOUT });
  await joinGame(page, "player", gameName);

  // On mobile landscape, players menu should be collapsed by default
  await expect(page.locator('[data-players-menu-state="collapsed"]')).toBeVisible();
  await expect(page.locator('[class*="players-container"]')).not.toBeVisible();

  // Expand overlay button should be visible
  const expandOverlay = page.locator("[data-expand-button]");
  await expect(expandOverlay).toBeVisible();
  await screenshot(page, "mobile-collapsed-default");

  // Click expand to show the menu
  await expandOverlay.click();

  // Players container should now be visible
  await expect(page.locator('[class*="players-container"]')).toBeVisible();
  await expect(expandOverlay).not.toBeVisible();

  const playerDiv = page.locator('[data-player="player"]');
  await expect(playerDiv).toBeVisible();
  await screenshot(page, "mobile-menu-expanded");

  // Collapse it again via the collapse button
  const collapseButton = page.locator("[data-collapse-button]");
  await collapseButton.click();

  await expect(page.locator('[class*="players-container"]')).not.toBeVisible();
  await expect(expandOverlay).toBeVisible();
  await screenshot(page, "mobile-collapsed-again");
});
