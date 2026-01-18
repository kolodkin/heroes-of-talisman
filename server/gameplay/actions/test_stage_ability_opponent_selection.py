"""
Tests for Ability Opponent Selection Stage Actions.

These tests verify ability opponent selection behavior including highlighting
selected opponents for ability targeting and confirming selections to apply effects.
"""

import pytest

from .stage_ability_opponent_selection import AbilityOpponentPressAction, AbilityOpponentSelectAction
from ..models import GameException, ReportedException, KNIGHT, MAGE
from ..abilities import BATTLE_HOWL, FREEZE, ABILITIES_MAP
from ..gameplay import (
    ABILITY_OPPONENT_SELECTION,
    OPPONENT_SELECTION,
    GamePlay,
    Player,
    ActivePlayer2,
    Opponent2,
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

    action = AbilityOpponentPressAction("player1", game)
    updated_game = action.run(opponent="player2", character=KNIGHT)

    assert updated_game.stage_meta is not None
    assert isinstance(updated_game.stage_meta, Opponent2)
    assert updated_game.stage_meta.player == "player2"
    assert updated_game.stage_meta.character == KNIGHT
    assert updated_game.stage == ABILITY_OPPONENT_SELECTION  # Still in ability opponent selection


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

    action = AbilityOpponentPressAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run(opponent="player1", character=KNIGHT)


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

    action = AbilityOpponentPressAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run(opponent="player2", character=KNIGHT)


def test_ability_opponent_press_action_invalid_opponent():
    """Test pressing non-existent opponent raises error"""
    characters = init_characters()
    game = GamePlay(
        stage=ABILITY_OPPONENT_SELECTION,
        active=ActivePlayer2(player="player1", character=KNIGHT),
        ability=ABILITIES_MAP[BATTLE_HOWL],
        players={"player1": Player(name="player1", characters=characters)},
    )

    action = AbilityOpponentPressAction("player1", game)

    with pytest.raises(ReportedException, match="not in game"):
        action.run(opponent="nonexistent", character=KNIGHT)


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

    action = AbilityOpponentPressAction("player1", game)

    with pytest.raises(ReportedException, match="Cannot select yourself as opponent"):
        action.run(opponent="player1", character=KNIGHT)


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

    action = AbilityOpponentPressAction("player1", game)

    with pytest.raises(ReportedException, match="is dead and can't be targeted"):
        action.run(opponent="player2", character=KNIGHT)


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

    action = AbilityOpponentSelectAction("player1", game)
    updated_game = action.run()

    # Check stage transition
    assert updated_game.stage == OPPONENT_SELECTION
    assert updated_game.stage_meta is None

    # Check ability_opponent is set
    assert updated_game.ability_opponent is not None
    assert updated_game.ability_opponent.player == "player2"
    assert updated_game.ability_opponent.character == KNIGHT

    # Check effects were applied to target character
    target_character = updated_game.players["player2"].characters[KNIGHT]
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

    action = AbilityOpponentSelectAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run()


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

    action = AbilityOpponentSelectAction("player1", game)

    with pytest.raises(GameException, match="Cannot perform action in stage"):
        action.run()


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

    action = AbilityOpponentSelectAction("player1", game)

    with pytest.raises(ReportedException, match="No ability target selected"):
        action.run()


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

    action = AbilityOpponentSelectAction("player1", game)

    with pytest.raises(ReportedException, match="is dead and can't be targeted"):
        action.run()
