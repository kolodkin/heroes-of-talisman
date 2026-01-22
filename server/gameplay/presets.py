from typing import Literal, Optional

from .common import CHARACTER_KNIGHT, CHARACTER_MAGE, CHARACTER_ARCHER
from .abilities import ABILITY_BATTLE_HOWL, ABILITY_BOUNCING_ARROW, ABILITY_FREEZE
from .effects import (
    AttackBonusEffect,
    AttackNegBonusEffect,
    DefenseBonusEffect,
    SkipTurnEffect,
    RerollDiceEffect,
    DrawCardEffect,
)
from .gameplay import (
    StageName,
    STAGE_STAGE_ABILITY_SELECTION,
    STAGE_BATTLE_DICE_ROLL,
    STAGE_BATTLE_END,
    STAGE_CARD_DRAW,
    STAGE_CHARACTER_SELECT,
    STAGE_OPPONENT_SELECTION,
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
    CardDrawMeta,
    init_characters,
)

PRESET_STAGE_ABILITY_SELECTION_KNIGHT = "ability_selection_knight"
PRESET_STAGE_ABILITY_SELECTION_ARCHER = "ability_selection_archer"
PRESET_STAGE_ABILITY_SELECTION_MAGE = "ability_selection_mage"
PRESET_EFFECT_REROLL = "effect_reroll"
PRESET_ARCHER_NOT_ALIVE = "archer_not_alive"
PRESET_BATTLE_DRAW = "battle_draw"
PRESET_BATTLE_PLAYER_1_WIN = "battle_player_1_win"
PRESET_BATTLE_PLAYER_2_WIN = "battle_player_2_win"
PRESET_BATTLE_WITH_EFFECTS = "battle_with_effects"
PRESET_BATTLE_METAL_ARMOR = "battle_metal_armor"
PRESET_BATTLE_SACRED_SWORD = "battle_sacred_sword"
PRESET_CARD_DRAW_KNIGHT_METAL_ARMOR = "card_draw_knight_metal_armor"
PRESET_CARD_DRAW_ARCHER_SACRED_SWORD = "card_draw_archer_sacred_sword"
PRESET_HEALTH_1 = "health_1"
PRESET_KNIGHT_NOT_ALIVE = "knight_not_alive"
PRESET_EFFECT_ATTACK_BONUS = "effect_attack_bonus"
PRESET_EFFECT_SKIP_TURN = "effect_skip_turn"
PRESET_MAGE_NOT_ALIVE = "mage_not_alive"
PRESET_OPPONENT_SELECTION = "opponent_selection_preset"
PRESET_SINGLE_PLAYER = "single_player"
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
    "battle_metal_armor",
    "battle_sacred_sword",
    "card_draw_knight_metal_armor",
    "card_draw_archer_sacred_sword",
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
            stage=STAGE_ABILITY_SELECTION,
            active=ActivePlayer2(player=p1_name, character=CHARACTER_KNIGHT),
            stage_meta=AbilitySelectMeta(selected=ABILITY_BATTLE_HOWL),
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
            stage=STAGE_ABILITY_SELECTION,
            active=ActivePlayer2(player=p1_name, character=CHARACTER_ARCHER),
            stage_meta=AbilitySelectMeta(selected=ABILITY_BOUNCING_ARROW),
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
            stage=STAGE_ABILITY_SELECTION,
            active=ActivePlayer2(player=p1_name, character=CHARACTER_MAGE),
            stage_meta=AbilitySelectMeta(selected=ABILITY_FREEZE),
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
            ActivePlayer4(player=p1_name, character=CHARACTER_KNIGHT, dice_roll=[6], result=BattleResult(winner=True, score=7)),
            Opponent4(player=p2_name, character=CHARACTER_MAGE, dice_roll=[3], result=BattleResult(winner=False, score=3)),
            stage=STAGE_BATTLE_END,
        )
    elif preset == "battle_player_2_win":
        # Player 1: mage (dice=[2], attack=0) = 2
        # Player 2: knight (dice=[5], attack=1) = 6
        # Winner: player2
        ret = create_battle_preset(
            ActivePlayer4(player=p1_name, character=CHARACTER_MAGE, dice_roll=[2], result=BattleResult(winner=False, score=2)),
            Opponent4(player=p2_name, character=CHARACTER_KNIGHT, dice_roll=[5], result=BattleResult(winner=True, score=6)),
            stage=STAGE_BATTLE_END,
        )
    elif preset == "battle_draw":
        # Player 1: knight (dice=[5], attack=1) = 6
        # Player 2: archer (dice=[6], attack=0) = 6
        # Draw: 6 == 6
        ret = create_battle_preset(
            ActivePlayer4(
                player=p1_name, character=CHARACTER_KNIGHT, dice_roll=[5], result=BattleResult(winner=False, score=6)
            ),
            Opponent4(player=p2_name, character=CHARACTER_ARCHER, dice_roll=[6], result=BattleResult(winner=False, score=6)),
            stage=STAGE_BATTLE_DICE_ROLL,
        )
    elif preset == "knight_not_alive":
        # Character select stage with knight dead (health=0)
        characters = init_characters()
        characters[CHARACTER_KNIGHT].health = 0
        ret = GamePlay(
            stage=STAGE_CHARACTER_SELECT,
            players={
                p1_name: Player(name=p1_name, characters=characters),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "mage_not_alive":
        # Character select stage with mage dead (health=0)
        characters = init_characters()
        characters[CHARACTER_MAGE].health = 0
        ret = GamePlay(
            stage=STAGE_CHARACTER_SELECT,
            players={
                p1_name: Player(name=p1_name, characters=characters),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "archer_not_alive":
        # Character select stage with archer dead (health=0)
        characters = init_characters()
        characters[CHARACTER_ARCHER].health = 0
        ret = GamePlay(
            stage=STAGE_CHARACTER_SELECT,
            players={
                p1_name: Player(name=p1_name, characters=characters),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "opponent_selection_preset":
        # Opponent selection stage - player1 has selected knight
        ret = GamePlay(
            stage=STAGE_OPPONENT_SELECTION,
            active=ActivePlayer2(player=p1_name, character=CHARACTER_KNIGHT),
            players={
                p1_name: Player(name=p1_name, characters=init_characters()),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "single_player":
        # Character select stage with only one player (less than minimum 2 players)
        ret = GamePlay(
            stage=STAGE_CHARACTER_SELECT,
            players={
                p1_name: Player(name=p1_name, characters=init_characters()),
            },
        )
    elif preset == "battle_with_effects":
        # Battle dice roll stage with effects
        # Player 1: knight with attack_bonus (+2 from BATTLE_HOWL) and reroll_dice (from BOUNCING_ARROW)
        # Player 2: mage with attack_neg_bonus (-2 from BATTLE_HOWL) and skip_turn (from FREEZE)
        characters_p1 = init_characters()
        characters_p1[CHARACTER_KNIGHT].effects = [
            AttackBonusEffect(source=ABILITY_BATTLE_HOWL, attack_bonus=2),
            RerollDiceEffect(source=ABILITY_BOUNCING_ARROW),
        ]

        characters_p2 = init_characters()
        characters_p2[CHARACTER_MAGE].effects = [
            AttackNegBonusEffect(source=ABILITY_BATTLE_HOWL, attack_neg_bonus=-2),
            SkipTurnEffect(source=ABILITY_FREEZE),
        ]

        ret = GamePlay(
            stage=STAGE_BATTLE_DICE_ROLL,
            active=ActivePlayer3(player=p1_name, character=CHARACTER_KNIGHT, dice_roll=[]),
            opponent=Opponent3(player=p2_name, character=CHARACTER_MAGE, dice_roll=[]),
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
        characters_p1[CHARACTER_ARCHER].effects = [
            RerollDiceEffect(source=ABILITY_BOUNCING_ARROW),
        ]

        characters_p2 = init_characters()

        ret = GamePlay(
            stage=STAGE_BATTLE_DICE_ROLL,
            active=ActivePlayer4(
                player=p1_name, character=CHARACTER_ARCHER, dice_roll=[2], result=BattleResult(winner=False, score=2)
            ),
            opponent=Opponent4(
                player=p2_name, character=CHARACTER_MAGE, dice_roll=[5], result=BattleResult(winner=True, score=5)
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
        characters_p1[CHARACTER_KNIGHT].effects = [
            AttackBonusEffect(source=ABILITY_BATTLE_HOWL, attack_bonus=2),
        ]

        characters_p2 = init_characters()

        ret = GamePlay(
            stage=STAGE_BATTLE_DICE_ROLL,
            active=ActivePlayer4(
                player=p1_name, character=CHARACTER_KNIGHT, dice_roll=[4], result=BattleResult(winner=False, score=7)
            ),
            opponent=Opponent4(
                player=p2_name, character=CHARACTER_KNIGHT, dice_roll=[6], result=BattleResult(winner=False, score=7)
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
        characters_p1[CHARACTER_KNIGHT].effects = [
            SkipTurnEffect(source=ABILITY_FREEZE),
        ]

        characters_p2 = init_characters()

        ret = GamePlay(
            stage=STAGE_CHARACTER_SELECT,
            players={
                p1_name: Player(name=p1_name, characters=characters_p1),
                p2_name: Player(name=p2_name, characters=characters_p2),
            },
        )
    elif preset == "battle_metal_armor":
        # Knight with metal_armor loses to mage but takes 0 damage due to +2 defense
        # Player 1: knight (dice=[3], attack=1) with metal_armor (+2 defense) = 4
        # Player 2: mage (dice=[5], attack=0) = 5
        # Result: knight loses (4 < 5) but takes 0 damage (1 - 2 defense = 0)
        from .cards import CARD_METAL_ARMOR

        characters_p1 = init_characters()
        characters_p1[CHARACTER_KNIGHT].effects = [
            DefenseBonusEffect(source=CARD_METAL_ARMOR, defense_bonus=2, dispose_actions=[]),
        ]

        characters_p2 = init_characters()

        ret = GamePlay(
            stage=STAGE_BATTLE_END,
            active=ActivePlayer4(
                player=p1_name, character=CHARACTER_KNIGHT, dice_roll=[3], result=BattleResult(winner=False, score=4)
            ),
            opponent=Opponent4(
                player=p2_name, character=CHARACTER_MAGE, dice_roll=[5], result=BattleResult(winner=True, score=5)
            ),
            players={
                p1_name: Player(name=p1_name, characters=characters_p1),
                p2_name: Player(name=p2_name, characters=characters_p2),
            },
        )
    elif preset == "battle_sacred_sword":
        # Knight with sacred_sword wins against mage
        # Player 1: knight (dice=[2], attack=1, +3 from sacred_sword) = 6
        # Player 2: mage (dice=[5], attack=0) = 5
        # Result: knight wins (6 > 5)
        from .cards import CARD_SACRED_SWORD

        characters_p1 = init_characters()
        characters_p1[CHARACTER_KNIGHT].effects = [
            AttackBonusEffect(source=CARD_SACRED_SWORD, attack_bonus=3, dispose_actions=[]),
        ]

        characters_p2 = init_characters()

        ret = GamePlay(
            stage=STAGE_BATTLE_END,
            active=ActivePlayer4(
                player=p1_name, character=CHARACTER_KNIGHT, dice_roll=[2], result=BattleResult(winner=True, score=6)
            ),
            opponent=Opponent4(
                player=p2_name, character=CHARACTER_MAGE, dice_roll=[5], result=BattleResult(winner=False, score=5)
            ),
            players={
                p1_name: Player(name=p1_name, characters=characters_p1),
                p2_name: Player(name=p2_name, characters=characters_p2),
            },
        )
    elif preset == "card_draw_knight_metal_armor":
        # Knight draws metal_armor (successful card draw)
        # Card will be applied and added to knight's card list
        from .cards import CARD_METAL_ARMOR

        ret = GamePlay(
            stage=STAGE_CARD_DRAW,
            active=ActivePlayer2(player=p1_name, character=CHARACTER_KNIGHT),
            stage_meta=CardDrawMeta(drawn_card=CARD_METAL_ARMOR),
            players={
                p1_name: Player(name=p1_name, characters=init_characters()),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "card_draw_archer_sacred_sword":
        # Archer draws sacred_sword (restricted card)
        # Card will not be applied or added to archer's card list
        from .cards import CARD_SACRED_SWORD

        ret = GamePlay(
            stage=STAGE_CARD_DRAW,
            active=ActivePlayer2(player=p1_name, character=CHARACTER_ARCHER),
            stage_meta=CardDrawMeta(drawn_card=CARD_SACRED_SWORD),
            players={
                p1_name: Player(name=p1_name, characters=init_characters()),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    else:
        raise ValueError(f"Invalid preset: {preset}")

    if stage is not None:
        ret.stage = stage

    return ret
