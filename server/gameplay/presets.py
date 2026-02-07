from typing import Literal, Optional, get_args

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
    STAGE_ABILITY_SELECTION,
    STAGE_BATTLE_DICE_ROLL,
    STAGE_BATTLE_END,
    STAGE_CARD_DRAW,
    STAGE_CHARACTER_SELECT,
    STAGE_OPPONENT_SELECTION,
    GamePlay,
    DEFAULT_GAME,
    Player,
    ActivePlayer1,
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

PRESET_ABILITY_SELECTION_KNIGHT = "ability_selection_knight"
PRESET_ABILITY_SELECTION_ARCHER = "ability_selection_archer"
PRESET_ABILITY_SELECTION_MAGE = "ability_selection_mage"
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
PRESET_CARD_DRAW_KNIGHT_SACRED_SWORD = "card_draw_knight_sacred_sword"
PRESET_CARD_DRAW_KNIGHT_GOLDEN_APPLE = "card_draw_knight_golden_apple"
PRESET_CARD_DRAW_GOLDEN_APPLE_MAX_HEALTH = "card_draw_golden_apple_max_health"
PRESET_CARD_DRAW_KNIGHT_MAGIC_BALL = "card_draw_knight_magic_ball"
PRESET_CARD_DRAW_KNIGHT_MAGIC_BALL_MAX_LEVEL = "card_draw_knight_magic_ball_max_level"
PRESET_BATTLE_LEVEL_DOWN = "battle_level_down"
PRESET_HEALTH_1 = "health_1"
PRESET_KNIGHT_NOT_ALIVE = "knight_not_alive"
PRESET_EFFECT_ATTACK_BONUS = "effect_attack_bonus"
PRESET_EFFECT_SKIP_TURN = "effect_skip_turn"
PRESET_SKIP_TURN_NO_CHARACTER = "skip_turn_no_character"
PRESET_MAGE_NOT_ALIVE = "mage_not_alive"
PRESET_OPPONENT_SELECTION = "opponent_selection_preset"
PRESET_SINGLE_PLAYER = "single_player"
DebugPresetsType = Literal[
    "default",
    "ability_selection_knight",
    "ability_selection_archer",
    "ability_selection_mage",
    "archer_not_alive",
    "battle_draw",
    "battle_level_down",
    "battle_player_1_win",
    "battle_player_2_win",
    "battle_with_effects",
    "battle_metal_armor",
    "battle_sacred_sword",
    "card_draw_knight_metal_armor",
    "card_draw_archer_sacred_sword",
    "card_draw_knight_sacred_sword",
    "card_draw_knight_golden_apple",
    "card_draw_golden_apple_max_health",
    "card_draw_knight_magic_ball",
    "card_draw_knight_magic_ball_max_level",
    "effect_attack_bonus",
    "effect_reroll",
    "effect_skip_turn",
    "skip_turn_no_character",
    "health_1",
    "knight_not_alive",
    "mage_not_alive",
    "opponent_selection_preset",
    "single_player",
]


DEBUG_PRESETS = list(get_args(DebugPresetsType))


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
    preset: DebugPresetsType,
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
    elif preset == "skip_turn_no_character":
        # No character available for selection:
        # - Knight: dead (health=0)
        # - Archer: dead (health=0)
        # - Mage: has skip_turn effect (from FREEZE)
        # Expected behavior: SKIP_TURN action should be triggered
        # Stage: CHARACTER_SELECT
        characters_p1 = init_characters()
        characters_p1[CHARACTER_KNIGHT].health = 0
        characters_p1[CHARACTER_ARCHER].health = 0
        characters_p1[CHARACTER_MAGE].effects = [
            SkipTurnEffect(source=ABILITY_FREEZE),
        ]

        characters_p2 = init_characters()

        ret = GamePlay(
            stage=STAGE_CHARACTER_SELECT,
            active=ActivePlayer1(player=p1_name),
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
    elif preset == "card_draw_knight_sacred_sword":
        # Knight draws sacred_sword (successful card draw)
        # Card will be applied and added to knight's card list
        from .cards import CARD_SACRED_SWORD

        ret = GamePlay(
            stage=STAGE_CARD_DRAW,
            active=ActivePlayer2(player=p1_name, character=CHARACTER_KNIGHT),
            stage_meta=CardDrawMeta(drawn_card=CARD_SACRED_SWORD),
            players={
                p1_name: Player(name=p1_name, characters=init_characters()),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "card_draw_knight_golden_apple":
        # Knight with 1 health draws golden_apple (heals to 2)
        from .cards import CARD_GOLDEN_APPLE

        characters_p1 = init_characters()
        characters_p1[CHARACTER_KNIGHT].health = 1

        ret = GamePlay(
            stage=STAGE_CARD_DRAW,
            active=ActivePlayer2(player=p1_name, character=CHARACTER_KNIGHT),
            stage_meta=CardDrawMeta(drawn_card=CARD_GOLDEN_APPLE),
            players={
                p1_name: Player(name=p1_name, characters=characters_p1),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "card_draw_golden_apple_max_health":
        # Knight at max health draws golden_apple (health stays at max)
        from .cards import CARD_GOLDEN_APPLE

        ret = GamePlay(
            stage=STAGE_CARD_DRAW,
            active=ActivePlayer2(player=p1_name, character=CHARACTER_KNIGHT),
            stage_meta=CardDrawMeta(drawn_card=CARD_GOLDEN_APPLE),
            players={
                p1_name: Player(name=p1_name, characters=init_characters()),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "card_draw_knight_magic_ball":
        # Knight draws magic_ball (levels up from 1 to 2)
        # Knight L1: health=1 (damaged), max_health=2, dice=1, attack=1
        # After level up: health=3, max_health=3, dice=1, attack=3 (health restored to new max)
        from .cards import CARD_MAGIC_BALL

        characters_p1 = init_characters()
        characters_p1[CHARACTER_KNIGHT].health = 1  # Damaged knight to show health restore on level up

        ret = GamePlay(
            stage=STAGE_CARD_DRAW,
            active=ActivePlayer2(player=p1_name, character=CHARACTER_KNIGHT),
            stage_meta=CardDrawMeta(drawn_card=CARD_MAGIC_BALL),
            players={
                p1_name: Player(name=p1_name, characters=characters_p1),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "card_draw_knight_magic_ball_max_level":
        # Knight at MAX_LEVEL draws magic_ball (no effect)
        # Knight L4: health=4 (damaged), max_health=5, dice=2, attack=3
        # After level up attempt: no change (already at max level)
        from .cards import CARD_MAGIC_BALL

        characters_p1 = init_characters(level=4)
        characters_p1[CHARACTER_KNIGHT].health = 4  # Damaged to verify health is NOT restored

        ret = GamePlay(
            stage=STAGE_CARD_DRAW,
            active=ActivePlayer2(player=p1_name, character=CHARACTER_KNIGHT),
            stage_meta=CardDrawMeta(drawn_card=CARD_MAGIC_BALL),
            players={
                p1_name: Player(name=p1_name, characters=characters_p1),
                p2_name: Player(name=p2_name, characters=init_characters()),
            },
        )
    elif preset == "battle_level_down":
        # Level 2 knight loses battle and should drop to level 1
        # Player 1: knight L2 with 1 health (dice=[2], attack=3) = 5
        # Player 2: mage L1 (dice=[6], attack=0) = 6
        # Result: knight loses (5 < 6), takes 1 damage, health drops to 0
        # Level down triggers: knight becomes L1 (health=2, max_health=2, dice=1, attack=1)
        characters_p1 = init_characters(level=2)  # Start at level 2
        characters_p1[CHARACTER_KNIGHT].health = 1  # Set health to 1 so damage triggers level down

        characters_p2 = init_characters()

        ret = GamePlay(
            stage=STAGE_BATTLE_END,
            active=ActivePlayer4(
                player=p1_name, character=CHARACTER_KNIGHT, dice_roll=[2], result=BattleResult(winner=False, score=5)
            ),
            opponent=Opponent4(
                player=p2_name, character=CHARACTER_MAGE, dice_roll=[6], result=BattleResult(winner=True, score=6)
            ),
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
