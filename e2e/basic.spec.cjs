const { test, expect } = require("@playwright/test");

const TIMEOUT = 2000;

async function screenshot(page, name) {
  const screenshot = await page.screenshot();
  await test.info().attach(name, { body: screenshot, contentType: "image/jpg" });
}

async function setupHomePage(page) {
  await page.goto("/");
  await expect(page).toHaveTitle(/Heroes of Talisman/);
  await page.waitForSelector('h2:has-text("Join A Game:")');
}

async function cleanupTestGame(page) {
  const testGame = page.getByRole("button", { name: "test-e2e", exact: true });
  if (await testGame.count()) {
    await page.locator("li", { has: testGame }).getByRole("button", { name: "🗑️" }).click();
    await expect(testGame).toHaveCount(0);
  }
}

async function createTestGame(page) {
  await page.getByLabel("Add New Game:").fill("test-e2e");
  await page.getByRole("button", { name: "+" }).click();
  const testGame = page.getByRole("button", { name: "test-e2e", exact: true });
  await expect(testGame).toBeVisible();
  return testGame;
}

async function joinGame(page, playerName, gameName) {
  await page.getByLabel("Enter your name:").fill(playerName);
  const gameButton = page.getByRole("button", { name: gameName });

  const [connectedLog] = await Promise.all([
    page.waitForEvent("console", {
      predicate: (msg) => msg.text().includes("notify.connected"),
      timeout: TIMEOUT,
    }),
    gameButton.click(),
  ]);

  await expect(page).toHaveURL(new RegExp(`/games/${gameName}/`));
  const connectedText = await connectedLog.args()[2].jsonValue();
  await test.info().attach(`${playerName}-connection-message`, { body: connectedText, contentType: "text/plain" });
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

  // Player1 confirms selection with בחר button
  await selectButton.click();

  // Wait for game_update event
  await page.waitForEvent("console", {
    predicate: (msg) => msg.text().includes("onmessage") && msg.text().includes("game_update"),
    timeout: TIMEOUT,
  });
  await screenshot(page, "character-selected-confirmed");
}

test("basic game flow", async ({ page }) => {
  // Setup and create game
  await setupHomePage(page);
  await cleanupTestGame(page);
  await screenshot(page, "home");

  await createTestGame(page);
  await screenshot(page, "home-with-test");

  // Player1 joins
  await joinGame(page, "player", "test-e2e");
  await screenshot(page, "joined-game");

  // Validate player1's characters
  await validatePlayerCharacters(page, "player");

  // Player2 joins in new page
  const page2 = await page.context().newPage();
  await setupHomePage(page2);
  await joinGame(page2, "player2", "test-e2e");

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

  // Clean up
  await page2.close();
});
