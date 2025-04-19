import json
import random


class GameException(Exception):
    pass


class ReportedException(GameException):
    pass


__MAX_PLAYERS__ = 4

__DECK__ = ["talisman", "golden_apple"]


def shuffled_deck():
    deck = __DECK__.copy()
    random.shuffle(deck)
    return deck


__DEFAULT_GAME__ = {
    "stage": None,
    # None ->
    # [character_select] ->
    # [card_draw] ->
    # [use_skill] -> [battle] ->
    # [character_select]
    "stage_meta": None,  # stage meta data
    "deck": shuffled_deck(),  # deck of cards
    "playing": None,  # username
    "selected_character": None,  # current round selected character
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

    @stage.setter
    def stage(self, value):
        self.game["stage"] = value

    @property
    def stage_meta(self):
        return self.game["stage_meta"]

    @stage_meta.setter
    def stage_meta(self, value):
        self.game["stage_meta"] = value

    @property
    def selected_character(self):
        return self.game["selected_character"]

    @selected_character.setter
    def selected_character(self, value):
        self.game["selected_character"] = value

    @property
    def deck(self):
        return self.game["deck"]

    @deck.setter
    def deck(self, value):
        self.game["deck"] = value

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

    def run_action(self, action: dict, *args, **kwargs):
        if not hasattr(self, f"action_{action}"):
            raise ReportedException(f"Invalid action", f"cannot find action '{action}'")

        func = getattr(self, f"action_{action}")
        if not callable(func):
            raise ReportedException("Invalid action", f"action '{action}' is not callable")

        func(*args, **kwargs)
        return self.game

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

    def action_character_select(self, character: str = None):
        self.assert_stage("character_select")

        if character is not None and character not in self.player["characters"]:
            raise ReportedException("Invalid action. (character not found)")

        # Stage Meta Update
        self.stage_meta = {"selected": character}

    def action_character_selected(self, character: str):
        self.assert_stage("character_select")

        if character not in self.player["characters"]:
            raise ReportedException("Invalid action. (character not found)")

        self.selected_character = character

        # Stage Update -> card_draw
        self.stage = "card_draw"

        selected_card = random.choice(self.deck)  # Randomly select a card from the deck
        self.stage_meta = {"card": selected_card, "drawn": False}

    def action_card_draw(self, card: str = None, drawn=False):
        self.assert_stage("card_draw")

        self.stage_meta = {"card": card, "drawn": drawn}

    def action_card_select(self, card):
        self.assert_stage("card_draw")

        if card not in self.deck:
            raise ReportedException(f"Invalid action. (card '{card}' not in dec)")

        # Remove the selected card from the deck
        self.deck.remove(card)
        if len(self.game["deck"]) == 0:
            self.deck = shuffled_deck()

        # Update Stage -> use_skill
        self.stage = "use_skill"
        self.stage_meta = {}

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

        self.player["status"] = "connected"

    def action_leave(self):
        if self.username not in self.players:
            raise GameException("Player not in game")

        self.players.pop(self.username)

    def action_disconnect(self):
        self.player["status"] = "disconnected"
