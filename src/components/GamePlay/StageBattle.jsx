/**
 * Battle Stage
 *
 * Displays the current player and opponent facing each other in battle.
 * Shows character cards and dice for both players.
 *
 * Layout:
 * - First section: Current player (gamePlay.active.player) with their selected character and dice
 * - Second section: Opponent player with their character and dice (showing roll animation)
 */
import React from "react";
import { useTranslation } from "react-i18next";
import CharacterCard from "../CharacterCard";
import Dice from "../Dice";
import styles from "./StageBattle.module.css";

const BattleParticipant = ({ playerName, characterName, character, diceValue, diceRollDuration }) => {
  return (
    <div className={styles.battleRow} data-battle-participant={playerName}>
      <h2 className={styles.playerName}>{playerName}</h2>
      <CharacterCard name={characterName} character={character} isSelected={false} size="small" />
      <Dice value={diceValue} rollDuration={diceRollDuration} />
    </div>
  );
};

const StageBattle = ({ gamePlay, rollDuration = 2000 }) => {
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

  return (
    <div className={styles.battleContainer}>
      <BattleParticipant
        playerName={currentPlayerName}
        characterName={selectedCharacterName}
        character={selectedCharacter}
        diceValue={3}
        diceRollDuration={rollDuration}
      />
      <BattleParticipant
        playerName={opponent.player}
        characterName={opponent.character}
        character={opponentCharacter}
        diceValue={opponent.dice_roll}
        diceRollDuration={rollDuration}
      />
    </div>
  );
};

export default StageBattle;
