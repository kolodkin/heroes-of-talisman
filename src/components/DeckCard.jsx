import { useTranslation } from "react-i18next";

import styles from "./DeckCard.module.css";

const DeckCard = () => {
  const { t } = useTranslation();

  return (
    <div className={styles.deckCard} data-deck-card="true">
      <img src="/images/deck.png" alt={t("card_draw.deck")} className={styles.deckImage} />
    </div>
  );
};

export default DeckCard;
