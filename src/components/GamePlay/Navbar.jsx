import { useParams, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import className from "classnames";
import styles from "./Navbar.module.css";

function Navbar({ stage, playing, isPlaying }) {
  const { gamename, username } = useParams();
  const { t } = useTranslation();

  return (
    <nav className={className(styles.navbar, { [styles.active]: isPlaying })}>
      <div className={styles.content}>
        <div className={styles.startGroup}>
          <h1 className={styles.gameName}>{gamename || "Heroes of Talisman"}</h1>
          <div className={styles.username}>{username || "Guest"}</div>
          <div className={styles.stage}>{stage ? t(`stageNames.${stage}`) : "Loading..."}</div>
          <div className={styles.playing}>
            {t("nav.playing")}: {playing || "..."}
          </div>
        </div>
        <div className={styles.endGroup}>
          {import.meta.env.DEV && (
            <Link to="/presets" className={styles.homeButton}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
              </svg>
            </Link>
          )}
          <Link to="/" className={styles.homeButton}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
          </Link>
          <div className={styles.gameTitle}>{t("game_name")}</div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
