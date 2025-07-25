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

    def run_action(self, action: str, *args, **kwargs):
        action_cls = ACTION_MAP.get(action)
        if action_cls is None:
            raise ReportedException("Invalid action", f"cannot find action '{action}'")

        action_obj = action_cls(self.username, self.game)
        return action_obj.run(*args, **kwargs)

    def action(self, action_meta: dict):
        action_meta = {**action_meta}
        action = action_meta.pop("action")
        username = action_meta.pop("username")
        if username != self.username:
            raise GameException(f"Invalid action. (wrong username). expected: {self.username}, got:{username}")

        kwargs = action_meta

        return self.run_action(action, **kwargs)
