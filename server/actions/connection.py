from typing import Dict

from .base import Action
from .models import (
    GameModel,
    GameException,
    ReportedException,
    PlayerModel,
    CharacterModel,
    CHARACTER_DEFAULT_STATS,
    __MAX_PLAYERS__,
)


class ConnectAction(Action):
    def run(self) -> GameModel:
        if self.user not in self.players:
            if len(self.players) >= __MAX_PLAYERS__:
                raise ReportedException("Game is full")

            characters: Dict[str, CharacterModel] = {}
            for char_type in ["knight", "archer", "mage"]:
                characters[char_type] = CharacterModel(level=1, **CHARACTER_DEFAULT_STATS[char_type])

            self.players[self.user] = PlayerModel(name=self.user, status="connected", cards=[], characters=characters)

        if self.game.playing is None:
            if self.game.stage is None:
                self.game.stage = "character_select"
            self.game.playing = self.user

        self.player.status = "connected"
        return self.game


class LeaveAction(Action):
    def run(self) -> GameModel:
        if self.user not in self.players:
            raise GameException("Player not in game")

        self.players.pop(self.user)
        return self.game


class DisconnectAction(Action):
    def run(self) -> GameModel:
        self.player.status = "disconnected"
        return self.game
