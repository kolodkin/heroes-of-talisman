import { createPresetGameViaAPI } from "./api_helpers.js";
import { test, expect, screenshot, joinGameViaUrl, waitForStage } from "./test_helpers.js";

/**
 * Tests for card draw stage functionality using presets.
 *
 * Tests cover:
 * - Successful card draw and application (knight + metal_armor)
 * - Restricted card handling (archer + sacred_sword)
 */

test("card_draw stage - knight draws metal_armor successfully", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with knight having drawn metal_armor
  await createPresetGameViaAPI(gameName, "card_draw_knight_metal_armor");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-player]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Verify metal_armor card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const metalArmorCard = sharedArea.locator('[data-card="metal_armor"]');
  await expect(metalArmorCard).toBeVisible();
  await screenshot(page, "card-draw-knight-metal-armor");

  // Verify card details are displayed
  await expect(metalArmorCard).toContainText("שריון מתכת"); // Metal Armor
  await expect(metalArmorCard).toContainText("+2 להגנה"); // +2 to defense

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");
  await screenshot(page, "card-selected-transition-to-ability");

  // Verify knight has the defense effect applied
  const knightCard = page.locator('[data-character="knight"]').last();
  await expect(knightCard).toHaveAttribute("data-effects", /defense_bonus/);

  // Cleanup
  await page2.close();
});

test("card_draw stage - archer draws sacred_sword (restricted)", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with archer having drawn sacred_sword
  await createPresetGameViaAPI(gameName, "card_draw_archer_sacred_sword");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-player]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Verify sacred_sword card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const sacredSwordCard = sharedArea.locator('[data-card="sacred_sord"]'); // Note: typo in card name
  await expect(sacredSwordCard).toBeVisible();
  await screenshot(page, "card-draw-archer-sacred-sword-restricted");

  // Verify card details are displayed
  await expect(sacredSwordCard).toContainText("חרב קדושה"); // Sacred Sword
  await expect(sacredSwordCard).toContainText("+3 להתקפה"); // +3 to attack

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage even though card is restricted
  await waitForStage(page, "ability_selection");
  await screenshot(page, "restricted-card-transition-to-ability");

  // Verify archer does NOT have attack bonus effect (card was restricted)
  const archerCard = page.locator('[data-character="archer"]').last();
  // Archer should not have attack_bonus effect from sacred_sword
  const effectsAttr = await archerCard.getAttribute("data-effects");
  if (effectsAttr) {
    expect(effectsAttr).not.toMatch(/attack_bonus/);
  }

  // Cleanup
  await page2.close();
});
