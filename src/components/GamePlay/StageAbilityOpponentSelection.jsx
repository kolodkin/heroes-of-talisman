/**
 * Ability Opponent Selection Stage
 *
 * Displays all players (except current player) with their characters for ability targeting.
 * Players start minimized, can be expanded to see character details.
 *
 * Flow:
 * - Click on opponent's character: invokes 'ability_opponent_press' action, setting stage_meta
 *   with opponent and character in backend, triggering game_update to highlight selection
 * - Click Select button: invokes 'ability_opponent_select' action, applying ability effects,
 *   confirming selection and transitioning stage to 'opponent_selection'
 */
import React from "react";
import className from "classnames";
import { useTranslation } from "react-i18next";
import { notify } from "../../utils/notify";
import { useScrollAlignment } from "../../hooks/useScrollAlignment";
import { SharedAreaContent } from "./SharedAreaContent";

import styles from "./StageOpponentSelection.module.css";
import Opponent from "./Opponent";

const StageAbilityOpponentSelection = ({ players, activePlayer, sendAction, active, selectedOpponent = null }) => {
  const { t } = useTranslation();
  const { containerRef, hasScroll } = useScrollAlignment();

  const handleCharacterClick = (playerName, characterName) => {
    if (!active) {
      return;
    }

    sendAction("ability_opponent_press", { opponent: playerName, character: characterName });
  };

  const handleSubmit = () => {
    if (!active) {
      return;
    }

    if (selectedOpponent) {
      sendAction("ability_opponent_select");
    } else {
      notify("ability_opponent_selection.select_opponent");
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
      actionButtonContent={t("ability_opponent_selection.submit")}
      actionButtonDisabled={!active}
    />
  );
};

export default StageAbilityOpponentSelection;
