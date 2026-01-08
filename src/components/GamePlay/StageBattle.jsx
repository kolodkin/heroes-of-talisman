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
import React, { useState, useCallback } from "react";
import { useTranslation } from "react-i18next";
import className from "classnames";
import CharacterCard from "../CharacterCard";
import Dice from "../Dice";
import { RerollIcon } from "../Icons";
import { SharedAreaContent } from "./SharedAreaContent";
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
              <img src="/images/dragon_w.png" alt={t("battle.winner")} className={styles.winnerIcon} />
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

  // React Hooks must be called before any early returns
  const handleDiceStop = useCallback(() => {
    setDiceStoppedCount((prev) => prev + 1);
  }, []);

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
  const activeIsWinner = gamePlay.active?.result?.winner ?? false;
  const opponentIsWinner = opponent?.result?.winner ?? false;

  const bothRolled = activeDiceRoll && opponentDiceRoll;

  // Calculate total expected dice count
  const totalExpectedDice = bothRolled ? (activeDiceRoll?.length || 0) + (opponentDiceRoll?.length || 0) : 0;

  // Show winner when all dice have stopped AND winner is set in backend
  const showWinner = diceStoppedCount >= totalExpectedDice && (activeIsWinner || opponentIsWinner);

  // Detect draw: both rolled, all dice stopped, but neither is winner
  const isDraw = diceStoppedCount >= totalExpectedDice && bothRolled && !activeIsWinner && !opponentIsWinner;

  // Detect if active player lost and has reroll effect available
  const activeLost = diceStoppedCount >= totalExpectedDice && bothRolled && opponentIsWinner && !activeIsWinner;
  const hasRerollEffect = activeCharacter?.effect?.reroll_dice_available ?? false;
  const canUseRerollEffect = activeLost && hasRerollEffect;

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

  const handleReroll = () => {
    if (active) {
      sendAction("action_reroll", {});
      // Reset dice stopped count for next rolls
      setDiceStoppedCount(0);
    }
  };

  const handleRerollEffect = () => {
    if (active) {
      sendAction("action_reroll_effect", {});
      // Reset dice stopped count for next rolls
      setDiceStoppedCount(0);
    }
  };

  // Get scores from backend (only when winner is set)
  const activeScore = showWinner ? (gamePlay.active?.result?.score ?? null) : null;
  const opponentScore = showWinner ? (opponent?.result?.score ?? null) : null;

  // Determine action button
  let actionButtonContent = null;
  let actionButtonOnClick = null;

  if (canUseRerollEffect) {
    actionButtonOnClick = handleRerollEffect;
    actionButtonContent = (
      <span style={{ display: "flex", alignItems: "center", gap: "8px", justifyContent: "center" }}>
        {t("battle.reroll")} <RerollIcon size={20} color="white" fill="purple" />
      </span>
    );
  } else if (showWinner) {
    actionButtonContent = t("battle.continue");
    actionButtonOnClick = handleContinue;
  } else if (isDraw) {
    actionButtonContent = t("battle.reroll");
    actionButtonOnClick = handleReroll;
  }

  const content = (
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
    </div>
  );

  return (
    <SharedAreaContent
      content={content}
      onActionClick={actionButtonOnClick}
      actionButtonContent={actionButtonContent}
      actionButtonDisabled={!active}
    />
  );
};

export default StageBattle;
