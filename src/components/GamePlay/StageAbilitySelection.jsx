/**
 * Ability Selection Stage
 *
 * Displays ability cards for the selected character.
 *
 * Flow:
 * - On ability click: invokes 'ability_press' action, creating stage_meta
 *   with 'selected' in backend, triggering game_update to highlight selected ability
 * - On Select button press: invokes 'ability_select' action, populating
 *   ability in game and switching GamePlay.stage to 'ability_opponent_selection'
 */
import className from "classnames";
import { useTranslation } from "react-i18next";
import { notify } from "../../utils/notify";
import { useScrollAlignment } from "../../hooks/useScrollAlignment";
import { SharedAreaContent } from "./SharedAreaContent";

import commonStyles from "../Common.module.css";
import AbilityCard from "../AbilityCard";

const StageAbilitySelection = ({ abilities, sendAction, active, selectedAbility = null }) => {
  const { t } = useTranslation();
  const { containerRef, hasScroll } = useScrollAlignment();

  const handleAbilityClick = (abilityName) => {
    if (!active) {
      return;
    }

    sendAction("ability_press", { ability: abilityName });
  };

  const handleSubmit = () => {
    if (!active) {
      return;
    }

    if (selectedAbility) {
      sendAction("ability_select", { ability: selectedAbility });
    } else {
      notify("ability_selection.select_ability");
    }
  };

  const content = (
    <div className={className("flex max-w-full", hasScroll ? "self-start" : "self-center")}>
      <div ref={containerRef} className={className(commonStyles.cardsContainer, "mb-8")}>
        {abilities.map((ability) => (
          <AbilityCard
            key={ability.name}
            ability={ability}
            isSelected={ability.name === selectedAbility}
            onClick={() => handleAbilityClick(ability.name)}
          />
        ))}
      </div>
    </div>
  );

  return (
    <SharedAreaContent
      content={content}
      onActionClick={handleSubmit}
      actionButtonContent={t("ability_selection.submit")}
      actionButtonDisabled={!active}
    />
  );
};

export default StageAbilitySelection;
