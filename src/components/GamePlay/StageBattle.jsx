/**
 * Battle Stage
 *
 * Displays the active player and opponent facing each other in battle.
 * Shows character cards and dice/roll buttons for both players.
 *
 * Layout:
 * - First section: Active player (gamePlay.active.player) with their active character and dice/roll button
 * - Second section: Opponent player with their character and dice/roll button
 */
import React, { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";
import className from "classnames";
import CharacterCard from "../CharacterCard";
import Dice from "../Dice";
import commonStyles from "../Common.module.css";
import styles from "./StageBattle.module.css";

const BattleParticipant = ({
  playerName,
  characterName,
  character,
  diceValues,
  onRoll,
  canRoll,
  role,
  score,
  onDiceStop,
  winner,
  showScore,
}) => {
  const { t } = useTranslation();

  // Determine the number of dice based on character's dice value
  const numDice = character?.dice || 1;
  const rollKey = numDice === 1 ? "battle.roll_the_dice" : "battle.roll_the_dice_mult";

  return (
    <div
      className={className(styles.battleRow, { [styles.winner]: winner })}
      data-battle-participant={playerName}
      data-battle-role={role}
    >
      <h2 className={styles.playerName}>{playerName}</h2>
      <CharacterCard name={characterName} character={character} isSelected={false} size="small" />
      {diceValues && diceValues.length > 0 ? (
        <>
          <div className={styles.diceGroup}>
            {diceValues.map((value, index) => (
              <Dice key={index} value={value} onStop={onDiceStop} />
            ))}
          </div>
          {showScore && score !== null && score !== undefined && (
            <div className={styles.scoreDisplay}>
              <span className={styles.scoreLabel}>{t("battle.total")}:</span>
              <span className={styles.scoreValue} data-score>
                {score}
              </span>
            </div>
          )}
          {winner && (
            <div className={styles.winnerBadge} data-winner-badge>
              {t("battle.winner")}
            </div>
          )}
        </>
      ) : (
        <button
          className={className(commonStyles.gamebtn, commonStyles.submitButton, styles.rollButton)}
          onClick={onRoll}
          disabled={!canRoll}
          style={{ pointerEvents: canRoll ? "auto" : "none" }}
          data-roll-button
        >
          {t(rollKey)}
        </button>
      )}
    </div>
  );
};

const StageBattle = ({ gamePlay, sendAction, active, currentUser }) => {
  const { t } = useTranslation();
  const [diceStoppedCount, setDiceStoppedCount] = useState(0);

  // Active player data
  const activePlayerName = gamePlay.active?.player;
  const activePlayer = activePlayerName ? gamePlay.players[activePlayerName] : null;
  const activeCharacterName = gamePlay.active?.character;
  const activeCharacter = activePlayer?.characters[activeCharacterName];

  // Opponent data
  const opponent = gamePlay.opponent;
  const opponentPlayer = opponent ? gamePlay.players[opponent.player] : null;
  const opponentCharacter = opponentPlayer?.characters[opponent.character];

  if (!activePlayer || !activeCharacter || !opponent || !opponentCharacter) {
    return <div className={styles.loading}>{t("loading")}</div>;
  }

  // Get dice rolls and winner status from game state
  const activeDiceRoll = gamePlay.active?.dice_roll;
  const opponentDiceRoll = opponent.dice_roll;
  const activeIsWinner = gamePlay.active?.winner ?? false;
  const opponentIsWinner = opponent?.winner ?? false;

  const bothRolled = activeDiceRoll && opponentDiceRoll;

  // Calculate total expected dice count
  const totalExpectedDice = bothRolled ? (activeDiceRoll?.length || 0) + (opponentDiceRoll?.length || 0) : 0;

  // Show winner when all dice have stopped AND winner is set in backend
  const showWinner = diceStoppedCount >= totalExpectedDice && (activeIsWinner || opponentIsWinner);

  const handleDiceStop = useCallback(() => {
    setDiceStoppedCount((prev) => prev + 1);
  }, []);

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

  const handleContinue = () => {
    if (active) {
      sendAction("battle_end", {});
    }
  };

  // Calculate scores for display (only when winner is set)
  const activeScore =
    showWinner && activeDiceRoll
      ? activeDiceRoll.reduce((sum, val) => sum + val, 0) + (activeCharacter?.attack || 0)
      : null;
  const opponentScore =
    showWinner && opponentDiceRoll
      ? opponentDiceRoll.reduce((sum, val) => sum + val, 0) + (opponentCharacter?.attack || 0)
      : null;

  return (
    <div className={styles.battleContainer}>
      <BattleParticipant
        playerName={activePlayerName}
        characterName={activeCharacterName}
        character={activeCharacter}
        diceValues={gamePlay.active?.dice_roll}
        onRoll={handleActivePlayerRoll}
        canRoll={active}
        role="active"
        score={activeScore}
        onDiceStop={handleDiceStop}
        winner={showWinner && activeIsWinner}
        showScore={showWinner}
      />
      <BattleParticipant
        playerName={opponent.player}
        characterName={opponent.character}
        character={opponentCharacter}
        diceValues={opponent.dice_roll}
        onRoll={handleOpponentRoll}
        canRoll={currentUser === opponent.player}
        role="opponent"
        score={opponentScore}
        onDiceStop={handleDiceStop}
        winner={showWinner && opponentIsWinner}
        showScore={showWinner}
      />
      {showWinner && (
        <button
          className={className(commonStyles.gamebtn, commonStyles.submitButton, styles.continueButton)}
          onClick={handleContinue}
          disabled={!active}
          style={{ pointerEvents: active ? "auto" : "none" }}
        >
          {t("battle.continue")}
        </button>
      )}
    </div>
  );
};

export default StageBattle;
