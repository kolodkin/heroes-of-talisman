"""
Tests for Opponent Selection Stage Actions.

These tests verify opponent selection behavior including selecting
opponents and their characters to transition to battle.
"""

import pytest

from server.actions.stage_opponent_selection import OpponentSelectAction
from server.gameplay.models import (
    GamePlay,
    Player,
    CharacterCard,
    GameException,
    ReportedException,
    Opponent,
    CHARACTER_DEFAULT_STATS,
    OPPONENT_SELECTION,
    BATTLE,
    KNIGHT,
    ARCHER,
    MAGE,
)


def test_opponent_select_action_valid():
    """Test selecting opponent and character transitions to battle"""
    game = GamePlay(stage=OPPONENT_SELECTION, playing="player1")
    characters = {}
    for char_type in [KNIGHT, ARCHER, MAGE]:
        characters[char_type] = CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    action = OpponentSelectAction("player1", game)
    updated_game = action.run(opponent="player2", character=KNIGHT)

    assert updated_game.opponent is not None
    assert updated_game.opponent.player == "player2"
    assert updated_game.opponent.character == KNIGHT
    assert updated_game.stage == BATTLE
    assert updated_game.stage_meta is None  # Cleared after transition


def test_opponent_select_action_not_active_player():
    """Test selecting opponent when not active player raises error"""
    game = GamePlay(stage=OPPONENT_SELECTION, playing="player1")
    characters = {}
    for char_type in [KNIGHT, ARCHER, MAGE]:
        characters[char_type] = CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    action = OpponentSelectAction("player2", game)

    with pytest.raises(ReportedException, match="It's not your turn"):
        action.run(opponent="player1", character=KNIGHT)


def test_opponent_select_action_wrong_stage():
    """Test selecting opponent in wrong stage raises error"""
    game = GamePlay(stage=BATTLE, playing="player1")
    characters = {}
    for char_type in [KNIGHT, ARCHER, MAGE]:
        characters[char_type] = CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    action = OpponentSelectAction("player1", game)

    with pytest.raises(GameException, match="Cannot select opponent in stage"):
        action.run(opponent="player2", character=KNIGHT)


def test_opponent_select_action_invalid_opponent():
    """Test selecting non-existent opponent raises error"""
    game = GamePlay(stage=OPPONENT_SELECTION, playing="player1")
    characters = {}
    for char_type in [KNIGHT, ARCHER, MAGE]:
        characters[char_type] = CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", characters=characters)

    action = OpponentSelectAction("player1", game)

    with pytest.raises(ReportedException, match="not in game"):
        action.run(opponent="player2", character=KNIGHT)


def test_opponent_select_action_self_as_opponent():
    """Test selecting self as opponent raises error"""
    game = GamePlay(stage=OPPONENT_SELECTION, playing="player1")
    characters = {}
    for char_type in [KNIGHT, ARCHER, MAGE]:
        characters[char_type] = CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", characters=characters)

    action = OpponentSelectAction("player1", game)

    with pytest.raises(ReportedException, match="Cannot select yourself as opponent"):
        action.run(opponent="player1", character=KNIGHT)


def test_opponent_select_action_invalid_character():
    """Test selecting non-existent character for opponent raises error"""
    game = GamePlay(stage=OPPONENT_SELECTION, playing="player1")
    player1_characters = {
        KNIGHT: CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[KNIGHT])
    }
    player2_characters = {}  # No characters
    game.players["player1"] = Player(name="player1", characters=player1_characters)
    game.players["player2"] = Player(name="player2", characters=player2_characters)

    action = OpponentSelectAction("player1", game)

    with pytest.raises(ReportedException, match="not available for opponent"):
        action.run(opponent="player2", character=KNIGHT)
