from typing import Optional

from .base import Action
from ..models import GameModel, ReportedException, shuffled_deck


class CardDrawAction(Action):
    def run(self, card: Optional[str] = None, drawn: bool = False) -> GameModel:
        self.assert_stage("card_draw")

        self.stage_meta = {"card": card, "drawn": drawn}
        return self.game


class CardSelectAction(Action):
    def run(self, card: str) -> GameModel:
        self.assert_stage("card_draw")

        if card not in self.deck:
            raise ReportedException(f"Invalid action. (card '{card}' not in deck)")

        self.deck.remove(card)
        if len(self.deck) == 0:
            self.deck = shuffled_deck()

        self.stage = "use_skill"
        self.stage_meta = {}
        return self.game
