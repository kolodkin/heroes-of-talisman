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

test("card_draw stage - knight draws talisman", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with knight having drawn talisman
  const page2 = await setupPresetGame(page, gameName, "card_draw_knight_talisman", "[data-card]");

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
  await expandAllPlayers(page);

  // Verify knight has the talisman effect applied
  const knightCard = getCharacterCard(page, "player1", "knight");
  await expect(knightCard).toHaveAttribute("data-effects", /talisman/);

  // Verify talisman icon is visible on knight card
  await expect(knightCard.locator("[data-icon-talisman]")).toBeVisible();

  // Screenshot with expanded player menu showing talisman icon
  await screenshot(page, "card-selected-knight-with-talisman");

  // Minimize players after check
  await collapseAllPlayers(page);

  // Cleanup
  await page2.close();
});
