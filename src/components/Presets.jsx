import React, { useState, useEffect } from "react";
import styles from "./Presets.module.css";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

const PRESET_OPTIONS = [
  { value: "default", label: "Default" },
  { value: "archer_bouncing_arrow", label: "Archer Bouncing Arrow" },
  { value: "archer_not_alive", label: "Archer Not Alive" },
  { value: "battle_draw", label: "Battle Draw" },
  { value: "battle_player_1_win", label: "Battle Player 1 Win" },
  { value: "battle_player_2_win", label: "Battle Player 2 Win" },
  { value: "battle_with_effects", label: "Battle with Effects" },
  { value: "health_1", label: "Health 1" },
  { value: "knight_not_alive", label: "Knight Not Alive" },
  { value: "knights_attack_bonus_draw", label: "Knights Attack Bonus Draw" },
  { value: "mage_not_alive", label: "Mage Not Alive" },
  { value: "opponent_selection_preset", label: "Opponent Selection" },
  { value: "single_player", label: "Single Player" },
];

const Presets = () => {
  const navigate = useNavigate();
  const [gameName, setGameName] = useState(localStorage.getItem("preset_game_name") || "");
  const [player1Name, setPlayer1Name] = useState(localStorage.getItem("preset_player1_name") || "");
  const [player2Name, setPlayer2Name] = useState(localStorage.getItem("preset_player2_name") || "");
  const [preset, setPreset] = useState(localStorage.getItem("preset_selected") || "default");

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate inputs
    if (!gameName.trim()) {
      toast.error("Game name is required");
      return;
    }
    if (!player1Name.trim()) {
      toast.error("Player 1 name is required");
      return;
    }
    if (!player2Name.trim()) {
      toast.error("Player 2 name is required");
      return;
    }

    // Save to localStorage
    localStorage.setItem("preset_game_name", gameName);
    localStorage.setItem("preset_player1_name", player1Name);
    localStorage.setItem("preset_player2_name", player2Name);
    localStorage.setItem("preset_selected", preset);

    try {
      // Delete existing game if it exists
      const deleteResponse = await fetch(`/api/games/${gameName}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      });

      // Ignore 404 errors (game didn't exist)
      if (!deleteResponse.ok && deleteResponse.status !== 404) {
        const deleteResult = await deleteResponse.json();
        toast.error(deleteResult.detail || "Failed to delete existing game");
        return;
      }

      // Create game with preset
      const response = await fetch("/api/games/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: gameName,
          preset: preset,
          player1_name: player1Name,
          player2_name: player2Name,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        toast.error(result.detail || "Failed to create game");
        return;
      }

      toast.success(`Game "${gameName}" created with preset "${preset}"`);

      // Navigate to the game as player1
      navigate(`/games/${gameName}/${player1Name}`);
    } catch (error) {
      toast.error("Error creating game: " + error.message);
    }
  };

  const handleGameNameChange = (e) => {
    setGameName(e.target.value);
  };

  const handlePlayer1NameChange = (e) => {
    setPlayer1Name(e.target.value);
  };

  const handlePlayer2NameChange = (e) => {
    setPlayer2Name(e.target.value);
  };

  const handlePresetChange = (e) => {
    setPreset(e.target.value);
  };

  return (
    <div className={styles.presets}>
      <div className={styles.container}>
        <h1>Create Game from Preset</h1>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.inputGroup}>
            <label htmlFor="gameName">Game Name:</label>
            <input
              id="gameName"
              className={styles.input}
              type="text"
              value={gameName}
              onChange={handleGameNameChange}
              placeholder="Enter game name"
            />
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="player1Name">Player 1 Name:</label>
            <input
              id="player1Name"
              className={styles.input}
              type="text"
              value={player1Name}
              onChange={handlePlayer1NameChange}
              placeholder="Enter player 1 name"
            />
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="player2Name">Player 2 Name:</label>
            <input
              id="player2Name"
              className={styles.input}
              type="text"
              value={player2Name}
              onChange={handlePlayer2NameChange}
              placeholder="Enter player 2 name"
            />
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="preset">Preset:</label>
            <select id="preset" className={styles.select} value={preset} onChange={handlePresetChange}>
              {PRESET_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <button type="submit" className={styles.submitButton}>
            (Re)Create Game
          </button>
        </form>

        <button className={styles.backButton} onClick={() => navigate("/")}>
          Back to Home
        </button>
      </div>
    </div>
  );
};

export default Presets;
