import { test as base, expect } from "@playwright/test";

import { createPresetGameViaAPI } from "./api_helpers.js";

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
  await dismissToasts(page);
}

/**
 * Dismiss all visible toast notifications.
 * Closes each toast and waits for full detach from DOM.
 * Works both with and without VITE_E2E (real toasts or stubbed toasts).
 * @param {Page} page - Playwright page object
 */
export async function dismissToasts(page) {
  // Dismiss all visible toasts one by one.
  // Cap at 10 iterations to prevent infinite loops if toasts keep re-appearing.
  for (let i = 0; i < 10; i++) {
    const toastLocator = page.locator(".Toastify__toast").first();
    const isVisible = await toastLocator.isVisible().catch(() => false);
    if (!isVisible) break;

    const closeButton = toastLocator.locator(".Toastify__close-button");
    await closeButton.click({ force: true, timeout: 1000 }).catch(() => {});
    await toastLocator.waitFor({ state: "detached", timeout: 5000 }).catch(() => {});
  }
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
  await dismissToasts(page);
}

/**
 * Wait for a toast notification to appear and optionally verify its content.
 * Works in two modes:
 * - VITE_E2E=true: toasts are stubbed to console.log, listens for console events
 * - Without VITE_E2E: waits for real toast DOM element and reads its text
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

  // Race: console-based (VITE_E2E) vs DOM-based (real toasts)
  const consolePromise = page
    .waitForEvent("console", {
      predicate: (msg) => msg.text().startsWith(prefix),
      timeout,
    })
    .then((consoleMsg) => consoleMsg.text().slice(prefix.length).trim());

  const domPromise = page
    .locator(".Toastify__toast")
    .first()
    .waitFor({ state: "visible", timeout })
    .then(() => page.locator(".Toastify__toast").first().innerText());

  return Promise.race([consolePromise, domPromise]).then((toastText) => {
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
 * Set up a two-player preset game and join both players.
 * Returns page2 which must be closed after the test completes.
 * @param {Page} page - Playwright page for player1
 * @param {string} gameName - Game name (from gameName fixture)
 * @param {string} presetName - Preset name (e.g., "battle_player_1_win")
 * @param {string} p1Selector - Selector to wait for after player1 joins (default: '[data-battle-participant]')
 * @param {string} p2Selector - Selector to wait for after player2 joins (default: '[data-game-stage]')
 * @returns {Promise<Page>} page2 - The second player's page
 */
export async function setupPresetGame(
  page,
  gameName,
  presetName,
  p1Selector = "[data-battle-participant]",
  p2Selector = "[data-game-stage]",
) {
  await createPresetGameViaAPI(gameName, presetName);
  await joinGameViaUrl(page, "player1", gameName, p1Selector);
  const page2 = await page.context().newPage();
  await joinGameViaUrl(page2, "player2", gameName, p2Selector);
  // Dismiss any toasts on page1 that may have appeared from player2 joining
  await dismissToasts(page);
  return page2;
}

/**
 * Expand the players menu (if collapsed) and expand all character cards.
 * @param {Page} page - Playwright page object
 */
export async function expandAllPlayers(page) {
  await expandPlayersMenuIfCollapsed(page);
  await page.getByRole("button", { name: "Expand all players" }).click();
}

/**
 * Collapse all character cards by clicking "Minimize all players".
 * @param {Page} page - Playwright page object
 */
export async function collapseAllPlayers(page) {
  await page.getByRole("button", { name: "Minimize all players" }).click();
}

/**
 * Get a character card locator for a specific player and character.
 * @param {Page} page - Playwright page object
 * @param {string} playerName - Player name (e.g., "player1")
 * @param {string} characterName - Character name (e.g., "knight")
 * @returns {Locator} Playwright locator for the character card
 */
export function getCharacterCard(page, playerName, characterName) {
  return page.locator(`[data-player="${playerName}"] [data-player-cards] [data-character="${characterName}"]`);
}

/**
 * Assert the level and/or health of a character card.
 * @param {Locator} card - Playwright locator for the character card
 * @param {Object} state - Expected state
 * @param {string|number} [state.level] - Expected data-level attribute value
 * @param {string} [state.health] - Expected health text (e.g., "[1/2]")
 */
export async function expectCharacterState(card, { level, health } = {}) {
  if (level !== undefined) {
    await expect(card).toHaveAttribute("data-level", String(level));
  }
  if (health !== undefined) {
    await expect(card).toContainText(health);
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

/**
 * Helper to get score from battle row
 * @param {Page} page - Playwright page object
 * @param {string} role - Battle role: 'active' or 'opponent'
 * @returns {Promise<number>} The score value
 */
export async function getScore(page, role) {
  const scoreElement = page.locator(`[data-battle-role="${role}"] [data-score]`);
  await expect(scoreElement).toBeVisible();
  const scoreText = await scoreElement.textContent();
  return parseInt(scoreText.trim());
}

/**
 * Helper to verify winner badge is shown for the correct role
 * Waits for the initial appearance animation to complete
 * @param {Page} page - Playwright page object
 * @param {string} winnerRole - Battle role of the winner: 'active' or 'opponent'
 */
export async function verifyWinner(page, winnerRole) {
  const winnerBadge = page.locator(`[data-battle-role="${winnerRole}"] [data-winner-badge]`);
  await expect(winnerBadge).toBeVisible();

  await winnerBadge.evaluate((element) => {
    const animations = element.getAnimations();
    const appearAnimation = animations.find((anim) =>
      anim.effect?.getKeyframes().some((frame) => frame.opacity !== undefined),
    );
    return appearAnimation ? appearAnimation.finished : Promise.resolve();
  });
}
