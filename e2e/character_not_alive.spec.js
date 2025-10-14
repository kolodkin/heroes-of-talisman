import { test, expect } from "@playwright/test";
import { screenshot, joinGameViaUrl } from "./test-helpers.js";
import { createPresetGameViaAPI, deleteGameViaAPI } from "./api_helpers.js";

/**
 * Helper to verify character is not clickable (not alive)
 * Targets the main character card (not the minimized one)
 */
async function verifyCharacterNotClickable(page, characterName, screenshotName) {
  // Target the larger character card (not the minimized one)
  const character = page.locator(`[data-character="${characterName}"]`).last();
  await expect(character).toBeVisible();

  // Take screenshot before clicking to show the not-alive state
  if (screenshotName) {
    await screenshot(page, screenshotName);
  }

  // Try to click the character
  await character.click({ force: true });

  // Wait a bit to see if any selection happens
  await page.waitForTimeout(100);

  // Verify the character has "not-alive" class and is not selected
  await expect(character).toHaveClass(/not-alive/);
}

/**
 * Helper to verify character is clickable (alive) and select it
 * Targets the main character card (not the minimized one)
 */
async function verifyCharacterClickable(page, characterName) {
  // Target the larger character card (not the minimized one)
  const character = page.locator(`[data-character="${characterName}"]`).last();
  await expect(character).toBeVisible();

  // Character should have "alive" class
  await expect(character).toHaveClass(/alive/);

  // Click the character
  await character.click();

  // Wait for selection to register
  await page.waitForTimeout(100);

  // Verify character is now selected
  await expect(character).toHaveClass(/selected/);
}

test("character_select stage - knight not alive", async ({ page }) => {
  const gameName = "knight_not_alive_test";

  // Create preset game with knight dead
  await deleteGameViaAPI(gameName);
  await createPresetGameViaAPI(gameName, "knight_not_alive");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-character]");

  // Verify we're in character_select stage
  await expect(page.locator('[data-character="knight"]').first()).toBeVisible();
  await expect(page.locator('[data-character="mage"]').first()).toBeVisible();
  await expect(page.locator('[data-character="archer"]').first()).toBeVisible();

  // Verify knight is dead and not clickable
  await verifyCharacterNotClickable(page, "knight", "knight-not-alive-before-click");

  // Verify mage is alive and clickable
  await verifyCharacterClickable(page, "mage");

  await screenshot(page, "knight-not-alive-after-select");

  // Cleanup
  await deleteGameViaAPI(gameName);
});

test("character_select stage - mage not alive", async ({ page }) => {
  const gameName = "mage_not_alive_test";

  // Create preset game with mage dead
  await deleteGameViaAPI(gameName);
  await createPresetGameViaAPI(gameName, "mage_not_alive");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-character]");

  // Verify mage is dead and not clickable
  await verifyCharacterNotClickable(page, "mage", "mage-not-alive-before-click");

  // Verify knight is alive and clickable
  await verifyCharacterClickable(page, "knight");

  await screenshot(page, "mage-not-alive-after-select");

  // Cleanup
  await deleteGameViaAPI(gameName);
});

test("character_select stage - archer not alive", async ({ page }) => {
  const gameName = "archer_not_alive_test";

  // Create preset game with archer dead
  await deleteGameViaAPI(gameName);
  await createPresetGameViaAPI(gameName, "archer_not_alive");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-character]");

  // Verify archer is dead and not clickable
  await verifyCharacterNotClickable(page, "archer", "archer-not-alive-before-click");

  // Verify knight is alive and clickable
  await verifyCharacterClickable(page, "knight");

  await screenshot(page, "archer-not-alive-after-select");

  // Cleanup
  await deleteGameViaAPI(gameName);
});
