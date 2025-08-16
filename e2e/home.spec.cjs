const { test, expect } = require('@playwright/test');

test('create and join test game', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Heroes of Talisman/);
  await page.waitForResponse(
    (response) =>
      response.url().includes('/api/games/') && response.request().method() === 'GET',
  );

  await page.getByLabel('Enter your name:').fill('player');

  const testGame = page.getByRole('button', { name: 'test' });
  if (await testGame.count()) {
    await page
      .locator('li', { has: testGame })
      .getByRole('button', { name: '🗑️' })
      .click();
    await expect(testGame).toHaveCount(0);
  }

  let screenshot = await page.screenshot();
  await test.info().attach('home', { body: screenshot, contentType: 'image/jpeg' });

  await page.getByLabel('Add New Game:').fill('test');
  await page.getByRole('button', { name: '+' }).click();
  await expect(testGame).toBeVisible();

  screenshot = await page.screenshot();
  await test.info().attach('home-with-test', { body: screenshot, contentType: 'image/jpeg' });

  await testGame.click();
  await expect(page).toHaveURL(/\/games\/test\//);

  screenshot = await page.screenshot();
  await test.info().attach('joined-game', { body: screenshot, contentType: 'image/jpeg' });
});
