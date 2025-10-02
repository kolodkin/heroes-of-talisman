import { useParams } from "react-router-dom";
import styles from "./Navbar.module.css";

function Navbar({ stage }) {
  const { gamename, username } = useParams();

  return (
    <nav className={styles.navbar}>
      <div className={styles.content}>
        <h1 className={styles.gameName}>{gamename || "Heroes of Talisman"}</h1>
        <div className={styles.username}>{username || "Guest"}</div>
        <div className={styles.stage}>{stage || "Loading..."}</div>
      </div>
    </nav>
  );
}

export default Navbar;
