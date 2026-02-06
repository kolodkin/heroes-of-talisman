import { sendDebugActionViaWS } from "./api_helpers.js";
import {
  test,
  expect,
  TIMEOUT,
  screenshot,
  setupHomePage,
  joinGame,
  waitForStage,
  dismissConnectionToast,
  validateCardHoverEffect,
} from "./test_helpers.js";

async function cleanupTestGame(page, gameName) {
  const testGame = page.getByRole("button", { name: gameName, exact: true });
  if (await testGame.count()) {
    await page.locator('[class*="game-list-item"]', { has: testGame }).getByRole("button", { name: "🗑️" }).click();
    await expect(testGame).toHaveCount(0);
  }
}

async function createTestGame(page, gameName) {
  await page.getByLabel("Add New Game:").fill(gameName);
  await page.getByRole("button", { name: "+" }).click();
  const testGame = page.getByRole("button", { name: gameName, exact: true });
  await expect(testGame).toBeVisible();
  return testGame;
}

async function validateStatusIndicator(page, expectedStatus, expectedPlayerName = null) {
  const statusIndicator = page.locator("[data-status][data-player-name]");
  await expect(statusIndicator).toBeVisible();
  await expect(statusIndicator).toHaveAttribute("data-status", expectedStatus);

  if (expectedPlayerName) {
    await expect(statusIndicator).toHaveAttribute("data-player-name", expectedPlayerName);
  }
}

async function validatePlayerCharacters(page, playerName) {
  const playerDiv = page.locator(`[data-player="${playerName}"]`);

  // Validate player div is visible
  await expect(playerDiv).toBeVisible();

  // Dismiss any toasts that might be overlaying the expand button
  await dismissConnectionToast(page);

  // Expand player cards if minimized (click + button to show full cards with images)
  const expandButton = page.getByRole("button", { name: "Expand all players" });
  if (await expandButton.isVisible()) {
    await expandButton.click();
    // Wait for cards to appear
    await expect(playerDiv.getByAltText("knight")).toBeVisible({ timeout: TIMEOUT });
  }

  // Validate character cards appear (all 3 characters)
  await expect(playerDiv.getByAltText("knight")).toBeVisible();
  await expect(playerDiv.getByAltText("archer")).toBeVisible();
  await expect(playerDiv.getByAltText("mage")).toBeVisible();

  // Validate character stats are visible using data attributes
  await expect(playerDiv.locator('[data-character="knight"][data-level="1"]')).toBeVisible();
  await expect(playerDiv.locator('[data-character="archer"][data-level="1"]')).toBeVisible();
  await expect(playerDiv.locator('[data-character="mage"][data-level="1"]')).toBeVisible();
}

async function testCharacterSelection(page, page2) {
  // Validate status indicator shows "your turn" for player1
  await validateStatusIndicator(page, "your_turn");

  // Validate status indicator shows "opponent playing" for player2
  await validateStatusIndicator(page2, "opponent_playing", "player");

  // Get the select button to locate the character selection area
  const selectButton = page.getByRole("button", { name: "בחר" });
  await expect(selectButton).toBeVisible();

  // Validate card sizes: player section should have small cards
  const playerSectionCard = page.locator('[data-player="player"] [alt="knight"]').locator("..");
  await expect(playerSectionCard).toHaveClass(/card-small/);

  // Validate card sizes: shared area should have normal cards
  const sharedAreaCard = page.locator('[alt="knight"]').nth(2).locator("..");
  await expect(sharedAreaCard).toHaveClass(/card-normal/);

  // Validate card hover effects
  await validateCardHoverEffect(sharedAreaCard);
  await screenshot(page, "card-hover-and-sizes");

  // Test that non-active player (player2) cannot interact with SharedArea
  const page2SharedArea = page2.locator('[data-shared-area-active="false"]');
  await expect(page2SharedArea).toBeVisible();

  // Verify SharedArea children have pointer-events: none (container has auto for scrolling)
  const page2SharedAreaButton = page2SharedArea.locator("[data-action-button]");
  await expect(page2SharedAreaButton).toHaveCSS("pointer-events", "none");

  // Player1 selects knight character (the one near the בחר button)
  // Click the knight that's a sibling/near the select button (in shared area, not player area)
  const knightCard = page.locator('[alt="knight"]').nth(2).locator("..");
  await page.locator('[alt="knight"]').nth(2).click();
  await expect(knightCard).toHaveClass(/selected/);
  await screenshot(page, "knight-selected");

  // Player1 selects mage character
  const mageCard = page.locator('[alt="mage"]').nth(2).locator("..");
  await page.locator('[alt="mage"]').nth(2).click();
  await expect(mageCard).toHaveClass(/selected/);
  await expect(knightCard).not.toHaveClass(/selected/);
  await screenshot(page, "mage-selected");

  // Validate submit button hover effects
  await selectButton.hover();
  await expect(selectButton).toHaveCSS("cursor", "pointer");

  // Player1 confirms selection with בחר button
  await selectButton.click();

  // Wait for transition to card_draw stage
  await waitForStage(page, "card_draw");
}

async function testCardDraw(page, page2, gameName) {
  // Verify we're in card draw stage
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible();
  await screenshot(page, "card-draw-stage");

  // DEBUG: Set specific card for deterministic test
  await sendDebugActionViaWS(gameName, "player", "debug_set_drawn_card", {
    card_name: "metal_armor",
  });

  // Wait for card to be visible
  const drawnCard = page.locator('[data-card="metal_armor"]');
  await expect(drawnCard).toBeVisible();
  await screenshot(page, "card-drawn-metal-armor");

  // Verify select button is enabled after card is drawn
  const selectButton = page.getByRole("button", { name: "בחר" });
  await expect(selectButton).toBeVisible();
  await expect(selectButton).toBeEnabled();

  // Confirm card selection
  await selectButton.click();

  // Wait for transition to ability selection stage
  await waitForStage(page, "ability_selection");
}

async function testAbilitySelection(page, page2) {
  // Verify we're in ability selection stage
  const selectButton = page.getByRole("button", { name: "בחר" });
  await expect(selectButton).toBeVisible();

  // Select the freeze ability using data-ability attribute
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const freezeAbility = sharedArea.locator('[data-ability="freeze"]');
  await freezeAbility.click();
  await screenshot(page, "freeze-ability-selected");

  // Confirm ability selection with בחר button
  await selectButton.click();

  // Wait for transition to ability_opponent_selection stage
  await waitForStage(page, "ability_opponent_selection");
}

async function testAbilityOpponentSelection(page, page2) {
  // Verify we're in ability opponent selection stage
  const selectButton = page.getByRole("button", { name: "בחר" });
  await expect(selectButton).toBeVisible();

  // Select opponent's knight character from the shared area
  // In this stage, opponents are shown in minimized format with data-character attribute
  const sharedArea = page.locator('[data-shared-area-active="true"]');
  const opponentPlayer = sharedArea.locator('[data-player="player2"]');
  const knightChar = opponentPlayer.locator('[data-character="knight"]');
  await knightChar.click();
  await screenshot(page, "ability-opponent-selected");

  // Confirm selection
  await selectButton.click();

  // Wait for transition to opponent_selection stage
  await waitForStage(page, "opponent_selection");
}

async function testOpponentSelection(page, page2) {
  // Verify we're in opponent selection stage
  const selectButton = page.getByRole("button", { name: "בחר" });
  await expect(selectButton).toBeVisible();

  // Find opponent player div in shared area (should be visible as opponent card)
  // Look for player2's minimized view in the opponents container
  const opponentDiv = page.locator('[data-player="player2"]').last();
  await expect(opponentDiv).toBeVisible();

  // Verify opponent player2 starts minimized (character data attributes visible)
  await expect(opponentDiv.locator('[data-character="knight"]')).toBeVisible();
  await expect(opponentDiv.locator('[data-character="archer"]')).toBeVisible();
  await expect(opponentDiv.locator('[data-character="mage"]')).toBeVisible();

  // Test that non-active player (player2) cannot interact with SharedArea
  const page2SharedArea = page2.locator('[data-shared-area-active="false"]');
  await expect(page2SharedArea).toBeVisible();

  // Verify SharedArea children have pointer-events: none (container has auto for scrolling)
  const page2SharedAreaButton = page2SharedArea.locator("[data-action-button]");
  await expect(page2SharedAreaButton).toHaveCSS("pointer-events", "none");

  // Click on opponent's knight character (minimized view) using data attribute
  await opponentDiv.locator('[data-character="knight"]').click();
  await screenshot(page, "opponent-knight-selected");

  // Validate submit button hover effects
  await selectButton.hover();
  await expect(selectButton).toHaveCSS("cursor", "pointer");

  // Confirm opponent selection with בחר button
  await selectButton.click();

  // Wait for transition to battle_dice_roll stage
  await waitForStage(page, "battle_dice_roll");
}

async function testBattleStage(page, page2, gameName) {
  // Wait for battle stage to load - verify battle participant is visible
  const playerBattleRow = page.locator('[data-battle-participant="player"]');
  await expect(playerBattleRow).toBeVisible();
  await screenshot(page, "battle-stage-start");

  // Verify opponent's battle participant is visible
  const opponentBattleRow = page.locator('[data-battle-participant="player2"]');
  await expect(opponentBattleRow).toBeVisible();

  // Verify player's character card is visible (mage was selected)
  await expect(playerBattleRow.getByAltText("mage")).toBeVisible();

  // Verify opponent's character card is visible (knight was selected)
  await expect(opponentBattleRow.getByAltText("knight")).toBeVisible();

  // Initially, roll buttons should be visible instead of dice
  // Note: The translation key will be either "roll_the_dice" or "roll_the_dices" depending on character's dice value
  const activeRollButton = page.locator('[data-battle-role="active"] [data-roll-button]');
  const opponentRollButton = page.locator('[data-battle-role="opponent"] [data-roll-button]');
  await expect(activeRollButton).toBeVisible();
  await expect(opponentRollButton).toBeVisible();

  // Active player rolls dice
  await activeRollButton.click();

  // Wait for active player dice to be visible
  const activeDice = page.locator('[data-battle-role="active"] [class*="diceContainer"]');
  await expect(activeDice).toBeVisible();
  await screenshot(page, "battle-player-rolled");

  // Opponent (player2) rolls dice from their own page
  // Validate status indicator shows "roll dice" for player2
  await validateStatusIndicator(page2, "roll_dice");
  await screenshot(page2, "player2-roll-dice-status");

  const player2RollButton = page2.locator('[data-battle-role="opponent"] [data-roll-button]');
  await player2RollButton.click();

  // Wait for opponent dice to be visible
  const opponentDice = page.locator('[data-battle-role="opponent"] [class*="diceContainer"]');
  await expect(opponentDice).toBeVisible();
  await screenshot(page, "battle-opponent-rolled");

  // DEBUG: Set deterministic dice rolls to ensure player1 (mage) wins
  // Player1 (active): mage has 1 dice, with attack=0, dice=[6] → score = 6
  // Player2 (opponent): knight has 1 dice, with attack=1, dice=[1] → score = 2
  // This will automatically transition to battle_end stage since there's a winner
  await sendDebugActionViaWS(gameName, "player", "debug_set_battle_dice_rolls", {
    active_dice_roll: [6],
    opponent_dice_roll: [1],
  });

  // Wait for dice animations to complete - continue button appears after animations
  const continueButton = page.getByRole("button", { name: /המשך/i });
  await expect(continueButton).toBeVisible();
  await screenshot(page, "battle-scores-visible");

  // Click continue to end battle
  await continueButton.click();

  // After battle, the next player (circular rotation) becomes active
  // In this 2-player game, the next player after player1 is player2
  // So page2 should now be active
  await page2.waitForSelector('[data-shared-area-active="true"]', { timeout: TIMEOUT });
  await screenshot(page, "battle-ended-page1");
  await screenshot(page2, "battle-ended-page2-now-active");
}

test("basic game flow", async ({ page, gameName }) => {
  // Setup and create game
  await setupHomePage(page);
  await cleanupTestGame(page, gameName);
  await screenshot(page, "homepage-initial");

  await createTestGame(page, gameName);
  await screenshot(page, "homepage-with-test-game-created");

  // Player1 joins
  await joinGame(page, "player", gameName);
  await screenshot(page, "player1-joined-game");

  // Validate player1's characters
  await validatePlayerCharacters(page, "player");

  // Player2 joins in new page
  const page2 = await page.context().newPage();
  await setupHomePage(page2);
  await joinGame(page2, "player2", gameName);

  // Wait for player2's div to be visible
  await page2.waitForSelector('[data-player="player2"]', { timeout: TIMEOUT });

  // Wait a moment for page1 to receive player2 join notification
  await page.waitForSelector('[data-player="player2"]', { timeout: TIMEOUT });

  // Dismiss any remaining toasts before screenshots
  await dismissConnectionToast(page);
  await dismissConnectionToast(page2);

  await screenshot(page, "player2-joined-game-page1");
  await screenshot(page2, "player2-joined-game-page2");

  // Validate all players see both players' characters (interactive)
  // Validate player2 sees both players' characters
  await validatePlayerCharacters(page2, "player");
  await validatePlayerCharacters(page2, "player2");

  // Wait for player1 to receive the update about player2
  await page.waitForSelector('[data-player="player2"]', { timeout: TIMEOUT });

  // Validate player sees both players' characters
  await validatePlayerCharacters(page, "player");
  await validatePlayerCharacters(page, "player2");

  // Test character selection flow
  await testCharacterSelection(page, page2);

  // Test card draw flow
  await testCardDraw(page, page2, gameName);

  // Test ability selection flow
  await testAbilitySelection(page, page2);

  // Test ability opponent selection flow
  await testAbilityOpponentSelection(page, page2);

  // Test opponent selection flow
  await testOpponentSelection(page, page2);

  // Test battle stage
  await testBattleStage(page, page2, gameName);

  // Clean up
  await page2.close();

  // Navigate back to home and delete the test game
  await page.goto("/");
  await screenshot(page, "homepage-before-cleanup");
  await cleanupTestGame(page, gameName);
  await screenshot(page, "homepage-after-cleanup");
});
