const { test, expect } = require("@playwright/test");

async function screenshot(page, name) {
  const screenshot = await page.screenshot();
  await test.info().attach(name, { body: screenshot, contentType: "image/jpg" });
}

test("basic game flow", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Heroes of Talisman/);

  // Wait for games list to load
  await page.waitForSelector('h2:has-text("Join A Game:")');

  await page.getByLabel("Enter your name:").fill("player");

  const testGame = page.getByRole("button", { name: "test" });
  if (await testGame.count()) {
    await page.locator("li", { has: testGame }).getByRole("button", { name: "🗑️" }).click();
    await expect(testGame).toHaveCount(0);
  }

  await screenshot(page, "home");

  await page.getByLabel("Add New Game:").fill("test");
  await page.getByRole("button", { name: "+" }).click();
  await expect(testGame).toBeVisible();

  await screenshot(page, "home-with-test");

  const [connectedLog] = await Promise.all([
    page.waitForEvent("console", {
      predicate: (msg) => msg.text().includes("notify.connected"),
      timeout: 1000,
    }),
    testGame.click(),
  ]);
  await expect(page).toHaveURL(/\/games\/test\//);
  const connectedText = await connectedLog.args()[2].jsonValue();
  await test.info().attach("connection-message", { body: connectedText, contentType: "text/plain" });

  await screenshot(page, "joined-game");

  // Get player's div using data-player attribute
  const playerDiv = page.locator('[data-player="player"]');

  // Validate player name appears
  await expect(playerDiv.getByText("player")).toBeVisible();

  // Validate character cards appear (all 3 characters) within player's div
  await expect(playerDiv.getByAltText("knight")).toBeVisible();
  await expect(playerDiv.getByAltText("archer")).toBeVisible();
  await expect(playerDiv.getByAltText("mage")).toBeVisible();

  // Validate character stats are visible
  await expect(playerDiv.getByText(/אביר דרגה 1/)).toBeVisible();
  await expect(playerDiv.getByText(/קשת דרגה 1/)).toBeVisible();
  await expect(playerDiv.getByText(/קוסם דרגה 1/)).toBeVisible();

  // Open a new page for player2
  const page2 = await page.context().newPage();
  await page2.goto("/");
  await expect(page2).toHaveTitle(/Heroes of Talisman/);
  await page2.waitForSelector('h2:has-text("Join A Game:")');

  // Player2 joins the test game
  await page2.getByLabel("Enter your name:").fill("player2");
  await page2.getByRole("button", { name: "test" }).click();
  await expect(page2).toHaveURL(/\/games\/test\/player2/);

  // Wait for player2's div to be visible before screenshot
  await page2.waitForSelector('[data-player="player2"]', { timeout: 5000 });

  await screenshot(page2, "player2-joined-game");

  // Get both players' divs
  const player1Div = page2.locator('[data-player="player"]');
  const player2Div = page2.locator('[data-player="player2"]');

  // Validate player2 sees their own div with name
  await expect(player2Div.getByText("player2")).toBeVisible();

  // Validate player2 sees their own characters
  await expect(player2Div.getByAltText("knight")).toBeVisible();
  await expect(player2Div.getByAltText("archer")).toBeVisible();
  await expect(player2Div.getByAltText("mage")).toBeVisible();

  // Validate player2 also sees player1's div with characters
  await expect(player1Div.getByText("player")).toBeVisible();
  await expect(player1Div.getByAltText("knight")).toBeVisible();

  // Clean up
  await page2.close();
});
