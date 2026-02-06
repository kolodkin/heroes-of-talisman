import { createPresetGameViaAPI } from "./api_helpers.js";
import { test, expect, screenshot, FRONTEND_URL, dismissConnectionToast } from "./test_helpers.js";

test("shared area dynamic alignment - character selection stage", async ({ page, gameName }) => {
  const playerName = "player1";

  // Setup: Create game in character selection stage using default preset
  await createPresetGameViaAPI(gameName, "default");

  // Navigate directly to the game
  await page.goto(`${FRONTEND_URL}/games/${gameName}/${playerName}`);
  await page.waitForSelector('h2:has-text("בחר דמות")', { timeout: 5000 });
  await screenshot(page, "character-select-loaded");

  // Test 1: Narrow viewport - should align to start with scroll
  await page.setViewportSize({ width: 700, height: 900 });
  await page.waitForTimeout(200); // Wait for hook to detect scroll

  const narrowViewportInfo = await page.evaluate(() => {
    const contentArea = document.querySelector("[data-shared-content]");
    if (!contentArea) return { error: "content area not found" };

    const cardsWrapper = contentArea.firstElementChild;
    const cardsContainer = cardsWrapper.querySelector('[class*="cardsContainer"]');

    return {
      wrapperJustifyContent: window.getComputedStyle(cardsWrapper).justifyContent,
      canScroll: cardsContainer.scrollWidth > cardsContainer.clientWidth,
      scrollWidth: cardsContainer.scrollWidth,
      clientWidth: cardsContainer.clientWidth,
    };
  });

  // Verify alignment to start and scroll enabled
  expect(narrowViewportInfo.wrapperJustifyContent).toBe("flex-start");
  expect(narrowViewportInfo.canScroll).toBe(true);

  // Verify first card (mage in RTL) is visible
  await expect(page.locator('[data-character="mage"]').first()).toBeInViewport();
  await screenshot(page, "narrow-viewport-scroll-enabled");

  // Scroll to the end (left in RTL) to show last card (knight)
  await page.evaluate(() => {
    const contentArea = document.querySelector("[data-shared-content]");
    const cardsWrapper = contentArea.firstElementChild;
    const cardsContainer = cardsWrapper.querySelector('[class*="cardsContainer"]');

    // In RTL, scroll to the left (negative scrollLeft)
    cardsContainer.scrollLeft = -cardsContainer.scrollWidth;
  });
  await page.waitForTimeout(100); // Wait for scroll to complete

  // Verify last card (knight in RTL) is visible after scrolling
  await expect(page.locator('[data-character="knight"]').first()).toBeInViewport();

  // Test 2: Wide viewport - should center with no scroll
  await page.setViewportSize({ width: 1200, height: 900 });
  await page.waitForTimeout(200); // Wait for hook to re-detect

  const wideViewportInfo = await page.evaluate(() => {
    const contentArea = document.querySelector("[data-shared-content]");
    const cardsWrapper = contentArea.firstElementChild;
    const cardsContainer = cardsWrapper.querySelector('[class*="cardsContainer"]');

    return {
      wrapperJustifyContent: window.getComputedStyle(cardsWrapper).justifyContent,
      canScroll: cardsContainer.scrollWidth > cardsContainer.clientWidth,
    };
  });

  // Verify centered and no scroll
  expect(wideViewportInfo.wrapperJustifyContent).toBe("center");
  expect(wideViewportInfo.canScroll).toBe(false);
  await screenshot(page, "shared-area-wide-centered");

  // All cards should be visible
  await expect(page.locator('[data-character="mage"]').first()).toBeInViewport();
  await expect(page.locator('[data-character="archer"]').first()).toBeInViewport();
  await expect(page.locator('[data-character="knight"]').first()).toBeInViewport();
});

test("shared area dynamic alignment - opponent selection stage", async ({ page, gameName }) => {
  const playerName = "player1";

  // Setup: Create game in opponent selection stage
  await createPresetGameViaAPI(gameName, "opponent_selection_preset");

  // Navigate directly to the game
  await page.goto(`${FRONTEND_URL}/games/${gameName}/${playerName}`);
  await page.waitForSelector('h2:has-text("בחר את יריבך")', { timeout: 5000 });

  // Expand first opponent to see character cards (look in shared area)
  const firstOpponent = page.locator('[data-shared-area-active="true"] [data-player="player2"]').first();
  await firstOpponent.locator('button[aria-label="Expand player"]').click();
  await page.waitForSelector("[data-opponent-cards-expanded]", { timeout: 1000 });
  await screenshot(page, "opponent-expanded");

  // Test 1: Narrow viewport - expanded character cards should have scroll
  await page.setViewportSize({ width: 700, height: 900 });
  await page.waitForTimeout(200); // Wait for hook to detect scroll

  const narrowViewportInfo = await page.evaluate(() => {
    const expandedCards = document.querySelector("[data-opponent-cards-expanded]");
    if (!expandedCards) return { error: "expanded cards not found" };

    return {
      canScroll: expandedCards.scrollWidth > expandedCards.clientWidth,
      scrollWidth: expandedCards.scrollWidth,
      clientWidth: expandedCards.clientWidth,
    };
  });

  // Verify scroll is enabled for character cards
  expect(narrowViewportInfo.canScroll).toBe(true);

  // Verify first character card (mage in RTL) is visible
  await expect(firstOpponent.locator('[data-character="mage"]').first()).toBeInViewport();

  // Scroll to the end (left in RTL) to show last card (knight)
  await page.evaluate(() => {
    const expandedCards = document.querySelector("[data-opponent-cards-expanded]");
    if (expandedCards) {
      // In RTL, scroll to the left (negative scrollLeft)
      expandedCards.scrollLeft = -expandedCards.scrollWidth;
    }
  });
  await page.waitForTimeout(100); // Wait for scroll to complete
  await screenshot(page, "opponent-narrow-scrolled-to-end");

  // Verify last card (knight in RTL) is visible after scrolling
  await expect(firstOpponent.locator('[data-character="knight"]').first()).toBeInViewport();

  // Test 2: Wide viewport - no scroll needed
  await page.setViewportSize({ width: 1200, height: 900 });
  await page.waitForTimeout(200); // Wait for hook to re-detect

  const wideViewportInfo = await page.evaluate(() => {
    const expandedCards = document.querySelector("[data-opponent-cards-expanded]");
    if (!expandedCards) return { error: "expanded cards not found" };

    return {
      canScroll: expandedCards.scrollWidth > expandedCards.clientWidth,
    };
  });

  // Verify no scroll needed
  expect(wideViewportInfo.canScroll).toBe(false);
  await screenshot(page, "opponent-wide-no-scroll");

  // All cards should be visible
  await expect(firstOpponent.locator('[data-character="mage"]').first()).toBeInViewport();
  await expect(firstOpponent.locator('[data-character="archer"]').first()).toBeInViewport();
  await expect(firstOpponent.locator('[data-character="knight"]').first()).toBeInViewport();
});

test("Enter key triggers action button on desktop", async ({ page, gameName }) => {
  const playerName = "player1";

  // Setup: Create game in character selection stage with 2 players
  await createPresetGameViaAPI(gameName, "mage_not_alive");

  // Navigate to game with desktop viewport
  await page.setViewportSize({ width: 1200, height: 900 });
  await page.goto(`${FRONTEND_URL}/games/${gameName}/${playerName}`);
  await page.waitForSelector('[data-game-stage="character_select"]', { timeout: 5000 });
  await dismissConnectionToast(page);
  await screenshot(page, "enter-key-character-select-loaded");

  // Select knight character by clicking it
  const knightCard = page.locator('[data-shared-area-active="true"] [data-character="knight"]').first();
  await knightCard.click();
  await expect(knightCard).toHaveClass(/selected/);
  await screenshot(page, "enter-key-knight-selected");

  // Press Enter to confirm selection (instead of clicking action button)
  await page.keyboard.press("Enter");

  // Verify stage transitioned to card_draw (action button was triggered)
  await expect(page.locator('[data-game-stage="card_draw"]')).toBeVisible({ timeout: 5000 });
  await screenshot(page, "enter-key-stage-transitioned-to-card-draw");
});
