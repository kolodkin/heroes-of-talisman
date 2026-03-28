import { createPresetGameViaAPI } from "./api_helpers.js";
import {
  test,
  expect,
  screenshot,
  joinGameViaUrl,
  waitForStage,
  expandPlayersMenuIfCollapsed,
} from "./test_helpers.js";

test("card_draw stage - knight draws devils_fork and levels down", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with L2 knight having drawn devils_fork
  // Knight L2: health=2 (damaged), max_health=3, dice=1, attack=3
  // After level down: level=1, max_health=2, health=max(2,2)=2, dice=1, attack=1
  await createPresetGameViaAPI(gameName, "card_draw_knight_devils_fork");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Expand players to see knight's stats before level down
  await expandPlayersMenuIfCollapsed(page);
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight starts at level 2 with damaged health (2/3)
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toHaveAttribute("data-level", "2");
  await expect(knightCard).toContainText("[2/3]");

  // Verify devils_fork card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const devilsForkCard = sharedArea.locator('[data-card="devils_fork"]');
  await expect(devilsForkCard).toBeVisible();

  // Verify card details are displayed in Hebrew
  await expect(devilsForkCard).toContainText("קלשון השטן"); // Devil's Fork
  await expect(devilsForkCard).toContainText("מוריד דרגה"); // Reduces level

  // Screenshot with both card and character stats visible before selection
  await screenshot(page, "devils-fork-knight-before-level-down");

  // Minimize players before card selection so we can expand again after
  const minimizeButtonBefore = page.getByRole("button", { name: "Minimize all players" });
  await minimizeButtonBefore.click();

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "שלוף" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players to see knight's stats after level down
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expandButtonAfter.click();

  // Verify knight leveled down to level 1 with health = max(2, 2) = 2
  await expect(knightCard).toHaveAttribute("data-level", "1");
  await expect(knightCard).toContainText("[2/2]");
  await screenshot(page, "devils-fork-knight-after-level-down");

  // Cleanup
  await page2.close();
});

test("card_draw stage - knight at min level draws devils_fork (no effect)", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with L1 knight having drawn devils_fork
  // Knight L1: health=1 (damaged), max_health=2 — no effect since already at level 1
  await createPresetGameViaAPI(gameName, "card_draw_knight_devils_fork_min_level");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Expand players to see knight's stats before card
  await expandPlayersMenuIfCollapsed(page);
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight starts at level 1 with damaged health (1/2)
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toHaveAttribute("data-level", "1");
  await expect(knightCard).toContainText("[1/2]");

  // Verify devils_fork card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const devilsForkCard = sharedArea.locator('[data-card="devils_fork"]');
  await expect(devilsForkCard).toBeVisible();

  await screenshot(page, "devils-fork-knight-min-level-before");

  // Minimize players before card selection so we can expand again after
  const minimizeButtonBefore = page.getByRole("button", { name: "Minimize all players" });
  await minimizeButtonBefore.click();

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "שלוף" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players to see knight's stats after card (should be unchanged)
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expandButtonAfter.click();

  // Verify knight is still at level 1 with same damaged health (no level down occurred)
  await expect(knightCard).toHaveAttribute("data-level", "1");
  await expect(knightCard).toContainText("[1/2]");
  await screenshot(page, "devils-fork-knight-min-level-after");

  // Cleanup
  await page2.close();
});
