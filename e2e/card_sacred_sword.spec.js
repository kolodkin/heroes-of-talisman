import { createPresetGameViaAPI } from "./api_helpers.js";
import {
  test,
  expect,
  screenshot,
  joinGameViaUrl,
  waitForStage,
  expandPlayersMenuIfCollapsed,
} from "./test_helpers.js";

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
