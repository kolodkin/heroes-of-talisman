/**
 * Character Select Stage
 *
 * Displays character cards for each character (similar to players menu).
 *
 * Flow:
 * - On character click: invokes 'character_press' action, creating stage_meta
 *   with 'selected' in backend, triggering game_update to highlight selected character
 * - On Select button press: invokes 'character_select' action, populating
 *   selected_character in game meta and switching GamePlay.stage to 'battle'
 * - If no character is available (all dead or have skip_turn effect), show Skip Turn button
 */
import { useMemo, useCallback } from "react";

import className from "classnames";
import { useTranslation } from "react-i18next";

import { notify } from "../utils/notify";
import { useScrollAlignment } from "../hooks/useScrollAlignment";

import { SharedAreaContent } from "./SharedAreaContent";
import CharacterCard from "./CharacterCard";
import commonStyles from "./Common.module.css";

const StageCharacterSelect = ({ characters, sendAction, active, selectedCharacter = null }) => {
  const { t } = useTranslation();
  const { containerRef, hasScroll } = useScrollAlignment();

  // List of available character names (computed by backend: alive and no skip_turn)
  const availableCharacters = useMemo(() => {
    return Object.entries(characters)
      .filter(([, char]) => char.is_available)
      .map(([name]) => name);
  }, [characters]);

  const hasAvailableCharacter = availableCharacters.length > 0;

  const handleCharacterClick = (name) => {
    if (!active) {
      return;
    }

    sendAction("character_press", { character: name });
  };

  const handleArrowNavigation = useCallback(
    (direction) => {
      if (!active || availableCharacters.length === 0) return;

      if (!selectedCharacter) {
        sendAction("character_press", { character: availableCharacters[0] });
        return;
      }

      const currentIndex = availableCharacters.indexOf(selectedCharacter);
      let nextIndex;
      if (direction === "right") {
        nextIndex = currentIndex === -1 ? 0 : (currentIndex + 1) % availableCharacters.length;
      } else {
        nextIndex =
          currentIndex === -1 ? 0 : (currentIndex - 1 + availableCharacters.length) % availableCharacters.length;
      }

      sendAction("character_press", { character: availableCharacters[nextIndex] });
    },
    [active, availableCharacters, selectedCharacter, sendAction],
  );

  const handleSubmit = () => {
    if (!active) {
      return;
    }

    if (!hasAvailableCharacter) {
      // No character available - skip turn
      sendAction("skip_turn");
      return;
    }

    if (selectedCharacter) {
      sendAction("character_select", { character: selectedCharacter });
    } else {
      notify("character_select.select_character");
    }
  };

  const content = (
    <div className={className("flex w-full", hasScroll ? "justify-start" : "justify-center")}>
      <div ref={containerRef} className={className(commonStyles.cardsContainer, "mb-8")}>
        {Object.entries(characters).map(([name, character]) => (
          <CharacterCard
            key={name}
            name={name}
            character={character}
            isSelected={name === selectedCharacter}
            onClick={() => handleCharacterClick(name)}
            size="normal"
          />
        ))}
      </div>
    </div>
  );

  // Determine button text - "Skip Turn" if no character available, otherwise "Select"
  const buttonText = hasAvailableCharacter ? t("character_select.submit") : t("character_select.skip_turn");

  return (
    <SharedAreaContent
      content={content}
      onActionClick={handleSubmit}
      actionButtonContent={buttonText}
      actionButtonDisabled={!active}
      actionButtonDataAttrs={!hasAvailableCharacter ? { "data-skip-turn": true } : {}}
      onArrowNavigation={handleArrowNavigation}
    />
  );
};

export default StageCharacterSelect;
