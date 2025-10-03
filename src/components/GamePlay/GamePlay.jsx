import React from "react";
import styles from "./GamePlay.module.css";
import Card from "./Card";
import CharacterCard from "../CharacterCard";
import StageCharacterSelect from "./StageCharacterSelect";

const GamePlay = ({ username, gamePlay, sendAction }) => {
  if (!gamePlay || !gamePlay.players) {
    return null;
  }

  // Convert players object to array
  const playersArray = Object.values(gamePlay.players);

  if (playersArray.length === 0) {
    return null;
  }

  return (
    <div className={styles["game-play"]}>
      <div className={styles["players-container"]}>
        {playersArray.map((player, index) => (
          <div key={player.name} className={styles.player} data-player={player.name}>
            <div className={styles["player-content"]}>
              <div className={styles["player-name"]}>{player.name}</div>
              <div className={styles["player-characters"]}>
                {player.characters &&
                  Object.entries(player.characters).map(([charName, character]) => (
                    <Card key={charName} faceUp={true}>
                      <CharacterCard name={charName} character={character} />
                    </Card>
                  ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className={styles["shared-area"]}>
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
