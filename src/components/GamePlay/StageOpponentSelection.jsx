/**
 * Opponent Selection Stage
 *
 * Displays all players (except current player) with their characters.
 * Players start minimized, can be expanded to see character details.
 *
 * Flow:
 * - Click on opponent's character to select
 * - Invokes 'opponent_select' action with opponent player name and character
 * - Backend transitions stage to 'battle'
 */
import React, { useState } from "react";
import className from "classnames";
import { useTranslation } from "react-i18next";
import { notify } from "../../utils/notify";

import styles from "./StageOpponentSelection.module.css";
import commonStyles from "../Common.module.css";
import CharacterCard from "../CharacterCard";

const StageOpponentSelection = ({ players, currentPlayer, sendAction, active }) => {
  const { t } = useTranslation();
  const [expandedPlayers, setExpandedPlayers] = useState({});
  const [selectedOpponent, setSelectedOpponent] = useState(null);
  const [selectedCharacter, setSelectedCharacter] = useState(null);

  const togglePlayer = (playerName) => {
    setExpandedPlayers((prev) => ({
      ...prev,
      [playerName]: !prev[playerName],
    }));
  };

  const handleCharacterClick = (playerName, characterName) => {
    if (!active) {
      return;
    }

    setSelectedOpponent(playerName);
    setSelectedCharacter(characterName);
  };

  const handleSubmit = () => {
    if (!active) {
      return;
    }

    if (selectedOpponent && selectedCharacter) {
      sendAction("opponent_select", {
        opponent: selectedOpponent,
        character: selectedCharacter,
      });
    } else {
      notify("opponent_selection.select_opponent");
    }
  };

  // Filter out current player
  const opponents = Object.entries(players).filter(([name, _]) => name !== currentPlayer);

  return (
    <div className="flex flex-col items-center space-y-3">
      <div className={styles["opponents-container"]}>
        {opponents.map(([playerName, player]) => {
          const isExpanded = expandedPlayers[playerName];

          return (
            <div key={playerName} className={styles.opponent} data-player={playerName}>
              <div className={styles["opponent-header"]}>
                <div className={styles["opponent-name"]}>{playerName}</div>
                <button
                  className={styles["toggle-button"]}
                  onClick={() => togglePlayer(playerName)}
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
                        isSelected={selectedOpponent === playerName && selectedCharacter === charName}
                        onClick={() => handleCharacterClick(playerName, charName)}
                      />
                    ))}
                </div>
              ) : (
                <div className={styles["opponent-minimized"]}>
                  {player.characters &&
                    Object.entries(player.characters).map(([charName, character]) => (
                      <div
                        key={charName}
                        className={className(
                          styles["character-minimized"],
                          selectedOpponent === playerName &&
                            selectedCharacter === charName &&
                            styles["character-selected"],
                        )}
                        onClick={() => handleCharacterClick(playerName, charName)}
                      >
                        <span className={styles["character-name"]}>{t(`characterNames.${charName}`)}</span>
                        <span className={styles["character-level"]}>
                          {t("character_card.level")} {character.level}
                        </span>
                      </div>
                    ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <button className={className(commonStyles.gamebtn, styles.submit, "text-2xl", "rounded")} onClick={handleSubmit}>
        <p>{t("character_select.submit")}</p>
      </button>
    </div>
  );
};

export default StageOpponentSelection;
