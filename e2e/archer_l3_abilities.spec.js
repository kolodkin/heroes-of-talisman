import {
  test,
  expect,
  screenshot,
  waitForStage,
  setupPresetGame,
  expandAllPlayers,
  collapseAllPlayers,
  getCharacterCard,
} from "./test_helpers.js";

/**
 * Tests for Archer Level 3 skills:
 *   1. bouncing_arrow_l3 (חץ קופץ) — same as L2: two rematches on loss, no damage on win in second reroll
 *   2. burning_arrow (חץ בוער) — deals 0 damage on win this turn, but target loses 2 HP after 2 turn starts
 *
 * Burning Arrow flow:
 *   1. Archer L3 selects burning_arrow ability
 *   2. Archer wins battle → burning_arrow:2 stored on opponent's character
 *   3. After 2 turn starts (decrements), 2 damage fires on opponent
 */

test("archer L3 ability selection shows bouncing_arrow_l3 and burning_arrow", async ({ page, gameName }) => {
  const page2 = await setupPresetGame(page, gameName, "ability_selection_archer_l3", "[data-ability]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // L3 shows bouncing_arrow_l3 and burning_arrow — not L1 or L2 versions
  const bouncingArrowAbility = sharedArea.locator('[data-ability="bouncing_arrow"]');
  const bouncingArrowL2Ability = sharedArea.locator('[data-ability="bouncing_arrow_l2"]');
  const bouncingArrowL3Ability = sharedArea.locator('[data-ability="bouncing_arrow_l3"]');
  const burningArrowAbility = sharedArea.locator('[data-ability="burning_arrow"]');
  const noAbilityCard = sharedArea.locator('[data-ability="no_ability"]');

  await expect(bouncingArrowL3Ability).toBeVisible();
  await expect(burningArrowAbility).toBeVisible();
  await expect(noAbilityCard).toBeVisible();
  await expect(bouncingArrowAbility).not.toBeVisible();
  await expect(bouncingArrowL2Ability).not.toBeVisible();

  await screenshot(page, "archer-l3-ability-selection");

  await page2.close();
});

test("archer L3 selects bouncing_arrow_l3, skips to opponent_selection", async ({ page, gameName }) => {
  const page2 = await setupPresetGame(page, gameName, "ability_selection_archer_l3", "[data-ability]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Select bouncing_arrow_l3
  const bouncingArrowL3Ability = sharedArea.locator('[data-ability="bouncing_arrow_l3"]');
  await bouncingArrowL3Ability.click();
  await screenshot(page, "archer-l3-bouncing-arrow-l3-selected");

  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Should skip ability_opponent_selection and go directly to opponent_selection
  await waitForStage(page, "opponent_selection");
  await screenshot(page, "archer-l3-bouncing-skipped-to-opponent-selection");

  const opponentPlayer = sharedArea.locator('[data-player="player2"]');
  await expect(opponentPlayer).toBeVisible();

  await page2.close();
});

test("archer L3 selects burning_arrow, skips to opponent_selection", async ({ page, gameName }) => {
  const page2 = await setupPresetGame(page, gameName, "ability_selection_archer_l3", "[data-ability]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Select burning_arrow
  const burningArrowAbility = sharedArea.locator('[data-ability="burning_arrow"]');
  await burningArrowAbility.click();
  await screenshot(page, "archer-l3-burning-arrow-selected");

  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // burning_arrow also skips to opponent_selection (applies to self)
  await waitForStage(page, "opponent_selection");
  await screenshot(page, "archer-l3-burning-arrow-skipped-to-opponent-selection");

  await page2.close();
});

test("archer L3 burning_arrow win: stores burning_arrow:2 on opponent", async ({ page, gameName }) => {
  // Preset: archer L3 won battle with burning_arrow active (battle_end stage)
  const page2 = await setupPresetGame(page, gameName, "burning_arrow_win");

  await expect(page.locator('[data-game-stage="battle_end"]')).toBeVisible();

  await screenshot(page, "archer-l3-burning-arrow-win-before-confirm");

  // Expand players to check initial mage health
  await expandAllPlayers(page);

  const mageCard = getCharacterCard(page, "player2", "mage");
  await expect(mageCard).toContainText("[2/2]");

  await collapseAllPlayers(page);

  // Confirm battle end — burning_arrow win should NOT deal immediate damage
  const continueButton = page.locator("[data-continue-button]");
  await expect(continueButton).toBeVisible();
  await continueButton.click();

  await waitForStage(page, "character_select");
  await screenshot(page, "archer-l3-burning-arrow-win-after-confirm");

  // Mage health should still be 2/2 (no immediate damage)
  await expandAllPlayers(page);

  await expect(mageCard).toContainText("[2/2]");

  // Mage should have burning_arrow:2 effect stored
  await expect(mageCard).toHaveAttribute("data-effects", /burning_arrow:2/);

  await screenshot(page, "archer-l3-burning-arrow-countdown-on-mage");

  await page2.close();
});

test("archer L3 burning_arrow fires after 2 turn starts: mage loses 2 HP", async ({ page, gameName }) => {
  // Preset: mage has burning_arrow:1 (one decrement already happened on opponent turn).
  // Archer's turn start (character_select) triggers final decrement → 2 damage on mage.
  const page2 = await setupPresetGame(page, gameName, "burning_arrow_next_turn", "[data-character]");

  await expect(page.locator('[data-game-stage="character_select"]')).toBeVisible();

  // Expand players to verify mage has burning_arrow:1 and health 2/2 before
  await expandAllPlayers(page);

  const mageCard = getCharacterCard(page, "player2", "mage");
  await expect(mageCard).toHaveAttribute("data-effects", /burning_arrow:1/);
  await expect(mageCard).toContainText("[2/2]");

  await screenshot(page, "archer-l3-burning-arrow-before-fire");

  await collapseAllPlayers(page);

  // Select archer to trigger turn start (decrement fires, 2 damage on mage)
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const archerCard = sharedArea.locator('[data-character="archer"]');
  await archerCard.click();

  const selectButton = page.locator("[data-action-button]");
  await expect(selectButton).toBeVisible();
  await selectButton.click();

  // After character select the stage advances to card_draw
  await waitForStage(page, "card_draw");
  await screenshot(page, "archer-l3-burning-arrow-after-fire");

  // Expand players to check mage health — should be reduced by 2
  await expandAllPlayers(page);

  // Mage L1 starts at 2/2 and loses 2 HP → 0/2 (dead)
  await expect(mageCard).toContainText("[0/2]");

  // burning_arrow effect should be cleared from mage
  await expect(mageCard).not.toHaveAttribute("data-effects", /burning_arrow/);

  await screenshot(page, "archer-l3-burning-arrow-mage-damaged");

  await page2.close();
});
