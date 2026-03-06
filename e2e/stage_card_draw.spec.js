import { createPresetGameViaAPI } from "./api_helpers.js";
import {
  test,
  expect,
  screenshot,
  joinGameViaUrl,
  waitForStage,
  expandPlayersMenuIfCollapsed,
} from "./test_helpers.js";

/**
 * Tests for card draw stage functionality using presets.
 *
 * Tests cover:
 * - Successful card draw and application (knight + metal_armor)
 * - Restricted card handling (archer + sacred_sword)
 * - Healing cards (golden_apple)
 * - Level up cards (magic_ball)
 * - Darkness rise instant effect (skip_turn on level 2+ characters)
 */

test("card_draw stage - knight draws metal_armor successfully", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with knight having drawn metal_armor
  await createPresetGameViaAPI(gameName, "card_draw_knight_metal_armor");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Verify metal_armor card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const metalArmorCard = sharedArea.locator('[data-card="metal_armor"]');
  await expect(metalArmorCard).toBeVisible();
  await screenshot(page, "card-draw-knight-metal-armor");

  // Verify card details are displayed
  await expect(metalArmorCard).toContainText("שריון מתכת"); // Metal Armor
  await expect(metalArmorCard).toContainText("+2 להגנה"); // +2 to defense

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "שלוף" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players to see character cards with armor icon
  await expandPlayersMenuIfCollapsed(page);
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight has the defense effect applied
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toHaveAttribute("data-effects", /defense_bonus/);

  // Verify armor icon is visible on knight card
  await expect(knightCard.locator("[data-icon-armor]")).toBeVisible();

  // Screenshot with expanded player menu showing armor icon
  await screenshot(page, "card-selected-transition-to-ability");

  // Minimize players after check
  const minimizeButton = page.getByRole("button", { name: "Minimize all players" });
  await minimizeButton.click();

  // Cleanup
  await page2.close();
});

test("card_draw stage - archer draws sacred_sword (restricted)", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with archer having drawn sacred_sword
  await createPresetGameViaAPI(gameName, "card_draw_archer_sacred_sword");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Verify sacred_sword card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const sacredSwordCard = sharedArea.locator('[data-card="sacred_sord"]'); // Note: typo in card name
  await expect(sacredSwordCard).toBeVisible();
  await screenshot(page, "card-draw-archer-sacred-sword-restricted");

  // Verify card details are displayed
  await expect(sacredSwordCard).toContainText("חרב קדושה"); // Sacred Sword
  await expect(sacredSwordCard).toContainText("+3 להתקפה"); // +3 to attack

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "שלוף" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage even though card is restricted
  await waitForStage(page, "ability_selection");

  // Expand players to see character cards
  await expandPlayersMenuIfCollapsed(page);
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify archer does NOT have attack bonus effect (card was restricted)
  const player1Div = page.locator('[data-player="player1"]');
  const archerCard = player1Div.locator('[data-player-cards] [data-character="archer"]');
  // Archer should not have attack_bonus effect from sacred_sword
  const effectsAttr = await archerCard.getAttribute("data-effects");
  if (effectsAttr) {
    expect(effectsAttr).not.toMatch(/attack_bonus/);
  }

  // Verify sword icon is NOT visible on archer card (restricted)
  await expect(archerCard.locator("[data-icon-sword]")).not.toBeVisible();

  // Screenshot with expanded player menu showing no sword icon on archer
  await screenshot(page, "restricted-card-transition-to-ability");

  // Minimize players after check
  const minimizeButton = page.getByRole("button", { name: "Minimize all players" });
  await minimizeButton.click();

  // Cleanup
  await page2.close();
});

test("card_draw stage - knight draws sacred_sword successfully", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with knight having drawn sacred_sword
  await createPresetGameViaAPI(gameName, "card_draw_knight_sacred_sword");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Verify sacred_sword card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const sacredSwordCard = sharedArea.locator('[data-card="sacred_sord"]'); // Note: typo in card name
  await expect(sacredSwordCard).toBeVisible();
  await screenshot(page, "card-draw-knight-sacred-sword");

  // Verify card details are displayed
  await expect(sacredSwordCard).toContainText("חרב קדושה"); // Sacred Sword
  await expect(sacredSwordCard).toContainText("+3 להתקפה"); // +3 to attack

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "שלוף" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players to see character cards with sword icon
  await expandPlayersMenuIfCollapsed(page);
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight has the attack bonus effect applied
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toHaveAttribute("data-effects", /attack_bonus/);

  // Verify sword icon is visible on knight card
  await expect(knightCard.locator("[data-icon-sword]")).toBeVisible();

  // Screenshot with expanded player menu showing sword icon
  await screenshot(page, "card-selected-knight-with-sword");

  // Minimize players after check
  const minimizeButton = page.getByRole("button", { name: "Minimize all players" });
  await minimizeButton.click();

  // Cleanup
  await page2.close();
});

test("card_draw stage - knight draws golden_apple and heals", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with damaged knight having drawn golden_apple
  await createPresetGameViaAPI(gameName, "card_draw_knight_golden_apple");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Expand players to see knight's health before healing
  await expandPlayersMenuIfCollapsed(page);
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight starts at 1 health
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toContainText("[1/2]");

  // Verify golden_apple card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const goldenAppleCard = sharedArea.locator('[data-card="golden_apple"]');
  await expect(goldenAppleCard).toBeVisible();

  // Verify card details are displayed
  await expect(goldenAppleCard).toContainText("תפוח זהב"); // Golden Apple
  await expect(goldenAppleCard).toContainText("+1 לבריאות"); // +1 to health

  // Screenshot with both card and character health visible before selection
  await screenshot(page, "golden-apple-knight-before-heal");

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

  // Expand players to see knight's health after healing
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expandButtonAfter.click();

  // Verify knight healed to 2 health
  await expect(knightCard).toContainText("[2/2]");
  await screenshot(page, "golden-apple-knight-after-heal");

  // Cleanup
  await page2.close();
});

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

test("card_draw stage - knight at max health draws golden_apple (no overheal)", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with knight at max health having drawn golden_apple
  await createPresetGameViaAPI(gameName, "card_draw_golden_apple_max_health");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Expand players to see knight's health before card
  await expandPlayersMenuIfCollapsed(page);
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight starts at max health (2/2)
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toContainText("[2/2]");

  // Verify golden_apple card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const goldenAppleCard = sharedArea.locator('[data-card="golden_apple"]');
  await expect(goldenAppleCard).toBeVisible();

  // Screenshot with both card and character health visible before selection
  await screenshot(page, "golden-apple-knight-max-health-before");

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

  // Expand players to see knight's health after card
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expect(expandButtonAfter).toBeVisible();
  await expandButtonAfter.click();

  // Verify knight is still at max health (no overheal)
  await expect(knightCard).toContainText("[2/2]");
  await screenshot(page, "golden-apple-knight-max-health-after");

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

test("card_draw stage - knight draws talisman", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with knight having drawn talisman
  await createPresetGameViaAPI(gameName, "card_draw_knight_talisman");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Verify talisman card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const talismanCard = sharedArea.locator('[data-card="talisman"]');
  await expect(talismanCard).toBeVisible();
  await screenshot(page, "card-draw-knight-talisman");

  // Verify card details are displayed in Hebrew
  await expect(talismanCard).toContainText("קמע"); // Talisman
  await expect(talismanCard).toContainText("משמיד"); // Destroys

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "שלוף" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players to see character cards with talisman icon
  await expandPlayersMenuIfCollapsed(page);
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify knight has the talisman effect applied
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  await expect(knightCard).toHaveAttribute("data-effects", /talisman/);

  // Verify talisman icon is visible on knight card
  await expect(knightCard.locator("[data-icon-talisman]")).toBeVisible();

  // Screenshot with expanded player menu showing talisman icon
  await screenshot(page, "card-selected-knight-with-talisman");

  // Minimize players after check
  const minimizeButton = page.getByRole("button", { name: "Minimize all players" });
  await minimizeButton.click();

  // Cleanup
  await page2.close();
});

test("card_draw stage - darkness_rise with all level 1 (no effect)", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with darkness_rise card, all characters level 1
  await createPresetGameViaAPI(gameName, "card_draw_darkness_rise_all_level_1");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Verify darkness_rise card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const darknessRiseCard = sharedArea.locator('[data-card="darkness_rise"]');
  await expect(darknessRiseCard).toBeVisible();

  // Verify card details are displayed in Hebrew
  await expect(darknessRiseCard).toContainText("עליית חושך"); // Darkness Rise
  await expect(darknessRiseCard).toContainText("מדלגות על התור"); // skip turn
  await screenshot(page, "card-draw-darkness-rise-all-level-1");

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "שלוף" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players to verify no skip_turn effects applied (all level 1)
  await expandPlayersMenuIfCollapsed(page);
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Verify no character has skip_turn effect (all are level 1)
  const player1Div = page.locator('[data-player="player1"]');
  const player2Div = page.locator('[data-player="player2"]');

  for (const playerDiv of [player1Div, player2Div]) {
    for (const charName of ["knight", "archer", "mage"]) {
      const charCard = playerDiv.locator(`[data-player-cards] [data-character="${charName}"]`);
      await expect(charCard.locator("[data-icon-skip-turn-overlay]")).not.toBeVisible();
    }
  }

  await screenshot(page, "darkness-rise-no-skip-turn-level-1");

  // Minimize players after check
  const minimizeButton = page.getByRole("button", { name: "Minimize all players" });
  await minimizeButton.click();

  // Cleanup
  await page2.close();
});

test("card_draw stage - darkness_rise applies skip_turn to level 2+ characters", async ({ page, gameName }) => {
  // Create preset game with mixed levels: player1 has level 2 characters, player2 has level 1
  await createPresetGameViaAPI(gameName, "card_draw_darkness_rise_mixed_levels");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Verify darkness_rise card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const darknessRiseCard = sharedArea.locator('[data-card="darkness_rise"]');
  await expect(darknessRiseCard).toBeVisible();
  await screenshot(page, "card-draw-darkness-rise-mixed-levels");

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "שלוף" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players to verify skip_turn effects
  await expandPlayersMenuIfCollapsed(page);
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  await expandButton.click();

  // Player1's characters (level 2) should have skip_turn effect
  const player1Div = page.locator('[data-player="player1"]');
  for (const charName of ["knight", "archer", "mage"]) {
    const charCard = player1Div.locator(`[data-player-cards] [data-character="${charName}"]`);
    await expect(charCard).toHaveAttribute("data-effects", /skip_turn/);
    await expect(charCard.locator("[data-icon-skip-turn-overlay]")).toBeVisible();
  }

  // Player2's characters (level 1) should NOT have skip_turn effect
  const player2Div = page.locator('[data-player="player2"]');
  for (const charName of ["knight", "archer", "mage"]) {
    const charCard = player2Div.locator(`[data-player-cards] [data-character="${charName}"]`);
    await expect(charCard.locator("[data-icon-skip-turn-overlay]")).not.toBeVisible();
  }

  await screenshot(page, "darkness-rise-skip-turn-mixed-levels");

  // Minimize players after check
  const minimizeButton = page.getByRole("button", { name: "Minimize all players" });
  await minimizeButton.click();

  // Cleanup
  await page2.close();
});
