import className from "classnames";
import { useTranslation } from "react-i18next";
import styles from "./CharacterCard.module.css";
import cardStyles from "./Card.module.css";
import { DiceIcon, HeartIcon, RerollIcon, SkipTurnIcon, NotAliveIcon, ArmorIcon, SwordIcon, TalismanIcon } from "./Icons";

const signStr = (num) => (num ? (num >= 0 ? `+${num}` : `${num}`) : "");

const CharacterCard = ({ name, character, isSelected, onClick, size = "small" }) => {
  const { t } = useTranslation();
  const nameStr = t(`characterNames.${name}`);

  const cardClass = size === "normal" ? styles["card-normal"] : styles["card-small"];
  const isAlive = character.is_alive !== false; // Default to true if not specified

  // Check if character has skip_turn effect
  const hasSkipTurn = character.effects?.some((effect) => effect.name === "skip_turn") || false;

  // Character is selectable only if alive AND doesn't have skip_turn
  const isSelectable = isAlive && !hasSkipTurn;

  // Calculate total attack with effects
  const baseAttack = character.attack || 0;
  const attackBonus = character.effect?.attack_bonus || 0;
  const attackNegBonus = character.effect?.attack_neg_bonus || 0;
  const totalAttack = baseAttack + attackBonus + attackNegBonus;
  const netEffect = attackBonus + attackNegBonus; // Positive = bonus, negative = penalty
  const hasReroll = character.effect?.reroll_dice_available || false;
  const hasArmor = character.cards?.includes("metal_armor") || false;
  const hasSword = character.cards?.includes("sacred_sord") || false;
  const hasTalisman = character.cards?.includes("talisman") || false;

  // Get all effect names for data attribute
  const effectNames = character.effects?.map((effect) => effect.name).join(",") || "";

  const handleClick = () => {
    if (!isSelectable) {
      console.error(`Attempted to click non-selectable character: ${name}. This should be prevented by CSS.`);
      return;
    }
    if (onClick) {
      onClick();
    }
  };

  return (
    <div
      className={className(
        { [cardStyles.selected]: isSelected },
        { [styles.alive]: isSelectable },
        { [styles["not-alive"]]: !isSelectable },
        cardStyles.card,
        styles.card,
        cardClass,
      )}
      onClick={handleClick}
      data-character={name}
      data-level={character.level}
      data-effects={effectNames}
      data-is-alive={isAlive ? "true" : "false"}
    >
      <img className={styles["card-img"]} src={`/images/${name}.png`} alt={name} />
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
        {hasReroll && <RerollIcon color="white" fill="purple" />}
        {hasSkipTurn && <SkipTurnIcon color="white" fill="orange" />}
        {hasArmor && <ArmorIcon />}
        {hasSword && <SwordIcon />}
        {hasTalisman && <TalismanIcon />}
      </div>
      <div className={className("flex items-center gap-1", styles.stats)}>
        <HeartIcon color="red" />
        <span className="font-bold">
          [{character.health}/{character.max_health}]
        </span>
      </div>
      {!isAlive ? (
        <div className={styles.overlay}>
          <NotAliveIcon size={size === "normal" ? 64 : 32} color="white" fill="rgba(0, 0, 0, 0.7)" />
        </div>
      ) : hasSkipTurn ? (
        <div className={styles.overlay}>
          <SkipTurnIcon size={size === "normal" ? 64 : 32} color="white" fill="orange" />
        </div>
      ) : null}
    </div>
  );
};

export default CharacterCard;
