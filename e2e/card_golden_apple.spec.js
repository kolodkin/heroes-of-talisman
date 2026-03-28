import { createPresetGameViaAPI } from "./api_helpers.js";
import {
  test,
  expect,
  screenshot,
  joinGameViaUrl,
  waitForStage,
  expandPlayersMenuIfCollapsed,
} from "./test_helpers.js";

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
