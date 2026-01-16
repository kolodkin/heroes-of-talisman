from typing import Dict

from .action import Action
from ..models import (
    GamePlay,
    GameException,
    ReportedException,
    Player,
    CharacterCard,
    ActivePlayer1,
    CHARACTER_DEFAULT_STATS,
    KNIGHT,
    ARCHER,
    MAGE,
    CONNECTED,
    DISCONNECTED,
    CHARACTER_SELECT,
)

MAX_PLAYERS = 4


class ConnectAction(Action):
    @property
    def action_stages(self):
        return None  # Can connect at any time

    def run(self) -> GamePlay:
        if self.user not in self.players:
            if len(self.players) >= MAX_PLAYERS:
                raise ReportedException("Game is full")

            characters: Dict[str, CharacterCard] = {}
            for char_type in [KNIGHT, ARCHER, MAGE]:
                characters[char_type] = CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[char_type])

            self.players[self.user] = Player(name=self.user, status=CONNECTED, cards=[], characters=characters)

        if self.game.active is None:
            if self.game.stage is None:
                self.game.stage = CHARACTER_SELECT
            self.game.active = ActivePlayer1(player=self.user)

        self.player.status = CONNECTED
        return self.game


class LeaveAction(Action):
    @property
    def action_stages(self):
        return None  # Can leave at any time

    def run(self) -> GamePlay:
        if self.user not in self.players:
            raise GameException("Player not in game")

        self.players.pop(self.user)
        return self.game


class DisconnectAction(Action):
    @property
    def action_stages(self):
        return None  # Can disconnect at any time

    def run(self) -> GamePlay:
        self.player.status = DISCONNECTED
        return self.game
