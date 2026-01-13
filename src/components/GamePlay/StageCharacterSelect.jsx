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
 */
import className from "classnames";
import { useTranslation } from "react-i18next";
import { notify } from "../../utils/notify";
import { useScrollAlignment } from "../../hooks/useScrollAlignment";
import { SharedAreaContent } from "./SharedAreaContent";

import commonStyles from "../Common.module.css";
import CharacterCard from "../CharacterCard";

const StageCharacterSelect = ({ characters, sendAction, active, selectedCharacter = null }) => {
  const { t } = useTranslation();
  const { containerRef, hasScroll } = useScrollAlignment();

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

  return (
    <SharedAreaContent
      content={content}
      onActionClick={handleSubmit}
      actionButtonContent={t("character_select.submit")}
      actionButtonDisabled={!active}
    />
  );
};

export default StageCharacterSelect;
