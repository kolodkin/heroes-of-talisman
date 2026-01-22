from typing import Dict

from .action import Action
from ..common import (
    GameException,
    ReportedException,
    CHARACTER_KNIGHT,
    CHARACTER_ARCHER,
    CHARACTER_MAGE,
    STATUS_CONNECTED,
    STATUS_DISCONNECTED,
)
from ..gameplay import (
    STAGE_CHARACTER_SELECT,
    GamePlay,
    Player,
    Character,
    ActivePlayer1,
    CHARACTER_DEFAULT_STATS,
)

MAX_PLAYERS = 4


class ConnectAction(Action):
    @property
    def action_stages(self):
        return None  # Can connect at any time

    def _run(self) -> GamePlay:
        if self.user not in self.players:
            if len(self.players) >= MAX_PLAYERS:
                raise ReportedException("Game is full")

            characters: Dict[str, Character] = {}
            for char_type in [CHARACTER_KNIGHT, CHARACTER_ARCHER, CHARACTER_MAGE]:
                characters[char_type] = Character(level=1, **CHARACTER_DEFAULT_STATS[char_type])

            self.players[self.user] = Player(name=self.user, status=STATUS_CONNECTED, characters=characters)

        if self.game.active is None:
            if self.game.stage is None:
                self.game.stage = STAGE_CHARACTER_SELECT
            self.game.active = ActivePlayer1(player=self.user)

        self.player.status = STATUS_CONNECTED
        return self.game


class LeaveAction(Action):
    @property
    def action_stages(self):
        return None  # Can leave at any time

    def _run(self) -> GamePlay:
        if self.user not in self.players:
            raise GameException("Player not in game")

        self.players.pop(self.user)
        return self.game


class DisconnectAction(Action):
    @property
    def action_stages(self):
        return None  # Can disconnect at any time

    def _run(self) -> GamePlay:
        self.player.status = STATUS_DISCONNECTED
        return self.game
