"""
Tests for Ability Selection Stage Actions.

These tests verify ability selection behavior including highlighting
selected abilities and confirming selections to transition to:
- ability_opponent_selection (for effects requiring target selection, e.g., FREEZE)
- opponent_selection (for effects applied to battle opponent, e.g., BATTLE_HOWL, BOUNCING_ARROW)
"""

import pytest

from server.game_engine import GameEngine
from ..models import (
    GamePlay,
    Player,
    ActivePlayer2,
    GameException,
    ReportedException,
    RerollDiceEffect,
    ABILITY_SELECTION,
    ABILITY_OPPONENT_SELECTION,
    OPPONENT_SELECTION,
    CHARACTER_SELECT,
    KNIGHT,
    ARCHER,
    MAGE,
    BATTLE_HOWL,
    BOUNCING_ARROW,
    FREEZE,
    REROLL_DICE,
    ABILITY_PRESS,
    ABILITY_SELECT,
    init_characters,
)


def test_ability_press_action_valid():
    """Test pressing an ability highlights it in stage_meta"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(ABILITY_PRESS, ability=BATTLE_HOWL)

    assert game.stage_meta is not None
    assert game.stage_meta.selected == BATTLE_HOWL
    assert game.stage == ABILITY_SELECTION  # Still in ability selection


def test_ability_press_action_not_active_player():
    """Test pressing ability when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    engine = GameEngine("test_game", "player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        engine.run_action(ABILITY_PRESS, ability=BATTLE_HOWL)


def test_ability_press_action_wrong_stage():
    """Test pressing ability in wrong stage raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        engine.run_action(ABILITY_PRESS, ability=BATTLE_HOWL)


def test_ability_press_action_invalid_ability():
    """Test pressing ability not available for character raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    engine = GameEngine("test_game", "player1", game)

    # Knight should have BATTLE_HOWL, not FREEZE (which is for mage)
    with pytest.raises(ReportedException, match="not available for this character"):
        engine.run_action(ABILITY_PRESS, ability=FREEZE)


def test_ability_press_action_archer():
    """Test pressing archer's ability (BOUNCING_ARROW) works correctly"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=ARCHER),
        players={"player1": Player(name="player1", characters=characters)},
    )

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(ABILITY_PRESS, ability=BOUNCING_ARROW)

    assert game.stage_meta is not None
    assert game.stage_meta.selected == BOUNCING_ARROW


def test_ability_press_action_mage():
    """Test pressing mage's ability (FREEZE) works correctly"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=MAGE),
        players={"player1": Player(name="player1", characters=characters)},
    )

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(ABILITY_PRESS, ability=FREEZE)

    assert game.stage_meta is not None
    assert game.stage_meta.selected == FREEZE


def test_ability_select_action_valid():
    """Test confirming ability selection transitions to opponent_selection (for battle opponent effects)"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(ABILITY_SELECT, ability=BATTLE_HOWL)

    # BATTLE_HOWL applies to battle opponent, so skip ability_opponent_selection
    assert game.stage == OPPONENT_SELECTION
    assert game.ability is not None
    assert game.ability.name == BATTLE_HOWL
    assert game.stage_meta is None


def test_ability_select_action_not_active_player():
    """Test confirming ability selection when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    engine = GameEngine("test_game", "player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        engine.run_action(ABILITY_SELECT, ability=BATTLE_HOWL)


def test_ability_select_action_wrong_stage():
    """Test confirming ability selection in wrong stage raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=CHARACTER_SELECT,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        engine.run_action(ABILITY_SELECT, ability=BATTLE_HOWL)


def test_ability_select_action_invalid_ability():
    """Test confirming ability not available for character raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        players={"player1": Player(name="player1", characters=characters)},
    )

    engine = GameEngine("test_game", "player1", game)

    # Knight should have BATTLE_HOWL, not BOUNCING_ARROW (which is for archer)
    with pytest.raises(ReportedException, match="not available for this character"):
        engine.run_action(ABILITY_SELECT, ability=BOUNCING_ARROW)


def test_ability_select_action_archer():
    """Test confirming archer's ability selection skips to opponent_selection"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=ARCHER),
        players={"player1": Player(name="player1", characters=characters)},
    )

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(ABILITY_SELECT, ability=BOUNCING_ARROW)

    # BOUNCING_ARROW applies to self, so skip ability_opponent_selection
    assert game.stage == OPPONENT_SELECTION
    assert game.ability is not None
    assert game.ability.name == BOUNCING_ARROW
    assert game.stage_meta is None


def test_ability_select_action_archer_applies_reroll_effect():
    """Test confirming BOUNCING_ARROW applies RerollDiceEffect to active player's character"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=ARCHER),
        players={"player1": Player(name="player1", characters=characters)},
    )

    # Verify archer has no effects before
    assert len(game.players["player1"].characters[ARCHER].effects) == 0

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(ABILITY_SELECT, ability=BOUNCING_ARROW)

    # Verify RerollDiceEffect was applied to the active player's archer
    archer = game.players["player1"].characters[ARCHER]
    assert len(archer.effects) == 1
    assert isinstance(archer.effects[0], RerollDiceEffect)
    assert archer.effects[0].name == REROLL_DICE
    # Verify the effect is available in effect totals
    assert archer.effect.reroll_dice_available is True


def test_ability_select_action_mage():
    """Test confirming mage's ability selection transitions to ability_opponent_selection"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_SELECTION,
        active=ActivePlayer2(player="player1", character=MAGE),
        players={"player1": Player(name="player1", characters=characters)},
    )

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(ABILITY_SELECT, ability=FREEZE)

    # FREEZE requires opponent selection (SkipTurnEffect), so go to ability_opponent_selection
    assert game.stage == ABILITY_OPPONENT_SELECTION
    assert game.ability is not None
    assert game.ability.name == FREEZE
    assert game.stage_meta is None
