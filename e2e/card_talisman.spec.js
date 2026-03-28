import { createPresetGameViaAPI } from "./api_helpers.js";
import {
  test,
  expect,
  screenshot,
  joinGameViaUrl,
  waitForStage,
  expandPlayersMenuIfCollapsed,
} from "./test_helpers.js";

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
