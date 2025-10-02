from typing import Dict

from .base import Action
from ..gameplay.models import (
    GameBoard,
    GameException,
    ReportedException,
    Player,
    CharacterCard,
    CHARACTER_DEFAULT_STATS,
)

__MAX_PLAYERS__ = 4


class ConnectAction(Action):
    def run(self) -> GameBoard:
        if self.user not in self.players:
            if len(self.players) >= __MAX_PLAYERS__:
                raise ReportedException("Game is full")

            characters: Dict[str, CharacterCard] = {}
            for char_type in ["knight", "archer", "mage"]:
                characters[char_type] = CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[char_type])

            self.players[self.user] = Player(name=self.user, status="connected", cards=[], characters=characters)

        if self.game.playing is None:
            if self.game.stage is None:
                self.game.stage = "character_select"
            self.game.playing = self.user

        self.player.status = "connected"
        return self.game


class LeaveAction(Action):
    def run(self) -> GameBoard:
        if self.user not in self.players:
            raise GameException("Player not in game")

        self.players.pop(self.user)
        return self.game


class DisconnectAction(Action):
    def run(self) -> GameBoard:
        self.player.status = "disconnected"
        return self.game
