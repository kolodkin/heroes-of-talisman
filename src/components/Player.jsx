/**
 * Player Component
 *
 * A reusable wrapper component that displays a dark overlay with "disconnected" text
 * when the player status is "disconnected".
 *
 * Usage:
 * <Player player={player} className={styles.player}>
 *   <YourPlayerCard />
 * </Player>
 */
import React from "react";
import { useTranslation } from "react-i18next";
import styles from "./Player.module.css";

const Player = ({ player, className, children }) => {
  const { t } = useTranslation();
  const isDisconnected = player?.status === "disconnected";

  return (
    <div className={`${styles.container} ${className}`} data-player={player?.name} data-status={player?.status}>
      {children}
      {isDisconnected && (
        <div className={styles["disconnected-overlay"]}>
          <div className={styles["disconnected-text"]}>{t("disconnected")}</div>
        </div>
      )}
    </div>
  );
};

export default Player;
