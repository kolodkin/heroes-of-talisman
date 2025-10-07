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

const BattleParticipant = ({
  playerName,
  characterName,
  character,
  diceValues,
  onRoll,
  canRoll,
  role,
  isWinner,
  score,
  onDiceStop,
  showResults,
}) => {
  const { t } = useTranslation();

  // Determine the number of dice based on character's dice value
  const numDice = character?.dice || 1;
  const rollKey = numDice === 1 ? "battle.roll_the_dice" : "battle.roll_the_dice_mult";

  return (
    <div
      className={className(styles.battleRow, { [styles.winner]: showResults && isWinner })}
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
          {showResults && score !== null && score !== undefined && (
            <div className={styles.scoreDisplay}>
              <span className={styles.scoreLabel}>{t("battle.total")}:</span>
              <span className={styles.scoreValue}>{score}</span>
            </div>
          )}
          {showResults && isWinner && <div className={styles.winnerBadge}>{t("battle.winner")}</div>}
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
  const [diceStoppedCount, setDiceStoppedCount] = React.useState(0);

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

  // Calculate scores and determine winner
  const activeDiceRoll = gamePlay.active?.dice_roll;
  const opponentDiceRoll = opponent.dice_roll;

  const bothRolled = activeDiceRoll && opponentDiceRoll;

  // Calculate total expected dice count
  const totalExpectedDice = bothRolled ? (activeDiceRoll?.length || 0) + (opponentDiceRoll?.length || 0) : 0;

  // Show results only after all dice have stopped
  const showResults = bothRolled && diceStoppedCount >= totalExpectedDice;

  // Reset counter when dice values change
  React.useEffect(() => {
    if (bothRolled) {
      setDiceStoppedCount(0);
    }
  }, [activeDiceRoll, opponentDiceRoll, bothRolled]);

  const handleDiceStop = React.useCallback(() => {
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

  const activeScore = activeDiceRoll
    ? activeDiceRoll.reduce((sum, val) => sum + val, 0) + (selectedCharacter?.attack || 0)
    : null;
  const opponentScore = opponentDiceRoll
    ? opponentDiceRoll.reduce((sum, val) => sum + val, 0) + (opponentCharacter?.attack || 0)
    : null;

  const activeIsWinner = bothRolled && activeScore > opponentScore;
  const opponentIsWinner = bothRolled && opponentScore > activeScore;

  return (
    <div className={styles.battleContainer}>
      <BattleParticipant
        playerName={currentPlayerName}
        characterName={selectedCharacterName}
        character={selectedCharacter}
        diceValues={gamePlay.active?.dice_roll}
        onRoll={handleActivePlayerRoll}
        canRoll={active}
        role="active"
        isWinner={activeIsWinner}
        score={activeScore}
        onDiceStop={handleDiceStop}
        showResults={showResults}
      />
      <BattleParticipant
        playerName={opponent.player}
        characterName={opponent.character}
        character={opponentCharacter}
        diceValues={opponent.dice_roll}
        onRoll={handleOpponentRoll}
        canRoll={currentUser === opponent.player}
        role="opponent"
        isWinner={opponentIsWinner}
        score={opponentScore}
        onDiceStop={handleDiceStop}
        showResults={showResults}
      />
      {showResults && (
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
