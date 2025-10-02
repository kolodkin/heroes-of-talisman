import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import styles from "./Navbar.module.css";

function Navbar() {
  const [isVisible, setIsVisible] = useState(true);
  const { gamename, username } = useParams();

  const toggleNavbar = () => {
    setIsVisible((prev) => !prev);
  };

  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key === "Escape") {
        toggleNavbar();
      }
    };

    window.addEventListener("keydown", handleKeyPress);
    return () => window.removeEventListener("keydown", handleKeyPress);
  }, []);

  return (
    <>
      <nav className={`${styles.navbar} ${isVisible ? styles.visible : styles.hidden}`}>
        <div className={styles.content}>
          <h1 className={styles.gameName}>{gamename || "Heroes of Talisman"}</h1>
          <div className={styles.username}>{username || "Guest"}</div>
        </div>
        <button className={styles.toggleBtn} onClick={toggleNavbar} aria-label="Toggle navbar">
          {isVisible ? "▲" : "▼"}
        </button>
      </nav>
      {!isVisible && (
        <button className={styles.showBtn} onClick={toggleNavbar} aria-label="Show navbar">
          ▼
        </button>
      )}
    </>
  );
}

export default Navbar;
