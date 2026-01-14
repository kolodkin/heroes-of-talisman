import React from "react";
import { useTranslation } from "react-i18next";
import styles from "./StatusIndicator.module.css";

/**
 * StatusIndicator component displays the current turn status as an overlay
 *
 * @param {Object} props
 * @param {"your_turn" | "opponent_playing" | "roll_dice"} props.status - The current game status
 * @param {string} props.playerName - The name of the player who is playing (for opponent_playing status)
 */
export const StatusIndicator = ({ status, playerName }) => {
  const { t } = useTranslation();

  if (!status) {
    return null;
  }

  const getStatusContent = () => {
    switch (status) {
      case "your_turn":
        return {
          text: t("status_indicator.your_turn"),
          className: styles.yourTurn,
        };
      case "roll_dice":
        return {
          text: t("status_indicator.roll_dice"),
          className: styles.rollDice,
        };
      case "opponent_playing":
        return {
          text: t("status_indicator.player_playing", { player: playerName }),
          className: styles.opponentPlaying,
        };
      default:
        return null;
    }
  };

  const statusContent = getStatusContent();

  if (!statusContent) {
    return null;
  }

  return (
    <div
      className={`${styles.statusIndicator} ${statusContent.className}`}
      data-status={status}
      data-player-name={playerName || ""}
    >
      {statusContent.text}
    </div>
  );
};
