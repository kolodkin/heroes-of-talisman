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
    def __init__(self, game_name: str, game: dict):
        self.game_name = game_name
        self.game = game

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

    @property
    def players(self):
        return self.game["players"]

    async def connect(self, username: str):
        if username not in self.players:
            self.add_new_player(username)

    async def leave(self, username: str):
        if username in self.players:
            self.players.pop(username)
