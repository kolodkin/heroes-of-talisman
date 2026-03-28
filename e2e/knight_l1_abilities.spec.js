import { test, expect, screenshot, waitForStage, setupPresetGame } from "./test_helpers.js";

test("ability_selection stage - knight (BATTLE_HOWL) skips to opponent_selection", async ({ page, gameName }) => {
  // Create preset game at ability_selection stage with knight selected
  const page2 = await setupPresetGame(page, gameName, "ability_selection_knight", "[data-ability]");

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

test("ability_selection stage - no ability option skips to opponent_selection", async ({ page, gameName }) => {
  // Player selects "ללא יכולת" (no ability) and goes directly to opponent_selection
  const page2 = await setupPresetGame(page, gameName, "ability_selection_knight", "[data-ability]");

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
