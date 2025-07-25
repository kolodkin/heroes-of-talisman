import random
from typing import Optional

from .base import Action
from ..models import GameModel, ReportedException


class CharacterSelectAction(Action):
    def run(self, character: Optional[str] = None) -> GameModel:
        self.assert_stage("character_select")

        if character is not None and character not in self.player.characters:
            raise ReportedException("Invalid action. (character not found)")

        self.stage_meta = {"selected": character}
        return self.game


class CharacterSelectedAction(Action):
    def run(self, character: str) -> GameModel:
        self.assert_stage("character_select")

        if character not in self.player.characters:
            raise ReportedException("Invalid action. (character not found)")

        self.selected_character = character
        self.stage = "card_draw"
        selected_card = random.choice(self.deck)
        self.stage_meta = {"card": selected_card, "drawn": False}
        return self.game
