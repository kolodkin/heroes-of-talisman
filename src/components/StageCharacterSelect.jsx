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
import { useMemo } from "react";

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

  // Check if any character is available (alive and no skip_turn effect)
  const hasAvailableCharacter = useMemo(() => {
    return Object.values(characters).some((char) => {
      const isAlive = char.is_alive !== false;
      const hasSkipTurn = char.effects?.some((effect) => effect.name === "skip_turn") || false;
      return isAlive && !hasSkipTurn;
    });
  }, [characters]);

  const handleCharacterClick = (name) => {
    if (!active) {
      return;
    }

    sendAction("character_press", { character: name });
  };

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
  const buttonText = hasAvailableCharacter
    ? t("character_select.submit")
    : t("character_select.skip_turn");

  return (
    <SharedAreaContent
      content={content}
      onActionClick={handleSubmit}
      actionButtonContent={buttonText}
      actionButtonDisabled={!active}
      actionButtonDataAttrs={!hasAvailableCharacter ? { "data-skip-turn": true } : {}}
    />
  );
};

export default StageCharacterSelect;
