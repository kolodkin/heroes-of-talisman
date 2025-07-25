import random
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


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


class CharacterModel(BaseModel):
    health: int
    level: int
    max_health: int
    skills: Dict[str, Any] = Field(default_factory=dict)
    dice: int
    attack: Optional[int] = None  # Only knight has attack


class PlayerModel(BaseModel):
    status: str = "connected"
    cards: list[str] = Field(default_factory=list)
    characters: Dict[str, CharacterModel] = Field(default_factory=dict)


class GameModel(BaseModel):
    stage: Optional[str] = None
    stage_meta: Optional[Dict[str, Any]] = None
    deck: list[str] = Field(default_factory=shuffled_deck)
    playing: Optional[str] = None
    selected_character: Optional[str] = None
    players: Dict[str, PlayerModel] = Field(default_factory=dict)


__DEFAULT_GAME__ = GameModel()


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


class Action(ABC):
    def __init__(self, user: str, game: GameModel):
        self.user = user
        self.game = game

    # convenience helpers similar to GameEngine properties
    @property
    def players(self):
        return self.game.players

    @property
    def player(self) -> PlayerModel:
        if self.user not in self.players:
            raise GameException("Player not in game")
        return self.players[self.user]

    @property
    def stage(self) -> Optional[str]:
        return self.game.stage

    @stage.setter
    def stage(self, value: Optional[str]):
        self.game.stage = value

    @property
    def stage_meta(self) -> Optional[Dict[str, Any]]:
        return self.game.stage_meta

    @stage_meta.setter
    def stage_meta(self, value: Optional[Dict[str, Any]]):
        self.game.stage_meta = value

    @property
    def selected_character(self) -> Optional[str]:
        return self.game.selected_character

    @selected_character.setter
    def selected_character(self, value: Optional[str]):
        self.game.selected_character = value

    @property
    def deck(self) -> list[str]:
        return self.game.deck

    @deck.setter
    def deck(self, value: list[str]):
        self.game.deck = value

    def assert_stage(self, req_stage: str):
        if self.stage != req_stage:
            raise ReportedException(f"Invalid action. (wrong stage '{self.stage}')")

    @abstractmethod
    def run(self) -> GameModel:
        """Execute the action and return the updated game."""


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

    def action_character_select(self, character: str | None = None):
        return CharacterSelectAction(self.username, self.game).run(character=character)

    def action_character_selected(self, character: str):
        return CharacterSelectedAction(self.username, self.game).run(character=character)

    def action_card_draw(self, card: str | None = None, drawn: bool = False):
        return CardDrawAction(self.username, self.game).run(card=card, drawn=drawn)

    def action_card_select(self, card: str):
        return CardSelectAction(self.username, self.game).run(card=card)

    def action_connect(self):
        return ConnectAction(self.username, self.game).run()

    def action_leave(self):
        return LeaveAction(self.username, self.game).run()

    def action_disconnect(self):
        return DisconnectAction(self.username, self.game).run()


class CharacterSelectAction(Action):
    def run(self, character: Optional[str] = None) -> GameModel:
        self.assert_stage("character_select")

        if character is not None and character not in self.player.characters:
            raise ReportedException("Invalid action. (character not found)")

        self.stage_meta = {"selected": character}
        return self.game


class CharacterSelectedAction(Action):
    def run(self, character: str) -> GameModel:
        self.assert_stage("character_select")

        if character not in self.player.characters:
            raise ReportedException("Invalid action. (character not found)")

        self.selected_character = character
        self.stage = "card_draw"
        selected_card = random.choice(self.deck)
        self.stage_meta = {"card": selected_card, "drawn": False}
        return self.game


class CardDrawAction(Action):
    def run(self, card: Optional[str] = None, drawn: bool = False) -> GameModel:
        self.assert_stage("card_draw")

        self.stage_meta = {"card": card, "drawn": drawn}
        return self.game


class CardSelectAction(Action):
    def run(self, card: str) -> GameModel:
        self.assert_stage("card_draw")

        if card not in self.deck:
            raise ReportedException(f"Invalid action. (card '{card}' not in deck)")

        self.deck.remove(card)
        if len(self.deck) == 0:
            self.deck = shuffled_deck()

        self.stage = "use_skill"
        self.stage_meta = {}
        return self.game


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
        return self.game


class LeaveAction(Action):
    def run(self) -> GameModel:
        if self.user not in self.players:
            raise GameException("Player not in game")

        self.players.pop(self.user)
        return self.game


class DisconnectAction(Action):
    def run(self) -> GameModel:
        self.player.status = "disconnected"
        return self.game


ACTION_MAP: Dict[str, type[Action]] = {
    "character_select": CharacterSelectAction,
    "character_selected": CharacterSelectedAction,
    "card_draw": CardDrawAction,
    "card_select": CardSelectAction,
    "connect": ConnectAction,
    "leave": LeaveAction,
    "disconnect": DisconnectAction,
}
