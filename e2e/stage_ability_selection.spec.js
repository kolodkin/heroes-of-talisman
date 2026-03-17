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
test("ability_selection stage - knight L2 shows both abilities (battle_howl and disarm)", async ({
  page,
  gameName,
}) => {
  // Knight L2 has two abilities: battle_howl and disarm (no auto-select)
  await createPresetGameViaAPI(gameName, "ability_selection_knight_l2");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-ability]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in ability_selection stage
  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Both ability cards should be visible
  const battleHowlAbility = sharedArea.locator('[data-ability="battle_howl"]');
  const disarmAbility = sharedArea.locator('[data-ability="disarm"]');
  await expect(battleHowlAbility).toBeVisible();
  await expect(disarmAbility).toBeVisible();

  // No-ability card should also be visible
  const noAbilityCard = sharedArea.locator('[data-ability="no_ability"]');
  await expect(noAbilityCard).toBeVisible();

  await screenshot(page, "knight-l2-both-abilities-visible");

  // Cleanup
  await page2.close();
});

test("ability_selection stage - knight L2 selects disarm, goes to card_draw", async ({ page, gameName }) => {
  // Knight L2 selects disarm → instead of attacking, draw another card (card_draw stage)
  await createPresetGameViaAPI(gameName, "ability_selection_knight_l2");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-ability]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Click the disarm ability card
  const disarmAbility = sharedArea.locator('[data-ability="disarm"]');
  await disarmAbility.click();
  await screenshot(page, "disarm-ability-selected");

  // Confirm ability selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Should go to card_draw stage (disarm draws extra card instead of attacking)
  await waitForStage(page, "card_draw", 5000);
  await screenshot(page, "disarm-routes-to-card-draw");

  // Cleanup
  await page2.close();
});

test("ability_selection stage - disarm full flow: draw second card then turn ends", async ({ page, gameName }) => {
  // Knight L2 selects disarm → card_draw → draws second card → turn ends (character_select for player2)
  await createPresetGameViaAPI(gameName, "ability_selection_knight_l2");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-ability]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Select disarm and confirm
  const disarmAbility = sharedArea.locator('[data-ability="disarm"]');
  await disarmAbility.click();
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Wait for second card_draw stage
  await waitForStage(page, "card_draw", 5000);
  await screenshot(page, "disarm-second-card-draw-stage");

  // First click: draw a card from the deck
  const drawButton = page.getByRole("button", { name: "שלוף" });
  await expect(drawButton).toBeVisible();
  await expect(drawButton).toBeEnabled();
  await drawButton.click();

  // Wait for card to appear
  await page.waitForSelector("[data-card]", { timeout: 3000 });
  await screenshot(page, "disarm-second-card-revealed");

  // Second click: confirm card selection → ends the turn
  await expect(drawButton).toBeEnabled();
  await drawButton.click();

  // Turn ends: should go to character_select (player2's turn)
  await waitForStage(page2, "character_select", 5000);
  await screenshot(page2, "disarm-turn-ended-player2-turn");

  // Cleanup
  await page2.close();
});

test("ability_selection stage - no ability option skips to opponent_selection", async ({ page, gameName }) => {
  // Player selects "ללא יכולת" (no ability) and goes directly to opponent_selection
  await createPresetGameViaAPI(gameName, "ability_selection_knight");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-ability]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // The "no ability" card should be visible as the last option
  const noAbilityCard = sharedArea.locator('[data-ability="no_ability"]');
  await expect(noAbilityCard).toBeVisible();
  await expect(noAbilityCard).toContainText("ללא יכולת");
  await screenshot(page, "no-ability-card-visible");

  // Click no ability card
  await noAbilityCard.click();
  await screenshot(page, "no-ability-card-selected");

  // Confirm selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Should go directly to opponent_selection (skipping battle preparation)
  await waitForStage(page, "opponent_selection", 5000);
  await screenshot(page, "no-ability-went-to-opponent-selection");

  // Verify opponent selection is available
  const opponentPlayer = sharedArea.locator('[data-player="player2"]');
  await expect(opponentPlayer).toBeVisible();

  // Cleanup
  await page2.close();
});
