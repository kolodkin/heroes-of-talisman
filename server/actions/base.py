from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..gameplay.models import GameBoard, Player, GameException, ReportedException


class Action(ABC):
    def __init__(self, user: str, game: GameBoard):
        self.user: str = user
        self.game: GameBoard = game

    # convenience helpers similar to GameEngine properties
    @property
    def players(self):
        return self.game.players_hands

    @property
    def player(self) -> Player:
        if self.user not in self.players:
            raise GameException("Player not in game")
        return self.players[self.user]

    @property
    def stage(self) -> Optional[str]:
        return self.game.stage

    @stage.setter
    def stage(self, value: Optional[str]):
        self.game.stage = value

    @property
    def stage_meta(self) -> Optional[Dict[str, Any]]:
        return self.game.stage_meta

    @stage_meta.setter
    def stage_meta(self, value: Optional[Dict[str, Any]]):
        self.game.stage_meta = value

    @property
    def selected_character(self) -> Optional[str]:
        return self.game.selected_character

    @selected_character.setter
    def selected_character(self, value: Optional[str]):
        self.game.selected_character = value

    @property
    def deck(self) -> list[str]:
        return self.game.deck

    @deck.setter
    def deck(self, value: list[str]):
        self.game.deck = value

    def assert_stage(self, req_stage: str):
        if self.stage != req_stage:
            raise ReportedException(f"Invalid action. (wrong stage '{self.stage}')")

    @abstractmethod
    def run(self, *args, **kwargs) -> GameBoard:
        """Execute the action and return the updated game."""
