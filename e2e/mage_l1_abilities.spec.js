import { createPresetGameViaAPI } from "./api_helpers.js";
import { test, expect, screenshot, joinGameViaUrl, waitForStage } from "./test_helpers.js";

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
