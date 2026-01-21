import className from "classnames";
import { useTranslation } from "react-i18next";
import styles from "./GamePlayCard.module.css";
import cardStyles from "./Card.module.css";

const GameplayCard = ({ cardName, isSelected, onClick, size = "normal" }) => {
  const { t } = useTranslation();
  const cardDisplayName = t(`cards.${cardName}.name`);
  const cardDescription = t(`cards.${cardName}.description`);
  const imagePath = `/images/cards/${cardName}.png`;

  const cardClass = size === "normal" ? styles["card-normal"] : styles["card-small"];

  return (
    <div
      className={className({ [cardStyles.selected]: isSelected }, cardStyles.card, styles.card, cardClass)}
      onClick={onClick}
      data-card={cardName}
    >
      <img src={imagePath} alt={cardDisplayName} className={styles.image} />
      <div className={styles.content}>
        <p className={styles.name}>{cardDisplayName}</p>
        <p className={styles.description}>{cardDescription}</p>
      </div>
    </div>
  );
};

export default GameplayCard;
