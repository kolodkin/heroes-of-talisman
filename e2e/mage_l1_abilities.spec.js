import { test, expect, screenshot, waitForStage, setupPresetGame } from "./test_helpers.js";

test("ability_selection stage - mage (FREEZE) goes to ability_opponent_selection", async ({ page, gameName }) => {
  // Create preset game at ability_selection stage with mage selected
  const page2 = await setupPresetGame(page, gameName, "ability_selection_mage", "[data-ability]");

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
