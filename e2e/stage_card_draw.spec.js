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

  // Expand players to see character cards with effects
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight has the defense effect applied
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toHaveAttribute("data-effects", /defense_bonus/);

  // Minimize players after check
  const minimizeButton = page.getByRole("button", { name: "Minimize all players" });
  await minimizeButton.click();

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

  // Expand players to see character cards with effects
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify archer does NOT have attack bonus effect (card was restricted)
  const player1Div = page.locator('[data-player="player1"]');
  const archerCard = player1Div.locator('[data-player-cards] [data-character="archer"]');
  // Archer should not have attack_bonus effect from sacred_sword
  const effectsAttr = await archerCard.getAttribute("data-effects");
  if (effectsAttr) {
    expect(effectsAttr).not.toMatch(/attack_bonus/);
  }

  // Minimize players after check
  const minimizeButton = page.getByRole("button", { name: "Minimize all players" });
  await minimizeButton.click();

  // Cleanup
  await page2.close();
});

test("card_draw stage - knight draws golden_apple and heals", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with damaged knight having drawn golden_apple
  await createPresetGameViaAPI(gameName, "card_draw_knight_golden_apple");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-player]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Expand players to see knight's health before healing
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight starts at 1 health
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toContainText("[1/2]");

  // Verify golden_apple card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const goldenAppleCard = sharedArea.locator('[data-card="golden_apple"]');
  await expect(goldenAppleCard).toBeVisible();

  // Verify card details are displayed
  await expect(goldenAppleCard).toContainText("תפוח זהב"); // Golden Apple
  await expect(goldenAppleCard).toContainText("+1 לבריאות"); // +1 to health

  // Screenshot with both card and character health visible before selection
  await screenshot(page, "golden-apple-knight-before-heal");

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players again (state resets on stage transition) to see knight's health after healing
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expandButtonAfter.click();

  // Verify knight healed to 2 health
  await expect(knightCard).toContainText("[2/2]");
  await screenshot(page, "golden-apple-knight-after-heal");

  // Cleanup
  await page2.close();
});

test("card_draw stage - knight at max health draws golden_apple (no overheal)", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with knight at max health having drawn golden_apple
  await createPresetGameViaAPI(gameName, "card_draw_golden_apple_max_health");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-player]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Expand players to see knight's health before card
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight starts at max health (2/2)
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toContainText("[2/2]");

  // Verify golden_apple card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const goldenAppleCard = sharedArea.locator('[data-card="golden_apple"]');
  await expect(goldenAppleCard).toBeVisible();

  // Screenshot with both card and character health visible before selection
  await screenshot(page, "golden-apple-knight-max-health-before");

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players again (state resets on stage transition) to see knight's health after card
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expandButtonAfter.click();

  // Verify knight is still at max health (no overheal)
  await expect(knightCard).toContainText("[2/2]");
  await screenshot(page, "golden-apple-knight-max-health-after");

  // Cleanup
  await page2.close();
});
