import { useParams, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import className from "classnames";
import styles from "./Navbar.module.css";

function Navbar({ stage, playing }) {
  const { gamename, username } = useParams();
  const { t } = useTranslation();
  const isActivePlayer = playing === username;

  return (
    <nav className={className(styles.navbar, { [styles.active]: isActivePlayer })}>
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
