import { getGamesViaAPI, deleteGameViaAPI } from "./api_helpers.js";

/**
 * Global teardown function that runs after all tests
 * Deletes all games starting with "test" to clean up test data
 */
async function globalTeardown() {
  console.log("\n🧹 Running global teardown: Cleaning up test games...");

  try {
    // Get all games from the API
    const games = await getGamesViaAPI();
    console.log(`Found ${games.length} total games`);

    // Filter games that start with "test"
    const testGames = games.filter((game) => game.toLowerCase().startsWith("test"));

    if (testGames.length === 0) {
      console.log("✓ No test games to clean up");
      return;
    }

    console.log(`Found ${testGames.length} test games to delete:`);
    testGames.forEach((game) => console.log(`  - ${game}`));

    // Delete each test game
    let successCount = 0;
    let failCount = 0;

    for (const gameName of testGames) {
      try {
        await deleteGameViaAPI(gameName);
        console.log(`  ✓ Deleted: ${gameName}`);
        successCount++;
      } catch (error) {
        console.error(`  ✗ Failed to delete ${gameName}: ${error.message}`);
        failCount++;
      }
    }

    console.log(`\n✓ Teardown complete: ${successCount} deleted, ${failCount} failed\n`);
  } catch (error) {
    console.error(`✗ Teardown failed: ${error.message}`);
    // Don't throw - we don't want teardown failures to fail the entire test run
  }
}

export default globalTeardown;
