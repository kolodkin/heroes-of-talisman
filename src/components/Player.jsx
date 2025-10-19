/**
 * Player Component
 *
 * A reusable wrapper component that displays a dark overlay with "disconnected" text
 * when the player status is "disconnected" and showDisconnected is true.
 *
 * Usage:
 * <Player player={player} className={styles.player} showDisconnected={true}>
 *   <YourPlayerCard />
 * </Player>
 */
import React from "react";
import { useTranslation } from "react-i18next";
import styles from "./Player.module.css";
import commonStyles from "./Common.module.css";

const Player = ({ player, className, children, showDisconnected = false }) => {
  const { t } = useTranslation();
  const isDisconnected = player?.status === "disconnected";

  return (
    <div className={`${styles.container} ${className}`} data-player={player?.name} data-status={player?.status}>
      {children}
      {isDisconnected && showDisconnected && (
        <div className={commonStyles["gray-overlay"]}>
          <div className={`${commonStyles["gray-overlay-text"]} ${styles["disconnected-text"]}`}>
            {t("disconnected")}
          </div>
        </div>
      )}
    </div>
  );
};

export default Player;
