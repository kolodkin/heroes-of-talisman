import { createPresetGameViaAPI } from "./api_helpers.js";
import { test, expect, screenshot, joinGameViaUrl, waitForStage } from "./test_helpers.js";

/**
 * Tests for battle stage functionality using presets.
 *
 * Tests cover:
 * - Player 1 wins, Player 2 wins scenarios
 * - Draw with reroll
 * - Reroll effect after loss
 * - Attack bonus effect causing draw
 * - Level down mechanic (L2 character drops to L1 instead of dying)
 */

/**
 * Helper to verify battle stage is displayed with expected participants
 */
async function verifyBattleStage(page, activePlayer, opponentPlayer, activeChar, opponentChar) {
  // Verify we're in battle stage
  const playerBattleRow = page.locator('[data-battle-participant="player1"]');
  const opponentBattleRow = page.locator('[data-battle-participant="player2"]');

  await expect(playerBattleRow).toBeVisible();
  await expect(opponentBattleRow).toBeVisible();

  // Verify character images are visible
  await expect(playerBattleRow.getByAltText(activeChar)).toBeVisible();
  await expect(opponentBattleRow.getByAltText(opponentChar)).toBeVisible();

  // Verify dice are visible (not roll buttons, since dice are already rolled in preset)
  const activeDice = page.locator('[data-battle-role="active"] [class*="diceContainer"]');
  const opponentDice = page.locator('[data-battle-role="opponent"] [class*="diceContainer"]');

  await expect(activeDice.first()).toBeVisible();
  await expect(opponentDice.first()).toBeVisible();
}

/**
 * Helper to get score from battle row
 */
async function getScore(page, role) {
  const scoreElement = page.locator(`[data-battle-role="${role}"] [data-score]`);
  await expect(scoreElement).toBeVisible();
  const scoreText = await scoreElement.textContent();
  return parseInt(scoreText.trim());
}

/**
 * Helper to verify winner badge is shown for the correct role
 * Waits for the initial appearance animation to complete
 */
async function verifyWinner(page, winnerRole) {
  const winnerBadge = page.locator(`[data-battle-role="${winnerRole}"] [data-winner-badge]`);
  await expect(winnerBadge).toBeVisible();

  // Wait for winnerAppear animation to complete (ignoring infinite pulse animation)
  await winnerBadge.evaluate((element) => {
    const animations = element.getAnimations();
    const appearAnimation = animations.find((anim) =>
      anim.effect?.getKeyframes().some((frame) => frame.opacity !== undefined),
    );
    return appearAnimation ? appearAnimation.finished : Promise.resolve();
  });
}

test("battle stage - player 1 wins", async ({ page, gameName }) => {
  // Create preset game with player 1 winning
  await createPresetGameViaAPI(gameName, "battle_player_1_win");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName);

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName);

  // Verify battle stage
  await verifyBattleStage(page, "player1", "player2", "knight", "mage");

  // Get scores
  const player1Score = await getScore(page, "active");
  const player2Score = await getScore(page, "opponent");

  // Verify player 1 wins (knight with dice=[6], attack=1 = 7 > mage with dice=[3] = 3)
  expect(player1Score).toBeGreaterThan(player2Score);
  expect(player1Score).toBe(7);
  expect(player2Score).toBe(3);

  // Verify winner badge is shown for player 1 (waits for animation to complete)
  await verifyWinner(page, "active");
  await screenshot(page, "player1-wins");

  // Verify continue button appears and click it
  const continueButton = page.locator("[data-continue-button]");
  await expect(continueButton).toBeVisible();
  await continueButton.click();

  // Cleanup
  await page2.close();
});

test("battle stage - player 2 wins", async ({ page, gameName }) => {
  // Create preset game with player 2 winning
  await createPresetGameViaAPI(gameName, "battle_player_2_win");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName);

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName);

  // Verify battle stage
  await verifyBattleStage(page, "player1", "player2", "mage", "knight");

  // Get scores
  const player1Score = await getScore(page, "active");
  const player2Score = await getScore(page, "opponent");

  // Verify player 2 wins (mage with dice=[2] = 2 < knight with dice=[5], attack=1 = 6)
  expect(player2Score).toBeGreaterThan(player1Score);
  expect(player1Score).toBe(2);
  expect(player2Score).toBe(6);

  // Verify winner badge is shown for player 2 (waits for animation to complete)
  await verifyWinner(page, "opponent");

  // Verify continue button appears and click it
  const continueButton = page.locator("[data-continue-button]");
  await expect(continueButton).toBeVisible();
  await continueButton.click();
  await screenshot(page, "battle-after-continue-click");

  // Cleanup
  await page2.close();
});

test("battle stage - draw with reroll", async ({ page, gameName }) => {
  // Create preset game with draw
  await createPresetGameViaAPI(gameName, "battle_draw");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName);

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName);

  // Verify battle stage
  await verifyBattleStage(page, "player1", "player2", "knight", "archer");

  // For draw, scores are shown but winner badges are not
  // Verify dice are visible
  const activeDice = page.locator('[data-battle-role="active"] [class*="diceContainer"]');
  const opponentDice = page.locator('[data-battle-role="opponent"] [class*="diceContainer"]');
  await expect(activeDice.first()).toBeVisible();
  await expect(opponentDice.first()).toBeVisible();

  // Verify no winner badge is shown for draw
  const activeWinnerBadge = page.locator('[data-battle-role="active"] [data-winner-badge]');
  const opponentWinnerBadge = page.locator('[data-battle-role="opponent"] [data-winner-badge]');
  await expect(activeWinnerBadge).not.toBeVisible();
  await expect(opponentWinnerBadge).not.toBeVisible();

  // Verify scores are shown for draw (both should be equal: knight=5+1=6, archer=6+0=6)
  const player1Score = await getScore(page, "active");
  const player2Score = await getScore(page, "opponent");
  expect(player1Score).toBe(6);
  expect(player2Score).toBe(6);
  await screenshot(page, "draw-with-scores");

  // Verify reroll button appears
  const rerollButton = page.locator("[data-reroll-button]");
  await expect(rerollButton).toBeVisible();

  // Verify continue button does NOT appear
  const continueButton = page.locator("[data-continue-button]");
  await expect(continueButton).not.toBeVisible();

  // Click reroll button
  await rerollButton.click();
  await screenshot(page, "battle-after-reroll");

  // Verify dice rolls are reset - action button should show "Roll Dice" again
  const rollButton = page.locator("[data-action-button][data-roll-button]");
  await expect(rollButton).toBeVisible();

  // Verify dice are no longer visible after reroll
  await expect(activeDice.first()).not.toBeVisible();
  await expect(opponentDice.first()).not.toBeVisible();

  // Cleanup
  await page2.close();
});

test("battle stage - reroll effect after loss", async ({ page, gameName }) => {
  // Create preset game with reroll effect (archer with reroll vs mage, archer loses)
  await createPresetGameViaAPI(gameName, "effect_reroll");

  // Player1 joins (archer with reroll effect)
  await joinGameViaUrl(page, "player1", gameName);

  // Player2 joins (mage)
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName);

  // Verify battle stage
  await verifyBattleStage(page, "player1", "player2", "archer", "mage");

  // Verify reroll effect is present in character card data-effects attribute
  const activeCharacterCard = page.locator('[data-battle-role="active"] [data-character="archer"]');
  await expect(activeCharacterCard).toHaveAttribute("data-effects", /reroll_dice/);

  // Get scores - player1 (archer) should have lost (dice=[2] = 2 < mage dice=[5] = 5)
  const player1Score = await getScore(page, "active");
  const player2Score = await getScore(page, "opponent");
  expect(player2Score).toBeGreaterThan(player1Score);
  expect(player1Score).toBe(2);
  expect(player2Score).toBe(5);

  // Verify winner badge is shown for player 2 (opponent)
  await verifyWinner(page, "opponent");

  // Verify reroll effect button appears (player1 lost and has reroll effect)
  const rerollEffectButton = page.locator("[data-reroll-effect-button]");
  await expect(rerollEffectButton).toBeVisible();

  // Verify reroll icon is visible inside the reroll effect button
  const rerollIconInButton = page.locator("[data-reroll-effect-button] [data-icon-reroll]");
  await expect(rerollIconInButton).toBeVisible();
  await screenshot(page, "reroll-effect-button-visible");

  // Verify continue button does NOT appear (reroll effect is the only option)
  const continueButton = page.locator("[data-continue-button]");
  await expect(continueButton).not.toBeVisible();

  // Click reroll effect button
  await rerollEffectButton.click();

  // Verify reroll effect is removed from data-effects attribute
  await expect(activeCharacterCard).not.toHaveAttribute("data-effects", /reroll_dice/);

  // Verify dice rolls are reset - action button should show "Roll Dice" again
  const rollButton = page.locator("[data-action-button][data-roll-button]");
  await expect(rollButton).toBeVisible();

  // Verify dice are no longer visible after reroll
  const activeDice = page.locator('[data-battle-role="active"] [class*="diceContainer"]');
  const opponentDice = page.locator('[data-battle-role="opponent"] [class*="diceContainer"]');
  await expect(activeDice.first()).not.toBeVisible();
  await expect(opponentDice.first()).not.toBeVisible();

  // Verify winner badge is gone
  const opponentWinnerBadge = page.locator('[data-battle-role="opponent"] [data-winner-badge]');
  await expect(opponentWinnerBadge).not.toBeVisible();

  // Verify reroll effect button is also gone (since effect was used)
  await expect(rerollEffectButton).not.toBeVisible();

  await screenshot(page, "battle-after-reroll-effect-complete");

  // Cleanup
  await page2.close();
});

test("battle stage - draw with attack bonus effect", async ({ page, gameName }) => {
  // Create preset game with draw caused by attack bonus effect
  // Player 1: knight with attack_bonus (+2) -> dice=[4] + attack=1 + bonus=2 = 7
  // Player 2: knight with no effects -> dice=[6] + attack=1 = 7
  // Result: Draw (7 == 7)
  await createPresetGameViaAPI(gameName, "effect_attack_bonus");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName);

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName);

  // Verify battle stage
  await verifyBattleStage(page, "player1", "player2", "knight", "knight");

  // Verify attack bonus effect is present in player1's character card
  const activeCharacterCard = page.locator('[data-battle-role="active"] [data-character="knight"]');
  await expect(activeCharacterCard).toHaveAttribute("data-effects", /attack_bonus/);

  // Verify scores are shown for draw (player1: 4+1+2=7, player2: 6+1=7)
  const player1Score = await getScore(page, "active");
  const player2Score = await getScore(page, "opponent");
  expect(player1Score).toBe(7);
  expect(player2Score).toBe(7);

  // Verify reroll button is visible (indicates draw)
  const rerollButton = page.locator("[data-reroll-button]");
  await expect(rerollButton).toBeVisible();

  await screenshot(page, "draw-with-attack-bonus");

  // Verify continue button does NOT appear
  const continueButton = page.locator("[data-continue-button]");
  await expect(continueButton).not.toBeVisible();

  // Click reroll button
  await rerollButton.click();
  await screenshot(page, "battle-after-reroll-attack-bonus");

  // Verify dice rolls are reset - action button should show "Roll Dice" again
  const rollButton = page.locator("[data-action-button][data-roll-button]");
  await expect(rollButton).toBeVisible();

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

  // Verify knight starts at level 2 with 1 health (about to trigger level down)
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toHaveAttribute("data-level", "2");
  await expect(knightCard).toContainText("[1/3]");

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
  await expect(knightCard).toHaveAttribute("data-level", "1");
  await expect(knightCard).toContainText("[2/2]");
  await screenshot(page, "level-down-knight-after-battle-end");

  // Verify knight is still alive (didn't die because was at L2)
  await expect(knightCard).not.toHaveAttribute("data-is-alive", "false");

  // Cleanup
  await page2.close();
});

test("battle stage - talisman kills opponent at level 2 instead of level down", async ({ page, gameName }) => {
  // Create preset game: knight L2 with talisman wins against mage L2 with 1 health
  // Without talisman, mage would level down to L1. With talisman, mage dies.
  await createPresetGameViaAPI(gameName, "battle_talisman_kill");

  // Player1 joins (knight L2 with talisman)
  await joinGameViaUrl(page, "player1", gameName);

  // Player2 joins (mage L2 with 1 health)
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName);

  // Verify we're in battle_end stage
  await expect(page.locator('[data-game-stage="battle_end"]')).toBeVisible();
  await screenshot(page, "talisman-kill-battle-end-stage");

  // Click continue button to end battle
  const continueButton = page.locator("[data-continue-button]");
  await expect(continueButton).toBeVisible();
  await continueButton.click();

  // Wait for stage transition to character_select
  await waitForStage(page, "character_select");

  // Expand players to see character stats after battle end
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight has talisman icon and is at level 2
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toHaveAttribute("data-level", "2");
  await expect(knightCard.locator("[data-icon-talisman]")).toBeVisible();

  // Verify mage is DEAD (not level-downed) - level stays at 2, health is 0
  const player2Div = page.locator('[data-player="player2"]');
  const mageCard = player2Div.locator('[data-player-cards] [data-character="mage"]');
  await expect(mageCard).toHaveAttribute("data-level", "2");
  await expect(mageCard).toContainText("[0/3]");

  // Verify mage is marked as dead via data attribute
  await expect(mageCard).toHaveAttribute("data-is-alive", "false");

  // Verify not-alive overlay is shown on mage (skull icon)
  await expect(mageCard.locator('[class*="overlay"]')).toBeVisible();
  await screenshot(page, "talisman-kill-mage-dead");

  // Cleanup
  await page2.close();
});
