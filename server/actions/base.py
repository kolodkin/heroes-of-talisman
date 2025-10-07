from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..gameplay.models import (
    GamePlay,
    Player,
    GameException,
    ReportedException,
    ActivePlayer1,
    ActivePlayer2,
    ActivePlayer3,
    Opponent2,
    Opponent3,
)


class Action(ABC):
    def __init__(self, user: str, game: GamePlay):
        self.user: str = user
        self.game: GamePlay = game

    # convenience helpers similar to GameEngine properties

    @property
    def stage(self) -> Optional[str]:
        return self.game.stage

    @stage.setter
    def stage(self, value: Optional[str]):
        self.game.stage = value

    @property
    def active(self) -> Optional[ActivePlayer1 | ActivePlayer2 | ActivePlayer3]:
        return self.game.active

    @active.setter
    def active(self, value: Optional[ActivePlayer1 | ActivePlayer2 | ActivePlayer3]):
        self.game.active = value

    @property
    def players(self):
        return self.game.players

    @players.setter
    def players(self, value: dict[str, Player]):
        self.game.players = value

    @property
    def player(self) -> Player:
        if self.user not in self.players:
            raise GameException("Player not in game")
        return self.players[self.user]

    @property
    def stage_meta(self) -> Optional[Dict[str, Any]]:
        return self.game.stage_meta

    @stage_meta.setter
    def stage_meta(self, value: Optional[Dict[str, Any]]):
        self.game.stage_meta = value

    @property
    def opponent(self) -> Optional[Opponent2 | Opponent3]:
        return self.game.opponent

    @opponent.setter
    def opponent(self, value: Optional[Opponent2 | Opponent3]):
        self.game.opponent = value

    def assert_stage(self, req_stage: str):
        if self.stage != req_stage:
            raise ReportedException(f"Invalid action. (wrong stage '{self.stage}')")

    @abstractmethod
    def run(self, *args, **kwargs) -> GamePlay:
        """Execute the action and return the updated game."""
