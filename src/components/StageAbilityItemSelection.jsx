/**
 * Ability Item Selection Stage
 *
 * Displays the target opponent's active item cards for the active player to choose
 * which item to neutralize with Dragon Breath.
 *
 * Flow:
 * - Click on an item card: invokes 'ability_item_press' action, setting stage_meta.selected_item
 *   in the backend, triggering game_update to highlight the selected item
 * - Click Select button: invokes 'ability_item_select' action, removing the selected item from
 *   the target's active_cards and transitioning stage to 'opponent_selection'
 */
import React, { useCallback } from "react";

import className from "classnames";
import { useTranslation } from "react-i18next";
import { notify } from "../utils/notify";
import { useScrollAlignment } from "../hooks/useScrollAlignment";
import { SharedAreaContent } from "./SharedAreaContent";

import commonStyles from "./Common.module.css";
import GameplayCard from "./GameplayCard";

const StageAbilityItemSelection = ({ stageMeta, players, sendAction, active }) => {
  const { t } = useTranslation();
  const { containerRef, hasScroll } = useScrollAlignment();

  const targetPlayer = stageMeta?.target_player;
  const targetCharacter = stageMeta?.target_character;
  const selectedItem = stageMeta?.selected_item ?? null;

  const targetActiveCards =
    targetPlayer && targetCharacter ? (players?.[targetPlayer]?.characters?.[targetCharacter]?.active_cards ?? []) : [];

  const handleItemClick = useCallback(
    (cardName) => {
      if (!active) return;
      sendAction("ability_item_press", { item: cardName });
    },
    [active, sendAction],
  );

  const handleSubmit = () => {
    if (!active) return;

    if (selectedItem) {
      sendAction("ability_item_select");
    } else {
      notify("ability_item_selection.select_item");
    }
  };

  const handleArrowNavigation = useCallback(
    (direction) => {
      if (!active || targetActiveCards.length === 0) return;

      if (!selectedItem) {
        sendAction("ability_item_press", { item: targetActiveCards[0] });
        return;
      }

      const currentIndex = targetActiveCards.indexOf(selectedItem);
      let nextIndex;
      if (direction === "right") {
        nextIndex = currentIndex === -1 ? 0 : (currentIndex + 1) % targetActiveCards.length;
      } else {
        nextIndex = currentIndex === -1 ? 0 : (currentIndex - 1 + targetActiveCards.length) % targetActiveCards.length;
      }

      sendAction("ability_item_press", { item: targetActiveCards[nextIndex] });
    },
    [active, targetActiveCards, selectedItem, sendAction],
  );

  const content = (
    <div className={className("flex max-w-full", hasScroll ? "self-start" : "self-center")}>
      <div ref={containerRef} className={className(commonStyles.cardsContainer, "mb-8")}>
        {targetActiveCards.map((cardName) => (
          <GameplayCard
            key={cardName}
            cardName={cardName}
            isSelected={cardName === selectedItem}
            onClick={() => handleItemClick(cardName)}
          />
        ))}
      </div>
    </div>
  );

  return (
    <SharedAreaContent
      content={content}
      onActionClick={handleSubmit}
      actionButtonContent={t("ability_item_selection.submit")}
      actionButtonDisabled={!active}
      onArrowNavigation={handleArrowNavigation}
    />
  );
};

export default StageAbilityItemSelection;
