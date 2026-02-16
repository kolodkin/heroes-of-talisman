"""
Tests for Battle End Action.

These tests verify that battle end action correctly handles effects disposal,
health reduction, and stage transitions.

Effect disposal rules:
- BattleEffect (AttackBonusEffect, AttackNegBonusEffect, DrawCardEffect): Always removed at battle end
- RerollDiceEffect: Removed only if used (used=True), kept if unused (used=False)
- SkipTurnEffect: NOT removed at battle end (handled in character_select stage)
"""

import pytest

from .battle_end import BattleEndAction
from ..common import (
    GameException,
    ReportedException,
    CHARACTER_KNIGHT,
    CHARACTER_MAGE,
    CHARACTER_ARCHER,
)
from ..abilities import ABILITY_BATTLE_HOWL, ABILITY_FREEZE, ABILITY_BOUNCING_ARROW
from ..cards import CARD_TALISMAN
from ..gameplay import STAGE_BATTLE_END, STAGE_CHARACTER_SELECT
from ..effects import AttackNegBonusEffect, SkipTurnEffect, RerollDiceEffect, TalismanEffect
from ..gameplay import (
    GamePlay,
    Player,
    ActivePlayer4,
    Opponent4,
    BattleResult,
    init_characters,
)
from ..presets import get_debug_preset, PRESET_BATTLE_TALISMAN_KILL


def test_battle_end_clears_battle_effects():
    """Test that battle_end action clears BattleEffect from characters"""
    characters1 = init_characters()
    characters2 = init_characters()

    # Add BattleEffect to both characters
    characters1[CHARACTER_KNIGHT].effects.append(AttackNegBonusEffect(source=ABILITY_BATTLE_HOWL, attack_neg_bonus=-2))
    characters2[CHARACTER_MAGE].effects.append(AttackNegBonusEffect(source=ABILITY_BATTLE_HOWL, attack_neg_bonus=-1))

    game = GamePlay(
        stage=STAGE_BATTLE_END,
        active=ActivePlayer4(
            player="player1",
            character=CHARACTER_KNIGHT,
            dice_roll=[6],
            result=BattleResult(winner=True, score=7)
        ),
        opponent=Opponent4(
            player="player2",
            character=CHARACTER_MAGE,
            dice_roll=[5],
            result=BattleResult(winner=False, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    # Verify effects exist before battle end
    assert len(game.players["player1"].characters[CHARACTER_KNIGHT].effects) == 1
    assert len(game.players["player2"].characters[CHARACTER_MAGE].effects) == 1

    # Execute battle end action
    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Verify BattleEffects are cleared from both characters
    assert len(updated_game.players["player1"].characters[CHARACTER_KNIGHT].effects) == 0
    assert len(updated_game.players["player2"].characters[CHARACTER_MAGE].effects) == 0

    # Verify game transitioned to next turn
    assert updated_game.stage == STAGE_CHARACTER_SELECT
    assert updated_game.active.player == "player2"  # Next player's turn


def test_battle_end_disposes_reroll_effect():
    """Test that RerollDiceEffect is disposed at battle end"""
    characters1 = init_characters()
    characters2 = init_characters()

    # Add RerollDiceEffect to active player
    characters1[CHARACTER_ARCHER].effects.append(RerollDiceEffect(source=ABILITY_BOUNCING_ARROW, reroll_dice=True))

    # Add BattleEffect to opponent
    characters2[CHARACTER_KNIGHT].effects.append(AttackNegBonusEffect(source=ABILITY_BATTLE_HOWL, attack_neg_bonus=-2))

    game = GamePlay(
        stage=STAGE_BATTLE_END,
        active=ActivePlayer4(
            player="player1",
            character=CHARACTER_ARCHER,
            dice_roll=[6],
            result=BattleResult(winner=True, score=7)
        ),
        opponent=Opponent4(
            player="player2",
            character=CHARACTER_KNIGHT,
            dice_roll=[5],
            result=BattleResult(winner=False, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    # Verify effects exist before battle end
    assert len(game.players["player1"].characters[CHARACTER_ARCHER].effects) == 1
    assert len(game.players["player2"].characters[CHARACTER_KNIGHT].effects) == 1

    # Execute battle end action
    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Verify RerollDiceEffect is disposed (has battle_end in dispose_actions)
    assert len(updated_game.players["player1"].characters[CHARACTER_ARCHER].effects) == 0

    # Verify BattleEffect is cleared from opponent
    assert len(updated_game.players["player2"].characters[CHARACTER_KNIGHT].effects) == 0


def test_battle_end_mixed_effects():
    """Test battle end with mix of battle effects and reroll effects"""
    characters1 = init_characters()

    # Add multiple effects: AttackNegBonusEffect and multiple RerollDiceEffects
    characters1[CHARACTER_ARCHER].effects.append(AttackNegBonusEffect(source=ABILITY_BATTLE_HOWL, attack_neg_bonus=-2))
    characters1[CHARACTER_ARCHER].effects.append(RerollDiceEffect(source=ABILITY_BOUNCING_ARROW, reroll_dice=True))
    characters1[CHARACTER_ARCHER].effects.append(RerollDiceEffect(source=ABILITY_BOUNCING_ARROW, reroll_dice=True))

    game = GamePlay(
        stage=STAGE_BATTLE_END,
        active=ActivePlayer4(
            player="player1",
            character=CHARACTER_ARCHER,
            dice_roll=[6],
            result=BattleResult(winner=True, score=7)
        ),
        opponent=Opponent4(
            player="player2",
            character=CHARACTER_KNIGHT,
            dice_roll=[5],
            result=BattleResult(winner=False, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=init_characters()),
        },
    )

    # Verify 3 effects exist before battle end
    assert len(game.players["player1"].characters[CHARACTER_ARCHER].effects) == 3

    # Execute battle end action
    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Verify all battle_end effects are disposed
    assert len(updated_game.players["player1"].characters[CHARACTER_ARCHER].effects) == 0


def test_battle_end_keeps_skip_turn_effect():
    """Test that SkipTurnEffect is NOT removed at battle end (handled in character_select)"""
    characters1 = init_characters()
    characters2 = init_characters()

    # Add SkipTurnEffect to opponent's mage
    characters2[CHARACTER_MAGE].effects.append(SkipTurnEffect(source=ABILITY_FREEZE, skip_next_turn=True))
    # Add BattleEffect to active character
    characters1[CHARACTER_KNIGHT].effects.append(AttackNegBonusEffect(source=ABILITY_BATTLE_HOWL, attack_neg_bonus=-2))

    game = GamePlay(
        stage=STAGE_BATTLE_END,
        active=ActivePlayer4(
            player="player1",
            character=CHARACTER_KNIGHT,
            dice_roll=[6],
            result=BattleResult(winner=True, score=7)
        ),
        opponent=Opponent4(
            player="player2",
            character=CHARACTER_MAGE,
            dice_roll=[5],
            result=BattleResult(winner=False, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    # Verify effects exist before battle end
    assert len(game.players["player1"].characters[CHARACTER_KNIGHT].effects) == 1
    assert len(game.players["player2"].characters[CHARACTER_MAGE].effects) == 1

    # Execute battle end action
    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Verify BattleEffect is cleared from active character
    assert len(updated_game.players["player1"].characters[CHARACTER_KNIGHT].effects) == 0

    # Verify SkipTurnEffect is kept on opponent's character
    assert len(updated_game.players["player2"].characters[CHARACTER_MAGE].effects) == 1
    assert isinstance(updated_game.players["player2"].characters[CHARACTER_MAGE].effects[0], SkipTurnEffect)


def test_talisman_kills_opponent_at_level2():
    """Test that talisman kills opponent even at level 2+ when health drops to 0"""
    game = get_debug_preset(PRESET_BATTLE_TALISMAN_KILL)

    # Verify preset setup
    knight = game.players["player1"].characters[CHARACTER_KNIGHT]
    mage = game.players["player2"].characters[CHARACTER_MAGE]
    assert knight.effect.has_talisman is True
    assert mage.level == 2
    assert mage.health == 1
    assert mage.is_alive is True

    # Execute battle end
    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Mage should be dead (not level-downed) because of talisman
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == 0
    assert mage_after.is_alive is False
    assert mage_after.level == 2  # Level stays at 2 (no level down, just dead)


def test_talisman_no_kill_when_health_above_zero():
    """Test that talisman doesn't kill if opponent health stays above 0"""
    characters_p1 = init_characters()
    characters_p1[CHARACTER_KNIGHT].effects = [
        TalismanEffect(source=CARD_TALISMAN),
    ]

    characters_p2 = init_characters(level=2)
    # Mage L2 health=3, taking 1 damage goes to 2 (not 0)

    game = GamePlay(
        stage=STAGE_BATTLE_END,
        active=ActivePlayer4(
            player="player1", character=CHARACTER_KNIGHT, dice_roll=[6],
            result=BattleResult(winner=True, score=7)
        ),
        opponent=Opponent4(
            player="player2", character=CHARACTER_MAGE, dice_roll=[2],
            result=BattleResult(winner=False, score=4)
        ),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=characters_p2),
        },
    )

    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Mage takes 1 damage but health stays above 0
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == 2  # 3 - 1 = 2
    assert mage_after.is_alive is True
    assert mage_after.level == 2


def test_talisman_kept_after_battle():
    """Test that talisman effect is NOT disposed at battle end"""
    characters_p1 = init_characters()
    characters_p1[CHARACTER_KNIGHT].effects = [
        TalismanEffect(source=CARD_TALISMAN),
    ]

    game = GamePlay(
        stage=STAGE_BATTLE_END,
        active=ActivePlayer4(
            player="player1", character=CHARACTER_KNIGHT, dice_roll=[6],
            result=BattleResult(winner=True, score=7)
        ),
        opponent=Opponent4(
            player="player2", character=CHARACTER_MAGE, dice_roll=[2],
            result=BattleResult(winner=False, score=2)
        ),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=init_characters()),
        },
    )

    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Talisman should still be on knight (not disposed at battle end)
    knight_after = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert len(knight_after.effects) == 1
    assert isinstance(knight_after.effects[0], TalismanEffect)


def test_level1_death_sets_is_alive_false():
    """Test that level 1 character dying sets is_alive to False"""
    characters_p1 = init_characters()  # Level 1
    characters_p1[CHARACTER_KNIGHT].health = 1  # 1 health, will die

    game = GamePlay(
        stage=STAGE_BATTLE_END,
        active=ActivePlayer4(
            player="player1", character=CHARACTER_KNIGHT, dice_roll=[1],
            result=BattleResult(winner=False, score=2)
        ),
        opponent=Opponent4(
            player="player2", character=CHARACTER_MAGE, dice_roll=[6],
            result=BattleResult(winner=True, score=6)
        ),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=init_characters()),
        },
    )

    action = BattleEndAction("player1", game)
    updated_game = action.run()

    knight_after = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight_after.health == 0
    assert knight_after.is_alive is False


def test_level2_no_talisman_level_down_stays_alive():
    """Test that level 2+ character without talisman opponent levels down and stays alive"""
    characters_p1 = init_characters(level=2)
    characters_p1[CHARACTER_KNIGHT].health = 1  # Will drop to 0

    game = GamePlay(
        stage=STAGE_BATTLE_END,
        active=ActivePlayer4(
            player="player1", character=CHARACTER_KNIGHT, dice_roll=[1],
            result=BattleResult(winner=False, score=4)
        ),
        opponent=Opponent4(
            player="player2", character=CHARACTER_MAGE, dice_roll=[6],
            result=BattleResult(winner=True, score=6)
        ),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=init_characters()),
        },
    )

    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Knight should level down, not die
    knight_after = updated_game.players["player1"].characters[CHARACTER_KNIGHT]
    assert knight_after.level == 1
    assert knight_after.is_alive is True
    assert knight_after.health == knight_after.max_health
