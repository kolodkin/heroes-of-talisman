import { deleteGamesByPrefix } from "./api_helpers.js";

/**
 * Global teardown - runs once after all tests
 * Cleans up any games starting with "test"
 */
export default async function globalTeardown() {
  const deletedGames = await deleteGamesByPrefix("test");
  console.log(`Deleted ${deletedGames.length} test games:`, deletedGames);
}
