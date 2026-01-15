"""
Tests for Battle Stage Actions.

These tests verify battle stage actions including dice rolling, reroll on draw,
and winner determination.
"""

import pytest

from .stage_battle import (
    ActivePlayerRollAction,
    OpponentRollAction,
    RerollAction,
    DebugSetBattleDiceRollsAction,
    calculate_winner,
    set_winner_if_both_rolled,
)
from .battle_end import BattleEndAction
from ..models import (
    GamePlay,
    Player,
    ActivePlayer1,
    ActivePlayer2,
    ActivePlayer3,
    ActivePlayer4,
    Opponent2,
    Opponent3,
    Opponent4,
    GameException,
    ReportedException,
    AttackBonusEffect,
    AttackNegBonusEffect,
    SkipTurnEffect,
    RerollDiceEffect,
    BATTLE_DICE_ROLL,
    BATTLE_END,
    CHARACTER_SELECT,
    OPPONENT_SELECTION,
    KNIGHT,
    ARCHER,
    MAGE,
    BATTLE_HOWL,
    BOUNCING_ARROW,
    FREEZE,
    init_characters,
)
from ..presets import get_debug_preset, EFFECT_REROLL


# ============================================================================
# ActivePlayerRollAction Tests
# ============================================================================


def test_active_player_roll_action_valid():
    """Test active player successfully rolls dice"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=Opponent2(player="player2", character=MAGE),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = ActivePlayerRollAction("player1", game)
    updated_game = action.run()

    # Verify active player upgraded to ActivePlayer3 with dice_roll
    assert isinstance(updated_game.active, ActivePlayer3)
    assert updated_game.active.player == "player1"
    assert updated_game.active.character == KNIGHT
    assert updated_game.active.dice_roll is not None
    assert len(updated_game.active.dice_roll) == characters[KNIGHT].dice
    assert all(1 <= d <= 6 for d in updated_game.active.dice_roll)

    # Opponent should still be Opponent2 (hasn't rolled yet)
    assert isinstance(updated_game.opponent, Opponent2)


def test_active_player_roll_triggers_winner_calculation():
    """Test that when active player rolls and opponent already rolled, winner is calculated"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=Opponent3(player="player2", character=MAGE, dice_roll=[3]),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = ActivePlayerRollAction("player1", game)
    updated_game = action.run()

    # Both should be upgraded to Player4/Opponent4 (which have winner fields)
    assert isinstance(updated_game.active, ActivePlayer4)
    assert isinstance(updated_game.opponent, Opponent4)


def test_active_player_roll_wrong_stage():
    """Test active player roll fails in wrong stage"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ActivePlayerRollAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()


def test_active_player_roll_not_active_player():
    """Test active player roll fails when user is not the active player"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=Opponent2(player="player2", character=MAGE),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = ActivePlayerRollAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run()


def test_active_player_roll_player_not_in_game():
    """Test active player roll fails when player doesn't exist in game"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=Opponent2(player="player2", character=MAGE),
        players={
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = ActivePlayerRollAction("player1", game)

    with pytest.raises(GameException, match="Player not in game"):
        action.run()


def test_active_player_roll_no_character():
    """Test active player roll fails when no character selected"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = ActivePlayerRollAction("player1", game)

    with pytest.raises(GameException, match="Active player has no character selected"):
        action.run()


# ============================================================================
# OpponentRollAction Tests
# ============================================================================


def test_opponent_roll_action_valid():
    """Test opponent successfully rolls dice"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=Opponent2(player="player2", character=MAGE),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = OpponentRollAction("player2", game)
    updated_game = action.run()

    # Verify opponent upgraded to Opponent3 with dice_roll
    assert isinstance(updated_game.opponent, Opponent3)
    assert updated_game.opponent.player == "player2"
    assert updated_game.opponent.character == MAGE
    assert updated_game.opponent.dice_roll is not None
    assert len(updated_game.opponent.dice_roll) == characters[MAGE].dice
    assert all(1 <= d <= 6 for d in updated_game.opponent.dice_roll)

    # Active player should still be ActivePlayer2 (hasn't rolled yet)
    assert isinstance(updated_game.active, ActivePlayer2)


def test_opponent_roll_triggers_winner_calculation():
    """Test that when opponent rolls and active already rolled, winner is calculated"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer3(player="player1", character=KNIGHT, dice_roll=[6]),
        opponent=Opponent2(player="player2", character=MAGE),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = OpponentRollAction("player2", game)
    updated_game = action.run()

    # Both should be upgraded to Player4/Opponent4 (which have winner fields)
    assert isinstance(updated_game.active, ActivePlayer4)
    assert isinstance(updated_game.opponent, Opponent4)


def test_opponent_roll_wrong_stage():
    """Test opponent roll fails in wrong stage"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = OpponentRollAction("player2", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()


def test_opponent_roll_not_opponent():
    """Test opponent roll fails when user is not the opponent"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=Opponent2(player="player2", character=MAGE),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = OpponentRollAction("player1", game)

    with pytest.raises(ReportedException, match="You are not the opponent"):
        action.run()


def test_opponent_roll_no_opponent():
    """Test opponent roll fails when no opponent exists"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=None,
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = OpponentRollAction("player2", game)

    with pytest.raises(GameException, match="No opponent selected"):
        action.run()




# ============================================================================
# RerollAction Tests
# ============================================================================


def test_reroll_action_valid_draw():
    """Test reroll successfully resets dice in draw scenario"""
    game = get_debug_preset("battle_draw")

    # Verify initial state is a draw
    assert game.stage == BATTLE_DICE_ROLL
    assert isinstance(game.active, ActivePlayer4)
    assert isinstance(game.opponent, Opponent4)
    assert game.active.result.winner is False
    assert game.opponent.result.winner is False

    action = RerollAction("player1", game)
    updated_game = action.run()

    # Verify both players downgraded to Player2/Opponent2 (no dice_roll, no winner)
    assert isinstance(updated_game.active, ActivePlayer2)
    assert isinstance(updated_game.opponent, Opponent2)
    assert updated_game.active.player == "player1"
    assert updated_game.active.character == KNIGHT
    assert updated_game.opponent.player == "player2"
    assert updated_game.opponent.character == ARCHER


def test_reroll_action_wrong_stage():
    """Test reroll fails in wrong stage"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = RerollAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()


def test_reroll_action_not_active_player():
    """Test reroll fails when user is not the active player"""
    game = get_debug_preset("battle_draw")

    action = RerollAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run()


def test_reroll_action_active_not_rolled():
    """Test reroll fails when active player hasn't rolled yet (not ActivePlayer4)"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=Opponent3(player="player2", character=MAGE, dice_roll=[3]),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = RerollAction("player1", game)

    # RerollAction requires ActivePlayer4/Opponent4 with results, so this fails first
    with pytest.raises(GameException, match="Cannot reroll when winner not determined"):
        action.run()


def test_reroll_action_opponent_not_rolled():
    """Test reroll fails when opponent hasn't rolled yet (not Opponent4)"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer3(player="player1", character=KNIGHT, dice_roll=[6]),
        opponent=Opponent2(player="player2", character=MAGE),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = RerollAction("player1", game)

    # RerollAction requires ActivePlayer4/Opponent4 with results, so this fails first
    with pytest.raises(GameException, match="Cannot reroll when winner not determined"):
        action.run()


def test_reroll_action_winner_exists():
    """Test reroll fails when there's already a winner (stage is BATTLE_END)"""
    game = get_debug_preset("battle_player_1_win")

    # Verify initial state has a winner and is in BATTLE_END stage
    assert game.active.result.winner is True
    assert game.opponent.result.winner is False
    assert game.stage == BATTLE_END

    action = RerollAction("player1", game)

    # Should fail because stage is BATTLE_END, not BATTLE_DICE_ROLL
    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()


def test_reroll_action_winner_not_determined():
    """Test reroll fails when there's a winner (ActivePlayer4/Opponent4 with winner=True)"""
    # Use battle_player_1_win preset but keep stage as BATTLE_DICE_ROLL
    game = get_debug_preset("battle_player_1_win", stage=BATTLE_DICE_ROLL)

    # Verify state: player1 won (knight dice=[6] + attack=1 = 7 > mage dice=[3] = 3)
    assert isinstance(game.active, ActivePlayer4)
    assert isinstance(game.opponent, Opponent4)
    assert game.active.result.winner is True
    assert game.opponent.result.winner is False

    action = RerollAction("player1", game)

    # Should fail because there's a winner (not a draw)
    with pytest.raises(GameException, match="Cannot reroll when there is a winner"):
        action.run()


# ============================================================================
# Helper Function Tests
# ============================================================================


def test_calculate_winner_active_wins():
    """Test calculate_winner when active player wins"""
    game = get_debug_preset("battle_player_1_win")
    active_score, opponent_score = calculate_winner(game)

    # Knight with dice=[6], attack=1 = 7
    # Mage with dice=[3], attack=0 = 3
    assert active_score == 7
    assert opponent_score == 3
    assert active_score > opponent_score


def test_calculate_winner_opponent_wins():
    """Test calculate_winner when opponent wins"""
    game = get_debug_preset("battle_player_2_win")
    active_score, opponent_score = calculate_winner(game)

    # Mage with dice=[2], attack=0 = 2
    # Knight with dice=[5], attack=1 = 6
    assert active_score == 2
    assert opponent_score == 6
    assert opponent_score > active_score


def test_calculate_winner_draw():
    """Test calculate_winner when it's a draw"""
    game = get_debug_preset("battle_draw")
    active_score, opponent_score = calculate_winner(game)

    # Knight with dice=[5], attack=1 = 6
    # Archer with dice=[6], attack=0 = 6
    assert active_score == 6
    assert opponent_score == 6


def test_set_winner_if_both_rolled_upgrades_to_player4():
    """Test set_winner_if_both_rolled upgrades both players to Player4/Opponent4 and transitions to BATTLE_END"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer3(player="player1", character=KNIGHT, dice_roll=[6]),
        opponent=Opponent3(player="player2", character=MAGE, dice_roll=[3]),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    set_winner_if_both_rolled(game)

    # Verify both upgraded with result fields
    assert isinstance(game.active, ActivePlayer4)
    assert isinstance(game.opponent, Opponent4)
    assert game.active.result.winner is True  # 6+1=7 > 3+0=3
    assert game.opponent.result.winner is False
    assert game.active.result.score == 7
    assert game.opponent.result.score == 3
    # Verify stage transitioned to BATTLE_END
    assert game.stage == BATTLE_END


def test_set_winner_if_both_rolled_does_nothing_when_not_both_rolled():
    """Test set_winner_if_both_rolled does nothing when only one player rolled"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer3(player="player1", character=KNIGHT, dice_roll=[6]),
        opponent=Opponent2(player="player2", character=MAGE),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    set_winner_if_both_rolled(game)

    # Should remain unchanged (ActivePlayer3/Opponent2 don't have winner)
    assert isinstance(game.active, ActivePlayer3)
    assert isinstance(game.opponent, Opponent2)


# ============================================================================
# DebugSetBattleDiceRollsAction Tests
# ============================================================================


def test_debug_set_battle_dice_rolls_valid():
    """Test debug action successfully sets dice rolls and recalculates winner"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer3(player="player1", character=KNIGHT, dice_roll=[1]),
        opponent=Opponent3(player="player2", character=MAGE, dice_roll=[6]),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    # Initially knight with dice=[1], attack=1 = 2, mage with dice=[6], attack=0 = 6
    # Mage would win

    action = DebugSetBattleDiceRollsAction("player1", game)
    # Knight has 1 dice, mage has 1 dice
    # Set knight dice to [6], mage dice to [1]
    updated_game = action.run(active_dice_roll=[6], opponent_dice_roll=[1])

    # After debug action: knight with dice=[6], attack=1 = 7, mage with dice=[1], attack=0 = 1
    # Knight should win
    assert isinstance(updated_game.active, ActivePlayer4)
    assert isinstance(updated_game.opponent, Opponent4)
    assert updated_game.active.dice_roll == [6]
    assert updated_game.opponent.dice_roll == [1]
    assert updated_game.active.result.winner is True
    assert updated_game.opponent.result.winner is False
    assert updated_game.active.result.score == 7
    assert updated_game.opponent.result.score == 1


def test_debug_set_battle_dice_rolls_creates_draw():
    """Test debug action can create a draw scenario"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer3(player="player1", character=KNIGHT, dice_roll=[1]),
        opponent=Opponent3(player="player2", character=ARCHER, dice_roll=[1]),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = DebugSetBattleDiceRollsAction("player1", game)
    # Knight has 1 dice, archer has 1 dice
    # Knight with dice=[5], attack=1 = 6, archer with dice=[6], attack=0 = 6
    updated_game = action.run(active_dice_roll=[5], opponent_dice_roll=[6])

    assert isinstance(updated_game.active, ActivePlayer4)
    assert isinstance(updated_game.opponent, Opponent4)
    assert updated_game.active.dice_roll == [5]
    assert updated_game.opponent.dice_roll == [6]
    assert updated_game.active.result.winner is False
    assert updated_game.opponent.result.winner is False
    assert updated_game.active.result.score == 6
    assert updated_game.opponent.result.score == 6


def test_debug_set_battle_dice_rolls_wrong_stage():
    """Test debug action fails in wrong stage"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer1(player="player1"),
        players={
            "player1": Player(name="player1", characters=characters),
        },
    )

    action = DebugSetBattleDiceRollsAction("player1", game)
    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run(active_dice_roll=[6], opponent_dice_roll=[6])


def test_debug_set_battle_dice_rolls_active_not_rolled():
    """Test debug action fails when active player hasn't rolled yet"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        opponent=Opponent3(player="player2", character=MAGE, dice_roll=[3]),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = DebugSetBattleDiceRollsAction("player1", game)
    with pytest.raises(GameException, match="Active player has not rolled yet"):
        action.run(active_dice_roll=[6], opponent_dice_roll=[6])


def test_debug_set_battle_dice_rolls_opponent_not_rolled():
    """Test debug action fails when opponent hasn't rolled yet"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer3(player="player1", character=KNIGHT, dice_roll=[6]),
        opponent=Opponent2(player="player2", character=MAGE),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = DebugSetBattleDiceRollsAction("player1", game)
    with pytest.raises(GameException, match="Opponent has not rolled yet"):
        action.run(active_dice_roll=[6], opponent_dice_roll=[6])


def test_debug_set_battle_dice_rolls_invalid_dice_count():
    """Test debug action fails when dice count doesn't match character dice"""
    characters = init_characters()
    game = GamePlay(
        stage=BATTLE_DICE_ROLL,
        active=ActivePlayer3(player="player1", character=KNIGHT, dice_roll=[1]),
        opponent=Opponent3(player="player2", character=MAGE, dice_roll=[6]),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    action = DebugSetBattleDiceRollsAction("player1", game)
    # Knight has 1 dice but we're passing 2 dice
    with pytest.raises(GameException, match="Active dice roll count 2 does not match character dice 1"):
        action.run(active_dice_roll=[6, 6], opponent_dice_roll=[1])


# ============================================================================
# Effect Action Tests
# ============================================================================


def test_reroll_effect_action():
    """
    Test RerollEffectAction behavior:
    - Removes all RerollDiceEffects from the character
    - Preserves non-RerollDiceEffect effects
    - Resets game state for reroll
    """
    # Use the effect_reroll preset which has archer with RerollDiceEffect
    game = get_debug_preset(EFFECT_REROLL)

    # Add additional effects to test comprehensive behavior:
    # - Second RerollDiceEffect (to test all are removed)
    # - AttackBonusEffect and SkipTurnEffect (to test other effects are preserved)
    active_character = game.players[game.active.player].characters[game.active.character]
    active_character.effects.append(RerollDiceEffect(source=BOUNCING_ARROW))
    active_character.effects.append(AttackBonusEffect(source=BATTLE_HOWL, attack_bonus=2))
    active_character.effects.append(SkipTurnEffect(source=FREEZE))

    # Verify initial state: 4 effects total (1 original + 3 added)
    assert len(active_character.effects) == 4
    reroll_effects_count = sum(1 for eff in active_character.effects if isinstance(eff, RerollDiceEffect))
    assert reroll_effects_count == 2
    assert active_character.effect.reroll_dice_available

    # Verify preset created game state as ActivePlayer4/Opponent4 (both rolled, winner calculated)
    # Archer lost: dice=[2] = 2 < mage dice=[5] = 5
    # Stage stays BATTLE_DICE_ROLL because loser has reroll effect available
    assert isinstance(game.active, ActivePlayer4)
    assert isinstance(game.opponent, Opponent4)
    assert game.active.result.winner is False
    assert game.opponent.result.winner is True
    assert game.stage == BATTLE_DICE_ROLL

    # Perform reroll using RerollEffectAction
    from ..actions import RerollEffectAction

    action = RerollEffectAction("player1", game)
    updated_game = action.run()

    # Verify all RerollDiceEffects are removed, other effects preserved
    active_character_after = updated_game.players[updated_game.active.player].characters[updated_game.active.character]
    assert len(active_character_after.effects) == 2  # Only AttackBonusEffect and SkipTurnEffect

    # Verify no RerollDiceEffects remain
    reroll_effects_after = [eff for eff in active_character_after.effects if isinstance(eff, RerollDiceEffect)]
    assert len(reroll_effects_after) == 0

    # Verify reroll is no longer available
    assert active_character_after.effect.reroll_dice_available is False

    # Verify other effects are preserved
    assert any(isinstance(eff, AttackBonusEffect) for eff in active_character_after.effects)
    assert any(isinstance(eff, SkipTurnEffect) for eff in active_character_after.effects)

    # Verify the game state was reset (reroll happened)
    assert isinstance(updated_game.active, ActivePlayer2)
    assert isinstance(updated_game.opponent, Opponent2)
    assert not hasattr(updated_game.active, "dice_roll")
    assert not hasattr(updated_game.opponent, "dice_roll")
