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
 * @param {string} [stage] - Optional stage override (e.g., "opponent_selection", "battle")
 * @returns {Promise<void>}
 */
export async function createPresetGameViaAPI(gameName, preset, stage = null) {
  const body = { name: gameName, preset };
  if (stage !== null) {
    body.stage = stage;
  }

  const response = await fetch(`${API_BASE_URL}/api/games/preset_games`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
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

/**
 * Send a debug action via WebSocket
 * @param {string} gameName - Name of the game
 * @param {string} username - Username to send the action as
 * @param {string} action - Action name (e.g., "debug_set_battle_dice_rolls")
 * @param {object} data - Action data
 * @returns {Promise<void>}
 */
export async function sendDebugActionViaWS(gameName, username, action, data) {
  const wsUrl = `ws://localhost:8000/ws/${encodeURIComponent(gameName)}/${encodeURIComponent(username)}`;

  return new Promise((resolve, reject) => {
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      const actionPayload = {
        username,
        action,
        ...data,
      };
      ws.send(JSON.stringify(actionPayload));

      // Wait a bit for the action to be processed
      setTimeout(() => {
        ws.close();
        resolve();
      }, 100);
    };

    ws.onerror = (error) => {
      reject(new Error(`WebSocket error: ${error}`));
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.error) {
        ws.close();
        reject(new Error(`Action error: ${message.error}`));
      }
    };
  });
}
