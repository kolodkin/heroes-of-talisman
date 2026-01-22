import className from "classnames";
import { useTranslation } from "react-i18next";
import styles from "./GamePlayCard.module.css";
import cardStyles from "./Card.module.css";

const DeckCard = ({ onClick, size = "normal" }) => {
  const { t } = useTranslation();
  const cardClass = size === "normal" ? styles["card-normal"] : styles["card-small"];

  return (
    <div
      className={className(cardStyles.card, styles.card, cardClass)}
      onClick={onClick}
      data-deck-card="true"
    >
      <div className={styles.content} style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        fontSize: '3rem'
      }}>
        <span>🎴</span>
      </div>
      <div className={styles.content}>
        <p className={styles.name}>{t("card_draw.deck")}</p>
      </div>
    </div>
  );
};

export default DeckCard;
