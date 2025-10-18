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

import styles from "./StageCharacterSelect.module.css";
import submitButtonStyles from "./StageSubmitButton.module.css";
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

  return (
    <div className="flex flex-col items-center space-y-3 self-stretch">
      <div className={className("flex max-w-full", hasScroll ? "self-start" : "self-center")}>
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
      <button
        className={className(
          commonStyles.gamebtn,
          commonStyles.submitButton,
          submitButtonStyles["submit-button"],
          "text-2xl",
        )}
        onClick={handleSubmit}
      >
        <p>{t("character_select.submit")}</p>
      </button>
    </div>
  );
};

export default StageCharacterSelect;
