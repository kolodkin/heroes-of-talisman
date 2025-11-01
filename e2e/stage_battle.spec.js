import { test, expect } from "@playwright/test";
import { screenshot, joinGameViaUrl } from "./test_helpers.js";
import { createPresetGameViaAPI, deleteGameViaAPI } from "./api_helpers.js";

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

test("battle stage - player 1 wins", async ({ page }) => {
  const gameName = "test-battle-p1-win";

  // Create preset game with player 1 winning
  await deleteGameViaAPI(gameName); // Cleanup if exists
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
  await screenshot(page, "after-continue-click");

  // Cleanup - close all pages first to avoid WebSocket race condition
  await page2.close();
  await page.close();
  // Note: deleteGameViaAPI no longer needed - global teardown handles cleanup
});

test("battle stage - player 2 wins", async ({ page }) => {
  const gameName = "test-battle-p2-win";

  // Create preset game with player 2 winning
  await deleteGameViaAPI(gameName); // Cleanup if exists
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
  await screenshot(page, "player2-wins");

  // Verify continue button appears and click it
  const continueButton = page.locator("[data-continue-button]");
  await expect(continueButton).toBeVisible();
  await continueButton.click();
  await screenshot(page, "after-continue-click");

  // Cleanup - close all pages first to avoid WebSocket race condition
  await page2.close();
  await page.close();
  // Note: deleteGameViaAPI no longer needed - global teardown handles cleanup
});

test("battle stage - draw with reroll", async ({ page }) => {
  const gameName = "test-battle-draw";

  // Create preset game with draw
  await deleteGameViaAPI(gameName); // Cleanup if exists
  await createPresetGameViaAPI(gameName, "battle_draw");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName);

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName);

  // Verify battle stage
  await verifyBattleStage(page, "player1", "player2", "knight", "archer");

  // For draw, scores and winner badges are not shown (showWinner is false)
  // Just verify dice are visible
  const activeDice = page.locator('[data-battle-role="active"] [class*="diceContainer"]');
  const opponentDice = page.locator('[data-battle-role="opponent"] [class*="diceContainer"]');
  await expect(activeDice.first()).toBeVisible();
  await expect(opponentDice.first()).toBeVisible();

  // Verify no winner badge is shown for draw
  const activeWinnerBadge = page.locator('[data-battle-role="active"] [data-winner-badge]');
  const opponentWinnerBadge = page.locator('[data-battle-role="opponent"] [data-winner-badge]');
  await expect(activeWinnerBadge).not.toBeVisible();
  await expect(opponentWinnerBadge).not.toBeVisible();

  // Verify no score is shown for draw
  const activeScore = page.locator('[data-battle-role="active"] [data-score]');
  const opponentScore = page.locator('[data-battle-role="opponent"] [data-score]');
  await expect(activeScore).not.toBeVisible();
  await expect(opponentScore).not.toBeVisible();

  // Verify reroll button appears
  const rerollButton = page.locator("[data-reroll-button]");
  await expect(rerollButton).toBeVisible();

  await screenshot(page, "draw-before-reroll");

  // Verify continue button does NOT appear
  const continueButton = page.locator("[data-continue-button]");
  await expect(continueButton).not.toBeVisible();

  // Click reroll button
  await rerollButton.click();
  await screenshot(page, "after-reroll");

  // Verify dice rolls are reset - roll buttons should be visible again
  const activeRollButton = page.locator('[data-battle-role="active"] [data-roll-button]');
  const opponentRollButton = page.locator('[data-battle-role="opponent"] [data-roll-button]');
  await expect(activeRollButton).toBeVisible();
  await expect(opponentRollButton).toBeVisible();

  // Verify dice are no longer visible after reroll
  await expect(activeDice.first()).not.toBeVisible();
  await expect(opponentDice.first()).not.toBeVisible();

  // Cleanup - close all pages first to avoid WebSocket race condition
  await page2.close();
  await page.close();
  // Note: deleteGameViaAPI no longer needed - global teardown handles cleanup
});
