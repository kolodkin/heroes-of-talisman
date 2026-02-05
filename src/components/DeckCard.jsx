import { useTranslation } from "react-i18next";

import styles from "./DeckCard.module.css";

const DeckCard = ({ onClick }) => {
  const { t } = useTranslation();

  return (
    <div className={styles.deckCard} onClick={onClick} data-deck-card="true">
      <img src="/images/deck.png" alt={t("card_draw.deck")} className={styles.deckImage} />
    </div>
  );
};

export default DeckCard;
