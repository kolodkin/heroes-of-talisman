"""
Tests for Ability Opponent Selection Stage Actions.

These tests verify ability opponent selection behavior including highlighting
selected opponents for ability targeting and confirming selections to apply effects.
"""

import pytest

from server.game_engine import GameEngine
from ..models import (
    GamePlay,
    Player,
    ActivePlayer2,
    GameException,
    ReportedException,
    Opponent2,
    ABILITY_OPPONENT_SELECTION,
    OPPONENT_SELECTION,
    KNIGHT,
    MAGE,
    BATTLE_HOWL,
    FREEZE,
    ABILITIES_MAP,
    ABILITY_OPPONENT_PRESS,
    ABILITY_OPPONENT_SELECT,
    init_characters,
)


def test_ability_opponent_press_action_valid():
    """Test pressing opponent's character highlights it in stage_meta"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        ability=ABILITIES_MAP[BATTLE_HOWL],
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(ABILITY_OPPONENT_PRESS, opponent="player2", character=KNIGHT)

    assert game.stage_meta is not None
    assert isinstance(game.stage_meta, Opponent2)
    assert game.stage_meta.player == "player2"
    assert game.stage_meta.character == KNIGHT
    assert game.stage == ABILITY_OPPONENT_SELECTION  # Still in ability opponent selection


def test_ability_opponent_press_action_not_active_player():
    """Test pressing opponent when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        ability=ABILITIES_MAP[BATTLE_HOWL],
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    engine = GameEngine("test_game", "player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        engine.run_action(ABILITY_OPPONENT_PRESS, opponent="player1", character=KNIGHT)


def test_ability_opponent_press_action_wrong_stage():
    """Test pressing opponent in wrong stage raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        ability=ABILITIES_MAP[BATTLE_HOWL],
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        engine.run_action(ABILITY_OPPONENT_PRESS, opponent="player2", character=KNIGHT)


def test_ability_opponent_press_action_invalid_opponent():
    """Test pressing non-existent opponent raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        ability=ABILITIES_MAP[BATTLE_HOWL],
        players={"player1": Player(name="player1", characters=characters)},
    )

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(ReportedException, match="not in game"):
        engine.run_action(ABILITY_OPPONENT_PRESS, opponent="nonexistent", character=KNIGHT)


def test_ability_opponent_press_action_self_as_opponent():
    """Test pressing self as opponent raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        ability=ABILITIES_MAP[BATTLE_HOWL],
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(ReportedException, match="Cannot select yourself as opponent"):
        engine.run_action(ABILITY_OPPONENT_PRESS, opponent="player1", character=KNIGHT)


def test_ability_opponent_press_action_dead_character():
    """Test pressing dead character raises error"""
    characters = init_characters()
    # Kill the knight
    characters[KNIGHT].health = 0
    game = GamePlay(
        stage=ABILITY_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=MAGE),
        ability=ABILITIES_MAP[FREEZE],
        players={
            "player1": Player(name="player1", characters=init_characters()),
            "player2": Player(name="player2", characters=characters),
        },
    )

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(ReportedException, match="is dead and can't be targeted"):
        engine.run_action(ABILITY_OPPONENT_PRESS, opponent="player2", character=KNIGHT)


def test_ability_opponent_select_action_valid():
    """Test confirming ability opponent selection applies effects and transitions to opponent_selection"""
    characters1 = init_characters()
    characters2 = init_characters()
    game = GamePlay(
        stage=ABILITY_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        ability=ABILITIES_MAP[BATTLE_HOWL],
        stage_meta=Opponent2(player="player2", character=KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(ABILITY_OPPONENT_SELECT)

    # Check stage transition
    assert game.stage == OPPONENT_SELECTION
    assert game.stage_meta is None

    # Check ability_opponent is set
    assert game.ability_opponent is not None
    assert game.ability_opponent.player == "player2"
    assert game.ability_opponent.character == KNIGHT

    # Check effects were applied to target character
    target_character = game.players["player2"].characters[KNIGHT]
    assert len(target_character.effects) > 0
    assert target_character.effects[0].source == BATTLE_HOWL


def test_ability_opponent_select_action_not_active_player():
    """Test confirming ability opponent selection when not active player raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        ability=ABILITIES_MAP[BATTLE_HOWL],
        stage_meta=Opponent2(player="player2", character=KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    engine = GameEngine("test_game", "player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        engine.run_action(ABILITY_OPPONENT_SELECT)


def test_ability_opponent_select_action_wrong_stage():
    """Test confirming ability opponent selection in wrong stage raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        ability=ABILITIES_MAP[BATTLE_HOWL],
        stage_meta=Opponent2(player="player2", character=KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        engine.run_action(ABILITY_OPPONENT_SELECT)


def test_ability_opponent_select_action_no_target_selected():
    """Test confirming ability opponent selection without selecting target raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        ability=ABILITIES_MAP[BATTLE_HOWL],
        players={
            "player1": Player(name="player1", characters=characters),
            "player2": Player(name="player2", characters=characters),
        },
    )

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(ReportedException, match="No ability target selected"):
        engine.run_action(ABILITY_OPPONENT_SELECT)


def test_ability_opponent_select_action_dead_character():
    """Test confirming ability opponent selection with dead character raises error"""
    characters1 = init_characters()
    characters2 = init_characters()
    # Kill the target knight
    characters2[KNIGHT].health = 0

    game = GamePlay(
        stage=ABILITY_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=MAGE),
        ability=ABILITIES_MAP[FREEZE],
        stage_meta=Opponent2(player="player2", character=KNIGHT),
        players={
            "player1": Player(name="player1", characters=characters1),
            "player2": Player(name="player2", characters=characters2),
        },
    )

    engine = GameEngine("test_game", "player1", game)

    with pytest.raises(ReportedException, match="is dead and can't be targeted"):
        engine.run_action(ABILITY_OPPONENT_SELECT)
