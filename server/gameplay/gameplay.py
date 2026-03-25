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

from .abilities import (
    Ability,
    ABILITIES_MAP,
    AbilityName,
    ABILITY_BATTLE_HOWL,
    ABILITY_BOUNCING_ARROW,
    ABILITY_BOUNCING_ARROW_L2,
    ABILITY_FREEZE,
    ABILITY_DISARM,
)
from .effects import (
    EffectTotal,
    EFFECT_SKIP_TURN,
    EFFECT_NO_DAMAGE_ON_WIN,
    EFFECT_REROLL_DICE,
    AttackBonusEffect,
    AttackNegBonusEffect,
    DefenseBonusEffect,
    RerollDiceEffect,
    DrawCardEffect,
    TalismanEffect,
)

from .cards import CardName, CARDS_MAP, CARD_METAL_ARMOR, CARD_SACRED_SWORD, CARD_GOLDEN_APPLE, CARD_MAGIC_BALL, CARD_DEVILS_FORK, CARD_DARKNESS_RISE, CARD_TALISMAN, CARD_FOG

DEFAULT_CARD_COUNTS: dict[CardName, int] = {
    CARD_METAL_ARMOR: 5,
    CARD_SACRED_SWORD: 5,
    CARD_GOLDEN_APPLE: 5,
    CARD_MAGIC_BALL: 5,
    CARD_DEVILS_FORK: 5,
    CARD_DARKNESS_RISE: 5,
    CARD_TALISMAN: 4,
    CARD_FOG: 5,
}

########################################################
# Deck
########################################################
T = TypeVar("T")


class Deck(StrictModel, Generic[T]):
    """Generic deck for drawing cards with auto-reset when empty"""

    cards: list[T] = Field(default_factory=list)
    card_counts: dict[str, int]

    def draw(self) -> T:
        """Draw top card from deck, auto-reset when empty"""
        # Reset on first draw or when deck reaches 0
        if len(self.cards) == 0:
            self.reset()

        return self.cards.pop(0)

    def reset(self) -> None:
        """Reset deck with shuffled cards based on card_counts"""
        self.cards = []
        for card_name, count in self.card_counts.items():
            self.cards.extend([card_name] * count)
        random.shuffle(self.cards)


class Character(StrictModel):

    level: int
    health: int
    max_health: int
    dice: int
    attack: int
    is_alive: bool = True
    abilities: list[Ability] = Field(default_factory=list)
    active_abilities: list[str] = Field(default_factory=list)
    active_cards: list[str] = Field(default_factory=list)
    effects: list[str] = Field(default_factory=list)
    cards: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def effect(self) -> EffectTotal:
        """Aggregate all active effects by looking up definitions from ABILITIES_MAP and CARDS_MAP"""
        total = EffectTotal()

        # Aggregate effects from active abilities
        for ability_name in self.active_abilities:
            ability = ABILITIES_MAP.get(ability_name)
            if ability:
                for eff in ability.effects:
                    if isinstance(eff, AttackBonusEffect):
                        total.attack_bonus += eff.attack_bonus
                    elif isinstance(eff, AttackNegBonusEffect):
                        total.attack_neg_bonus += eff.attack_neg_bonus
                    elif isinstance(eff, RerollDiceEffect):
                        total.reroll_dice_available = True
                    elif isinstance(eff, DrawCardEffect):
                        total.draw_card_count += eff.draw_count

        # Aggregate effects from active cards
        for card_name in self.active_cards:
            card = CARDS_MAP.get(card_name)
            if card:
                for eff in card.effects:
                    if isinstance(eff, AttackBonusEffect):
                        total.attack_bonus += eff.attack_bonus
                    elif isinstance(eff, DefenseBonusEffect):
                        total.defense_bonus += eff.defense_bonus
                    elif isinstance(eff, TalismanEffect):
                        total.has_talisman = True

        # Aggregate string effects
        for eff_name in self.effects:
            if eff_name == EFFECT_SKIP_TURN:
                total.skip_next_turn = True
            elif eff_name == EFFECT_NO_DAMAGE_ON_WIN:
                total.no_damage_on_win = True
            elif eff_name == EFFECT_REROLL_DICE:
                total.reroll_dice_available = True

        return total

    @computed_field
    @property
    def is_available(self) -> bool:
        """Character is available for selection if alive and not skipping turn"""
        return self.is_alive and not self.effect.skip_next_turn

    def db_model_dump(self) -> dict:
        return self.model_dump(exclude={"effect", "is_available"})


class CharacterSelectMeta(StrictModel):
    """Stage metadata for character selection stage"""

    selected: str  # Currently highlighted character


class CardDrawMeta(StrictModel):
    """Stage metadata for card draw stage"""

    drawn_card: str  # The card that was randomly drawn


class AbilitySelectMeta(StrictModel):
    """Stage metadata for ability selection stage"""

    selected: Optional[str] = None  # Currently highlighted ability (None = no ability selected)


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
    deck: Deck[str] = Field(default_factory=lambda: Deck(card_counts=DEFAULT_CARD_COUNTS, cards=[]))
    players: dict[str, Player] = Field(default_factory=dict)
    active: Optional[ActivePlayer] = None  # The active player and its selections
    card: Optional[str] = None  # Turn-scoped, cleared by rotate_to_next_player
    ability: Optional[AbilityName] = None  # Turn-scoped, cleared by rotate_to_next_player
    ability_opponent: Optional[Opponent2] = None  # Turn-scoped, cleared by rotate_to_next_player
    opponent: Optional[Opponent] = None  # Turn-scoped, cleared by rotate_to_next_player
    stage_meta: Optional[Ability | CharacterSelectMeta | CardDrawMeta | AbilitySelectMeta | Opponent2] = None  # Within-stage, cleared after each press/select

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
KNIGHT_L2_ABILITY = ABILITY_DISARM

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
ARCHER_L2_ABILITY = ABILITY_BOUNCING_ARROW_L2

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
            "abilities": [ABILITIES_MAP[KNIGHT_L2_ABILITY]],
        },
        "archer": {
            "health": ARCHER_L2_DEFAULT_HEALTH,
            "max_health": ARCHER_L2_MAX_HEALTH,
            "dice": ARCHER_L2_DICE,
            "attack": ARCHER_L2_ATTACK,
            "abilities": [ABILITIES_MAP[ARCHER_L2_ABILITY]],
        },
        "mage": {
            "health": MAGE_L2_DEFAULT_HEALTH,
            "max_health": MAGE_L2_MAX_HEALTH,
            "dice": MAGE_L2_DICE,
            "attack": MAGE_L2_ATTACK,
            "abilities": [],
        },
    },
    3: {
        "knight": {
            "health": KNIGHT_L3_DEFAULT_HEALTH,
            "max_health": KNIGHT_L3_MAX_HEALTH,
            "dice": KNIGHT_L3_DICE,
            "attack": KNIGHT_L3_ATTACK,
            "abilities": [],
        },
        "archer": {
            "health": ARCHER_L3_DEFAULT_HEALTH,
            "max_health": ARCHER_L3_MAX_HEALTH,
            "dice": ARCHER_L3_DICE,
            "attack": ARCHER_L3_ATTACK,
            "abilities": [],
        },
        "mage": {
            "health": MAGE_L3_DEFAULT_HEALTH,
            "max_health": MAGE_L3_MAX_HEALTH,
            "dice": MAGE_L3_DICE,
            "attack": MAGE_L3_ATTACK,
            "abilities": [],
        },
    },
    4: {
        "knight": {
            "health": KNIGHT_L4_DEFAULT_HEALTH,
            "max_health": KNIGHT_L4_MAX_HEALTH,
            "dice": KNIGHT_L4_DICE,
            "attack": KNIGHT_L4_ATTACK,
            "abilities": [],
        },
        "archer": {
            "health": ARCHER_L4_DEFAULT_HEALTH,
            "max_health": ARCHER_L4_MAX_HEALTH,
            "dice": ARCHER_L4_DICE,
            "attack": ARCHER_L4_ATTACK,
            "abilities": [],
        },
        "mage": {
            "health": MAGE_L4_DEFAULT_HEALTH,
            "max_health": MAGE_L4_MAX_HEALTH,
            "dice": MAGE_L4_DICE,
            "attack": MAGE_L4_ATTACK,
            "abilities": [],
        },
    },
}

# Backwards compatibility alias
CHARACTER_DEFAULT_STATS = CHARACTER_STATS_BY_LEVEL[1]


def get_abilities_for_level(character_type: ChatacterType, level: int) -> list[Ability]:
    """Get abilities for a character at a given level, falling back to previous levels if none defined."""
    for lvl in range(level, 0, -1):
        abilities = CHARACTER_STATS_BY_LEVEL.get(lvl, {}).get(character_type, {}).get("abilities", [])
        if abilities:
            return abilities
    return []


def init_characters(level: int = 1) -> Dict[ChatacterType, Character]:
    """Initialize all character types with stats based on level"""
    level_stats = CHARACTER_STATS_BY_LEVEL.get(level, CHARACTER_STATS_BY_LEVEL[1])
    return {
        char_type: Character(
            level=level,
            **{**level_stats[char_type], "abilities": get_abilities_for_level(char_type, level)},
        )
        for char_type in [CHARACTER_KNIGHT, CHARACTER_ARCHER, CHARACTER_MAGE]
    }
