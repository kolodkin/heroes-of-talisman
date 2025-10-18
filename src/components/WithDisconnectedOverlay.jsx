/**
 * WithDisconnectedOverlay Component
 *
 * A reusable wrapper component that displays a dark overlay with "disconnected" text
 * when the player status is "disconnected".
 *
 * Usage:
 * <WithDisconnectedOverlay player={player}>
 *   <YourPlayerCard />
 * </WithDisconnectedOverlay>
 */
import React from "react";
import { useTranslation } from "react-i18next";
import styles from "./WithDisconnectedOverlay.module.css";

const WithDisconnectedOverlay = ({ player, children }) => {
  const { t } = useTranslation();
  const isDisconnected = player?.status === "disconnected";

  return (
    <div className={styles.container} data-player-disconnected={player?.name}>
      {children}
      {isDisconnected && (
        <div className={styles["disconnected-overlay"]} data-disconnected-indicator>
          <div className={styles["disconnected-text"]}>{t("disconnected")}</div>
        </div>
      )}
    </div>
  );
};

export default WithDisconnectedOverlay;
