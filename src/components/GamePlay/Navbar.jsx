import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import styles from "./Navbar.module.css";

function Navbar({ stage }) {
  const { gamename, username } = useParams();
  const { t } = useTranslation();

  return (
    <nav className={styles.navbar}>
      <div className={styles.content}>
        <h1 className={styles.gameName}>{gamename || "Heroes of Talisman"}</h1>
        <div className={styles.username}>{username || "Guest"}</div>
        <div className={styles.stage}>{stage ? t(`stageNames.${stage}`) : "Loading..."}</div>
      </div>
    </nav>
  );
}

export default Navbar;
