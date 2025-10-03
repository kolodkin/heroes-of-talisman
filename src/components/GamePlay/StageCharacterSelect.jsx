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

import styles from "./StageCharacterSelect.module.css";
import commonStyles from "../Common.module.css";
import CharacterCard from "../CharacterCard";

const StageCharacterSelect = ({ characters, sendAction, active, selectedCharacter = null }) => {
  const { t } = useTranslation();

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
    <div className="flex flex-col items-center space-y-3">
      <div className="flex justify-center space-x-3 mb-8">
        {Object.entries(characters).map(([name, character]) => (
          <CharacterCard
            key={name}
            name={name}
            character={character}
            isSelected={name === selectedCharacter}
            onClick={() => handleCharacterClick(name)}
          />
        ))}
      </div>
      <button
        className={className(commonStyles.gamebtn, styles.character, "text-2xl", "rounded")}
        onClick={handleSubmit}
      >
        <p>{t("character_select.submit")}</p>
      </button>
    </div>
  );
};

export default StageCharacterSelect;
