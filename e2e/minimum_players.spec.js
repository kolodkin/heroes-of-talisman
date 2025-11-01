import { createPresetGameViaAPI } from "./api_helpers.js";
import { test, expect, screenshot } from "./test_helpers.js";

test("minimum player overlay appears with single player", async ({ page, gameName }) => {
  const playerName = "player1";

  // Setup: Create game with only one player using single_player preset
  await createPresetGameViaAPI(gameName, "single_player");

  // Navigate to the game
  await page.goto(`http://localhost:5173/games/${gameName}/${playerName}`);
  await page.waitForSelector("[data-minimum-player-overlay]", { timeout: 5000 });
  await screenshot(page, "single-player-overlay-visible");

  // Verify the overlay is visible
  const overlay = page.locator("[data-minimum-player-overlay]");
  await expect(overlay).toBeVisible();

  // Verify the overlay text is present (Hebrew translation)
  await expect(overlay).toContainText("צריך לפחות שני שחקנים במשחק כדי שניתן יהיה להתחיל את המשחק");

  // Verify the overlay has the correct styling (gray-overlay class)
  const overlayClass = await overlay.getAttribute("class");
  expect(overlayClass).toContain("gray-overlay");

  // Verify the shared area is still visible but blocked by overlay
  const sharedArea = page.locator("[data-shared-area-active]");
  await expect(sharedArea).toBeVisible();

  // Verify stage title is visible behind the overlay
  const stageTitle = page.locator('h2:has-text("בחר דמות")');
  await expect(stageTitle).toBeVisible();

  await screenshot(page, "single-player-overlay-final");
});

test("minimum player overlay not present with two players", async ({ page, gameName }) => {
  const playerName = "player1";

  // Setup: Create game with knight_not_alive preset (has 2 players)
  await createPresetGameViaAPI(gameName, "knight_not_alive");

  // Navigate to the game
  await page.goto(`http://localhost:5173/games/${gameName}/${playerName}`);
  await page.waitForSelector('h2:has-text("בחר דמות")', { timeout: 5000 });
  await screenshot(page, "two-players-no-overlay");

  // Verify the overlay is NOT visible
  const overlay = page.locator("[data-minimum-player-overlay]");
  await expect(overlay).not.toBeVisible();

  // Verify the shared area is interactive (active player can see content)
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  await expect(sharedArea).toBeVisible();

  // Verify character cards are visible and accessible
  const characterCard = page.locator('[data-character="knight"]').first();
  await expect(characterCard).toBeVisible();

  await screenshot(page, "two-players-interactive");
});
