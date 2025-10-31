import { test, expect } from "@playwright/test";

export const FRONTEND_URL = `http://localhost:${process.env.WWW_PORT ?? "5173"}`;
// Increase timeout for containerized environments with single-process Chromium
// Use longer timeout (30s) when custom Chromium args are set, otherwise 10s
export const TIMEOUT = process.env.PLAYWRIGHT_CHROMIUM_ARGS ? 30000 : 10000;

export async function screenshot(page, name) {
  const screenshot = await page.screenshot();
  await test.info().attach(name, { body: screenshot, contentType: "image/jpg" });
}

export async function setupHomePage(page) {
  await page.goto("/");
  await expect(page).toHaveTitle(/Heroes of Talisman/);
  await page.waitForSelector('[data-section="join-game"]');
}

export async function joinGame(page, playerName, gameName) {
  await page.getByLabel("Enter your name:").fill(playerName);
  const gameButton = page.getByRole("button", { name: gameName });

  const [connectedLog] = await Promise.all([
    page.waitForEvent("console", {
      predicate: (msg) => msg.text().includes("notify.connected"),
      timeout: TIMEOUT,
    }),
    gameButton.click(),
  ]);

  await expect(page).toHaveURL(new RegExp(`/games/${encodeURIComponent(gameName)}/`));
  const connectedText = await connectedLog.args()[2].jsonValue();
  await test.info().attach(`${playerName}-connection-message`, { body: connectedText, contentType: "text/plain" });
}

/**
 * Join a game directly by URL (simpler version without console log wait)
 * Use this for preset games that already have players connected
 * @param {string} waitForSelector - CSS selector to wait for (default: '[data-battle-participant]')
 */
export async function joinGameViaUrl(page, playerName, gameName, waitForSelector = "[data-battle-participant]") {
  await page.goto(`/games/${encodeURIComponent(gameName)}/${encodeURIComponent(playerName)}`);
  await page.waitForSelector(waitForSelector, { timeout: 5000 });
}

/**
 * Wait for a toast notification to appear and optionally verify its content
 * @param {Page} page - Playwright page object
 * @param {Object} options - Options object
 * @param {string} options.type - Toast type: 'error', 'success', 'info', 'warning' (optional)
 * @param {string|RegExp} options.message - Expected message content (optional)
 * @param {number} options.timeout - Timeout in ms (default: 3000)
 * @returns {Promise<string>} The toast message text
 */
export async function waitForToast(page, { type, message, timeout = 3000 } = {}) {
  const selector = type ? `.Toastify__toast--${type}` : ".Toastify__toast";
  const toast = await page.waitForSelector(selector, { timeout, state: "visible" });
  const toastText = await toast.textContent();

  if (message) {
    if (message instanceof RegExp) {
      expect(toastText).toMatch(message);
    } else {
      expect(toastText).toContain(message);
    }
  }

  return toastText;
}
