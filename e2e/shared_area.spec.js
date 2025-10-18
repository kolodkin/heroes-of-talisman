import { test, expect } from "@playwright/test";
import { createGameViaAPI, deleteGameViaAPI } from "./api_helpers.js";
import { TIMEOUT, screenshot, setupHomePage, joinGame } from "./test-helpers.js";

test("cards maintain minimum size and enable horizontal scroll on narrow viewport", async ({ page }) => {
  const testName = "shared-area-scroll";
  const gameName = `test-${testName}`;

  // Setup: Create game via API
  await deleteGameViaAPI(gameName); // Clean up if exists
  await createGameViaAPI(gameName);

  try {
    // Navigate to home and join game
    await setupHomePage(page);
    await joinGame(page, "player1", gameName);
    await screenshot(page, "player1-joined");

    // Add a second player so we have opponent selection stage
    const page2 = await page.context().newPage();
    await setupHomePage(page2);
    await joinGame(page2, "player2", gameName);
    await page.waitForSelector('[data-player="player2"]', { timeout: TIMEOUT });
    await screenshot(page, "player2-joined");

    // Test 1: Narrow viewport - Player menu cards
    await page.setViewportSize({ width: 350, height: 900 });
    await screenshot(page, "narrow-viewport-350");

    // Get player1's card container using data attribute
    const player1Container = page.locator('[data-player="player1"] [data-player-cards]');
    await expect(player1Container).toBeAttached();

    // Verify all 3 character cards exist in the DOM
    const player1Div = page.locator('[data-player="player1"]');
    await expect(player1Div.locator('[data-character="knight"]')).toBeAttached();
    await expect(player1Div.locator('[data-character="archer"]')).toBeAttached();
    await expect(player1Div.locator('[data-character="mage"]')).toBeAttached();

    // Verify container has horizontal scroll enabled
    const containerScrollInfo = await player1Container.evaluate((el) => {
      const styles = window.getComputedStyle(el);
      return {
        scrollWidth: el.scrollWidth,
        clientWidth: el.clientWidth,
        canScroll: el.scrollWidth > el.clientWidth,
        overflowX: styles.overflowX,
        flexWrap: styles.flexWrap,
      };
    });

    expect(containerScrollInfo.canScroll).toBe(true);
    expect(containerScrollInfo.overflowX).toBe("auto");
    expect(containerScrollInfo.flexWrap).toBe("nowrap");

    // Test 2: Player2's menu should also have scroll
    const player2Container = page.locator('[data-player="player2"] [data-player-cards]');
    await expect(player2Container).toBeAttached();

    const player2ScrollInfo = await player2Container.evaluate((el) => {
      const styles = window.getComputedStyle(el);
      return {
        scrollWidth: el.scrollWidth,
        clientWidth: el.clientWidth,
        canScroll: el.scrollWidth > el.clientWidth,
        overflowX: styles.overflowX,
        flexWrap: styles.flexWrap,
      };
    });

    expect(player2ScrollInfo.canScroll).toBe(true);
    expect(player2ScrollInfo.overflowX).toBe("auto");
    expect(player2ScrollInfo.flexWrap).toBe("nowrap");
    await screenshot(page, "player-menus-scrollable");

    // Test 3: Verify cards maintain size (flex-shrink: 0)
    // Get a card from the player menu (which uses Card wrapper)
    const cardInPlayerMenu = page.locator('[data-player="player1"] [data-player-cards] [data-character="knight"]');
    const cardShrinkInfo = await cardInPlayerMenu.evaluate((card) => {
      // Check the parent Card component for flex-shrink
      const cardWrapper = card.closest('[class*="card"]');
      const cardStyles = window.getComputedStyle(cardWrapper || card);
      const charCardStyles = window.getComputedStyle(card);
      return {
        cardWrapperFlexShrink: cardWrapper ? window.getComputedStyle(cardWrapper).flexShrink : null,
        charCardFlexShrink: charCardStyles.flexShrink,
        width: card.offsetWidth,
      };
    });

    // Debug: log the flex-shrink values
    console.log("Card shrink info:", cardShrinkInfo);

    // Either the Card wrapper or the CharacterCard should have flex-shrink: 0
    const hasFlexShrink0 = cardShrinkInfo.cardWrapperFlexShrink === "0" || cardShrinkInfo.charCardFlexShrink === "0";
    expect(hasFlexShrink0).toBe(true);
    expect(cardShrinkInfo.width).toBeGreaterThan(80); // Cards should maintain minimum size (small cards are ~100px)

    // Test 4: Wide viewport - verify no scroll needed
    await page.setViewportSize({ width: 1200, height: 900 });
    await screenshot(page, "wide-viewport-1200");

    const wideViewportScrollInfo = await player1Container.evaluate((el) => {
      const styles = window.getComputedStyle(el);
      return {
        scrollWidth: el.scrollWidth,
        clientWidth: el.clientWidth,
        canScroll: el.scrollWidth > el.clientWidth,
      };
    });

    // On wide viewport, scroll should not be needed (or minimal)
    expect(wideViewportScrollInfo.canScroll).toBe(false);

    // Clean up
    await page2.close();
  } finally {
    // Cleanup: Delete game via API
    await deleteGameViaAPI(gameName);
  }
});
