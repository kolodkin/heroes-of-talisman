import { test, expect, screenshot, waitForStage, setupPresetGame, waitForToast } from "./test_helpers.js";

test("ability_selection stage - mage L3 shows two abilities (mind_reading, drain)", async ({ page, gameName }) => {
  // Mage L3 has two abilities: mind_reading and drain
  const page2 = await setupPresetGame(page, gameName, "ability_selection_mage_l3", "[data-ability]");

  // Verify we're in ability_selection stage
  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Both L3 ability cards should be visible
  const mindReadingAbility = sharedArea.locator('[data-ability="mind_reading"]');
  const drainAbility = sharedArea.locator('[data-ability="drain"]');
  await expect(mindReadingAbility).toBeVisible();
  await expect(drainAbility).toBeVisible();

  // L1/L2 abilities should NOT be visible
  const freezeAbility = sharedArea.locator('[data-ability="freeze"]');
  const stormAbility = sharedArea.locator('[data-ability="storm"]');
  const dragonBreathAbility = sharedArea.locator('[data-ability="dragon_breath"]');
  await expect(freezeAbility).not.toBeVisible();
  await expect(stormAbility).not.toBeVisible();
  await expect(dragonBreathAbility).not.toBeVisible();

  // No-ability card should also be visible
  const noAbilityCard = sharedArea.locator('[data-ability="no_ability"]');
  await expect(noAbilityCard).toBeVisible();

  await screenshot(page, "mage-l3-two-abilities-visible");

  // Cleanup
  await page2.close();
});

test("ability_selection stage - mage L3 selects mind_reading, goes to opponent_selection", async ({
  page,
  gameName,
}) => {
  // Mind reading has APPLY_TO_SELF -> goes directly to opponent_selection (no target pre-selection)
  const page2 = await setupPresetGame(page, gameName, "ability_selection_mage_l3", "[data-ability]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Click the mind_reading ability card
  const mindReadingAbility = sharedArea.locator('[data-ability="mind_reading"]');
  await mindReadingAbility.click();
  await screenshot(page, "mind-reading-ability-selected");

  // Confirm ability selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Mind reading should go directly to opponent_selection (self-target effect)
  await waitForStage(page, "opponent_selection");
  await screenshot(page, "mind-reading-routes-to-opponent-selection");

  // Cleanup
  await page2.close();
});

test("ability_selection stage - mage L3 selects drain, goes to ability_opponent_selection", async ({
  page,
  gameName,
}) => {
  // Drain has APPLY_TO_SELECTED_OPPONENT -> requires target selection first
  const page2 = await setupPresetGame(page, gameName, "ability_selection_mage_l3", "[data-ability]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Click the drain ability card
  const drainAbility = sharedArea.locator('[data-ability="drain"]');
  await drainAbility.click();
  await screenshot(page, "drain-ability-selected");

  // Confirm ability selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Drain should go to ability_opponent_selection (target must be selected)
  await waitForStage(page, "ability_opponent_selection");
  await screenshot(page, "drain-routes-to-ability-opponent-selection");

  // Verify opponents are visible for target selection
  const opponentPlayer = sharedArea.locator('[data-player="player2"]');
  await expect(opponentPlayer).toBeVisible();

  // Cleanup
  await page2.close();
});

test("drain full flow: select target, select item to borrow, then opponent_selection", async ({
  page,
  gameName,
}) => {
  // Full Drain flow: ability_selection -> ability_opponent_selection -> ability_item_selection -> opponent_selection
  // Player2's knight has metal_armor and sacred_sword so drain triggers item selection
  const page2 = await setupPresetGame(page, gameName, "ability_selection_mage_l3_with_items", "[data-ability]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Select drain ability and confirm
  const drainAbility = sharedArea.locator('[data-ability="drain"]');
  await drainAbility.click();
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Wait for ability_opponent_selection
  await waitForStage(page, "ability_opponent_selection");
  await screenshot(page, "drain-full-flow-opponent-selection");

  // Click on player2's knight (has items) and confirm
  const knightChar = sharedArea.locator('[data-player="player2"] [data-character="knight"]');
  await knightChar.click();
  await selectButton.click();

  // Player2's knight has items -> should go to ability_item_selection
  await waitForStage(page, "ability_item_selection");
  await screenshot(page, "drain-full-flow-item-selection");

  // Both item cards should be visible
  const metalArmor = sharedArea.locator('[data-card="metal_armor"]');
  const sacredSword = sharedArea.locator('[data-card="sacred_sord"]');
  await expect(metalArmor).toBeVisible();
  await expect(sacredSword).toBeVisible();

  // Select metal_armor and confirm
  await metalArmor.click();
  await expect(metalArmor).toHaveClass(/selected/);
  await selectButton.click();

  // Should transition to opponent_selection
  await waitForStage(page, "opponent_selection");
  await screenshot(page, "drain-full-flow-complete");

  // Cleanup
  await page2.close();
});

test("mind_reading protection - opponent cannot select mage as battle target", async ({ page, gameName }) => {
  // Player2's turn - player1's mage has mind_reading protection against player2
  // Player2 should not be able to select player1's mage as a battle target
  const page2 = await setupPresetGame(page, gameName, "mind_reading_opponent_blocked", "[data-character]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Switch to player2's view (active player)
  await screenshot(page2, "mind-reading-player2-opponent-selection");

  // Try to click on player1's mage (should be blocked by mind_reading)
  const mageChar = sharedArea.locator('[data-player="player1"] [data-character="mage"]');

  // Set up toast listener before clicking
  const toastPromise = waitForToast(page2, { type: "error" });
  await mageChar.click();
  await toastPromise;
  await screenshot(page2, "mind-reading-mage-click-blocked");

  // Player1's knight should still be selectable
  const knightChar = sharedArea.locator('[data-player="player1"] [data-character="knight"]');
  await knightChar.click();
  await screenshot(page2, "mind-reading-knight-selectable");

  // Cleanup
  await page2.close();
});
