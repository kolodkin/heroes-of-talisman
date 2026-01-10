/**
 * Opponent Selection Stage
 *
 * Displays all players (except current player) with their characters.
 * Players start minimized, can be expanded to see character details.
 *
 * Flow:
 * - Click on opponent's character: invokes 'opponent_press' action, setting stage_meta
 *   with opponent and character in backend, triggering game_update to highlight selection
 * - Click Select button: invokes 'opponent_select' action, confirming selection and
 *   transitioning stage to 'battle'
 */
import React from "react";
import className from "classnames";
import { useTranslation } from "react-i18next";
import { notify } from "../../utils/notify";
import { useScrollAlignment } from "../../hooks/useScrollAlignment";
import { SharedAreaContent } from "./SharedAreaContent";

import styles from "./StageOpponentSelection.module.css";
import Opponent from "./Opponent";

const StageOpponentSelection = ({
  players,
  activePlayer,
  sendAction,
  active,
  selectedOpponent = null,
  statusIndicator,
  statusPlayerName,
}) => {
  const { t } = useTranslation();
  const { containerRef, hasScroll } = useScrollAlignment();

  const handleCharacterClick = (playerName, characterName) => {
    if (!active) {
      return;
    }

    sendAction("opponent_press", { opponent: playerName, character: characterName });
  };

  const handleSubmit = () => {
    if (!active) {
      return;
    }

    if (selectedOpponent) {
      sendAction("opponent_select");
    } else {
      notify("opponent_selection.select_opponent");
    }
  };

  // Filter out active player (whose turn it is)
  const opponents = Object.entries(players).filter(([name]) => name !== activePlayer);

  const content = (
    <div className={className("flex max-w-full", hasScroll ? "self-start" : "self-center")}>
      <div ref={containerRef} className={styles["opponents-container"]}>
        {opponents.map(([playerName, player]) => (
          <Opponent
            key={playerName}
            playerName={playerName}
            player={player}
            selectedOpponent={selectedOpponent}
            onCharacterClick={handleCharacterClick}
          />
        ))}
      </div>
    </div>
  );

  return (
    <SharedAreaContent
      content={content}
      onActionClick={handleSubmit}
      actionButtonContent={t("character_select.submit")}
      actionButtonDisabled={!active}
      statusIndicator={statusIndicator}
      statusPlayerName={statusPlayerName}
    />
  );
};

export default StageOpponentSelection;
