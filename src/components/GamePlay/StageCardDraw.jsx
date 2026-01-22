/**
 * Card Draw Stage
 *
 * Displays a deck card to draw from, then shows the drawn card.
 *
 * Flow:
 * - Shows face-down deck card
 * - On deck card click: invokes 'card_draw' action, backend draws and stores in stage_meta
 * - Shows the drawn card from stage_meta.drawn_card
 * - On Select button press: invokes 'card_select' action, applying card effects
 *   and transitioning to 'ability_selection' stage
 */
import { useTranslation } from "react-i18next";
import { SharedAreaContent } from "./SharedAreaContent";
import GameplayCard from "../GameplayCard";
import DeckCard from "../DeckCard";

import commonStyles from "../Common.module.css";

const StageCardDraw = ({ drawnCard, sendAction, active }) => {
  const { t } = useTranslation();

  const handleDeckClick = () => {
    if (!active || drawnCard) {
      return;
    }
    sendAction("card_draw");
  };

  const handleSubmit = () => {
    if (!active || !drawnCard) {
      return;
    }
    sendAction("card_select");
  };

  const content = (
    <div className="flex max-w-full self-center">
      <div className={commonStyles.cardsContainer}>
        {!drawnCard ? (
          <DeckCard onClick={handleDeckClick} />
        ) : (
          <GameplayCard cardName={drawnCard} isSelected={true} onClick={() => {}} />
        )}
      </div>
    </div>
  );

  return (
    <SharedAreaContent
      content={content}
      onActionClick={handleSubmit}
      actionButtonContent={t("card_draw.select")}
      actionButtonDisabled={!active || !drawnCard}
    />
  );
};

export default StageCardDraw;
