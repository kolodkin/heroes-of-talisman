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
 * Tests for Knight Level 3 abilities:
 *   1. backhand_strike - Battle opponent gets skip_turn for next turn
 *   2. triple_strike - Removes ALL active cards (items) from battle opponent
 *
 * Both target battle_opponent (no separate opponent selection needed).
 * Knight L3 has two abilities (like Archer L3), so player chooses one per turn.
 */

test("knight L3 ability selection shows backhand_strike and triple_strike", async ({ page, gameName }) => {
  const page2 = await setupPresetGame(page, gameName, "ability_selection_knight_l3", "[data-ability]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // L3 shows backhand_strike and triple_strike
  const backhandStrikeAbility = sharedArea.locator('[data-ability="backhand_strike"]');
  const tripleStrikeAbility = sharedArea.locator('[data-ability="triple_strike"]');
  const noAbilityCard = sharedArea.locator('[data-ability="no_ability"]');

  // L1 ability (battle_howl) should NOT be visible
  const battleHowlAbility = sharedArea.locator('[data-ability="battle_howl"]');

  await expect(backhandStrikeAbility).toBeVisible();
  await expect(tripleStrikeAbility).toBeVisible();
  await expect(noAbilityCard).toBeVisible();
  await expect(battleHowlAbility).not.toBeVisible();

  await screenshot(page, "knight-l3-ability-selection");

  await page2.close();
});

test("knight L3 selects backhand_strike, goes to opponent_selection", async ({ page, gameName }) => {
  const page2 = await setupPresetGame(page, gameName, "ability_selection_knight_l3", "[data-ability]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Select backhand_strike
  const backhandStrikeAbility = sharedArea.locator('[data-ability="backhand_strike"]');
  await backhandStrikeAbility.click();
  await screenshot(page, "knight-l3-backhand-strike-selected");

  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Should go directly to opponent_selection (battle_opponent, no pre-selection)
  await waitForStage(page, "opponent_selection");
  await screenshot(page, "knight-l3-backhand-strike-opponent-selection");

  const opponentPlayer = sharedArea.locator('[data-player="player2"]');
  await expect(opponentPlayer).toBeVisible();

  await page2.close();
});

test("knight L3 selects triple_strike, goes to opponent_selection", async ({ page, gameName }) => {
  const page2 = await setupPresetGame(page, gameName, "ability_selection_knight_l3", "[data-ability]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Select triple_strike
  const tripleStrikeAbility = sharedArea.locator('[data-ability="triple_strike"]');
  await tripleStrikeAbility.click();
  await screenshot(page, "knight-l3-triple-strike-selected");

  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Should go directly to opponent_selection (battle_opponent, no pre-selection)
  await waitForStage(page, "opponent_selection");
  await screenshot(page, "knight-l3-triple-strike-opponent-selection");

  const opponentPlayer = sharedArea.locator('[data-player="player2"]');
  await expect(opponentPlayer).toBeVisible();

  await page2.close();
});

test("knight L3 triple_strike removes all items from battle opponent", async ({ page, gameName }) => {
  // Preset: Knight L3 at ability_selection, opponent mage has sacred_sword and metal_armor
  const page2 = await setupPresetGame(page, gameName, "ability_selection_knight_l3_with_items", "[data-ability]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Verify opponent mage has items before triple_strike
  await expandAllPlayers(page);
  const mageCard = getCharacterCard(page, "player2", "mage");
  await expect(mageCard).toHaveAttribute("data-active-cards", /sacred_sword/);
  await expect(mageCard).toHaveAttribute("data-active-cards", /metal_armor/);
  await screenshot(page, "knight-l3-triple-strike-opponent-has-items");
  await collapseAllPlayers(page);

  // Select triple_strike ability
  const tripleStrikeAbility = sharedArea.locator('[data-ability="triple_strike"]');
  await tripleStrikeAbility.click();

  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  await waitForStage(page, "opponent_selection");

  // Select the opponent's mage character
  const opponentMage = sharedArea.locator('[data-player="player2"] [data-character="mage"]');
  await opponentMage.click();
  await screenshot(page, "knight-l3-triple-strike-opponent-mage-selected");

  // Confirm opponent selection
  const confirmButton = page.locator("[data-action-button]");
  await expect(confirmButton).toBeVisible();
  await confirmButton.click();

  // Should transition to battle_dice_roll
  await waitForStage(page, "battle_dice_roll");
  await screenshot(page, "knight-l3-triple-strike-battle-dice-roll");

  // Verify opponent mage's items are removed
  await expandAllPlayers(page);
  await expect(mageCard).not.toHaveAttribute("data-active-cards", /sacred_sword/);
  await expect(mageCard).not.toHaveAttribute("data-active-cards", /metal_armor/);
  await screenshot(page, "knight-l3-triple-strike-items-removed");

  await page2.close();
});
