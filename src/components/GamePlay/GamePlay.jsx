import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import className from "classnames";
import styles from "./GamePlay.module.css";
import commonStyles from "../Common.module.css";
import Card from "./Card";
import CharacterCard from "../CharacterCard";
import StageCharacterSelect from "./StageCharacterSelect";
import StageAbilitySelection from "./StageAbilitySelection";
import StageAbilityOpponentSelection from "./StageAbilityOpponentSelection";
import StageOpponentSelection from "./StageOpponentSelection";
import StageBattle from "./StageBattle";
import Player from "../Player";
import {
  CHARACTER_SELECT,
  ABILITY_SELECTION,
  ABILITY_OPPONENT_SELECTION,
  OPPONENT_SELECTION,
  BATTLE_DICE_ROLL,
  BATTLE_END,
} from "../../constants/stages";

const PlayersCards = ({ player }) => {
  return (
    <div className={commonStyles.cardsContainer} data-player-cards>
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
          <div key={charName} className={styles["character-minimized"]} data-character={charName}>
            <span className={styles["character-name"]}>{t(`characterNames.${charName}`)}</span>
            <span className={styles["character-level"]} data-level={character.level}>
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

  // Check total player count (regardless of connection status)
  const hasMinimumPlayers = playersArray.length >= 2;

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
            <Player key={player.name} player={player} className={styles.player} showDisconnected={true}>
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
            </Player>
          );
        })}
      </div>

      <div
        className={className(styles["shared-area"], {
          [styles["shared-area-disabled"]]: gamePlay.active?.player !== username,
          [styles["shared-area-battle"]]: gamePlay.stage === BATTLE_DICE_ROLL || gamePlay.stage === BATTLE_END,
        })}
        data-shared-area-active={gamePlay.active?.player === username}
      >
        {!hasMinimumPlayers && (
          <div className={commonStyles["gray-overlay"]} data-minimum-player-overlay>
            <div className={`${commonStyles["gray-overlay-text"]} ${styles["minimum-player-text"]}`}>
              {t("shared_area.player_minimum")}
            </div>
          </div>
        )}
        <h2 className={styles["stage-title"]}>{t(`stageInstructions.${gamePlay.stage}`)}</h2>
        {(() => {
          const activePlayer = gamePlay.players[gamePlay.active?.player];
          const isActivePlayer = gamePlay.active?.player === username;

          switch (gamePlay.stage) {
            case CHARACTER_SELECT:
              return (
                <StageCharacterSelect
                  characters={activePlayer?.characters || {}}
                  sendAction={sendAction}
                  active={isActivePlayer}
                  selectedCharacter={gamePlay.stage_meta?.selected}
                />
              );
            case ABILITY_SELECTION:
              const selectedCharacter = activePlayer?.characters?.[gamePlay.active?.character];
              return (
                <StageAbilitySelection
                  abilities={selectedCharacter?.abilities || []}
                  sendAction={sendAction}
                  active={isActivePlayer}
                  selectedAbility={gamePlay.stage_meta?.selected}
                />
              );
            case ABILITY_OPPONENT_SELECTION:
              return (
                <StageAbilityOpponentSelection
                  players={gamePlay.players}
                  activePlayer={gamePlay.active?.player}
                  sendAction={sendAction}
                  active={isActivePlayer}
                  selectedOpponent={gamePlay.stage_meta}
                />
              );
            case OPPONENT_SELECTION:
              return (
                <StageOpponentSelection
                  players={gamePlay.players}
                  activePlayer={gamePlay.active?.player}
                  sendAction={sendAction}
                  active={isActivePlayer}
                  selectedOpponent={gamePlay.stage_meta}
                />
              );
            case BATTLE_DICE_ROLL:
            case BATTLE_END:
              return (
                <StageBattle
                  gamePlay={gamePlay}
                  sendAction={sendAction}
                  active={isActivePlayer}
                  currentUser={username}
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
