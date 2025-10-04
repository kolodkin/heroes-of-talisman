/**
 * Opponent Component
 *
 * Displays a single opponent in the opponent selection stage.
 * Can be expanded to show full character cards or minimized to show compact character list.
 */
import React, { useState } from "react";
import className from "classnames";
import { useTranslation } from "react-i18next";
import CharacterCard from "../CharacterCard";
import styles from "./Opponent.module.css";

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

const Opponent = ({ playerName, player, selectedOpponent, onCharacterClick }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = () => {
    setIsExpanded((prev) => !prev);
  };

  const handleCharacterClick = (charName) => {
    onCharacterClick(playerName, charName);
  };

  return (
    <div className={styles.opponent} data-player={playerName}>
      <div className={styles["opponent-header"]}>
        <div className={styles["opponent-name"]}>{playerName}</div>
        <button
          className={styles["toggle-button"]}
          onClick={toggleExpanded}
          aria-label={isExpanded ? "Minimize player" : "Expand player"}
        >
          {isExpanded ? "−" : "+"}
        </button>
      </div>

      {isExpanded ? (
        <div className={styles["opponent-characters"]}>
          {player.characters &&
            Object.entries(player.characters).map(([charName, character]) => (
              <CharacterCard
                key={charName}
                name={charName}
                character={character}
                isSelected={selectedOpponent?.player === playerName && selectedOpponent?.character === charName}
                onClick={() => handleCharacterClick(charName)}
                size="normal"
              />
            ))}
        </div>
      ) : (
        <OpponentMinified
          player={player}
          selectedOpponent={selectedOpponent?.player === playerName ? selectedOpponent : null}
          onCharacterClick={handleCharacterClick}
        />
      )}
    </div>
  );
};

export default Opponent;
