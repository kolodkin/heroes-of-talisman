from typing import Dict

from .base import Action
from ..models import GameModel, GameException, ReportedException, PlayerModel, CharacterModel, TraitDB, __MAX_PLAYERS__


class ConnectAction(Action):
    def run(self) -> GameModel:
        if self.user not in self.players:
            if len(self.players) >= __MAX_PLAYERS__:
                raise ReportedException("Game is full")

            characters: Dict[str, CharacterModel] = {}
            for char_type in ["knight", "archer", "mage"]:
                trait_key = f"{char_type}-1"
                trait_data = TraitDB[trait_key]
                characters[char_type] = CharacterModel(
                    health=trait_data["max_health"],
                    level=1,
                    max_health=trait_data["max_health"],
                    skills=trait_data.get("skills", {}),
                    dice=trait_data["dice"],
                    attack=trait_data.get("attack"),
                )

            self.players[self.user] = PlayerModel(status="connected", cards=[], characters=characters)

        if self.game.playing is None:
            if self.game.stage is None:
                self.game.stage = "character_select"
            self.game.playing = self.user

        self.player.status = "connected"


class LeaveAction(Action):
    def run(self) -> GameModel:
        if self.user not in self.players:
            raise GameException("Player not in game")

        self.players.pop(self.user)


class DisconnectAction(Action):
    def run(self) -> GameModel:
        self.player.status = "disconnected"
