import { createPresetGameViaAPI } from "./api_helpers.js";
import { test, expect, screenshot, joinGameViaUrl, waitForStage } from "./test_helpers.js";

/**
 * Tests for character level progression functionality using presets.
 *
 * Tests cover:
 * - Level up via Magic Ball card (knight L1 -> L2)
 * - Level down via battle loss (knight L2 -> L1)
 */

test("card_draw stage - knight draws magic_ball and levels up", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with knight having drawn magic_ball
  await createPresetGameViaAPI(gameName, "card_draw_knight_magic_ball");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-player]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Expand players to see knight's stats before level up
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight starts at level 1 with L1 stats (health=2/2)
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toContainText("L1");
  await expect(knightCard).toContainText("[2/2]");

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
  const selectButton = page.getByRole("button", { name: "בחר" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players to see knight's stats after level up
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expandButtonAfter.click();

  // Verify knight leveled up to level 2 with L2 stats (health=6/6)
  await expect(knightCard).toContainText("L2");
  await expect(knightCard).toContainText("[6/6]");
  await screenshot(page, "magic-ball-knight-after-level-up");

  // Cleanup
  await page2.close();
});

test("battle stage - level 2 knight loses and drops to level 1", async ({ page, gameName }) => {
  // Create preset game at battle_end stage with level 2 knight about to lose
  await createPresetGameViaAPI(gameName, "battle_level_down");

  // Player1 joins (knight L2)
  await joinGameViaUrl(page, "player1", gameName);

  // Player2 joins (mage L1)
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName);

  // Verify we're in battle_end stage
  await expect(page.locator('[data-game-stage="battle_end"]')).toBeVisible();

  // Expand players to see knight's stats before level down
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight starts at level 2 with L2 stats (health=6/6)
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toContainText("L2");
  await expect(knightCard).toContainText("[6/6]");

  // Screenshot with knight at level 2 before battle ends
  await screenshot(page, "level-down-knight-before-battle-end");

  // Minimize players before clicking continue
  const minimizeButton = page.getByRole("button", { name: "Minimize all players" });
  await minimizeButton.click();

  // Click continue button to end battle (knight loses and should drop level)
  const continueButton = page.locator("[data-continue-button]");
  await expect(continueButton).toBeVisible();
  await continueButton.click();

  // Wait for stage transition to character_select
  await waitForStage(page, "character_select");

  // Expand players to see knight's stats after level down
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expandButtonAfter.click();

  // Verify knight dropped to level 1 with L1 stats (health=2/2, restored to max)
  await expect(knightCard).toContainText("L1");
  await expect(knightCard).toContainText("[2/2]");
  await screenshot(page, "level-down-knight-after-battle-end");

  // Verify knight is still alive (didn't die because was at L2)
  await expect(knightCard).not.toHaveAttribute("data-is-alive", "false");

  // Cleanup
  await page2.close();
});
