const API_BASE_URL = "http://localhost:8000";

/**
 * Create a game via the server API
 * @param {string} gameName - Name of the game to create
 * @returns {Promise<void>}
 */
export async function createGameViaAPI(gameName) {
  const response = await fetch(`${API_BASE_URL}/api/games/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name: gameName }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`Failed to create game: ${error.detail || response.statusText}`);
  }

  return response.json();
}

/**
 * Create a preset game via the server API
 * @param {string} gameName - Name of the game to create
 * @param {string} preset - Preset type (e.g., "battle_player_1_win", "battle_player_2_win", "battle_draw")
 * @returns {Promise<void>}
 */
export async function createPresetGameViaAPI(gameName, preset) {
  const response = await fetch(`${API_BASE_URL}/api/games/preset_games`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name: gameName, preset }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`Failed to create preset game: ${error.detail || response.statusText}`);
  }

  return response.json();
}

/**
 * Delete a game via the server API
 * @param {string} gameName - Name of the game to delete
 * @returns {Promise<void>}
 */
export async function deleteGameViaAPI(gameName) {
  const response = await fetch(`${API_BASE_URL}/api/games/${gameName}`, {
    method: "DELETE",
  });

  if (!response.ok && response.status !== 404) {
    const error = await response.json();
    throw new Error(`Failed to delete game: ${error.detail || response.statusText}`);
  }

  return response.status === 404 ? null : response.json();
}

/**
 * Get all games via the server API
 * @returns {Promise<string[]>} Array of game names
 */
export async function getGamesViaAPI() {
  const response = await fetch(`${API_BASE_URL}/api/games/`);

  if (!response.ok) {
    throw new Error(`Failed to get games: ${response.statusText}`);
  }

  return response.json();
}
