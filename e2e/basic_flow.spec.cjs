const { test, expect } = require("@playwright/test");
const { TIMEOUT, screenshot, setupHomePage, joinGame } = require("./test-helpers.js");

const GAME_NAME = "test basic flow";

async function cleanupTestGame(page) {
  const testGame = page.getByRole("button", { name: GAME_NAME, exact: true });
  if (await testGame.count()) {
    await page.locator('[class*="game-list-item"]', { has: testGame }).getByRole("button", { name: "🗑️" }).click();
    await expect(testGame).toHaveCount(0);
  }
}

async function createTestGame(page) {
  await page.getByLabel("Add New Game:").fill(GAME_NAME);
  await page.getByRole("button", { name: "+" }).click();
  const testGame = page.getByRole("button", { name: GAME_NAME, exact: true });
  await expect(testGame).toBeVisible();
  return testGame;
}

async function validatePlayerCharacters(page, playerName) {
  const playerDiv = page.locator(`[data-player="${playerName}"]`);

  // Validate player name appears
  await expect(playerDiv.getByText(playerName)).toBeVisible();

  // Validate character cards appear (all 3 characters)
  await expect(playerDiv.getByAltText("knight")).toBeVisible();
  await expect(playerDiv.getByAltText("archer")).toBeVisible();
  await expect(playerDiv.getByAltText("mage")).toBeVisible();

  // Validate character stats are visible
  await expect(playerDiv.getByText(/אביר דרגה 1/)).toBeVisible();
  await expect(playerDiv.getByText(/קשת דרגה 1/)).toBeVisible();
  await expect(playerDiv.getByText(/קוסם דרגה 1/)).toBeVisible();
}

async function testCharacterSelection(page) {
  // Get the select button to locate the character selection area
  const selectButton = page.getByRole("button", { name: "בחר" });
  await expect(selectButton).toBeVisible();

  // Validate card sizes: player section should have small cards
  const playerSectionCard = page.locator('[data-player="player"] [alt="knight"]').locator("..");
  await expect(playerSectionCard).toHaveClass(/card-small/);
  await screenshot(page, "player-section-small-cards");

  // Validate card sizes: shared area should have normal cards
  const sharedAreaCard = page.locator('[alt="knight"]').nth(2).locator("..");
  await expect(sharedAreaCard).toHaveClass(/card-normal/);
  await screenshot(page, "shared-area-normal-cards");

  // Player1 selects knight character (the one near the בחר button)
  // Click the knight that's a sibling/near the select button (in shared area, not player area)
  await page.locator('[alt="knight"]').nth(2).click();

  // Wait for game_update event
  await page.waitForEvent("console", {
    predicate: (msg) => msg.text().includes("onmessage") && msg.text().includes("game_update"),
    timeout: TIMEOUT,
  });
  await screenshot(page, "knight-selected");

  // Verify knight is highlighted
  const knightCard = page.locator('[alt="knight"]').nth(2).locator("..");
  await expect(knightCard).toHaveClass(/selected/);

  // Player1 selects mage character
  await page.locator('[alt="mage"]').nth(2).click();

  // Wait for game_update event
  await page.waitForEvent("console", {
    predicate: (msg) => msg.text().includes("onmessage") && msg.text().includes("game_update"),
    timeout: TIMEOUT,
  });
  await screenshot(page, "mage-selected");

  // Verify mage is highlighted and knight is not
  const mageCard = page.locator('[alt="mage"]').nth(2).locator("..");
  await expect(mageCard).toHaveClass(/selected/);
  await expect(knightCard).not.toHaveClass(/selected/);

  // Validate submit button hover effects
  await selectButton.hover();
  await expect(selectButton).toHaveCSS("cursor", "pointer");
  await screenshot(page, "character-select-button-hover");

  // Player1 confirms selection with בחר button
  await selectButton.click();

  // Wait for game_update event
  await page.waitForEvent("console", {
    predicate: (msg) => msg.text().includes("onmessage") && msg.text().includes("game_update"),
    timeout: TIMEOUT,
  });
  await screenshot(page, "character-selected-confirmed");
}

async function testOpponentSelection(page) {
  // Verify we're in opponent selection stage
  const selectButton = page.getByRole("button", { name: "בחר" });
  await expect(selectButton).toBeVisible();
  await screenshot(page, "opponent-selection-stage");

  // Find opponent player div in shared area (should be visible as opponent card)
  // Look for player2's minimized view in the opponents container
  const opponentDiv = page.locator('[data-player="player2"]').last();
  await expect(opponentDiv).toBeVisible();

  // Verify opponent player2 starts minimized (no character images visible in shared area opponent card)
  // The character names should be visible in Hebrew
  await expect(opponentDiv.getByText(/אביר/)).toBeVisible(); // knight
  await expect(opponentDiv.getByText(/קשת/)).toBeVisible(); // archer
  await expect(opponentDiv.getByText(/קוסם/)).toBeVisible(); // mage
  await screenshot(page, "opponent-minimized");

  // Click on opponent's knight character (minimized view)
  await opponentDiv.getByText(/אביר/).click();

  // Wait for selection update (might not trigger game_update, but state should change)
  await page.waitForTimeout(500);
  await screenshot(page, "opponent-knight-selected");

  // Validate submit button hover effects
  await selectButton.hover();
  await expect(selectButton).toHaveCSS("cursor", "pointer");
  await screenshot(page, "opponent-select-button-hover");

  // Confirm opponent selection with בחר button
  await selectButton.click();

  // Wait for game_update event that transitions to battle
  await page.waitForEvent("console", {
    predicate: (msg) => msg.text().includes("onmessage") && msg.text().includes("game_update"),
    timeout: TIMEOUT,
  });
  await screenshot(page, "opponent-selection-confirmed");
}

async function testBattleStage(page) {
  // Wait for battle stage to load
  await page.waitForTimeout(1000);
  await screenshot(page, "battle-stage-start");

  // Verify current player's battle participant is visible
  const playerBattleRow = page.locator('[data-battle-participant="player"]');
  await expect(playerBattleRow).toBeVisible();

  // Verify opponent's battle participant is visible
  const opponentBattleRow = page.locator('[data-battle-participant="player2"]');
  await expect(opponentBattleRow).toBeVisible();
  await screenshot(page, "battle-participants-visible");

  // Verify player's character card is visible (mage was selected)
  await expect(playerBattleRow.getByAltText("mage")).toBeVisible();
  await screenshot(page, "battle-player-character");

  // Verify opponent's character card is visible (knight was selected)
  await expect(opponentBattleRow.getByAltText("knight")).toBeVisible();
  await screenshot(page, "battle-opponent-character");

  // Verify dice are visible for both participants
  const playerDice = playerBattleRow.locator('[class*="diceContainer"]');
  const opponentDice = opponentBattleRow.locator('[class*="diceContainer"]');
  await expect(playerDice).toBeVisible();
  await expect(opponentDice).toBeVisible();
  await screenshot(page, "battle-dice-visible");

  // Wait for dice roll animation to complete (rollDuration = 2000ms by default)
  await page.waitForTimeout(2500);
  await screenshot(page, "battle-dice-animation-complete");
}

test("basic game flow", async ({ page }) => {
  // Setup and create game
  await setupHomePage(page);
  await cleanupTestGame(page);
  await screenshot(page, "home");

  await createTestGame(page);
  await screenshot(page, "home-with-test");

  // Player1 joins
  await joinGame(page, "player", GAME_NAME);
  await screenshot(page, "joined-game");

  // Validate player1's characters
  await validatePlayerCharacters(page, "player");

  // Player2 joins in new page
  const page2 = await page.context().newPage();
  await setupHomePage(page2);
  await joinGame(page2, "player2", GAME_NAME);

  // Wait for player2's div to be visible before screenshot
  await page2.waitForSelector('[data-player="player2"]', { timeout: TIMEOUT });
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
  await testCharacterSelection(page);

  // Test opponent selection flow
  await testOpponentSelection(page);

  // Test battle stage
  await testBattleStage(page);

  // Clean up
  await page2.close();

  // Navigate back to home and delete the test game
  await page.goto("/");
  await screenshot(page, "homepage-before-cleanup");
  await cleanupTestGame(page);
  await screenshot(page, "homepage-after-cleanup");
});
