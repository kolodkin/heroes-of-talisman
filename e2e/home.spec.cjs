const { test, expect } = require('@playwright/test');

test('home page loads', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Heroes of Talisman/);
  const screenshot = await page.screenshot();
  await test.info().attach('home-page', { body: screenshot, contentType: 'image/png' });
});
