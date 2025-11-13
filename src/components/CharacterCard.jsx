import className from "classnames";
import { useTranslation } from "react-i18next";
import styles from "./CharacterCard.module.css";
import commonStyles from "./Common.module.css";
import { DiceIcon, HeartIcon } from "./Icons";

const signStr = (num) => (num ? (num >= 0 ? `+${num}` : `${num}`) : "");

const CharacterCard = ({ name, character, isSelected, onClick, size = "small" }) => {
  const { t } = useTranslation();
  const nameStr = t(`characterNames.${name}`);

  const cardClass = size === "normal" ? styles["card-normal"] : styles["card-small"];
  const isAlive = character.is_alive !== false; // Default to true if not specified

  // Calculate total attack with effects
  const baseAttack = character.attack || 0;
  const attackBonus = character.effect?.attack_bonus || 0;
  const attackNegBonus = character.effect?.attack_neg_bonus || 0;
  const totalAttack = baseAttack + attackBonus + attackNegBonus;
  const netEffect = attackBonus + attackNegBonus; // Positive = bonus, negative = penalty

  const handleClick = () => {
    if (!isAlive) {
      console.error(`Attempted to click not-alive character: ${name}. This should be prevented by CSS.`);
      return;
    }
    if (onClick) {
      onClick();
    }
  };

  return (
    <div
      className={className(
        { [commonStyles.selected]: isSelected },
        { [styles.alive]: isAlive },
        { [styles["not-alive"]]: !isAlive },
        commonStyles.gamebtn,
        styles.card,
        cardClass,
        "text-2xl",
      )}
      onClick={handleClick}
      data-character={name}
      data-level={character.level}
    >
      <img src={`/images/${name}.png`} alt={name} />
      <p className="w-full text-center font-bold">
        {nameStr} {t("character_card.level")} {character.level}
      </p>
      <div className={className("flex items-center gap-1", styles.stats)}>
        {[...Array(character.dice).keys()].map((i) => (
          <DiceIcon color="white" fill="black" key={i} />
        ))}
        {totalAttack !== 0 && (
          <span
            className={className("font-bold", {
              [styles["attack-bonus"]]: netEffect > 0,
              [styles["attack-penalty"]]: netEffect < 0,
            })}
            dir="ltr"
          >
            {signStr(totalAttack)}
          </span>
        )}
      </div>
      <div className={className("flex items-center gap-1", styles.stats)}>
        <HeartIcon color="red" />
        <span className="font-bold">
          [{character.health}/{character.max_health}]
        </span>
      </div>
    </div>
  );
};

export default CharacterCard;
