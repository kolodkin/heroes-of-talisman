/**
 * Ability Selection Stage
 *
 * Displays ability cards for the selected character plus a "no ability" option.
 *
 * Flow:
 * - On ability click: invokes 'ability_press' action, creating stage_meta
 *   with 'selected' in backend, triggering game_update to highlight selected ability
 * - On 'no ability' click: invokes 'ability_press' with ability=null to clear backend selection
 * - On Select button press: invokes 'ability_select' action, populating
 *   ability in game and switching GamePlay.stage accordingly
 */
import { useState } from "react";

import className from "classnames";
import { useTranslation } from "react-i18next";
import { notify } from "../utils/notify";
import { useScrollAlignment } from "../hooks/useScrollAlignment";
import { SharedAreaContent } from "./SharedAreaContent";

import Fade from "./Fade";
import commonStyles from "./Common.module.css";
import cardStyles from "./Card.module.css";
import gamePlayCardStyles from "./GamePlayCard.module.css";
import AbilityCard from "./AbilityCard";

const NO_ABILITY = "no_ability";

const StageAbilitySelection = ({ abilities, sendAction, active, selectedAbility = null }) => {
  const { t } = useTranslation();
  const { containerRef, hasScroll } = useScrollAlignment();
  const [noAbilitySelected, setNoAbilitySelected] = useState(false);

  const effectiveSelected = noAbilitySelected ? NO_ABILITY : selectedAbility;

  const handleAbilityClick = (abilityName) => {
    if (!active) {
      return;
    }

    setNoAbilitySelected(false);
    sendAction("ability_press", { ability: abilityName });
  };

  const handleNoAbilityClick = () => {
    if (!active) {
      return;
    }

    setNoAbilitySelected(true);
    sendAction("ability_press", { ability: null });
  };

  const handleSubmit = () => {
    if (!active) {
      return;
    }

    if (noAbilitySelected) {
      sendAction("ability_select", { ability: null });
    } else if (effectiveSelected) {
      sendAction("ability_select", { ability: effectiveSelected });
    } else {
      notify("ability_selection.select_ability");
    }
  };

  const content = (
    <div className={className("flex max-w-full", hasScroll ? "self-start" : "self-center")}>
      <Fade ref={containerRef} className={className(commonStyles.cardsContainer, "mb-8")}>
        {abilities.map((ability) => (
          <AbilityCard
            key={ability.name}
            ability={ability}
            isSelected={ability.name === effectiveSelected}
            onClick={() => handleAbilityClick(ability.name)}
          />
        ))}
        <div
          className={className(
            { [cardStyles.selected]: effectiveSelected === NO_ABILITY },
            cardStyles.card,
            gamePlayCardStyles.card,
            gamePlayCardStyles["card-normal"],
          )}
          onClick={handleNoAbilityClick}
          data-ability={NO_ABILITY}
        >
          <img src="/images/skip.png" alt={t("ability_selection.no_ability")} className={gamePlayCardStyles.image} />
          <div className={gamePlayCardStyles.content}>
            <p className={gamePlayCardStyles.name}>{t("ability_selection.no_ability")}</p>
          </div>
        </div>
      </Fade>
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
