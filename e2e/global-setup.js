import { getGamesViaAPI, deleteGameViaAPI } from "./api_helpers.js";

/**
 * Global setup function that runs before all tests
 * Deletes all games starting with "test" to ensure clean state
 */
async function globalSetup() {
  console.log("\n🧹 Running global setup: Cleaning up test games...");

  try {
    // Get all games from the API
    const games = await getGamesViaAPI();
    console.log(`Found ${games.length} total games`);

    // Filter games that start with "test" or common test game names
    const testGames = games.filter((game) => {
      const lowerName = game.toLowerCase();
      return (
        lowerName.startsWith("test") ||
        lowerName.includes("_test") ||
        lowerName.includes("not_alive") ||
        lowerName.includes("battle_") ||
        lowerName === "test basic flow"
      );
    });

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

    console.log(`\n✓ Setup complete: ${successCount} deleted, ${failCount} failed\n`);
  } catch (error) {
    console.error(`✗ Setup failed: ${error.message}`);
    // Don't throw - we don't want setup failures to fail the entire test run
  }
}

export default globalSetup;
