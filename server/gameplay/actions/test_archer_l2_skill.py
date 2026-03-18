"""
Tests for Archer Level 2 skill: bouncing_arrow_l2 (חץ קופץ).

Skill description:
  If the archer loses a battle, a rematch is performed twice.
  In the second rematch, the archer does NOT deal damage to the opponent if winning.

Flow:
  1. Archer L2 selects bouncing_arrow_l2 ability
  2. Archer loses → first reroll (normal)
  3. If archer loses first reroll → second reroll available (no-damage on win)
  4. If archer wins second reroll → battle ends, NO damage to opponent
  5. If archer loses second reroll → battle ends, archer loses normally
"""

import pytest

from .stage_battle import RerollEffectAction
from .battle_end import BattleEndAction
from ..common import CHARACTER_KNIGHT, CHARACTER_ARCHER, CHARACTER_MAGE
from ..abilities import ABILITY_BOUNCING_ARROW, ABILITY_BOUNCING_ARROW_L2
from ..effects import EFFECT_NO_DAMAGE_ON_WIN, EFFECT_REROLL_DICE
from ..gameplay import (
    STAGE_BATTLE_DICE_ROLL,
    STAGE_BATTLE_END,
    STAGE_CHARACTER_SELECT,
    GamePlay,
    Player,
    ActivePlayer4,
    Opponent4,
    BattleResult,
    init_characters,
)
from ..presets import (
    get_debug_preset,
    PRESET_ABILITY_SELECTION_ARCHER_L2,
    PRESET_EFFECT_REROLL_L2_FIRST,
    PRESET_EFFECT_REROLL_L2_SECOND,
)


def test_archer_l2_has_two_abilities():
    """Test that archer at level 2 has both bouncing_arrow and bouncing_arrow_l2 abilities"""
    characters = init_characters(level=2)
    archer = characters[CHARACTER_ARCHER]
    ability_names = [a.name for a in archer.abilities]
    assert ABILITY_BOUNCING_ARROW in ability_names
    assert ABILITY_BOUNCING_ARROW_L2 in ability_names


def test_archer_l2_ability_selection_preset():
    """Test that archer L2 ability selection preset has correct setup"""
    game = get_debug_preset(PRESET_ABILITY_SELECTION_ARCHER_L2)
    archer = game.players["player1"].characters[CHARACTER_ARCHER]
    ability_names = [a.name for a in archer.abilities]
    assert ABILITY_BOUNCING_ARROW in ability_names
    assert ABILITY_BOUNCING_ARROW_L2 in ability_names


def test_bouncing_arrow_l2_first_reroll_adds_second_reroll_state():
    """Test that using bouncing_arrow_l2 (first reroll) sets up second reroll with no-damage"""
    characters_p1 = init_characters(level=2)
    characters_p1[CHARACTER_ARCHER].active_abilities = [ABILITY_BOUNCING_ARROW_L2]

    characters_p2 = init_characters()

    game = GamePlay(
        stage=STAGE_BATTLE_DICE_ROLL,
        active=ActivePlayer4(
            player="player1", character=CHARACTER_ARCHER, dice_roll=[2], result=BattleResult(winner=False, score=4)
        ),
        opponent=Opponent4(
            player="player2", character=CHARACTER_MAGE, dice_roll=[5], result=BattleResult(winner=True, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=characters_p2),
        },
    )

    action = RerollEffectAction("player1", game)
    updated_game = action.run()

    archer = updated_game.players["player1"].characters[CHARACTER_ARCHER]

    # bouncing_arrow_l2 should be removed from active_abilities
    assert ABILITY_BOUNCING_ARROW_L2 not in archer.active_abilities

    # Second reroll + no-damage effects should be in effects
    assert EFFECT_REROLL_DICE in archer.effects
    assert EFFECT_NO_DAMAGE_ON_WIN in archer.effects

    # reroll_dice_available should be True (from EFFECT_REROLL_DICE in effects)
    assert archer.effect.reroll_dice_available is True
    assert archer.effect.no_damage_on_win is True


def test_bouncing_arrow_l2_second_reroll_consumes_reroll_keeps_no_damage():
    """Test that second reroll (via EFFECT_REROLL_DICE) removes reroll but keeps no-damage"""
    characters_p1 = init_characters(level=2)
    characters_p1[CHARACTER_ARCHER].effects = [EFFECT_REROLL_DICE, EFFECT_NO_DAMAGE_ON_WIN]

    characters_p2 = init_characters()

    game = GamePlay(
        stage=STAGE_BATTLE_DICE_ROLL,
        active=ActivePlayer4(
            player="player1", character=CHARACTER_ARCHER, dice_roll=[2], result=BattleResult(winner=False, score=4)
        ),
        opponent=Opponent4(
            player="player2", character=CHARACTER_MAGE, dice_roll=[5], result=BattleResult(winner=True, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=characters_p2),
        },
    )

    action = RerollEffectAction("player1", game)
    updated_game = action.run()

    archer = updated_game.players["player1"].characters[CHARACTER_ARCHER]

    # EFFECT_REROLL_DICE should be removed (consumed)
    assert EFFECT_REROLL_DICE not in archer.effects

    # EFFECT_NO_DAMAGE_ON_WIN should still be present (for battle end)
    assert EFFECT_NO_DAMAGE_ON_WIN in archer.effects
    assert archer.effect.no_damage_on_win is True


def test_bouncing_arrow_l2_second_reroll_win_deals_no_damage():
    """Test that when archer wins with no_damage_on_win effect, opponent takes no damage"""
    game = get_debug_preset(PRESET_EFFECT_REROLL_L2_SECOND)

    mage = game.players["player2"].characters[CHARACTER_MAGE]
    original_mage_health = mage.health

    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Archer won but mage should NOT take damage
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == original_mage_health

    # no_damage_on_win effect should be cleared
    archer_after = updated_game.players["player1"].characters[CHARACTER_ARCHER]
    assert EFFECT_NO_DAMAGE_ON_WIN not in archer_after.effects
    assert archer_after.effect.no_damage_on_win is False


def test_bouncing_arrow_l2_second_reroll_lose_deals_normal_damage():
    """Test that when archer loses on second reroll, normal damage is applied to archer"""
    characters_p1 = init_characters(level=2)
    characters_p1[CHARACTER_ARCHER].effects = [EFFECT_NO_DAMAGE_ON_WIN]

    characters_p2 = init_characters()

    game = GamePlay(
        stage=STAGE_BATTLE_END,
        active=ActivePlayer4(
            player="player1", character=CHARACTER_ARCHER, dice_roll=[1], result=BattleResult(winner=False, score=3)
        ),
        opponent=Opponent4(
            player="player2", character=CHARACTER_MAGE, dice_roll=[5], result=BattleResult(winner=True, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=characters_p2),
        },
    )

    archer_before_health = game.players["player1"].characters[CHARACTER_ARCHER].health
    mage_before_health = game.players["player2"].characters[CHARACTER_MAGE].health

    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Archer lost, so archer takes damage
    archer_after = updated_game.players["player1"].characters[CHARACTER_ARCHER]
    assert archer_after.health == archer_before_health - 1

    # Mage should NOT take damage (mage won)
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == mage_before_health

    # no_damage_on_win effect should be cleared
    assert EFFECT_NO_DAMAGE_ON_WIN not in archer_after.effects


def test_bouncing_arrow_l2_effect_reroll_state_gives_reroll_available():
    """Test that EFFECT_REROLL_DICE in character.effects triggers reroll_dice_available"""
    game = get_debug_preset(PRESET_EFFECT_REROLL_L2_FIRST)
    archer = game.players["player1"].characters[CHARACTER_ARCHER]

    # Verify preset setup
    assert EFFECT_REROLL_DICE in archer.effects
    assert EFFECT_NO_DAMAGE_ON_WIN in archer.effects
    assert archer.effect.reroll_dice_available is True
    assert archer.effect.no_damage_on_win is True

    # Game should stay in BATTLE_DICE_ROLL (not transition to BATTLE_END)
    # because loser has reroll available
    assert game.stage == STAGE_BATTLE_DICE_ROLL


def test_bouncing_arrow_l2_win_on_first_reroll_deals_normal_damage():
    """Test that if archer wins on the FIRST reroll, normal damage is applied"""
    characters_p1 = init_characters(level=2)
    characters_p1[CHARACTER_ARCHER].active_abilities = [ABILITY_BOUNCING_ARROW_L2]

    characters_p2 = init_characters()

    # Archer wins the battle (after using first reroll, no no-damage effect yet)
    game = GamePlay(
        stage=STAGE_BATTLE_END,
        active=ActivePlayer4(
            player="player1", character=CHARACTER_ARCHER, dice_roll=[6], result=BattleResult(winner=True, score=8)
        ),
        opponent=Opponent4(
            player="player2", character=CHARACTER_MAGE, dice_roll=[2], result=BattleResult(winner=False, score=2)
        ),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=characters_p2),
        },
    )

    mage_before_health = game.players["player2"].characters[CHARACTER_MAGE].health

    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Mage should take normal damage (no no_damage_on_win effect)
    mage_after = updated_game.players["player2"].characters[CHARACTER_MAGE]
    assert mage_after.health == mage_before_health - 1


def test_bouncing_arrow_l1_still_works_for_archer_l1():
    """Test that the original bouncing_arrow (L1) still works normally after L2 changes"""
    characters_p1 = init_characters()
    characters_p1[CHARACTER_ARCHER].active_abilities = [ABILITY_BOUNCING_ARROW]

    characters_p2 = init_characters()

    game = GamePlay(
        stage=STAGE_BATTLE_DICE_ROLL,
        active=ActivePlayer4(
            player="player1", character=CHARACTER_ARCHER, dice_roll=[2], result=BattleResult(winner=False, score=2)
        ),
        opponent=Opponent4(
            player="player2", character=CHARACTER_MAGE, dice_roll=[5], result=BattleResult(winner=True, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters_p1),
            "player2": Player(name="player2", characters=characters_p2),
        },
    )

    action = RerollEffectAction("player1", game)
    updated_game = action.run()

    archer = updated_game.players["player1"].characters[CHARACTER_ARCHER]

    # bouncing_arrow should be removed
    assert ABILITY_BOUNCING_ARROW not in archer.active_abilities

    # No second reroll state (L1 only has one reroll)
    assert EFFECT_REROLL_DICE not in archer.effects
    assert EFFECT_NO_DAMAGE_ON_WIN not in archer.effects
    assert archer.effect.no_damage_on_win is False
