import className from "classnames";
import { notify } from "../utils/notify";

import styles from "./CharacterSelect.module.css";
import commonStyles from "./Common.module.css";
import CharacterCard from "./CharacterCard";
import lang from "./he";

const CharacterSelect = ({ characters, sendAction, active, selectedCharacter = null }) => {
  const handleCharacterClick = (name) => {
    if (!active) {
      return;
    }

    sendAction("character_select", { character: name });
    // notify(`selected ${lang.characterNames[name]}`);
  };

  const handleSubmit = () => {
    if (!active) {
      return;
    }

    if (selectedCharacter) {
      sendAction("character_selected", { character: selectedCharacter });
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
        <p>{lang.character_select.submit}</p>
      </button>
    </div>
  );
};

export default CharacterSelect;
