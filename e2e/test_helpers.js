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
    const gameName = `test ${testInfo.project.name} ${testInfo.title}`;

    // Provide the game name to the test
    await use(gameName);

    // Cleanup: Delete the game after the test completes
    try {
      const API_URL = `http://localhost:${process.env.APP_PORT ?? "8000"}`;
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
  const screenshot = await page.screenshot({ type: "jpeg", quality: 80 });
  await test.info().attach(name, { body: screenshot, contentType: "image/jpeg" });
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

  // Dismiss connection toast to keep screenshots clean
  await dismissConnectionToast(page);
}

/**
 * Dismiss the connection toast notification
 * Waits for the toast to appear and clicks the close button
 * @param {Page} page - Playwright page object
 */
export async function dismissConnectionToast(page) {
  // Check if toast exists without throwing on timeout
  const toastLocator = page.locator(".Toastify__toast").first();
  const isVisible = await toastLocator.isVisible().catch(() => false);

  if (isVisible) {
    // Click the close button (× button) with force to avoid actionability issues
    const closeButton = toastLocator.locator(".Toastify__close-button");
    if (await closeButton.isVisible()) {
      await closeButton.click({ force: true, timeout: 1000 }).catch(() => {});
    }
    // Wait for toast to be fully removed from DOM (not just hidden)
    await toastLocator.waitFor({ state: "detached", timeout: 5000 }).catch(() => {});
  }

  // The container div stays in DOM but is inert when no toasts are present.
  // We already waited for the individual toast element to detach above.
}

/**
 * Join a game directly by URL (simpler version without console log wait)
 * Use this for preset games that already have players connected
 * @param {string} waitForSelector - CSS selector to wait for (default: '[data-battle-participant]')
 */
export async function joinGameViaUrl(page, playerName, gameName, waitForSelector = "[data-battle-participant]") {
  await page.goto(`/games/${encodeURIComponent(gameName)}/${encodeURIComponent(playerName)}`);
  await page.waitForSelector(waitForSelector, { timeout: 5000 });

  // Dismiss connection toast to keep screenshots clean
  await dismissConnectionToast(page);
}

/**
 * Wait for a toast notification to appear and optionally verify its content.
 * In E2E mode, toasts are stubbed to console.log so this listens for console events.
 *
 * IMPORTANT: Call this function BEFORE the action that triggers the toast, then await
 * the returned promise after the action. This ensures the listener is registered before
 * the toast fires, avoiding any race conditions.
 *
 * @param {Page} page - Playwright page object
 * @param {Object} options - Options object
 * @param {string} options.type - Toast type: 'error', 'success' (optional, defaults to any toast)
 * @param {string|RegExp} options.message - Expected message content (optional)
 * @param {number} options.timeout - Timeout in ms (default: 3000)
 * @returns {Promise<string>} The toast message text
 */
export function waitForToast(page, { type, message, timeout = 3000 } = {}) {
  const prefix = type ? `toast.${type}` : "toast";
  const consolePromise = page.waitForEvent("console", {
    predicate: (msg) => msg.text().startsWith(prefix),
    timeout,
  });

  return consolePromise.then((consoleMsg) => {
    const toastText = consoleMsg.text().slice(prefix.length).trim();

    if (message) {
      if (message instanceof RegExp) {
        expect(toastText).toMatch(message);
      } else {
        expect(toastText).toContain(message);
      }
    }

    return toastText;
  });
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

/**
 * Expand the players menu if it is currently collapsed (e.g., on mobile landscape).
 * Uses the data-players-menu-state attribute to check the current state.
 * @param {Page} page - Playwright page object
 */
export async function expandPlayersMenuIfCollapsed(page) {
  const gamePlay = page.locator('[data-players-menu-state="collapsed"]');
  if (await gamePlay.isVisible().catch(() => false)) {
    const expandButton = page.locator("[data-expand-button]");
    await expandButton.click();
  }
}

/**
 * Validate card hover effects (translateY and box-shadow)
 * @param {Locator} cardLocator - Playwright locator for the card element
 */
export async function validateCardHoverEffect(cardLocator) {
  await cardLocator.hover();
  await expect(cardLocator).toHaveCSS("transform", "matrix(1, 0, 0, 1, 0, -4)");
  await expect(cardLocator).toHaveCSS("box-shadow", "rgba(0, 0, 0, 0.3) 0px 4px 8px 0px");
}
