import { createPresetGameViaAPI } from "./api_helpers.js";
import { test, expect, screenshot, joinGameViaUrl, waitForStage } from "./test_helpers.js";

/**
 * Tests for ability selection stage transitions.
 *
 * Only abilities with effects requiring target selection (e.g., FREEZE with SkipTurnEffect)
 * should transition to ability_opponent_selection stage.
 * Other abilities (BATTLE_HOWL, BOUNCING_ARROW) skip directly to opponent_selection.
 */

test("ability_selection stage - knight (BATTLE_HOWL) skips to opponent_selection", async ({ page, gameName }) => {
  // Create preset game at ability_selection stage with knight selected
  await createPresetGameViaAPI(gameName, "ability_selection_knight");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-ability]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in ability_selection stage
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const battleHowlAbility = sharedArea.locator('[data-ability="battle_howl"]');
  await expect(battleHowlAbility).toBeVisible();

  // Select battle_howl ability
  await battleHowlAbility.click();
  await screenshot(page, "ability-selected-battle-howl");

  // Confirm ability selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Should skip ability_opponent_selection and go directly to opponent_selection
  await waitForStage(page, "opponent_selection");
  await screenshot(page, "knight-skipped-to-opponent-selection");

  // Verify we're in opponent_selection (not ability_opponent_selection)
  // Opponents should be visible for battle selection
  const opponentPlayer = sharedArea.locator('[data-player="player2"]');
  await expect(opponentPlayer).toBeVisible();

  // Cleanup
  await page2.close();
});

test("ability_selection stage - archer (BOUNCING_ARROW) skips to opponent_selection", async ({ page, gameName }) => {
  // Create preset game at ability_selection stage with archer selected
  await createPresetGameViaAPI(gameName, "ability_selection_archer");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-ability]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in ability_selection stage
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const bouncingArrowAbility = sharedArea.locator('[data-ability="bouncing_arrow"]');
  await expect(bouncingArrowAbility).toBeVisible();

  // Select bouncing_arrow ability
  await bouncingArrowAbility.click();
  await screenshot(page, "ability-selected-bouncing-arrow");

  // Confirm ability selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Should skip ability_opponent_selection and go directly to opponent_selection
  await waitForStage(page, "opponent_selection");
  await screenshot(page, "archer-skipped-to-opponent-selection");

  // Verify we're in opponent_selection (not ability_opponent_selection)
  const opponentPlayer = sharedArea.locator('[data-player="player2"]');
  await expect(opponentPlayer).toBeVisible();

  // Cleanup
  await page2.close();
});

test("ability_selection stage - mage (FREEZE) goes to ability_opponent_selection", async ({ page, gameName }) => {
  // Create preset game at ability_selection stage with mage selected
  await createPresetGameViaAPI(gameName, "ability_selection_mage");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-ability]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in ability_selection stage
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const freezeAbility = sharedArea.locator('[data-ability="freeze"]');
  await expect(freezeAbility).toBeVisible();

  // Select freeze ability
  await freezeAbility.click();
  await screenshot(page, "ability-selected-freeze");

  // Confirm ability selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Should go to ability_opponent_selection (FREEZE requires target selection)
  await waitForStage(page, "ability_opponent_selection");
  await screenshot(page, "mage-went-to-ability-opponent-selection");

  // Verify we're in ability_opponent_selection stage
  // Opponents should be visible for ability target selection
  const opponentPlayer = sharedArea.locator('[data-player="player2"]');
  await expect(opponentPlayer).toBeVisible();

  // Cleanup
  await page2.close();
});
