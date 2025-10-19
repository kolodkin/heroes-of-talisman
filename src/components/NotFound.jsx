import { useEffect } from "react";
import { Link } from "react-router-dom";
import styles from "./NotFound.module.css";

const NotFound = () => {
  useEffect(() => {
    // Update document title for 404 page
    document.title = "404 - Page Not Found";

    // Set meta tag for robots
    const metaRobots = document.querySelector('meta[name="robots"]');
    if (metaRobots) {
      metaRobots.setAttribute("content", "noindex, nofollow");
    } else {
      const meta = document.createElement("meta");
      meta.name = "robots";
      meta.content = "noindex, nofollow";
      document.head.appendChild(meta);
    }

    return () => {
      // Reset title when component unmounts
      document.title = "Heroes of Talisman";
    };
  }, []);

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <h1 className={styles.title}>404</h1>
        <h2 className={styles.subtitle}>Page Not Found</h2>
        <p className={styles.message}>The page you are looking for does not exist.</p>
        <Link to="/" className={styles.homeLink}>
          Go to Home
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
