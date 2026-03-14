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
 * - Devil's fork level down cards (devils_fork)
 * - Fog instant effect (skip_turn when all alive chars are level 3+)
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

test("card_draw stage - knight draws fog card when all chars are level 3+ (skip_turn applied)", async ({ page, gameName }) => {
  // Create preset: player1 all chars at level 3, player2 all chars at level 1
  // Fog should apply skip_turn to all of player1's characters
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

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players to verify skip_turn was applied to player1's characters
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expandButtonAfter.click();

  // All player1 characters should have skip_turn effect
  await expect(knightCard).toHaveAttribute("data-effects", /skip_turn/);
  await expect(archerCard).toHaveAttribute("data-effects", /skip_turn/);
  await expect(mageCard).toHaveAttribute("data-effects", /skip_turn/);

  // Player2 characters (level 1) should NOT have skip_turn
  const player2Div = page.locator('[data-player="player2"]');
  const knight2Card = player2Div.locator('[data-player-cards] [data-character="knight"]');
  const archer2Card = player2Div.locator('[data-player-cards] [data-character="archer"]');
  const mage2Card = player2Div.locator('[data-player-cards] [data-character="mage"]');
  await expect(knight2Card).not.toHaveAttribute("data-effects", /skip_turn/);
  await expect(archer2Card).not.toHaveAttribute("data-effects", /skip_turn/);
  await expect(mage2Card).not.toHaveAttribute("data-effects", /skip_turn/);

  await screenshot(page, "fog-all-high-level-after");

  // Cleanup
  await page2.close();
});

test("card_draw stage - knight draws fog card with mixed levels (no skip_turn applied)", async ({ page, gameName }) => {
  // Create preset: player1 has knight at level 3, others at level 1 → fog does NOT apply
  await createPresetGameViaAPI(gameName, "card_draw_fog_mixed_level");

  // Player1 joins
  await joinGameViaUrl(page, "player1", gameName, "[data-card]");

  // Player2 joins
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, "[data-game-stage]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Verify fog card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const fogCard = sharedArea.locator('[data-card="fog"]');
  await expect(fogCard).toBeVisible();

  await screenshot(page, "fog-mixed-level-before");

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "שלוף" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players to verify NO skip_turn was applied
  await expandPlayersMenuIfCollapsed(page);
  const expandButtonAfter = page.getByRole("button", { name: "Expand all players" });
  await expandButtonAfter.click();

  // None of player1's characters should have skip_turn (mixed levels)
  const player1Div = page.locator('[data-player="player1"]');
  const knightCard = player1Div.locator('[data-player-cards] [data-character="knight"]');
  const archerCard = player1Div.locator('[data-player-cards] [data-character="archer"]');
  const mageCard = player1Div.locator('[data-player-cards] [data-character="mage"]');
  await expect(knightCard).not.toHaveAttribute("data-effects", /skip_turn/);
  await expect(archerCard).not.toHaveAttribute("data-effects", /skip_turn/);
  await expect(mageCard).not.toHaveAttribute("data-effects", /skip_turn/);

  await screenshot(page, "fog-mixed-level-after");

  // Cleanup
  await page2.close();
});
