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
      <img
        src={`/images/${name}.png`}
        alt={name}
        style={{
          minWidth: "120px",
          width: "120px",
          height: "120px",
          borderRadius: "6px",
        }}
      />
      <p className="w-full text-center font-bold" style={{ fontSize: "0.9rem" }}>
        {nameStr} דרגה {character.level}
      </p>
      <div className="flex items-center gap-1">
        {[...Array(character.dice).keys()].map((i) => (
          <DiceIcon color="white" fill="black" size={"16px"} key={i} />
        ))}
        {character.attack && <span className="font-bold text-sm">{signStr(character.attack)}</span>}
      </div>
      <div className="flex items-center gap-1">
        <HeartIcon color="red" size={"16px"} />
        <span className="font-bold text-sm">
          [{character.health}/{character.max_health}]
        </span>
      </div>
    </div>
  );
};

export default CharacterCard;
