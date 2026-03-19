/**
 * Battle Stage
 *
 * Displays the active player and opponent facing each other in battle.
 * Shows character cards and dice for both players.
 * Rolling is done via the main action button, which is enabled for both
 * the active player and the opponent when they need to roll.
 *
 * Layout:
 * - First section: Active player (gamePlay.active.player) with their active character and dice
 * - Second section: Opponent player with their character and dice
 */
import React, { useState, useCallback } from "react";
import { useTranslation } from "react-i18next";
import className from "classnames";
import CharacterCard from "./CharacterCard";
import Dice from "./Dice";
import { RerollIcon } from "./Icons";
import { SharedAreaContent } from "./SharedAreaContent";
import Fade from "./Fade";
import styles from "./StageBattle.module.css";

const BattleParticipant = ({
  playerName,
  characterName,
  character,
  diceValues,
  role,
  score,
  onDiceStop,
  winner,
  showScore,
}) => {
  const { t } = useTranslation();

  return (
    <div
      className={className(styles.battleRow, { [styles.winner]: winner })}
      data-battle-participant={playerName}
      data-battle-role={role}
    >
      <h2 className={styles.playerName}>{playerName}</h2>
      <CharacterCard name={characterName} character={character} isSelected={false} size="small" />
      {diceValues && diceValues.length > 0 && (
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
      )}
    </div>
  );
};

const getActionButton = ({
  currentUser,
  opponentPlayer,
  activeDiceRoll,
  opponentDiceRoll,
  opponentCharacter,
  activeCharacter,
  handleOpponentRoll,
  handleActivePlayerRoll,
  canUseRerollEffect,
  handleRerollEffect,
  showWinner,
  handleContinue,
  isDraw,
  handleReroll,
  active,
  t,
}) => {
  const currentUserIsOpponent = currentUser === opponentPlayer;
  const activeNeedsRoll = !activeDiceRoll;
  const opponentNeedsRoll = !opponentDiceRoll;
  const currentUserNeedsToRoll = (active && activeNeedsRoll) || (currentUserIsOpponent && opponentNeedsRoll);

  if (currentUserNeedsToRoll) {
    const isOpponentRoll = currentUserIsOpponent && opponentNeedsRoll;
    const userCharacter = isOpponentRoll ? opponentCharacter : activeCharacter;
    const numDice = userCharacter?.dice || 1;
    const rollKey = numDice === 1 ? "battle.roll_the_dice" : "battle.roll_the_dice_mult";
    return {
      content: t(rollKey),
      onClick: isOpponentRoll ? handleOpponentRoll : handleActivePlayerRoll,
      dataAttrs: { "data-roll-button": "" },
      disabled: false,
      style: isOpponentRoll ? { pointerEvents: "auto" } : undefined,
    };
  }
  if (canUseRerollEffect) {
    return {
      content: (
        <span style={{ display: "flex", alignItems: "center", gap: "8px", justifyContent: "center" }}>
          {t("battle.reroll")} <RerollIcon size={20} color="white" fill="purple" />
        </span>
      ),
      onClick: handleRerollEffect,
      dataAttrs: { "data-reroll-effect-button": "" },
      disabled: !active,
    };
  }
  if (showWinner) {
    return {
      content: t("battle.continue"),
      onClick: handleContinue,
      dataAttrs: { "data-continue-button": "" },
      disabled: !active,
    };
  }
  if (isDraw) {
    return {
      content: t("battle.reroll"),
      onClick: handleReroll,
      dataAttrs: { "data-reroll-button": "" },
      disabled: !active,
    };
  }
  return null;
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

  // Show results (scores) when there's a winner OR it's a draw
  const showResults = showWinner || isDraw;

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

  // Get scores from backend (when winner is set or it's a draw)
  const activeScore = showResults ? (gamePlay.active?.result?.score ?? null) : null;
  const opponentScore = showResults ? (opponent?.result?.score ?? null) : null;

  const actionButton = getActionButton({
    currentUser,
    opponentPlayer: opponent.player,
    activeDiceRoll,
    opponentDiceRoll,
    opponentCharacter,
    activeCharacter,
    handleOpponentRoll,
    handleActivePlayerRoll,
    canUseRerollEffect,
    handleRerollEffect,
    showWinner,
    handleContinue,
    isDraw,
    handleReroll,
    active,
    t,
  });

  const content = (
    <Fade className={styles.battleContainer}>
      <BattleParticipant
        playerName={activePlayerName}
        characterName={activeCharacterName}
        character={activeCharacter}
        diceValues={gamePlay.active?.dice_roll}
        role="active"
        score={activeScore}
        onDiceStop={handleDiceStop}
        winner={showWinner && activeIsWinner}
        showScore={showResults}
      />
      <BattleParticipant
        playerName={opponent.player}
        characterName={opponent.character}
        character={opponentCharacter}
        diceValues={opponent.dice_roll}
        role="opponent"
        score={opponentScore}
        onDiceStop={handleDiceStop}
        winner={showWinner && opponentIsWinner}
        showScore={showResults}
      />
    </Fade>
  );

  return (
    <SharedAreaContent
      content={content}
      onActionClick={actionButton?.onClick}
      actionButtonContent={actionButton?.content}
      actionButtonDisabled={actionButton?.disabled}
      actionButtonDataAttrs={actionButton?.dataAttrs}
      actionButtonStyle={actionButton?.style}
    />
  );
};

export default StageBattle;
