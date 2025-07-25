from typing import Dict

from .models import (
    GameModel,
    PlayerModel,
    CharacterModel,
    GameException,
    ReportedException,
    TraitDB,
    __MAX_PLAYERS__,
    __DEFAULT_GAME__,
)
from .actions import (
    ACTION_MAP,
    CharacterSelectAction,
    CharacterSelectedAction,
    CardDrawAction,
    CardSelectAction,
    ConnectAction,
    LeaveAction,
    DisconnectAction,
)


class GameEngine:
    def __init__(self, gamename: str, username: str, game: GameModel):
        self._gamename = gamename
        self._username = username

        # load game
        self._game = game

    def dumps(self):
        return self.game.model_dump_json()

    @property
    def gamename(self):
        return self._gamename

    @property
    def username(self):
        return self._username

    @property
    def redis(self):
        return self._redis

    @property
    def game(self) -> GameModel:
        return self._game

    @property
    def players(self):
        return self.game.players

    @property
    def playing(self):
        return self.game.playing

    @property
    def stage(self):
        return self.game.stage

    @stage.setter
    def stage(self, value):
        self.game.stage = value

    @property
    def stage_meta(self):
        return self.game.stage_meta

    @stage_meta.setter
    def stage_meta(self, value):
        self.game.stage_meta = value

    @property
    def selected_character(self):
        return self.game.selected_character

    @selected_character.setter
    def selected_character(self, value):
        self.game.selected_character = value

    @property
    def deck(self):
        return self.game.deck

    @deck.setter
    def deck(self, value):
        self.game.deck = value

    @property
    def player(self):
        if self.username not in self.players:
            raise GameException("Player not in game")
        return self.players[self.username]

    def add_new_player(self, username: str):
        characters = {}
        for char_type in ["knight", "archer", "mage"]:
            trait_key = f"{char_type}-1"
            trait_data = TraitDB[trait_key]

            characters[char_type] = CharacterModel(
                health=trait_data["max_health"],
                level=1,
                max_health=trait_data["max_health"],
                skills=trait_data.get("skills", {}),
                dice=trait_data["dice"],
                attack=trait_data.get("attack"),  # Only knight has this
            )

        self.players[username] = PlayerModel(status="connected", cards=[], characters=characters)

    def run_action(self, action: str, *args, **kwargs):
        action_cls = ACTION_MAP.get(action)
        if action_cls is None:
            raise ReportedException("Invalid action", f"cannot find action '{action}'")

        action_obj = action_cls(self.username, self.game)
        return action_obj.run(*args, **kwargs)

    def assert_stage(self, req_stage: str):
        if self.stage != req_stage:
            raise ReportedException(f"Invalid action. (wrong stage '{self.stage}')")

    def action(self, action_meta: dict):
        action_meta = {**action_meta}
        action = action_meta.pop("action")
        username = action_meta.pop("username")
        if username != self.username:
            raise GameException(f"Invalid action. (wrong username). expected: {self.username}, got:{username}")

        kwargs = action_meta

        return self.run_action(action, **kwargs)
