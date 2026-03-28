import { createPresetGameViaAPI } from "./api_helpers.js";
import { test, expect, screenshot, joinGameViaUrl, waitForStage } from "./test_helpers.js";

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
  // Player2's knight has metal_armor and sacred_sword so dragon_breath triggers item selection
  await createPresetGameViaAPI(gameName, "ability_selection_mage_l2_with_items");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-ability]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Select dragon_breath ability and confirm
  const dragonBreathAbility = sharedArea.locator('[data-ability="dragon_breath"]');
  await dragonBreathAbility.click();
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Wait for ability_opponent_selection
  await waitForStage(page, "ability_opponent_selection");
  await screenshot(page, "dragon-breath-full-flow-opponent-selection");

  // Click on player2's knight and confirm
  const knightChar = sharedArea.locator('[data-player="player2"] [data-character="knight"]');
  await knightChar.click();
  await selectButton.click();

  // Player2's knight has items → should go to ability_item_selection
  await waitForStage(page, "ability_item_selection");
  await screenshot(page, "dragon-breath-full-flow-item-selection");

  // Select metal_armor and confirm
  const metalArmor = sharedArea.locator('[data-card="metal_armor"]');
  await metalArmor.click();
  await expect(metalArmor).toHaveClass(/selected/);
  await selectButton.click();

  // Should transition to opponent_selection
  await waitForStage(page, "opponent_selection");
  await screenshot(page, "dragon-breath-full-flow-complete");

  // Cleanup
  await page2.close();
});
