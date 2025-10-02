import className from "classnames";
import styles from "./CharacterSelect.module.css";
import commonStyles from "./Common.module.css";
import { DiceIcon, HeartIcon } from "./Icons";
import lang from "./he";

const signStr = (num) => (num ? (num >= 0 ? `+${num}` : `-${num}`) : "");

const CharacterCard = ({ name, character, isSelected, onClick }) => {
  const nameStr = lang.characterNames[name];

  return (
    <div
      className={className({ [commonStyles.selected]: isSelected }, commonStyles.gamebtn, styles.character, "text-2xl")}
      onClick={onClick}
    >
      <img src={`/images/${name}.png`} alt={name} style={{ minWidth: "200px", width: "200px", height: "200px" }} />
      <p className="align-text-center w-full">
        {nameStr} דרגה {character.level}
      </p>
      <div className="flex items-center space-x-1">
        {[...Array(character.dice).keys()].map((i) => (
          <DiceIcon color="white" fill="black" size={"20px"} key={i} />
        ))}
        <span>{signStr(character.attack)}</span>
      </div>
      <div className="flex items-center">
        <HeartIcon color="red" size={"20px"} />
        <span>
          [{character.health}/{character.max_health}]
        </span>
      </div>
    </div>
  );
};

export default CharacterCard;
