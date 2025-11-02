import className from "classnames";
import { useTranslation } from "react-i18next";
import styles from "./CharacterCard.module.css";
import commonStyles from "./Common.module.css";
import { DiceIcon, HeartIcon } from "./Icons";

const signStr = (num) => (num ? (num >= 0 ? `+${num}` : `-${num}`) : "");

const CharacterCard = ({ name, character, isSelected, onClick, size = "small" }) => {
  const { t } = useTranslation();
  const nameStr = t(`characterNames.${name}`);

  const cardClass = size === "normal" ? styles["card-normal"] : styles["card-small"];
  const isAlive = character.is_alive !== false; // Default to true if not specified
  const isFrozen = character.effects_total?.skip_next_turn || false;

  const handleClick = () => {
    if (!isAlive) {
      console.error(`Attempted to click not-alive character: ${name}. This should be prevented by CSS.`);
      return;
    }
    if (isFrozen) {
      console.error(`Attempted to click frozen character: ${name}. This should be prevented by CSS.`);
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
        { [styles.alive]: isAlive && !isFrozen },
        { [styles["not-alive"]]: !isAlive },
        { [styles.frozen]: isFrozen },
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
        {character.attack && <span className="font-bold">{signStr(character.attack)}</span>}
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
