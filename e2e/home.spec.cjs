const { test, expect } = require('@playwright/test');

test('home page loads', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: /welcome to heroes of talisman/i })).toBeVisible();
  const screenshot = await page.screenshot();
  await test.info().attach('home-page', { body: screenshot, contentType: 'image/png' });
});
