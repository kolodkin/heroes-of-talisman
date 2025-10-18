/**
 * Opponent Component
 *
 * Displays a single opponent in the opponent selection stage.
 * Can be expanded to show full character cards or minimized to show compact character list.
 */
import React, { useState } from "react";
import className from "classnames";
import { useTranslation } from "react-i18next";
import { useScrollAlignment } from "../../hooks/useScrollAlignment";
import CharacterCard from "../CharacterCard";
import styles from "./Opponent.module.css";
import commonStyles from "../Common.module.css";
import Player from "../Player";

const OpponentMinified = ({ player, selectedOpponent, onCharacterClick }) => {
  const { t } = useTranslation();
  const { containerRef } = useScrollAlignment();

  return (
    <div ref={containerRef} className={commonStyles.cardsContainer} data-opponent-cards-minimized>
      {player.characters &&
        Object.entries(player.characters).map(([charName, character]) => {
          const isAlive = character.is_alive !== false;
          const handleClick = () => {
            if (!isAlive) {
              console.error(`Attempted to click not-alive character: ${charName}. This should be prevented by CSS.`);
              return;
            }
            onCharacterClick(charName);
          };

          return (
            <div
              key={charName}
              className={className(
                styles["character-minimized"],
                selectedOpponent?.character === charName && styles["character-selected"],
                isAlive && styles["character-alive"],
                !isAlive && styles["character-not-alive"],
              )}
              onClick={handleClick}
              data-character={charName}
            >
              <span className={styles["character-name"]}>{t(`characterNames.${charName}`)}</span>
              <span className={styles["character-level"]}>
                {t("character_card.level")} {character.level}
              </span>
            </div>
          );
        })}
    </div>
  );
};

const Opponent = ({ playerName, player, selectedOpponent, onCharacterClick }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const { containerRef: expandedContainerRef } = useScrollAlignment();

  const toggleExpanded = () => {
    setIsExpanded((prev) => !prev);
  };

  const handleCharacterClick = (charName) => {
    onCharacterClick(playerName, charName);
  };

  return (
    <Player player={player} className={styles.opponent}>
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
        <div ref={expandedContainerRef} className={commonStyles.cardsContainer} data-opponent-cards-expanded>
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
    </Player>
  );
};

export default Opponent;
