import React from "react";
import styles from "./GamePlay.module.css";

const GamePlay = ({ username, gamePlay }) => {
  if (!gamePlay || !gamePlay.players) {
    return null;
  }

  // Convert players object to array
  const playersArray = Object.values(gamePlay.players);

  if (playersArray.length === 0) {
    return null;
  }

  // Find current user's player index
  const userPlayerIndex = playersArray.findIndex((p) => p.name === username);

  // Arrange players: user at bottom, second at top, third at left, fourth at right
  // For 5+ players, cycle through: top, left, right, bottom
  const arrangePlayer = (index) => {
    if (index === userPlayerIndex) return "bottom";

    const relativeIndex = (index - userPlayerIndex + playersArray.length) % playersArray.length;
    const positions = ["top", "left", "right", "bottom"];

    if (relativeIndex === 1) return "top";
    if (relativeIndex === 2 && playersArray.length === 3) return "top";
    if (relativeIndex === 2) return "left";
    if (relativeIndex === 3) return "right";

    // For 5+ players, cycle through positions
    return positions[(relativeIndex - 1) % 4];
  };

  return (
    <div className={styles["game-play"]}>
      <div className={styles["shared-area"]}>{/* Shared area content will go here */}</div>

      {playersArray.map((player, index) => {
        const position = arrangePlayer(index);
        return (
          <div key={player.name} className={`${styles.player} ${styles[`player--${position}`]}`}>
            {player.name}
          </div>
        );
      })}
    </div>
  );
};

export default GamePlay;
