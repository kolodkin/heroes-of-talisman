import { createPresetGameViaAPI } from "./api_helpers.js";
import { test, expect, screenshot, joinGameViaUrl } from "./test_helpers.js";

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

test("character_select stage - knight not alive", async ({ page, gameName }) => {
  // Create preset game with knight dead
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
});

test("character_select stage - mage not alive", async ({ page, gameName }) => {
  // Create preset game with mage dead
  await createPresetGameViaAPI(gameName, "mage_not_alive");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-character]");

  // Verify mage is dead and not clickable
  await verifyCharacterNotClickable(page, "mage", "mage-not-alive-before-click");

  // Verify knight is alive and clickable
  await verifyCharacterClickable(page, "knight");

  await screenshot(page, "mage-not-alive-after-select");
});

test("character_select stage - archer not alive", async ({ page, gameName }) => {
  // Create preset game with archer dead
  await createPresetGameViaAPI(gameName, "archer_not_alive");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-character]");

  // Verify archer is dead and not clickable
  await verifyCharacterNotClickable(page, "archer", "archer-not-alive-before-click");

  // Verify knight is alive and clickable
  await verifyCharacterClickable(page, "knight");

  await screenshot(page, "archer-not-alive-after-select");
});

test("character_select stage - knight has skip_turn effect", async ({ page, gameName }) => {
  // Create preset game with knight having skip_turn effect
  await createPresetGameViaAPI(gameName, "effect_skip_turn");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-character]");

  // Verify we're in character_select stage
  await expect(page.locator('[data-character="knight"]').first()).toBeVisible();
  await expect(page.locator('[data-character="mage"]').first()).toBeVisible();
  await expect(page.locator('[data-character="archer"]').first()).toBeVisible();

  // Verify knight has skip_turn effect and is not clickable
  await verifyCharacterNotClickable(page, "knight", "knight-skip-turn-before-click");

  // Verify mage is alive and clickable
  await verifyCharacterClickable(page, "mage");

  await screenshot(page, "knight-skip-turn-after-select");
});

test("character_select stage - skip_turn effect removed after character selection", async ({ page, gameName }) => {
  // Create preset game with knight having skip_turn effect
  await createPresetGameViaAPI(gameName, "effect_skip_turn");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-character]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-player]");

  // Verify knight has skip_turn effect (data-effects attribute contains skip_turn)
  const knightCard = page.locator('[data-character="knight"]').last();
  await expect(knightCard).toHaveAttribute("data-effects", /skip_turn/);
  await screenshot(page, "knight-has-skip-turn-effect");

  // Select mage (knight can't be selected due to skip_turn)
  await verifyCharacterClickable(page, "mage");

  // Confirm selection with בחר button
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Wait for transition to ability_selection stage
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const freezeAbility = sharedArea.locator('[data-ability="freeze"]');
  await expect(freezeAbility).toBeVisible();

  // Verify knight no longer has skip_turn effect (effect was removed)
  // The data-effects attribute should no longer contain skip_turn
  await expect(knightCard).not.toHaveAttribute("data-effects", /skip_turn/);

  // Verify the ability is auto-selected (has 'selected' class)
  // Mage has only one ability (freeze), so it should be auto-selected
  await expect(freezeAbility).toHaveClass(/selected/);
  await screenshot(page, "skip-turn-removed-and-ability-selected");

  // Cleanup
  await page2.close();
});
