import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import styles from "./GamePlay.module.css";
import Card from "./Card";
import CharacterCard from "../CharacterCard";
import StageCharacterSelect from "./StageCharacterSelect";

const PlayersCards = ({ player }) => {
  return (
    <div className={styles["player-characters"]}>
      {player.characters &&
        Object.entries(player.characters).map(([charName, character]) => (
          <Card key={charName} faceUp={true}>
            <CharacterCard name={charName} character={character} />
          </Card>
        ))}
    </div>
  );
};

const PlayersMinified = ({ player }) => {
  const { t } = useTranslation();
  return (
    <div className={styles["player-minimized"]}>
      {player.characters &&
        Object.entries(player.characters).map(([charName, character]) => (
          <div key={charName} className={styles["character-minimized"]}>
            <span className={styles["character-name"]}>{t(`characterNames.${charName}`)}</span>
            <span className={styles["character-level"]}>
              {t("character_card.level")} {character.level}
            </span>
          </div>
        ))}
    </div>
  );
};

const GamePlay = ({ username, gamePlay, sendAction }) => {
  const { t } = useTranslation();
  const [minimizedPlayers, setMinimizedPlayers] = useState({});

  if (!gamePlay || !gamePlay.players) {
    return null;
  }

  // Convert players object to array
  const playersArray = Object.values(gamePlay.players);

  if (playersArray.length === 0) {
    return null;
  }

  const togglePlayerMinimized = (playerName) => {
    setMinimizedPlayers((prev) => ({
      ...prev,
      [playerName]: !prev[playerName],
    }));
  };

  return (
    <div className={styles["game-play"]}>
      <div className={styles["players-container"]}>
        {playersArray.map((player, index) => {
          const isMinimized = minimizedPlayers[player.name];

          const playerDom = isMinimized ? <PlayersMinified player={player} /> : <PlayersCards player={player} />;

          return (
            <div key={player.name} className={styles.player} data-player={player.name}>
              <div className={styles["player-header"]}>
                <div className={styles["player-name"]}>{player.name}</div>
                <button
                  className={styles["toggle-button"]}
                  onClick={() => togglePlayerMinimized(player.name)}
                  aria-label={isMinimized ? "Expand player" : "Minimize player"}
                >
                  {isMinimized ? "+" : "−"}
                </button>
              </div>
              {playerDom}
            </div>
          );
        })}
      </div>

      <div className={styles["shared-area"]}>
        <h2 className={styles["stage-title"]}>{t(`stageInstructions.${gamePlay.stage}`)}</h2>
        {(() => {
          const currentPlayer = gamePlay.players[username];
          const isActivePlayer = gamePlay.playing === username;

          switch (gamePlay.stage) {
            case "character_select":
              return (
                <StageCharacterSelect
                  characters={currentPlayer?.characters || {}}
                  sendAction={sendAction}
                  active={isActivePlayer}
                  selectedCharacter={gamePlay.stage_meta?.selected}
                />
              );
            default:
              return <div>Stage: {gamePlay.stage}</div>;
          }
        })()}
      </div>
    </div>
  );
};

export default GamePlay;
