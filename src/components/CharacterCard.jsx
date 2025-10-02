import className from "classnames";
import { useTranslation } from "react-i18next";
import styles from "./CharacterSelect.module.css";
import commonStyles from "./Common.module.css";
import { DiceIcon, HeartIcon } from "./Icons";

const signStr = (num) => (num ? (num >= 0 ? `+${num}` : `-${num}`) : "");

const CharacterCard = ({ name, character, isSelected, onClick }) => {
  const { t } = useTranslation();
  const nameStr = t(`characterNames.${name}`);

  return (
    <div
      className={className({ [commonStyles.selected]: isSelected }, commonStyles.gamebtn, styles.character, "text-2xl")}
      onClick={onClick}
    >
      <img
        src={`/images/${name}.png`}
        alt={name}
        style={{
          minWidth: "80px",
          width: "80px",
          height: "80px",
          borderRadius: "4px",
        }}
      />
      <p className="w-full text-center font-bold" style={{ fontSize: "0.7rem" }}>
        {nameStr} {t("character_card.level")} {character.level}
      </p>
      <div className="flex items-center gap-1">
        {[...Array(character.dice).keys()].map((i) => (
          <DiceIcon color="white" fill="black" size={"12px"} key={i} />
        ))}
        {character.attack && (
          <span className="font-bold" style={{ fontSize: "0.65rem" }}>
            {signStr(character.attack)}
          </span>
        )}
      </div>
      <div className="flex items-center gap-1">
        <HeartIcon color="red" size={"12px"} />
        <span className="font-bold" style={{ fontSize: "0.65rem" }}>
          [{character.health}/{character.max_health}]
        </span>
      </div>
    </div>
  );
};

export default CharacterCard;
