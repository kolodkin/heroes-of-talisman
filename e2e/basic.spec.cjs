const { test, expect } = require("@playwright/test");

async function screenshot(page, name) {
  const screenshot = await page.screenshot();
  await test.info().attach(name, { body: screenshot, contentType: "image/jpg" });
}

test("basic game flow", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Heroes of Talisman/);
  await page.waitForResponse(
    (response) => response.url().includes("/api/games/") && response.request().method() === "GET",
  );

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
});
