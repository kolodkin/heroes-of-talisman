from typing import Literal, Optional

from .models import (
    GamePlay,
    DEFAULT_GAME,
    STAGES_NAMES,
    Player,
    ActivePlayer4,
    Opponent4,
    BATTLE,
    CHARACTER_SELECT,
    KNIGHT,
    MAGE,
    ARCHER,
    init_characters,
)

HEALTH_1 = "health_1"
BATTLE_PLAYER_1_WIN = "battle_player_1_win"
BATTLE_PLAYER_2_WIN = "battle_player_2_win"
BATTLE_DRAW = "battle_draw"
KNIGHT_NOT_ALIVE = "knight_not_alive"
MAGE_NOT_ALIVE = "mage_not_alive"
ARCHER_NOT_ALIVE = "archer_not_alive"
DEBUG_PRESETS = Literal[
    "default",
    "health_1",
    "battle_player_1_win",
    "battle_player_2_win",
    "battle_draw",
    "knight_not_alive",
    "mage_not_alive",
    "archer_not_alive",
]


def set_health_1(game: GamePlay) -> GamePlay:
    ret = game.model_copy(deep=True)
    for player in ret.players.values():
        for character in player.characters.values():
            character.health = 1
    return ret


def create_battle_preset(active: ActivePlayer4, opponent: Opponent4) -> GamePlay:
    """Create a battle preset with two players ready to show results"""
    game = GamePlay(
        stage=BATTLE,
        players={
            active.player: Player(name=active.player, characters=init_characters()),
            opponent.player: Player(name=opponent.player, characters=init_characters()),
        },
        active=active,
        opponent=opponent,
    )
    return game


def get_debug_preset(preset: DEBUG_PRESETS, stage: Optional[STAGES_NAMES] = None) -> GamePlay:
    if preset == "default":
        ret = DEFAULT_GAME.model_copy(deep=True)
    elif preset == "health_1":
        ret = set_health_1(DEFAULT_GAME)
    elif preset == "battle_player_1_win":
        # Player 1: knight (dice=[6], attack=1) = 7
        # Player 2: mage (dice=[3], attack=0) = 3
        # Winner: player1
        ret = create_battle_preset(
            ActivePlayer4(player="player1", character=KNIGHT, dice_roll=[6], winner=True),
            Opponent4(player="player2", character=MAGE, dice_roll=[3], winner=False),
        )
    elif preset == "battle_player_2_win":
        # Player 1: mage (dice=[2], attack=0) = 2
        # Player 2: knight (dice=[5], attack=1) = 6
        # Winner: player2
        ret = create_battle_preset(
            ActivePlayer4(player="player1", character=MAGE, dice_roll=[2], winner=False),
            Opponent4(player="player2", character=KNIGHT, dice_roll=[5], winner=True),
        )
    elif preset == "battle_draw":
        # Player 1: knight (dice=[5], attack=1) = 6
        # Player 2: archer (dice=[6], attack=0) = 6
        # Draw: 6 == 6
        ret = create_battle_preset(
            ActivePlayer4(player="player1", character=KNIGHT, dice_roll=[5], winner=False),
            Opponent4(player="player2", character=ARCHER, dice_roll=[6], winner=False),
        )
    elif preset == "knight_not_alive":
        # Character select stage with knight dead (health=0)
        characters = init_characters()
        characters[KNIGHT].health = 0
        ret = GamePlay(
            stage=CHARACTER_SELECT,
            players={
                "player1": Player(name="player1", characters=characters),
                "player2": Player(name="player2", characters=init_characters()),
            },
        )
    elif preset == "mage_not_alive":
        # Character select stage with mage dead (health=0)
        characters = init_characters()
        characters[MAGE].health = 0
        ret = GamePlay(
            stage=CHARACTER_SELECT,
            players={
                "player1": Player(name="player1", characters=characters),
                "player2": Player(name="player2", characters=init_characters()),
            },
        )
    elif preset == "archer_not_alive":
        # Character select stage with archer dead (health=0)
        characters = init_characters()
        characters[ARCHER].health = 0
        ret = GamePlay(
            stage=CHARACTER_SELECT,
            players={
                "player1": Player(name="player1", characters=characters),
                "player2": Player(name="player2", characters=init_characters()),
            },
        )
    else:
        raise ValueError(f"Invalid preset: {preset}")

    if stage is not None:
        ret.stage = stage

    return ret
