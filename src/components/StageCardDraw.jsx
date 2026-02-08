/**
 * Card Draw Stage
 *
 * Displays a deck card, then shows the drawn card after drawing.
 *
 * Flow:
 * - Shows face-down deck card
 * - On Draw button press: invokes 'card_draw' action, backend draws and stores in stage_meta
 * - Shows the drawn card from stage_meta.drawn_card
 * - On Draw button press again: invokes 'card_select' action, applying card effects
 *   and transitioning to 'ability_selection' stage
 */
import { useTranslation } from "react-i18next";
import { SharedAreaContent } from "./SharedAreaContent";
import GameplayCard from "./GameplayCard";
import DeckCard from "./DeckCard";

import commonStyles from "./Common.module.css";

const StageCardDraw = ({ drawnCard, sendAction, active }) => {
  const { t } = useTranslation();

  const handleActionClick = () => {
    if (!active) {
      return;
    }
    if (!drawnCard) {
      sendAction("card_draw");
    } else {
      sendAction("card_select");
    }
  };

  const content = (
    <div className="flex max-w-full self-center">
      <div className={commonStyles.cardsContainer}>
        {!drawnCard ? (
          <DeckCard />
        ) : (
          <GameplayCard cardName={drawnCard} isSelected={true} onClick={() => {}} />
        )}
      </div>
    </div>
  );

  return (
    <SharedAreaContent
      content={content}
      onActionClick={handleActionClick}
      actionButtonContent={t("card_draw.draw")}
      actionButtonDisabled={!active}
    />
  );
};

export default StageCardDraw;
