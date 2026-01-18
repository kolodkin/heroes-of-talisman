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
from ..models import (
    GameException,
    ReportedException,
    KNIGHT,
    MAGE,
    ARCHER,
)
from ..abilities import BATTLE_HOWL, FREEZE, BOUNCING_ARROW
from ..gameplay import BATTLE_END, CHARACTER_SELECT
from ..effects import AttackNegBonusEffect, SkipTurnEffect, RerollDiceEffect
from ..gameplay import (
    GamePlay,
    Player,
    ActivePlayer4,
    Opponent4,
    BattleResult,
    init_characters,
)


def test_battle_end_clears_battle_effects():
    """Test that battle_end action clears BattleEffect from characters"""
    characters1 = init_characters()
    characters2 = init_characters()

    # Add BattleEffect to both characters
    characters1[KNIGHT].effects.append(AttackNegBonusEffect(source=BATTLE_HOWL, attack_neg_bonus=-2))
    characters2[MAGE].effects.append(AttackNegBonusEffect(source=BATTLE_HOWL, attack_neg_bonus=-1))

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

    # Verify BattleEffects are cleared from both characters
    assert len(updated_game.players["player1"].characters[KNIGHT].effects) == 0
    assert len(updated_game.players["player2"].characters[MAGE].effects) == 0

    # Verify game transitioned to next turn
    assert updated_game.stage == CHARACTER_SELECT
    assert updated_game.active.player == "player2"  # Next player's turn


def test_battle_end_disposes_reroll_effect():
    """Test that RerollDiceEffect is disposed at battle end"""
    characters1 = init_characters()
    characters2 = init_characters()

    # Add RerollDiceEffect to active player
    characters1[ARCHER].effects.append(RerollDiceEffect(source=BOUNCING_ARROW, reroll_dice=True))

    # Add BattleEffect to opponent
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

    # Verify RerollDiceEffect is disposed (has battle_end in dispose_actions)
    assert len(updated_game.players["player1"].characters[ARCHER].effects) == 0

    # Verify BattleEffect is cleared from opponent
    assert len(updated_game.players["player2"].characters[KNIGHT].effects) == 0


def test_battle_end_mixed_effects():
    """Test battle end with mix of battle effects and reroll effects"""
    characters1 = init_characters()

    # Add multiple effects: AttackNegBonusEffect and multiple RerollDiceEffects
    characters1[ARCHER].effects.append(AttackNegBonusEffect(source=BATTLE_HOWL, attack_neg_bonus=-2))
    characters1[ARCHER].effects.append(RerollDiceEffect(source=BOUNCING_ARROW, reroll_dice=True))
    characters1[ARCHER].effects.append(RerollDiceEffect(source=BOUNCING_ARROW, reroll_dice=True))

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

    # Verify all battle_end effects are disposed
    assert len(updated_game.players["player1"].characters[ARCHER].effects) == 0


def test_battle_end_keeps_skip_turn_effect():
    """Test that SkipTurnEffect is NOT removed at battle end (handled in character_select)"""
    characters1 = init_characters()
    characters2 = init_characters()

    # Add SkipTurnEffect to opponent's mage
    characters2[MAGE].effects.append(SkipTurnEffect(source=FREEZE, skip_next_turn=True))
    # Add BattleEffect to active character
    characters1[KNIGHT].effects.append(AttackNegBonusEffect(source=BATTLE_HOWL, attack_neg_bonus=-2))

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

    # Verify BattleEffect is cleared from active character
    assert len(updated_game.players["player1"].characters[KNIGHT].effects) == 0

    # Verify SkipTurnEffect is kept on opponent's character
    assert len(updated_game.players["player2"].characters[MAGE].effects) == 1
    assert isinstance(updated_game.players["player2"].characters[MAGE].effects[0], SkipTurnEffect)
