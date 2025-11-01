import { deleteGamesByPrefix } from "./api_helpers.js";

/**
 * Global setup - runs once before all tests
 * Cleans up any games starting with "test"
 */
export default async function globalSetup() {
  const deletedGames = await deleteGamesByPrefix("test");
  console.log(`Deleted ${deletedGames.length} test games:`, deletedGames);
}
