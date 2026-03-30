import { createPresetGameViaAPI } from "./api_helpers.js";
import {
  test,
  expect,
  screenshot,
  joinGameViaUrl,
  waitForStage,
  expandPlayersMenuIfCollapsed,
  setupPresetGame,
} from "./test_helpers.js";

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

  // Verify character is now selected
  await expect(character).toHaveClass(/selected/);
}

const notAliveTestCases = [
  { preset: "knight_not_alive", deadChar: "knight", aliveChar: "mage" },
  { preset: "mage_not_alive", deadChar: "mage", aliveChar: "knight" },
  { preset: "archer_not_alive", deadChar: "archer", aliveChar: "knight" },
];

for (const { preset, deadChar, aliveChar } of notAliveTestCases) {
  test(`character_select stage - ${deadChar} not alive`, async ({ page, gameName }) => {
    await createPresetGameViaAPI(gameName, preset);

    await joinGameViaUrl(page, "player1", gameName, "[data-character]");

    await verifyCharacterNotClickable(page, deadChar, `${deadChar}-not-alive-before-click`);

    await verifyCharacterClickable(page, aliveChar);

    await screenshot(page, `${deadChar}-not-alive-after-select`);
  });
}

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
  // Use ability_selection_mage preset which is already past character_select (and card_draw)
  // This preset has mage selected, and any skip_turn effects should have been disposed
  const page2 = await setupPresetGame(page, gameName, "ability_selection_mage", "[data-ability]");

  // We should be at ability_selection stage
  await waitForStage(page, "ability_selection");
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const freezeAbility = sharedArea.locator('[data-ability="freeze"]');
  await expect(freezeAbility).toBeVisible();

  // Verify knight no longer has skip_turn effect (effect was disposed after character selection)
  // Expand players menu if collapsed (mobile)
  await expandPlayersMenuIfCollapsed(page);
  const knightCard = page.locator('[data-character="knight"]').last();
  await expect(knightCard).not.toHaveAttribute("data-effects", /skip_turn/);

  // Verify the ability is auto-selected (has 'selected' class)
  // Mage has only one ability (freeze), so it should be auto-selected
  await expect(freezeAbility).toHaveClass(/selected/);
  await screenshot(page, "skip-turn-removed-and-ability-selected");

  // Cleanup
  await page2.close();
});

test("character_select stage - no character available shows Skip Turn button", async ({ page, gameName }) => {
  // Create preset game where all characters are unavailable
  // (2 dead + 1 with skip_turn effect)
  await createPresetGameViaAPI(gameName, "skip_turn_no_character");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-character]");

  // Verify we're in character_select stage
  await waitForStage(page, "character_select");

  // Verify all characters are not clickable
  await verifyCharacterNotClickable(page, "knight"); // dead
  await verifyCharacterNotClickable(page, "archer"); // dead
  await verifyCharacterNotClickable(page, "mage"); // has skip_turn effect

  // Verify the Skip Turn button is shown (has data-skip-turn attribute)
  const skipTurnButton = page.locator("[data-skip-turn]");
  await expect(skipTurnButton).toBeVisible();

  await screenshot(page, "skip-turn-button-visible");
});

test("character_select stage - Skip Turn button passes turn to next player", async ({ page, gameName }) => {
  // Create preset game where all characters are unavailable
  const page2 = await setupPresetGame(page, gameName, "skip_turn_no_character", "[data-character]", "[data-character]");

  // Verify player1 is initially active
  await waitForStage(page, "character_select");
  const player1SharedArea = page.locator('[data-shared-area-active="true"]');
  await expect(player1SharedArea).toBeVisible();

  await screenshot(page, "before-skip-turn-player1-view");
  await screenshot(page2, "before-skip-turn-player2-view");

  // Click the Skip Turn button
  const skipTurnButton = page.locator("[data-skip-turn]");
  await skipTurnButton.click();

  // Wait for game update - player2 should now be active
  await page2.waitForSelector('[data-shared-area-active="true"]');

  // Verify player1's shared area is no longer active
  await expect(page.locator('[data-shared-area-active="true"]')).not.toBeVisible();

  // Verify player2's shared area is now active
  await expect(page2.locator('[data-shared-area-active="true"]')).toBeVisible();

  // Verify skip_turn effects were disposed from mage
  // (after character_select stage ends, effects with 'character_select' dispose action are removed)
  const mageCard = page.locator('[data-character="mage"]').last();
  await expect(mageCard).not.toHaveAttribute("data-effects", /skip_turn/);

  await screenshot(page, "after-skip-turn-player1-view");
  await screenshot(page2, "after-skip-turn-player2-view");

  // Cleanup
  await page2.close();
});
