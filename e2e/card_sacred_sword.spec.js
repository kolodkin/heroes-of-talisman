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

test("card_draw stage - archer draws sacred_sword (restricted)", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with archer having drawn sacred_sword
  const page2 = await setupPresetGame(page, gameName, "card_draw_archer_sacred_sword", "[data-card]");

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
  await expandAllPlayers(page);

  // Verify archer does NOT have attack bonus effect (card was restricted)
  const archerCard = getCharacterCard(page, "player1", "archer");
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
  await collapseAllPlayers(page);

  // Cleanup
  await page2.close();
});

test("card_draw stage - knight draws sacred_sword successfully", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with knight having drawn sacred_sword
  const page2 = await setupPresetGame(page, gameName, "card_draw_knight_sacred_sword", "[data-card]");

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
  await expandAllPlayers(page);

  // Verify knight has the attack bonus effect applied
  const knightCard = getCharacterCard(page, "player1", "knight");
  await expect(knightCard).toHaveAttribute("data-effects", /attack_bonus/);

  // Verify sword icon is visible on knight card
  await expect(knightCard.locator("[data-icon-sword]")).toBeVisible();

  // Screenshot with expanded player menu showing sword icon
  await screenshot(page, "card-selected-knight-with-sword");

  // Minimize players after check
  await collapseAllPlayers(page);

  // Cleanup
  await page2.close();
});
