/**
 * OpponentMinified Component
 *
 * Displays opponent's characters in a horizontal minimized view.
 * Used in the opponent selection stage when the opponent card is collapsed.
 */
import className from "classnames";
import { useTranslation } from "react-i18next";
import styles from "./OpponentMinified.module.css";

const OpponentMinified = ({ player, selectedOpponent, onCharacterClick }) => {
  const { t } = useTranslation();

  return (
    <div className={styles["opponent-minimized"]}>
      {player.characters &&
        Object.entries(player.characters).map(([charName, character]) => (
          <div
            key={charName}
            className={className(
              styles["character-minimized"],
              selectedOpponent?.character === charName && styles["character-selected"],
            )}
            onClick={() => onCharacterClick(charName)}
          >
            <span className={styles["character-name"]}>{t(`characterNames.${charName}`)}</span>
            <span className={styles["character-level"]}>
              {t("character_card.level")} {character.level}
            </span>
          </div>
        ))}
    </div>
  );
};

export default OpponentMinified;
