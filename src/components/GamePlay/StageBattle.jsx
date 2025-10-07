/**
 * Battle Stage
 *
 * Displays the current player and opponent facing each other in battle.
 * Shows character cards and dice/roll buttons for both players.
 *
 * Layout:
 * - First section: Current player (gamePlay.active.player) with their selected character and dice/roll button
 * - Second section: Opponent player with their character and dice/roll button
 */
import React from "react";
import { useTranslation } from "react-i18next";
import className from "classnames";
import CharacterCard from "../CharacterCard";
import Dice from "../Dice";
import commonStyles from "../Common.module.css";
import styles from "./StageBattle.module.css";

const BattleParticipant = ({ playerName, characterName, character, diceValue, onRoll, canRoll, role }) => {
  const { t } = useTranslation();

  return (
    <div className={styles.battleRow} data-battle-participant={playerName} data-battle-role={role}>
      <h2 className={styles.playerName}>{playerName}</h2>
      <CharacterCard name={characterName} character={character} isSelected={false} size="small" />
      {diceValue !== undefined && diceValue !== null ? (
        <Dice value={diceValue} />
      ) : (
        <button
          className={className(commonStyles.gamebtn, commonStyles.submitButton, styles.rollButton)}
          onClick={onRoll}
          disabled={!canRoll}
          style={{ pointerEvents: canRoll ? "auto" : "none" }}
          data-roll-button
        >
          {t("battle.roll")}
        </button>
      )}
    </div>
  );
};

const StageBattle = ({ gamePlay, sendAction, active, currentUser }) => {
  const { t } = useTranslation();

  // Current player data
  const currentPlayerName = gamePlay.active?.player;
  const currentPlayer = currentPlayerName ? gamePlay.players[currentPlayerName] : null;
  const selectedCharacterName = gamePlay.active?.character;
  const selectedCharacter = currentPlayer?.characters[selectedCharacterName];

  // Opponent data
  const opponent = gamePlay.opponent;
  const opponentPlayer = opponent ? gamePlay.players[opponent.player] : null;
  const opponentCharacter = opponentPlayer?.characters[opponent.character];

  if (!currentPlayer || !selectedCharacter || !opponent || !opponentCharacter) {
    return <div className={styles.loading}>{t("loading")}</div>;
  }

  const handleActivePlayerRoll = () => {
    if (active) {
      sendAction("active_player_roll", {});
    }
  };

  const handleOpponentRoll = () => {
    // Opponent can roll even if not active player
    if (currentUser === opponent.player) {
      sendAction("opponent_roll", {});
    }
  };

  return (
    <div className={styles.battleContainer}>
      <BattleParticipant
        playerName={currentPlayerName}
        characterName={selectedCharacterName}
        character={selectedCharacter}
        diceValue={gamePlay.active?.dice_roll}
        onRoll={handleActivePlayerRoll}
        canRoll={active}
        role="active"
      />
      <BattleParticipant
        playerName={opponent.player}
        characterName={opponent.character}
        character={opponentCharacter}
        diceValue={opponent.dice_roll}
        onRoll={handleOpponentRoll}
        canRoll={currentUser === opponent.player}
        role="opponent"
      />
    </div>
  );
};

export default StageBattle;
