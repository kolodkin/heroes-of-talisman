import json


class GameException(Exception):
    pass


class ReportedException(GameException):
    pass


__MAX_PLAYERS__ = 4

__DEFAULT_GAME__ = {
    "stage": None,  # None -> [character_select] -> [card_draw] -> [use_skill] -> [battle] -> |
    #                                      |                                                      |
    #                                      <------------------------------------------------------|
    "playing": None,  # username
    "players": {},
}


TraitDB = {
    "knight-1": {
        "max_health": 2,
        "skills": {},
        "dice": 1,
        "attack": 1,
    },
    "archer-1": {
        "max_health": 3,
        "skills": {},
        "dice": 1,
    },
    "mage-1": {
        "max_health": 2,
        "skills": {},
        "dice": 1,
    },
}


class GameEngine:
    def __init__(self, gamename: str, username: str, game: dict):
        self._gamename = gamename
        self._username = username

        # load game
        self._game = game

    def dumps(self):
        return json.dumps(self.game)

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
    def game(self: str):
        return self._game

    @property
    def players(self):
        return self.game["players"]

    @property
    def playing(self):
        return self.game["playing"]

    @property
    def stage(self):
        return self.game["stage"]

    @property
    def player(self):
        if self.username not in self.players:
            raise GameException("Player not in game")
        return self.players[self.username]

    def add_new_player(self, username: str):
        self.players[username] = {
            "status": "connected",
            "cards": [],
            "characters": {
                "knight": {
                    "health": 2,
                    "level": 1,
                    **TraitDB["knight-1"],
                },
                "archer": {
                    "health": 3,
                    "level": 1,
                    **TraitDB["archer-1"],
                },
                "mage": {
                    "health": 2,
                    "level": 1,
                    **TraitDB["mage-1"],
                },
            },
        }

    def action(self, action: dict, *args, **kwargs):
        if not hasattr(self, f'action_{action["action"]}'):
            raise ReportedException("Invalid action")

        func = getattr(self, f'action_{action["action"]}')
        if not callable(func):
            raise ReportedException("Invalid action")

        func(*args, **kwargs)
        return self.game

    def action_connect(self):
        # add player if not in game
        if self.username not in self.players:
            if len(self.players) >= __MAX_PLAYERS__:
                raise ReportedException("Game is full")
            self.add_new_player(self.username)

        if self.playing is None:
            # game not started, set playing to current player and initial stage
            if self.stage is None:
                self.game["stage"] = "character_select"
            self.game["playing"] = self.username

    def action_leave(self):
        if self.username not in self.players:
            raise GameException("Player not in game")

        self.players.pop(self.username)

    def action_disconnect(self):
        self.player["status"] = "disconnected"
