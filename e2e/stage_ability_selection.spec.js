import { createPresetGameViaAPI } from "./api_helpers.js";
import { test, expect, screenshot, joinGameViaUrl, waitForStage, TIMEOUT } from "./test_helpers.js";

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
test("ability_selection stage - knight L2 disarm: shows only disarm ability, routes to card_draw, turn ends", async ({
  page,
  gameName,
}) => {
  // Knight L2 has its own skill: disarm only (not L1's battle_howl)
  // Selects disarm → card_draw → draws second card → turn ends (character_select for player2)
  await createPresetGameViaAPI(gameName, "ability_selection_knight_l2");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-ability]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Only L2 skill (disarm) should be visible, not L1 (battle_howl)
  const battleHowlAbility = sharedArea.locator('[data-ability="battle_howl"]');
  const disarmAbility = sharedArea.locator('[data-ability="disarm"]');
  await expect(disarmAbility).toBeVisible();
  await expect(battleHowlAbility).not.toBeVisible();

  // No-ability card should also be visible
  const noAbilityCard = sharedArea.locator('[data-ability="no_ability"]');
  await expect(noAbilityCard).toBeVisible();

  // Click the disarm ability card and confirm
  await disarmAbility.click();
  await screenshot(page, "disarm-ability-selected");

  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Should go to card_draw stage (disarm draws extra card instead of attacking)
  await waitForStage(page, "card_draw", 10 * TIMEOUT);
  await screenshot(page, "disarm-second-card-draw-stage");

  // First click: draw a card from the deck
  const drawButton = page.getByRole("button", { name: "שלוף" });
  await expect(drawButton).toBeVisible();
  await expect(drawButton).toBeEnabled();
  await drawButton.click();

  // Wait for card to appear
  await page.waitForSelector("[data-card]", { timeout: 10 * TIMEOUT });
  await screenshot(page, "disarm-second-card-revealed");

  // Second click: confirm card selection → ends the turn
  await expect(drawButton).toBeEnabled();
  await drawButton.click();

  // Turn ends: should go to character_select (player2's turn)
  await waitForStage(page2, "character_select", 10 * TIMEOUT);
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

test("ability_selection stage - mage L2 shows two abilities (storm, dragon_breath)", async ({ page, gameName }) => {
  // Mage L2 has two abilities: storm and dragon_breath
  await createPresetGameViaAPI(gameName, "ability_selection_mage_l2");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-ability]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in ability_selection stage
  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Both L2 ability cards should be visible
  const stormAbility = sharedArea.locator('[data-ability="storm"]');
  const dragonBreathAbility = sharedArea.locator('[data-ability="dragon_breath"]');
  await expect(stormAbility).toBeVisible();
  await expect(dragonBreathAbility).toBeVisible();

  // Freeze (L1 ability) should NOT be visible
  const freezeAbility = sharedArea.locator('[data-ability="freeze"]');
  await expect(freezeAbility).not.toBeVisible();

  // No-ability card should also be visible
  const noAbilityCard = sharedArea.locator('[data-ability="no_ability"]');
  await expect(noAbilityCard).toBeVisible();

  await screenshot(page, "mage-l2-two-abilities-visible");

  // Cleanup
  await page2.close();
});

test("ability_selection stage - mage L2 selects storm, goes to opponent_selection", async ({ page, gameName }) => {
  // Storm has APPLY_TO_BATTLE_OPPONENT → goes directly to opponent_selection (no target pre-selection)
  await createPresetGameViaAPI(gameName, "ability_selection_mage_l2");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-ability]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Click the storm ability card
  const stormAbility = sharedArea.locator('[data-ability="storm"]');
  await stormAbility.click();
  await screenshot(page, "storm-ability-selected");

  // Confirm ability selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Storm should skip ability_opponent_selection and go directly to opponent_selection
  await waitForStage(page, "opponent_selection");
  await screenshot(page, "storm-routes-to-opponent-selection");

  // Verify opponent is available for battle selection
  const opponentPlayer = sharedArea.locator('[data-player="player2"]');
  await expect(opponentPlayer).toBeVisible();

  // Cleanup
  await page2.close();
});

test("ability_selection stage - mage L2 selects dragon_breath, goes to ability_opponent_selection", async ({
  page,
  gameName,
}) => {
  // Dragon Breath has APPLY_TO_SELECTED_OPPONENT → requires target selection first
  await createPresetGameViaAPI(gameName, "ability_selection_mage_l2");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-ability]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Click the dragon_breath ability card
  const dragonBreathAbility = sharedArea.locator('[data-ability="dragon_breath"]');
  await dragonBreathAbility.click();
  await screenshot(page, "dragon-breath-ability-selected");

  // Confirm ability selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Dragon Breath should go to ability_opponent_selection (target must be selected)
  await waitForStage(page, "ability_opponent_selection");
  await screenshot(page, "dragon-breath-routes-to-ability-opponent-selection");

  // Verify opponents are visible for target selection
  const opponentPlayer = sharedArea.locator('[data-player="player2"]');
  await expect(opponentPlayer).toBeVisible();

  // Cleanup
  await page2.close();
});

test("ability_item_selection stage - shows target's items and allows selecting which to neutralize", async ({
  page,
  gameName,
}) => {
  // Start at ability_item_selection stage: player1 used Dragon Breath on player2's knight
  // Player2's knight has metal_armor and sacred_sword
  await createPresetGameViaAPI(gameName, "ability_item_selection_dragon_breath");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Both item cards should be visible
  const metalArmor = sharedArea.locator('[data-card="metal_armor"]');
  const sacredSword = sharedArea.locator('[data-card="sacred_sord"]');
  await expect(metalArmor).toBeVisible();
  await expect(sacredSword).toBeVisible();
  await screenshot(page, "item-selection-both-items-visible");

  // Click to select metal_armor and wait for selection to be reflected in UI
  await metalArmor.click();
  await expect(metalArmor).toHaveClass(/selected/);
  await screenshot(page, "item-selection-metal-armor-selected");

  // Confirm item selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Should transition to opponent_selection
  await waitForStage(page, "opponent_selection");
  await screenshot(page, "item-selection-transitions-to-opponent-selection");

  // Cleanup
  await page2.close();
});

test("ability_item_selection stage - dragon_breath full flow: select target, select item, then opponent", async ({
  page,
  gameName,
}) => {
  // Full Dragon Breath flow: ability_selection → ability_opponent_selection → ability_item_selection → opponent_selection
  await createPresetGameViaAPI(gameName, "ability_selection_mage_l2");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-ability]");

  // Player2 joins (knight has metal_armor from L1 preset; give them items via preset)
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Select dragon_breath ability
  const dragonBreathAbility = sharedArea.locator('[data-ability="dragon_breath"]');
  await dragonBreathAbility.click();
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Wait for ability_opponent_selection
  await waitForStage(page, "ability_opponent_selection");
  await screenshot(page, "dragon-breath-full-flow-opponent-selection");

  // Click on player2's knight
  const opponentPlayer = sharedArea.locator('[data-player="player2"]');
  await expect(opponentPlayer).toBeVisible();

  // Cleanup
  await page2.close();
});
