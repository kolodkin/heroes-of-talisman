import json

from redis.asyncio import Redis


class GameException(Exception):
    pass


__DEFAULT_GAME__ = {"players": {}}

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

    @staticmethod
    async def from_redis(gamename: str, username: str, redis: Redis) -> "GameEngine":
        game = await redis.get(f"game:{gamename}")
        if game is None:
            raise GameException("Game not found")

        game = json.loads(game)
        return GameEngine(gamename, username, game)

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

    async def action(self, action: dict):
        if action["action"] == "connect":
            await self.connect()
        elif action["action"] == "leave":
            await self.leave()
        else:
            raise GameException("Invalid action")

    async def connect(self):
        if self.username not in self.players:
            self.add_new_player(self.username)

    async def leave(self):
        if self.username not in self.players:
            raise GameException("Player not in game")

        self.players.pop(self.username)

    async def disconnect(self):
        if self.username in self.players:
            self.players[self.username]["status"] = "disconnected"
