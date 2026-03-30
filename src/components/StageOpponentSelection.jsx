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
import React, { useMemo, useCallback } from "react";
import className from "classnames";
import { useTranslation } from "react-i18next";
import { notify } from "../utils/notify";
import { useScrollAlignment } from "../hooks/useScrollAlignment";
import { SharedAreaContent } from "./SharedAreaContent";

import Fade from "./Fade";
import styles from "./StageOpponentSelection.module.css";
import Opponent from "./Opponent";

const StageOpponentSelection = ({ players, activePlayer, sendAction, active, selectedOpponent = null }) => {
  const { t } = useTranslation();
  const { containerRef, hasScroll } = useScrollAlignment();

  // Filter out active player (whose turn it is)
  const opponents = useMemo(
    () => Object.entries(players).filter(([name]) => name !== activePlayer),
    [players, activePlayer],
  );

  // Flat list of all alive opponent characters for arrow navigation
  const availableOpponentCharacters = useMemo(() => {
    const result = [];
    for (const [playerName, player] of opponents) {
      if (!player.characters) continue;
      for (const [charName, character] of Object.entries(player.characters)) {
        if (character.is_alive !== false) {
          result.push({ player: playerName, character: charName });
        }
      }
    }
    return result;
  }, [opponents]);

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

  const handleArrowNavigation = useCallback(
    (direction) => {
      if (!active || availableOpponentCharacters.length === 0) return;

      if (!selectedOpponent) {
        const first = availableOpponentCharacters[0];
        sendAction("opponent_press", { opponent: first.player, character: first.character });
        return;
      }

      const currentIndex = availableOpponentCharacters.findIndex(
        (item) => item.player === selectedOpponent.player && item.character === selectedOpponent.character,
      );
      let nextIndex;
      if (direction === "right") {
        nextIndex = currentIndex === -1 ? 0 : (currentIndex + 1) % availableOpponentCharacters.length;
      } else {
        nextIndex =
          currentIndex === -1
            ? 0
            : (currentIndex - 1 + availableOpponentCharacters.length) % availableOpponentCharacters.length;
      }

      const next = availableOpponentCharacters[nextIndex];
      sendAction("opponent_press", { opponent: next.player, character: next.character });
    },
    [active, availableOpponentCharacters, selectedOpponent, sendAction],
  );

  const content = (
    <div className={className("flex max-w-full", hasScroll ? "self-start" : "self-center")}>
      <Fade ref={containerRef} className={styles["opponents-container"]}>
        {opponents.map(([playerName, player]) => (
          <Opponent
            key={playerName}
            playerName={playerName}
            player={player}
            selectedOpponent={selectedOpponent}
            onCharacterClick={handleCharacterClick}
          />
        ))}
      </Fade>
    </div>
  );

  return (
    <SharedAreaContent
      content={content}
      onActionClick={handleSubmit}
      actionButtonContent={t("character_select.submit")}
      actionButtonDisabled={!active}
      onArrowNavigation={handleArrowNavigation}
    />
  );
};

export default StageOpponentSelection;
