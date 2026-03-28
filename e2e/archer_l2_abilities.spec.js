import {
  test,
  expect,
  screenshot,
  waitForStage,
  setupPresetGame,
  expandAllPlayers,
  collapseAllPlayers,
  getCharacterCard,
  getScore,
  verifyWinner,
} from "./test_helpers.js";

/**
 * Tests for Archer Level 2 skill: bouncing_arrow_l2 (חץ קופץ).
 *
 * Skill description:
 *   If the archer loses a battle, a rematch is performed twice.
 *   In the second rematch, the archer does NOT deal damage to the opponent if winning.
 *
 * Flow:
 *   1. Archer L2 selects bouncing_arrow_l2 ability
 *   2. Archer loses → first reroll (normal)
 *   3. If archer loses first reroll → second reroll available (no-damage on win)
 *   4. If archer wins second reroll → battle ends, NO damage to opponent
 *   5. If archer loses second reroll → battle ends, archer loses normally
 */


test("archer L2 ability selection shows only bouncing_arrow_l2", async ({ page, gameName }) => {
  const page2 = await setupPresetGame(page, gameName, "ability_selection_archer_l2", "[data-ability]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Only L2 skill should be visible, not L1
  const bouncingArrowAbility = sharedArea.locator('[data-ability="bouncing_arrow"]');
  const bouncingArrowL2Ability = sharedArea.locator('[data-ability="bouncing_arrow_l2"]');
  await expect(bouncingArrowL2Ability).toBeVisible();
  await expect(bouncingArrowAbility).not.toBeVisible();

  // No-ability card should also be visible
  const noAbilityCard = sharedArea.locator('[data-ability="no_ability"]');
  await expect(noAbilityCard).toBeVisible();

  await screenshot(page, "archer-l2-own-ability-visible");

  await page2.close();
});

test("archer L2 selects bouncing_arrow_l2, skips to opponent_selection", async ({ page, gameName }) => {
  const page2 = await setupPresetGame(page, gameName, "ability_selection_archer_l2", "[data-ability]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Select bouncing_arrow_l2
  const bouncingArrowL2Ability = sharedArea.locator('[data-ability="bouncing_arrow_l2"]');
  await bouncingArrowL2Ability.click();
  await screenshot(page, "archer-l2-bouncing-arrow-l2-selected");

  // Confirm selection
  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Should skip ability_opponent_selection and go to opponent_selection
  await waitForStage(page, "opponent_selection");
  await screenshot(page, "archer-l2-skipped-to-opponent-selection");

  const opponentPlayer = sharedArea.locator('[data-player="player2"]');
  await expect(opponentPlayer).toBeVisible();

  await page2.close();
});

test("archer L2 - first reroll: bouncing_arrow_l2 sets up second reroll with no-damage", async ({ page, gameName }) => {
  // Preset: archer L2 with bouncing_arrow_l2 active ability, lost to mage (score 4 < 5)
  // Stage stays in battle_dice_roll because reroll is available
  const page2 = await setupPresetGame(page, gameName, "effect_reroll");

  // Verify archer has reroll_dice effect
  const activeCharacterCard = page.locator('[data-battle-role="active"] [data-character="archer"]');
  await expect(activeCharacterCard).toHaveAttribute("data-effects", /reroll_dice/);

  // Verify opponent (mage) won
  await verifyWinner(page, "opponent");

  // Reroll effect button should be visible
  const rerollEffectButton = page.locator("[data-reroll-effect-button]");
  await expect(rerollEffectButton).toBeVisible();
  await screenshot(page, "archer-l2-first-reroll-button-visible");

  // Click reroll effect (first reroll consumed)
  await rerollEffectButton.click();

  // Dice should be reset - roll button visible
  const rollButton = page.locator("[data-action-button][data-roll-button]");
  await expect(rollButton).toBeVisible();

  await screenshot(page, "archer-l2-after-first-reroll");

  await page2.close();
});

test("archer L2 - second reroll state: reroll_dice and no_damage_on_win effects visible", async ({
  page,
  gameName,
}) => {
  // Preset: archer L2 in second-reroll state (EFFECT_REROLL_DICE + EFFECT_NO_DAMAGE_ON_WIN in effects)
  const page2 = await setupPresetGame(page, gameName, "effect_reroll_l2_first");

  // Archer should have both reroll_dice and no_damage_on_win effects
  const activeCharacterCard = page.locator('[data-battle-role="active"] [data-character="archer"]');
  await expect(activeCharacterCard).toHaveAttribute("data-effects", /reroll_dice/);
  await expect(activeCharacterCard).toHaveAttribute("data-effects", /no_damage_on_win/);

  // Verify scores: archer (dice=[2], attack=2) = 4 < mage (dice=[5]) = 5
  const player1Score = await getScore(page, "active");
  const player2Score = await getScore(page, "opponent");
  expect(player1Score).toBe(4);
  expect(player2Score).toBe(5);

  // Reroll effect button should be visible (second reroll)
  const rerollEffectButton = page.locator("[data-reroll-effect-button]");
  await expect(rerollEffectButton).toBeVisible();
  await screenshot(page, "archer-l2-second-reroll-state");

  // Click second reroll
  await rerollEffectButton.click();

  // reroll_dice effect should be consumed, but no_damage_on_win remains
  await expect(activeCharacterCard).not.toHaveAttribute("data-effects", /reroll_dice/);
  await expect(activeCharacterCard).toHaveAttribute("data-effects", /no_damage_on_win/);

  // Dice reset - roll button visible
  const rollButton = page.locator("[data-action-button][data-roll-button]");
  await expect(rollButton).toBeVisible();

  await screenshot(page, "archer-l2-after-second-reroll-dice-reset");

  await page2.close();
});

test("archer L2 - wins on second reroll: opponent takes no damage", async ({ page, gameName }) => {
  // Preset: archer L2 wins battle_end with no_damage_on_win effect active
  // Archer: dice=[6], attack=2, score=8 > Mage: dice=[3], score=3
  // Mage health should NOT decrease
  const page2 = await setupPresetGame(page, gameName, "effect_reroll_l2_second");

  // Verify we're in battle_end stage, archer has no_damage_on_win
  await expect(page.locator('[data-game-stage="battle_end"]')).toBeVisible();
  const activeCharacterCard = page.locator('[data-battle-role="active"] [data-character="archer"]');
  await expect(activeCharacterCard).toHaveAttribute("data-effects", /no_damage_on_win/);

  // Archer is the winner
  await verifyWinner(page, "active");
  await screenshot(page, "archer-l2-second-reroll-win-no-damage-before");

  // Expand players to read mage health before
  await expandAllPlayers(page);

  const mageCard = getCharacterCard(page, "player2", "mage");
  // Mage L1 has health=2/2 (default) - no damage taken yet
  await expect(mageCard).toContainText("[2/2]");

  // Minimize players and click continue
  await collapseAllPlayers(page);

  const continueButton = page.locator("[data-continue-button]");
  await expect(continueButton).toBeVisible();
  await continueButton.click();

  // Wait for stage transition
  await waitForStage(page, "character_select");

  // Expand players to verify mage health UNCHANGED
  await expandAllPlayers(page);

  // Mage should still have 2/2 health - no damage from archer's win
  await expect(mageCard).toContainText("[2/2]");
  await screenshot(page, "archer-l2-second-reroll-win-no-damage-after");

  // no_damage_on_win effect should be cleared from archer
  const archerCard = getCharacterCard(page, "player1", "archer");
  await expect(archerCard).not.toHaveAttribute("data-effects", /no_damage_on_win/);

  await page2.close();
});
