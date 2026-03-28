import {
  test,
  expect,
  screenshot,
  waitForStage,
  setupPresetGame,
  expandAllPlayers,
  collapseAllPlayers,
  getCharacterCard,
  expectCharacterState,
} from "./test_helpers.js";

test("card_draw stage - knight draws devils_fork and levels down", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with L2 knight having drawn devils_fork
  // Knight L2: health=2 (damaged), max_health=3, dice=1, attack=3
  // After level down: level=1, max_health=2, health=max(2,2)=2, dice=1, attack=1
  const page2 = await setupPresetGame(page, gameName, "card_draw_knight_devils_fork", "[data-card]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Expand players to see knight's stats before level down
  await expandAllPlayers(page);

  // Verify knight starts at level 2 with damaged health (2/3)
  const knightCard = getCharacterCard(page, "player1", "knight");
  await expectCharacterState(knightCard, { level: 2, health: "[2/3]" });

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
  await collapseAllPlayers(page);

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "שלוף" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players to see knight's stats after level down
  await expandAllPlayers(page);

  // Verify knight leveled down to level 1 with health = max(2, 2) = 2
  await expectCharacterState(knightCard, { level: 1, health: "[2/2]" });
  await screenshot(page, "devils-fork-knight-after-level-down");

  // Cleanup
  await page2.close();
});

test("card_draw stage - knight at min level draws devils_fork (no effect)", async ({ page, gameName }) => {
  // Create preset game at card_draw stage with L1 knight having drawn devils_fork
  // Knight L1: health=1 (damaged), max_health=2 — no effect since already at level 1
  const page2 = await setupPresetGame(page, gameName, "card_draw_knight_devils_fork_min_level", "[data-card]");

  // Verify we're in card_draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();

  // Expand players to see knight's stats before card
  await expandAllPlayers(page);

  // Verify knight starts at level 1 with damaged health (1/2)
  const knightCard = getCharacterCard(page, "player1", "knight");
  await expectCharacterState(knightCard, { level: 1, health: "[1/2]" });

  // Verify devils_fork card is visible
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const devilsForkCard = sharedArea.locator('[data-card="devils_fork"]');
  await expect(devilsForkCard).toBeVisible();

  await screenshot(page, "devils-fork-knight-min-level-before");

  // Minimize players before card selection so we can expand again after
  await collapseAllPlayers(page);

  // Confirm card selection
  const selectButton = page.getByRole("button", { name: "שלוף" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();
  await selectButton.click();

  // Should transition to ability_selection stage
  await waitForStage(page, "ability_selection");

  // Expand players to see knight's stats after card (should be unchanged)
  await expandAllPlayers(page);

  // Verify knight is still at level 1 with same damaged health (no level down occurred)
  await expectCharacterState(knightCard, { level: 1, health: "[1/2]" });
  await screenshot(page, "devils-fork-knight-min-level-after");

  // Cleanup
  await page2.close();
});
