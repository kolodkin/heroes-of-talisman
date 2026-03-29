import { test, expect, screenshot, waitForStage, setupPresetGame, TIMEOUT } from "./test_helpers.js";

test("ability_selection stage - knight L2 disarm: shows only disarm ability, routes to card_draw, turn ends", async ({
  page,
  gameName,
}) => {
  // Knight L2 has its own skill: disarm only (not L1's battle_howl)
  // Selects disarm → card_draw → draws second card → turn ends (character_select for player2)
  const page2 = await setupPresetGame(page, gameName, "ability_selection_knight_l2", "[data-ability]");

  const sharedArea = page.locator('[data-shared-area-active="true"]');

  // Only L2 skill (disarm) should be visible, not L1 (battle_howl)
  const battleHowlAbility = sharedArea.locator('[data-ability="battle_howl"]');
  const disarmAbility = sharedArea.locator('[data-ability="disarm"]');
  await expect(disarmAbility).toBeVisible();
  await expect(battleHowlAbility).not.toBeVisible();

  // No-ability card should also be visible
  const noAbilityCard = sharedArea.locator('[data-ability="no_ability"]');
  await expect(noAbilityCard).toBeVisible();

  // Click the disarm ability card and confirm
  await disarmAbility.click();
  await screenshot(page, "disarm-ability-selected");

  const selectButton = page.getByRole("button", { name: "בחר" });
  await selectButton.click();

  // Should go to card_draw stage (disarm draws extra card instead of attacking)
  await waitForStage(page, "card_draw", 10 * TIMEOUT);
  await screenshot(page, "disarm-second-card-draw-stage");

  // First click: draw a card from the deck
  const drawButton = page.getByRole("button", { name: "שלוף" });
  await expect(drawButton).toBeVisible();
  await expect(drawButton).toBeEnabled();
  await drawButton.click();

  // Wait for card to appear
  await page.waitForSelector("[data-card]", { timeout: 10 * TIMEOUT });
  await screenshot(page, "disarm-second-card-revealed");

  // Second click: confirm card selection → ends the turn
  await expect(drawButton).toBeEnabled();
  await drawButton.click();

  // Turn ends: should go to character_select (player2's turn)
  await waitForStage(page2, "character_select", 10 * TIMEOUT);
  await screenshot(page2, "disarm-turn-ended-player2-turn");

  // Cleanup
  await page2.close();
});
