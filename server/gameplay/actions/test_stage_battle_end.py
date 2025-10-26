"""
Tests for Battle End Action.

These tests verify that battle end action correctly handles effects disposal,
health reduction, and stage transitions.
"""

import pytest

from .battle_end import BattleEndAction
from ..models import (
    GamePlay,
    Player,
    ActivePlayer4,
    Opponent4,
    BattleResult,
    GameException,
    ReportedException,
    AttackNegBonusEffect,
    SkipTurnEffect,
    RerollDiceEffect,
    BATTLE_END,
    CHARACTER_SELECT,
    KNIGHT,
    MAGE,
    ARCHER,
    BATTLE_HOWL,
    FREEZE,
    BOUNCING_ARROW,
    init_characters,
)


def test_battle_end_clears_regular_effects():
    """Test that battle_end action clears regular effects from both characters"""
    characters1 = init_characters()
    characters2 = init_characters()

    # Add regular effects to both characters
    characters1[KNIGHT].effects.append(AttackNegBonusEffect(source=BATTLE_HOWL, attack_neg_bonus=-2))
    characters2[MAGE].effects.append(SkipTurnEffect(source=FREEZE, skip_next_turn=True))

    game = GamePlay(
        stage=BATTLE_END,
        active=ActivePlayer4(
            player="player1",
            character=KNIGHT,
            dice_roll=[6],
            result=BattleResult(winner=True, score=7)
        ),
        opponent=Opponent4(
            player="player2",
            character=MAGE,
            dice_roll=[5],
            result=BattleResult(winner=False, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    # Verify effects exist before battle end
    assert len(game.players["player1"].characters[KNIGHT].effects) == 1
    assert len(game.players["player2"].characters[MAGE].effects) == 1

    # Execute battle end action
    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Verify regular effects are cleared from both characters
    assert len(updated_game.players["player1"].characters[KNIGHT].effects) == 0
    assert len(updated_game.players["player2"].characters[MAGE].effects) == 0

    # Verify game transitioned to next turn
    assert updated_game.stage == CHARACTER_SELECT
    assert updated_game.active.player == "player2"  # Next player's turn


def test_battle_end_keeps_unused_use_once_effects():
    """Test that unused UseOnceEffect effects are kept after battle end"""
    characters1 = init_characters()
    characters2 = init_characters()

    # Add unused UseOnceEffect (RerollDiceEffect with used=False)
    unused_reroll = RerollDiceEffect(source=BOUNCING_ARROW, reroll_dice=True, used=False)
    characters1[ARCHER].effects.append(unused_reroll)

    # Add regular effect to opponent
    characters2[KNIGHT].effects.append(AttackNegBonusEffect(source=BATTLE_HOWL, attack_neg_bonus=-2))

    game = GamePlay(
        stage=BATTLE_END,
        active=ActivePlayer4(
            player="player1",
            character=ARCHER,
            dice_roll=[6],
            result=BattleResult(winner=True, score=7)
        ),
        opponent=Opponent4(
            player="player2",
            character=KNIGHT,
            dice_roll=[5],
            result=BattleResult(winner=False, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    # Verify effects exist before battle end
    assert len(game.players["player1"].characters[ARCHER].effects) == 1
    assert len(game.players["player2"].characters[KNIGHT].effects) == 1

    # Execute battle end action
    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Verify unused UseOnceEffect is kept
    assert len(updated_game.players["player1"].characters[ARCHER].effects) == 1
    assert updated_game.players["player1"].characters[ARCHER].effects[0].source == BOUNCING_ARROW
    assert updated_game.players["player1"].characters[ARCHER].effects[0].used is False

    # Verify regular effect is cleared from opponent
    assert len(updated_game.players["player2"].characters[KNIGHT].effects) == 0


def test_battle_end_removes_used_use_once_effects():
    """Test that used UseOnceEffect effects are removed after battle end"""
    characters1 = init_characters()
    characters2 = init_characters()

    # Add used UseOnceEffect (RerollDiceEffect with used=True)
    used_reroll = RerollDiceEffect(source=BOUNCING_ARROW, reroll_dice=True, used=True)
    characters1[ARCHER].effects.append(used_reroll)

    game = GamePlay(
        stage=BATTLE_END,
        active=ActivePlayer4(
            player="player1",
            character=ARCHER,
            dice_roll=[6],
            result=BattleResult(winner=True, score=7)
        ),
        opponent=Opponent4(
            player="player2",
            character=KNIGHT,
            dice_roll=[5],
            result=BattleResult(winner=False, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    # Verify effect exists before battle end
    assert len(game.players["player1"].characters[ARCHER].effects) == 1
    assert game.players["player1"].characters[ARCHER].effects[0].used is True

    # Execute battle end action
    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Verify used UseOnceEffect is removed
    assert len(updated_game.players["player1"].characters[ARCHER].effects) == 0


def test_battle_end_mixed_effects():
    """Test battle end with mix of regular effects, used and unused UseOnceEffects"""
    characters1 = init_characters()

    # Add multiple effects: regular, unused UseOnce, and used UseOnce
    characters1[ARCHER].effects.append(AttackNegBonusEffect(source=BATTLE_HOWL, attack_neg_bonus=-2))
    characters1[ARCHER].effects.append(RerollDiceEffect(source=BOUNCING_ARROW, reroll_dice=True, used=False))
    characters1[ARCHER].effects.append(RerollDiceEffect(source=BOUNCING_ARROW, reroll_dice=True, used=True))

    game = GamePlay(
        stage=BATTLE_END,
        active=ActivePlayer4(
            player="player1",
            character=ARCHER,
            dice_roll=[6],
            result=BattleResult(winner=True, score=7)
        ),
        opponent=Opponent4(
            player="player2",
            character=KNIGHT,
            dice_roll=[5],
            result=BattleResult(winner=False, score=5)
        ),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=init_characters()),
        },
    )

    # Verify 3 effects exist before battle end
    assert len(game.players["player1"].characters[ARCHER].effects) == 3

    # Execute battle end action
    action = BattleEndAction("player1", game)
    updated_game = action.run()

    # Verify only the unused UseOnceEffect remains
    assert len(updated_game.players["player1"].characters[ARCHER].effects) == 1
    assert isinstance(updated_game.players["player1"].characters[ARCHER].effects[0], RerollDiceEffect)
    assert updated_game.players["player1"].characters[ARCHER].effects[0].used is False
