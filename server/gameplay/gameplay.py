from __future__ import annotations

from typing import Dict, Literal, Optional

from pydantic import Field, computed_field

from .models import (
    StrictModel,
    ConnectionStatus,
    ChatacterType,
    CONNECTED,
    KNIGHT,
    ARCHER,
    MAGE,
)

########################################################
# Stages
########################################################
CHARACTER_SELECT = "character_select"
ABILITY_SELECTION = "ability_selection"
ABILITY_OPPONENT_SELECTION = "ability_opponent_selection"
OPPONENT_SELECTION = "opponent_selection"
BATTLE_DICE_ROLL = "battle_dice_roll"
BATTLE_END = "battle_end"
STAGES_NAMES = [
    CHARACTER_SELECT,
    ABILITY_SELECTION,
    ABILITY_OPPONENT_SELECTION,
    OPPONENT_SELECTION,
    BATTLE_DICE_ROLL,
    BATTLE_END,
]
StageName = Literal[*STAGES_NAMES]

from .abilities import (
    Ability,
    ABILITIES_MAP,
    AbilityName,
    BATTLE_HOWL,
    BOUNCING_ARROW,
    FREEZE,
)
from .effects import (
    EffectUnion,
    EffectTotal,
    AttackBonusEffect,
    AttackNegBonusEffect,
    SkipTurnEffect,
    RerollDiceEffect,
    DrawCardEffect,
)


class Character(StrictModel):

    level: int
    health: int
    max_health: int
    dice: int
    attack: int
    abilities: list[Ability] = Field(default_factory=list)
    effects: list[EffectUnion] = Field(default_factory=list)

    @computed_field
    @property
    def is_alive(self) -> bool:
        """Character is alive if health > 0"""
        return self.health > 0

    @computed_field
    @property
    def effect(self) -> EffectTotal:
        """Aggregate all active effects into a single EffectTotal"""
        total = EffectTotal()

        for eff in self.effects:
            if isinstance(eff, AttackBonusEffect):
                total.attack_bonus += eff.attack_bonus
            elif isinstance(eff, AttackNegBonusEffect):
                total.attack_neg_bonus += eff.attack_neg_bonus
            elif isinstance(eff, SkipTurnEffect):
                total.skip_next_turn = total.skip_next_turn or eff.skip_next_turn
            elif isinstance(eff, RerollDiceEffect):
                total.reroll_dice_available = True
            elif isinstance(eff, DrawCardEffect):
                total.draw_card_count += eff.draw_count

        return total

    def db_model_dump(self) -> dict:
        return self.model_dump(exclude={"is_alive", "effect"})


class CharacterSelectMeta(StrictModel):
    """Stage metadata for character selection stage"""

    selected: str  # Currently highlighted character


class AbilitySelectMeta(StrictModel):
    """Stage metadata for ability selection stage"""

    selected: str  # Currently highlighted ability


class ActivePlayer1(StrictModel):
    """Selected character for battle"""

    player: str  # Character name


class BattleResult(StrictModel):
    winner: bool
    score: int  # result of the battle, sum of dice_roll and attack


class ActivePlayer2(StrictModel):
    player: str
    character: str


class ActivePlayer3(StrictModel):
    player: str
    character: str
    dice_roll: list[int]


class ActivePlayer4(StrictModel):
    player: str
    character: str
    dice_roll: list[int]
    result: BattleResult


ActivePlayer = ActivePlayer1 | ActivePlayer2 | ActivePlayer3 | ActivePlayer4


class Opponent2(StrictModel):
    player: str
    character: str


class Opponent3(StrictModel):
    player: str
    character: str
    dice_roll: list[int]


class Opponent4(StrictModel):
    player: str
    character: str
    dice_roll: list[int]
    result: BattleResult


Opponent = Opponent2 | Opponent3 | Opponent4


class Player(StrictModel):
    name: str
    status: ConnectionStatus = CONNECTED
    cards: list[str] = Field(default_factory=list)
    characters: Dict[ChatacterType, Character] = Field(default_factory=dict)


########################################################
# GamePlay model
########################################################
class GamePlay(StrictModel):
    stage: StageName = CHARACTER_SELECT
    players: dict[str, Player] = Field(default_factory=dict)
    active: Optional[ActivePlayer] = None  # The active player and its selections
    ability: Optional[Ability] = None  # Selected ability
    ability_opponent: Optional[Opponent2] = None  # Selected ability opponent
    opponent: Optional[Opponent] = None  # Selected opponent for battle
    stage_meta: Optional[Ability | CharacterSelectMeta | AbilitySelectMeta | Opponent2] = None  # Temporary stage-specific metadata

    def reorder_players(self, username: str):
        """Reorder players dict in-place with username first (circular shift)"""
        if username not in self.players:
            return

        # Get all player keys
        player_keys = list(self.players.keys())

        # Find the index of the username
        user_index = player_keys.index(username)

        # Circular shift: username first, then the rest
        reordered_keys = player_keys[user_index:] + player_keys[:user_index]

        # Build new dict with reordered keys
        reordered_dict = {key: self.players[key] for key in reordered_keys}

        # Update in-place
        self.players.clear()
        self.players.update(reordered_dict)


DEFAULT_GAME = GamePlay()

########################################################
# Character default stats
########################################################
KNIGHT_L1_DEFAULT_HEALTH = 2
KNIGHT_L1_MAX_HEALTH = 2
KNIGHT_L1_DICE = 1
KNIGHT_L1_ATTACK = 1
KNIGHT_L1_ABILITY = BATTLE_HOWL

ARCHER_L1_DEFAULT_HEALTH = 3
ARCHER_L1_MAX_HEALTH = 3
ARCHER_L1_DICE = 1
ARCHER_L1_ATTACK = 0
ARCHER_L1_ABILITY = BOUNCING_ARROW

MAGE_L1_DEFAULT_HEALTH = 2
MAGE_L1_MAX_HEALTH = 2
MAGE_L1_DICE = 1
MAGE_L1_ATTACK = 0
MAGE_L1_ABILITY = FREEZE

CHARACTER_DEFAULT_STATS = {
    "knight": {
        "health": KNIGHT_L1_DEFAULT_HEALTH,
        "max_health": KNIGHT_L1_MAX_HEALTH,
        "dice": KNIGHT_L1_DICE,
        "attack": KNIGHT_L1_ATTACK,
        "abilities": [ABILITIES_MAP[KNIGHT_L1_ABILITY]],
    },
    "archer": {
        "health": ARCHER_L1_DEFAULT_HEALTH,
        "max_health": ARCHER_L1_MAX_HEALTH,
        "dice": ARCHER_L1_DICE,
        "attack": ARCHER_L1_ATTACK,
        "abilities": [ABILITIES_MAP[ARCHER_L1_ABILITY]],
    },
    "mage": {
        "health": MAGE_L1_DEFAULT_HEALTH,
        "max_health": MAGE_L1_MAX_HEALTH,
        "dice": MAGE_L1_DICE,
        "attack": MAGE_L1_ATTACK,
        "abilities": [ABILITIES_MAP[MAGE_L1_ABILITY]],
    },
}


def init_characters(level: int = 1) -> Dict[ChatacterType, Character]:
    """Initialize all character types with default stats"""
    return {
        char_type: Character(level=level, **CHARACTER_DEFAULT_STATS[char_type])
        for char_type in [KNIGHT, ARCHER, MAGE]
    }
