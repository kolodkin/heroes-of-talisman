import { createPresetGameViaAPI } from "./api_helpers.js";
import {
  test,
  expect,
  screenshot,
  joinGameViaUrl,
  waitForStage,
  expandPlayersMenuIfCollapsed,
} from "./test_helpers.js";

test("card_draw stage - knight draws magic_ball and levels up", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with knight having drawn magic_ball
  // Knight starts damaged (1/2 health) to demonstrate that level up restores health to new max
  await createPresetGameViaAPI(gameName, "card_draw_knight_magic_ball");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Expand players to see knight's stats before level up
  await expandPlayersMenuIfCollapsed(page);
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight starts at level 1 with damaged health (1/2)
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toHaveAttribute("data-level", "1");
  await expect(knightCard).toContainText("[1/2]");

  // Verify magic_ball card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const magicBallCard = sharedArea.locator('[data-card="magic_ball"]');
  await expect(magicBallCard).toBeVisible();

  // Screenshot with both card and character stats visible before selection
  await screenshot(page, "magic-ball-knight-before-level-up");

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

  // Expand players to see knight's stats after level up
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expandButtonAfter.click();

  // Verify knight leveled up to level 2 with full health at new max (3/3)
  // Note: Level up restores health to new level's max_health
  await expect(knightCard).toHaveAttribute("data-level", "2");
  await expect(knightCard).toContainText("[3/3]");
  await screenshot(page, "magic-ball-knight-after-level-up");

  // Cleanup
  await page2.close();
});

test("card_draw stage - knight at max level draws magic_ball (no effect)", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with max level knight having drawn magic_ball
  // Knight L4 starts damaged (4/5 health) to verify level up has no effect
  await createPresetGameViaAPI(gameName, "card_draw_knight_magic_ball_max_level");

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

  // Verify knight starts at level 4 with damaged health (4/5)
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toHaveAttribute("data-level", "4");
  await expect(knightCard).toContainText("[4/5]");

  // Verify magic_ball card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const magicBallCard = sharedArea.locator('[data-card="magic_ball"]');
  await expect(magicBallCard).toBeVisible();

  await screenshot(page, "magic-ball-knight-max-level-before");

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

  // Expand players to see knight's stats after card (should be unchanged)
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expandButtonAfter.click();

  // Verify knight is still at level 4 with same damaged health (no level up occurred)
  await expect(knightCard).toHaveAttribute("data-level", "4");
  await expect(knightCard).toContainText("[4/5]");
  await screenshot(page, "magic-ball-knight-max-level-after");

  // Cleanup
  await page2.close();
});
