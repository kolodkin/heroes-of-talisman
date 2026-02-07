from __future__ import annotations

import random
from typing import Dict, Literal, Optional, TypeVar, Generic

from pydantic import Field, computed_field

from .common import (
    StrictModel,
    ConnectionStatus,
    ChatacterType,
    STATUS_CONNECTED,
    CHARACTER_KNIGHT,
    CHARACTER_ARCHER,
    CHARACTER_MAGE,
)

########################################################
# Stages
########################################################
STAGE_CHARACTER_SELECT = "character_select"
STAGE_CARD_DRAW = "card_draw"
STAGE_ABILITY_SELECTION = "ability_selection"
STAGE_ABILITY_OPPONENT_SELECTION = "ability_opponent_selection"
STAGE_OPPONENT_SELECTION = "opponent_selection"
STAGE_BATTLE_DICE_ROLL = "battle_dice_roll"
STAGE_BATTLE_END = "battle_end"
STAGES_NAMES = [
    STAGE_CHARACTER_SELECT,
    STAGE_CARD_DRAW,
    STAGE_ABILITY_SELECTION,
    STAGE_ABILITY_OPPONENT_SELECTION,
    STAGE_OPPONENT_SELECTION,
    STAGE_BATTLE_DICE_ROLL,
    STAGE_BATTLE_END,
]
StageName = Literal[*STAGES_NAMES]

########################################################
# Deck configuration
########################################################
DECK_SIZE = 10

from .abilities import (
    Ability,
    ABILITIES_MAP,
    AbilityName,
    ABILITY_BATTLE_HOWL,
    ABILITY_BOUNCING_ARROW,
    ABILITY_FREEZE,
)
from .effects import (
    EffectUnion,
    EffectTotal,
    AttackBonusEffect,
    AttackNegBonusEffect,
    DefenseBonusEffect,
    HealEffect,
    LevelUpEffect,
    SkipTurnEffect,
    RerollDiceEffect,
    DrawCardEffect,
)

########################################################
# Deck
########################################################
T = TypeVar("T")


class Deck(StrictModel, Generic[T]):
    """Generic deck for drawing cards with auto-reset when empty"""

    cards: list[T] = Field(default_factory=list)
    size: int

    def draw(self) -> T:
        """Draw top card from deck, auto-reset when empty"""
        # Reset on first draw or when deck reaches 0
        if len(self.cards) == 0:
            self.reset()

        return self.cards.pop(0)

    def reset(self) -> None:
        """Reset deck with shuffled cards (with replacement)"""
        from .cards import CARDS_NAMES

        self.cards = random.choices(CARDS_NAMES, k=self.size)
        random.shuffle(self.cards)


class Character(StrictModel):

    level: int
    health: int
    max_health: int
    dice: int
    attack: int
    abilities: list[Ability] = Field(default_factory=list)
    effects: list[EffectUnion] = Field(default_factory=list)
    cards: list[str] = Field(default_factory=list)

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
            elif isinstance(eff, DefenseBonusEffect):
                total.defense_bonus += eff.defense_bonus
            elif isinstance(eff, SkipTurnEffect):
                total.skip_next_turn = total.skip_next_turn or eff.skip_next_turn
            elif isinstance(eff, RerollDiceEffect):
                total.reroll_dice_available = True
            elif isinstance(eff, DrawCardEffect):
                total.draw_card_count += eff.draw_count
            elif isinstance(eff, HealEffect):
                total.heal_amount += eff.heal_amount
            elif isinstance(eff, LevelUpEffect):
                total.level_up_amount += eff.level_increase

        return total

    def db_model_dump(self) -> dict:
        return self.model_dump(exclude={"is_alive", "effect"})


class CharacterSelectMeta(StrictModel):
    """Stage metadata for character selection stage"""

    selected: str  # Currently highlighted character


class CardDrawMeta(StrictModel):
    """Stage metadata for card draw stage"""

    drawn_card: str  # The card that was randomly drawn


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
    status: ConnectionStatus = STATUS_CONNECTED
    characters: Dict[ChatacterType, Character] = Field(default_factory=dict)


########################################################
# GamePlay model
########################################################
class GamePlay(StrictModel):
    stage: StageName = STAGE_CHARACTER_SELECT
    deck: Deck[str] = Field(default_factory=lambda: Deck(size=DECK_SIZE, cards=[]))
    players: dict[str, Player] = Field(default_factory=dict)
    active: Optional[ActivePlayer] = None  # The active player and its selections
    card: Optional[str] = None  # Selected card from card_draw stage
    ability: Optional[Ability] = None  # Selected ability
    ability_opponent: Optional[Opponent2] = None  # Selected ability opponent
    opponent: Optional[Opponent] = None  # Selected opponent for battle
    stage_meta: Optional[Ability | CharacterSelectMeta | CardDrawMeta | AbilitySelectMeta | Opponent2] = None  # Temporary stage-specific metadata

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
MAX_LEVEL = 4

# Knight Level 1
KNIGHT_L1_DEFAULT_HEALTH = 2
KNIGHT_L1_MAX_HEALTH = 2
KNIGHT_L1_DICE = 1
KNIGHT_L1_ATTACK = 1
KNIGHT_L1_ABILITY = ABILITY_BATTLE_HOWL

# Knight Level 2
KNIGHT_L2_DEFAULT_HEALTH = 3
KNIGHT_L2_MAX_HEALTH = 3
KNIGHT_L2_DICE = 1
KNIGHT_L2_ATTACK = 3

# Knight Level 3
KNIGHT_L3_DEFAULT_HEALTH = 4
KNIGHT_L3_MAX_HEALTH = 4
KNIGHT_L3_DICE = 2
KNIGHT_L3_ATTACK = 1

# Knight Level 4
KNIGHT_L4_DEFAULT_HEALTH = 5
KNIGHT_L4_MAX_HEALTH = 5
KNIGHT_L4_DICE = 2
KNIGHT_L4_ATTACK = 3

# Archer Level 1
ARCHER_L1_DEFAULT_HEALTH = 3
ARCHER_L1_MAX_HEALTH = 3
ARCHER_L1_DICE = 1
ARCHER_L1_ATTACK = 0
ARCHER_L1_ABILITY = ABILITY_BOUNCING_ARROW

# Archer Level 2
ARCHER_L2_DEFAULT_HEALTH = 4
ARCHER_L2_MAX_HEALTH = 4
ARCHER_L2_DICE = 1
ARCHER_L2_ATTACK = 2

# Archer Level 3
ARCHER_L3_DEFAULT_HEALTH = 5
ARCHER_L3_MAX_HEALTH = 5
ARCHER_L3_DICE = 2
ARCHER_L3_ATTACK = 0

# Archer Level 4
ARCHER_L4_DEFAULT_HEALTH = 6
ARCHER_L4_MAX_HEALTH = 6
ARCHER_L4_DICE = 2
ARCHER_L4_ATTACK = 1

# Mage Level 1
MAGE_L1_DEFAULT_HEALTH = 2
MAGE_L1_MAX_HEALTH = 2
MAGE_L1_DICE = 1
MAGE_L1_ATTACK = 0
MAGE_L1_ABILITY = ABILITY_FREEZE

# Mage Level 2
MAGE_L2_DEFAULT_HEALTH = 3
MAGE_L2_MAX_HEALTH = 3
MAGE_L2_DICE = 1
MAGE_L2_ATTACK = 2

# Mage Level 3
MAGE_L3_DEFAULT_HEALTH = 4
MAGE_L3_MAX_HEALTH = 4
MAGE_L3_DICE = 2
MAGE_L3_ATTACK = 0

# Mage Level 4
MAGE_L4_DEFAULT_HEALTH = 5
MAGE_L4_MAX_HEALTH = 5
MAGE_L4_DICE = 2
MAGE_L4_ATTACK = 1

CHARACTER_STATS_BY_LEVEL = {
    1: {
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
    },
    2: {
        "knight": {
            "health": KNIGHT_L2_DEFAULT_HEALTH,
            "max_health": KNIGHT_L2_MAX_HEALTH,
            "dice": KNIGHT_L2_DICE,
            "attack": KNIGHT_L2_ATTACK,
            "abilities": [ABILITIES_MAP[KNIGHT_L1_ABILITY]],
        },
        "archer": {
            "health": ARCHER_L2_DEFAULT_HEALTH,
            "max_health": ARCHER_L2_MAX_HEALTH,
            "dice": ARCHER_L2_DICE,
            "attack": ARCHER_L2_ATTACK,
            "abilities": [ABILITIES_MAP[ARCHER_L1_ABILITY]],
        },
        "mage": {
            "health": MAGE_L2_DEFAULT_HEALTH,
            "max_health": MAGE_L2_MAX_HEALTH,
            "dice": MAGE_L2_DICE,
            "attack": MAGE_L2_ATTACK,
            "abilities": [ABILITIES_MAP[MAGE_L1_ABILITY]],
        },
    },
    3: {
        "knight": {
            "health": KNIGHT_L3_DEFAULT_HEALTH,
            "max_health": KNIGHT_L3_MAX_HEALTH,
            "dice": KNIGHT_L3_DICE,
            "attack": KNIGHT_L3_ATTACK,
            "abilities": [ABILITIES_MAP[KNIGHT_L1_ABILITY]],
        },
        "archer": {
            "health": ARCHER_L3_DEFAULT_HEALTH,
            "max_health": ARCHER_L3_MAX_HEALTH,
            "dice": ARCHER_L3_DICE,
            "attack": ARCHER_L3_ATTACK,
            "abilities": [ABILITIES_MAP[ARCHER_L1_ABILITY]],
        },
        "mage": {
            "health": MAGE_L3_DEFAULT_HEALTH,
            "max_health": MAGE_L3_MAX_HEALTH,
            "dice": MAGE_L3_DICE,
            "attack": MAGE_L3_ATTACK,
            "abilities": [ABILITIES_MAP[MAGE_L1_ABILITY]],
        },
    },
    4: {
        "knight": {
            "health": KNIGHT_L4_DEFAULT_HEALTH,
            "max_health": KNIGHT_L4_MAX_HEALTH,
            "dice": KNIGHT_L4_DICE,
            "attack": KNIGHT_L4_ATTACK,
            "abilities": [ABILITIES_MAP[KNIGHT_L1_ABILITY]],
        },
        "archer": {
            "health": ARCHER_L4_DEFAULT_HEALTH,
            "max_health": ARCHER_L4_MAX_HEALTH,
            "dice": ARCHER_L4_DICE,
            "attack": ARCHER_L4_ATTACK,
            "abilities": [ABILITIES_MAP[ARCHER_L1_ABILITY]],
        },
        "mage": {
            "health": MAGE_L4_DEFAULT_HEALTH,
            "max_health": MAGE_L4_MAX_HEALTH,
            "dice": MAGE_L4_DICE,
            "attack": MAGE_L4_ATTACK,
            "abilities": [ABILITIES_MAP[MAGE_L1_ABILITY]],
        },
    },
}

# Backwards compatibility alias
CHARACTER_DEFAULT_STATS = CHARACTER_STATS_BY_LEVEL[1]


def init_characters(level: int = 1) -> Dict[ChatacterType, Character]:
    """Initialize all character types with stats based on level"""
    level_stats = CHARACTER_STATS_BY_LEVEL.get(level, CHARACTER_STATS_BY_LEVEL[1])
    return {
        char_type: Character(level=level, **level_stats[char_type])
        for char_type in [CHARACTER_KNIGHT, CHARACTER_ARCHER, CHARACTER_MAGE]
    }
