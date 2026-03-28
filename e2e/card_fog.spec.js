import { createPresetGameViaAPI } from "./api_helpers.js";
import {
  test,
  expect,
  screenshot,
  joinGameViaUrl,
  waitForStage,
  expandPlayersMenuIfCollapsed,
} from "./test_helpers.js";

test("card_draw stage - knight draws fog card when all chars are level 3+ (no skip_turn, player resists fog)", async ({
  page,
  gameName,
}) => {
  // Create preset: player1 all chars at level 3 → player resists fog, NO skip_turn applied
  await createPresetGameViaAPI(gameName, "card_draw_fog_all_high_level");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Expand players to see characters before card selection
  await expandPlayersMenuIfCollapsed(page);
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify player1 characters are at level 3
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  const archerCard = player1Div.locator('[data-player-cards] [data-character="archer"]');
  const mageCard = player1Div.locator('[data-player-cards] [data-character="mage"]');
  await expect(knightCard).toHaveAttribute("data-level", "3");
  await expect(archerCard).toHaveAttribute("data-level", "3");
  await expect(mageCard).toHaveAttribute("data-level", "3");

  // Verify fog card is visible in the shared area
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const fogCard = sharedArea.locator('[data-card="fog"]');
  await expect(fogCard).toBeVisible();

  // Verify card details are displayed in Hebrew
  await expect(fogCard).toContainText("ערפל"); // Fog
  await expect(fogCard).toContainText("אובדן תור"); // Lost turn

  await screenshot(page, "fog-all-high-level-before");

  // Minimize players before card selection so we can expand again after
  const minimizeButton = page.getByRole("button", { name: "Minimize all players" });
  await minimizeButton.click();

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "שלוף" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage (no skip_turn, player resists fog)
  await waitForStage(page, "ability_selection");

  // Expand players to verify NO skip_turn was applied (all chars level 3+ resist fog)
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expandButtonAfter.click();

  await expect(knightCard).not.toHaveAttribute("data-effects", /skip_turn/);
  await expect(archerCard).not.toHaveAttribute("data-effects", /skip_turn/);
  await expect(mageCard).not.toHaveAttribute("data-effects", /skip_turn/);

  await screenshot(page, "fog-all-high-level-after");

  // Cleanup
  await page2.close();
});

test("card_draw stage - knight draws fog card with mixed levels (skip_turn applied)", async ({ page, gameName }) => {
  // Create preset: player1 has knight at level 3, others at level 1
  // Not ALL chars are level 3+ → fog applies skip_turn to all alive chars
  await createPresetGameViaAPI(gameName, "card_draw_fog_mixed_level");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Expand players to see character levels before drawing
  await expandPlayersMenuIfCollapsed(page);
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify fog card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const fogCard = sharedArea.locator('[data-card="fog"]');
  await expect(fogCard).toBeVisible();

  await screenshot(page, "fog-mixed-level-before");

  // Minimize players before card selection so we can expand again after
  const minimizeButton = page.getByRole("button", { name: "Minimize all players" });
  await minimizeButton.click();

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "שלוף" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players to verify skip_turn WAS applied to all player1's alive chars
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expandButtonAfter.click();

  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  const archerCard = player1Div.locator('[data-player-cards] [data-character="archer"]');
  const mageCard = player1Div.locator('[data-player-cards] [data-character="mage"]');
  await expect(knightCard).toHaveAttribute("data-effects", /skip_turn/);
  await expect(archerCard).toHaveAttribute("data-effects", /skip_turn/);
  await expect(mageCard).toHaveAttribute("data-effects", /skip_turn/);

  // Player2 is not affected (only active player is checked)
  const player2Div = page.locator('[data-player="player2"]');
  const knight2Card = player2Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knight2Card).not.toHaveAttribute("data-effects", /skip_turn/);

  await screenshot(page, "fog-mixed-level-after");

  // Cleanup
  await page2.close();
});
