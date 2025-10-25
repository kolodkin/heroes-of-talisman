import className from "classnames";
import { useTranslation } from "react-i18next";
import styles from "./AbilityCard.module.css";
import commonStyles from "./Common.module.css";

const AbilityCard = ({ ability, isSelected, onClick }) => {
  const { t } = useTranslation();
  const abilityName = t(`abilities.${ability.name}.name`);
  const abilityDescription = t(`abilities.${ability.name}.description`);

  return (
    <div
      className={className({ [commonStyles.selected]: isSelected }, commonStyles.gamebtn, styles.card, "text-2xl")}
      onClick={onClick}
      data-ability={ability.name}
    >
      <div className={styles.content}>
        <p className={styles.name}>{abilityName}</p>
        <p className={styles.description}>{abilityDescription}</p>
      </div>
    </div>
  );
};

export default AbilityCard;
