import { test as base, expect } from "@playwright/test";

export const FRONTEND_URL = `http://localhost:${process.env.WWW_PORT ?? "5173"}`;
export const TIMEOUT = 1000;

/**
 * Extended test with gameName fixture
 * Automatically generates unique game name and cleans up after test
 */
export const test = base.extend({
  gameName: async ({}, use) => {
    const testInfo = base.info();
    const gameName = `test ${testInfo.title}`;

    // Provide the game name to the test
    await use(gameName);

    // Cleanup: Delete the game after the test completes
    try {
      const API_URL = `http://localhost:${process.env.API_PORT ?? "8000"}`;
      await fetch(`${API_URL}/api/games/${encodeURIComponent(gameName)}`, {
        method: "DELETE",
      });
    } catch (error) {
      // Ignore cleanup errors (game might not exist)
      console.log(`Cleanup: Could not delete game "${gameName}":`, error.message);
    }
  },
});

export { expect };

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
  const gameButton = page.getByRole("button", { name: gameName, exact: true });

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

/**
 * Wait for the game to transition to a specific stage
 * @param {Page} page - Playwright page object
 * @param {string} stage - Stage name (e.g., 'character_select', 'ability_selection', 'battle_dice_roll')
 * @param {number} timeout - Timeout in ms (default: TIMEOUT constant)
 * @returns {Promise<void>}
 */
export async function waitForStage(page, stage, timeout = TIMEOUT) {
  await page.waitForSelector(`[data-game-stage="${stage}"]`, { timeout });
}

/**
 * Wait for a game_update WebSocket message to be logged to the console
 * @param {Page} page - Playwright page object
 * @param {number} timeout - Timeout in ms (default: TIMEOUT constant)
 * @returns {Promise<void>}
 */
export async function waitForGameUpdate(page, timeout = TIMEOUT) {
  await page.waitForEvent("console", {
    predicate: (msg) => msg.text().includes("onmessage") && msg.text().includes("game_update"),
    timeout,
  });
}
