import { test, expect, screenshot, waitForStage, setupPresetGame } from "./test_helpers.js";

test("ability_selection stage - archer (BOUNCING_ARROW) skips to opponent_selection", async ({ page, gameName }) => {
  // Create preset game at ability_selection stage with archer selected
  const page2 = await setupPresetGame(page, gameName, "ability_selection_archer", "[data-ability]");

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
