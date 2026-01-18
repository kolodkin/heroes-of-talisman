from typing import Literal, Optional

from .common import KNIGHT, MAGE, ARCHER
from .abilities import BATTLE_HOWL, BOUNCING_ARROW, FREEZE
from .effects import (
    AttackBonusEffect,
    AttackNegBonusEffect,
    SkipTurnEffect,
    RerollDiceEffect,
    DrawCardEffect,
)
from .gameplay import (
    StageName,
    ABILITY_SELECTION,
    BATTLE_DICE_ROLL,
    BATTLE_END,
    CHARACTER_SELECT,
    OPPONENT_SELECTION,
    GamePlay,
    DEFAULT_GAME,
    Player,
    ActivePlayer2,
    ActivePlayer3,
    ActivePlayer4,
    Opponent3,
    Opponent4,
    BattleResult,
    AbilitySelectMeta,
    init_characters,
)

ABILITY_SELECTION_KNIGHT = "ability_selection_knight"
ABILITY_SELECTION_ARCHER = "ability_selection_archer"
ABILITY_SELECTION_MAGE = "ability_selection_mage"
EFFECT_REROLL = "effect_reroll"
ARCHER_NOT_ALIVE = "archer_not_alive"
BATTLE_DRAW = "battle_draw"
BATTLE_PLAYER_1_WIN = "battle_player_1_win"
BATTLE_PLAYER_2_WIN = "battle_player_2_win"
BATTLE_WITH_EFFECTS = "battle_with_effects"
HEALTH_1 = "health_1"
KNIGHT_NOT_ALIVE = "knight_not_alive"
EFFECT_ATTACK_BONUS = "effect_attack_bonus"
EFFECT_SKIP_TURN = "effect_skip_turn"
MAGE_NOT_ALIVE = "mage_not_alive"
OPPONENT_SELECTION_PRESET = "opponent_selection_preset"
SINGLE_PLAYER = "single_player"
DEBUG_PRESETS = Literal[
    "default",
    "ability_selection_knight",
    "ability_selection_archer",
    "ability_selection_mage",
    "archer_not_alive",
    "battle_draw",
    "battle_player_1_win",
    "battle_player_2_win",
    "battle_with_effects",
    "effect_attack_bonus",
    "effect_reroll",
    "effect_skip_turn",
    "health_1",
    "knight_not_alive",
    "mage_not_alive",
    "opponent_selection_preset",
    "single_player",
]


def set_health_1(game: GamePlay) -> GamePlay:
    ret = game.model_copy(deep=True)
    for player in ret.players.values():
        for character in player.characters.values():
            character.health = 1
    return ret


def create_battle_preset(active: ActivePlayer4, opponent: Opponent4, stage: StageName) -> GamePlay:
    """Create a battle preset with two players ready to show results"""
    game = GamePlay(
        stage=stage,
        players={
            active.player: Player(name=active.player, characters=init_characters()),
            opponent.player: Player(name=opponent.player, characters=init_characters()),
        },
        active=active,
        opponent=opponent,
    )
    return game


def get_debug_preset(
    preset: DEBUG_PRESETS,
    stage: Optional[StageName] = None,
    player1_name: Optional[str] = None,
    player2_name: Optional[str] = None,
) -> GamePlay:
    # Use default player names if not provided
    p1_name = player1_name or "player1"
    p2_name = player2_name or "player2"

    if preset == "default":
        ret = DEFAULT_GAME.model_copy(deep=True)
    elif preset == "ability_selection_knight":
        # Ability selection stage - player1 has selected knight
        # Knight has BATTLE_HOWL which does NOT require ability_opponent_selection
        # Single ability is auto-selected
        ret = GamePlay(
            stage=ABILITY_SELECTION,
            active=ActivePlayer2(player=p1_name, character=KNIGHT),
            stage_meta=AbilitySelectMeta(selected=BATTLE_HOWL),
            players={
                p1_name: Player(name=p1_name, characters=init_characters()),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "ability_selection_archer":
        # Ability selection stage - player1 has selected archer
        # Archer has BOUNCING_ARROW which does NOT require ability_opponent_selection
        # Single ability is auto-selected
        ret = GamePlay(
            stage=ABILITY_SELECTION,
            active=ActivePlayer2(player=p1_name, character=ARCHER),
            stage_meta=AbilitySelectMeta(selected=BOUNCING_ARROW),
            players={
                p1_name: Player(name=p1_name, characters=init_characters()),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "ability_selection_mage":
        # Ability selection stage - player1 has selected mage
        # Mage has FREEZE which REQUIRES ability_opponent_selection (SkipTurnEffect)
        # Single ability is auto-selected
        ret = GamePlay(
            stage=ABILITY_SELECTION,
            active=ActivePlayer2(player=p1_name, character=MAGE),
            stage_meta=AbilitySelectMeta(selected=FREEZE),
            players={
                p1_name: Player(name=p1_name, characters=init_characters()),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "health_1":
        ret = set_health_1(DEFAULT_GAME)
    elif preset == "battle_player_1_win":
        # Player 1: knight (dice=[6], attack=1) = 7
        # Player 2: mage (dice=[3], attack=0) = 3
        # Winner: player1
        ret = create_battle_preset(
            ActivePlayer4(player=p1_name, character=KNIGHT, dice_roll=[6], result=BattleResult(winner=True, score=7)),
            Opponent4(player=p2_name, character=MAGE, dice_roll=[3], result=BattleResult(winner=False, score=3)),
            stage=BATTLE_END,
        )
    elif preset == "battle_player_2_win":
        # Player 1: mage (dice=[2], attack=0) = 2
        # Player 2: knight (dice=[5], attack=1) = 6
        # Winner: player2
        ret = create_battle_preset(
            ActivePlayer4(player=p1_name, character=MAGE, dice_roll=[2], result=BattleResult(winner=False, score=2)),
            Opponent4(player=p2_name, character=KNIGHT, dice_roll=[5], result=BattleResult(winner=True, score=6)),
            stage=BATTLE_END,
        )
    elif preset == "battle_draw":
        # Player 1: knight (dice=[5], attack=1) = 6
        # Player 2: archer (dice=[6], attack=0) = 6
        # Draw: 6 == 6
        ret = create_battle_preset(
            ActivePlayer4(
                player=p1_name, character=KNIGHT, dice_roll=[5], result=BattleResult(winner=False, score=6)
            ),
            Opponent4(player=p2_name, character=ARCHER, dice_roll=[6], result=BattleResult(winner=False, score=6)),
            stage=BATTLE_DICE_ROLL,
        )
    elif preset == "knight_not_alive":
        # Character select stage with knight dead (health=0)
        characters = init_characters()
        characters[KNIGHT].health = 0
        ret = GamePlay(
            stage=CHARACTER_SELECT,
            players={
                p1_name: Player(name=p1_name, characters=characters),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "mage_not_alive":
        # Character select stage with mage dead (health=0)
        characters = init_characters()
        characters[MAGE].health = 0
        ret = GamePlay(
            stage=CHARACTER_SELECT,
            players={
                p1_name: Player(name=p1_name, characters=characters),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "archer_not_alive":
        # Character select stage with archer dead (health=0)
        characters = init_characters()
        characters[ARCHER].health = 0
        ret = GamePlay(
            stage=CHARACTER_SELECT,
            players={
                p1_name: Player(name=p1_name, characters=characters),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "opponent_selection_preset":
        # Opponent selection stage - player1 has selected knight
        ret = GamePlay(
            stage=OPPONENT_SELECTION,
            active=ActivePlayer2(player=p1_name, character=KNIGHT),
            players={
                p1_name: Player(name=p1_name, characters=init_characters()),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "single_player":
        # Character select stage with only one player (less than minimum 2 players)
        ret = GamePlay(
            stage=CHARACTER_SELECT,
            players={
                p1_name: Player(name=p1_name, characters=init_characters()),
            },
        )
    elif preset == "battle_with_effects":
        # Battle dice roll stage with effects
        # Player 1: knight with attack_bonus (+2 from BATTLE_HOWL) and reroll_dice (from BOUNCING_ARROW)
        # Player 2: mage with attack_neg_bonus (-2 from BATTLE_HOWL) and skip_turn (from FREEZE)
        characters_p1 = init_characters()
        characters_p1[KNIGHT].effects = [
            AttackBonusEffect(source=BATTLE_HOWL, attack_bonus=2),
            RerollDiceEffect(source=BOUNCING_ARROW),
        ]

        characters_p2 = init_characters()
        characters_p2[MAGE].effects = [
            AttackNegBonusEffect(source=BATTLE_HOWL, attack_neg_bonus=-2),
            SkipTurnEffect(source=FREEZE),
        ]

        ret = GamePlay(
            stage=BATTLE_DICE_ROLL,
            active=ActivePlayer3(player=p1_name, character=KNIGHT, dice_roll=[]),
            opponent=Opponent3(player=p2_name, character=MAGE, dice_roll=[]),
            players={
                p1_name: Player(name=p1_name, characters=characters_p1),
                p2_name: Player(name=p2_name, characters=characters_p2),
            },
        )
    elif preset == "effect_reroll":
        # Archer loses to mage but has Bouncing Arrow effect (reroll dice)
        # Player 1: archer (dice=[2], attack=0) with BOUNCING_ARROW effect (RerollDiceEffect) = 2
        # Player 2: mage (dice=[5], attack=0) = 5
        # Result: archer loses (2 < 5), archer can use Bouncing Arrow to reroll
        # Stage stays BATTLE_DICE_ROLL because loser has reroll effect available
        characters_p1 = init_characters()
        characters_p1[ARCHER].effects = [
            RerollDiceEffect(source=BOUNCING_ARROW),
        ]

        characters_p2 = init_characters()

        ret = GamePlay(
            stage=BATTLE_DICE_ROLL,
            active=ActivePlayer4(
                player=p1_name, character=ARCHER, dice_roll=[2], result=BattleResult(winner=False, score=2)
            ),
            opponent=Opponent4(
                player=p2_name, character=MAGE, dice_roll=[5], result=BattleResult(winner=True, score=5)
            ),
            players={
                p1_name: Player(name=p1_name, characters=characters_p1),
                p2_name: Player(name=p2_name, characters=characters_p2),
            },
        )
    elif preset == "effect_attack_bonus":
        # Battle between 2 knights where one has positive attack bonus causing a draw
        # Player 1: knight with attack_bonus (+2 from BATTLE_HOWL) -> dice=[4] + attack=1 + bonus=2 = 7
        # Player 2: knight with no effects -> dice=[6] + attack=1 = 7
        # Result: Draw (7 == 7)
        characters_p1 = init_characters()
        characters_p1[KNIGHT].effects = [
            AttackBonusEffect(source=BATTLE_HOWL, attack_bonus=2),
        ]

        characters_p2 = init_characters()

        ret = GamePlay(
            stage=BATTLE_DICE_ROLL,
            active=ActivePlayer4(
                player=p1_name, character=KNIGHT, dice_roll=[4], result=BattleResult(winner=False, score=7)
            ),
            opponent=Opponent4(
                player=p2_name, character=KNIGHT, dice_roll=[6], result=BattleResult(winner=False, score=7)
            ),
            players={
                p1_name: Player(name=p1_name, characters=characters_p1),
                p2_name: Player(name=p2_name, characters=characters_p2),
            },
        )
    elif preset == "effect_skip_turn":
        # Knight has skip_turn effect from FREEZE, can't be selected in character select stage
        # Player 1: knight with skip_turn effect (from FREEZE) - can't be selected
        # Player 2: no effects
        # Stage: CHARACTER_SELECT
        characters_p1 = init_characters()
        characters_p1[KNIGHT].effects = [
            SkipTurnEffect(source=FREEZE),
        ]

        characters_p2 = init_characters()

        ret = GamePlay(
            stage=CHARACTER_SELECT,
            players={
                p1_name: Player(name=p1_name, characters=characters_p1),
                p2_name: Player(name=p2_name, characters=characters_p2),
            },
        )
    else:
        raise ValueError(f"Invalid preset: {preset}")

    if stage is not None:
        ret.stage = stage

    return ret
