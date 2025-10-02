from .gameplay.models import (
    GameBoard,
    GameException,
    ReportedException,
)
from .actions import (
    ACTION_MAP,
)


class GameEngine:
    def __init__(self, gamename: str, username: str, game: GameBoard):
        self._gamename = gamename
        self._username = username

        # load game
        self._game = game

    def dumps(self):
        return self.game.model_dump_json()

    def model_dump(self):
        """Return game state with players reordered for this user"""
        game_dict = self.game.model_dump()
        # Reorder players and convert to dict
        reordered_players = self.game.reorder_players(self.username)
        game_dict["players"] = {key: player.model_dump() for key, player in reordered_players.items()}
        return game_dict

    @property
    def gamename(self):
        return self._gamename

    @property
    def username(self):
        return self._username

    @property
    def game(self) -> GameBoard:
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
