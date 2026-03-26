import className from "classnames";
import { useTranslation } from "react-i18next";
import styles from "./GamePlayCard.module.css";
import cardStyles from "./Card.module.css";

const AbilityCard = ({ ability, isSelected, onClick, size = "normal" }) => {
  const { t } = useTranslation();
  const abilityName = t(`abilities.${ability.name}.name`);
  const abilityDescription = t(`abilities.${ability.name}.description`);
  const imagePath = `/images/abilities/${ability.name}.jpg`;

  const cardClass = size === "normal" ? styles["card-normal"] : styles["card-small"];

  return (
    <div
      className={className({ [cardStyles.selected]: isSelected }, cardStyles.card, styles.card, cardClass)}
      onClick={onClick}
      data-ability={ability.name}
    >
      <img src={imagePath} alt={abilityName} className={styles.image} />
      <div className={styles.content}>
        <p className={styles.name}>{abilityName}</p>
        <p className={styles.description}>{abilityDescription}</p>
      </div>
    </div>
  );
};

export default AbilityCard;
