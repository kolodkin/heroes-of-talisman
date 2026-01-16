"""
Tests for LeaveAction.

These tests verify player leave behavior including removing players
from the game, handling nonexistent players, and edge cases like
the only player leaving.
"""

import pytest

from server.game_engine import GameEngine
from ..models import CONNECT, LEAVE, DISCONNECT
from ..models import (
    GamePlay,
    Player,
    CharacterCard,
    GameException,
    CHARACTER_DEFAULT_STATS,
    KNIGHT,
    ARCHER,
    MAGE,
)


def test_leave_action_existing_player():
    """Test a player leaving the game"""
    game = GamePlay()
    characters = {}
    for char_type in [KNIGHT, ARCHER, MAGE]:
        characters[char_type] = CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", characters=characters)
    game.players["player2"] = Player(name="player2", characters=characters)

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(LEAVE)

    assert "player1" not in game.players
    assert "player2" in game.players  # Other players remain


def test_leave_action_nonexistent_player():
    """Test a player who is not in the game trying to leave"""
    game = GamePlay()
    engine = GameEngine("test_game", "nonexistent_player", game)

    with pytest.raises(GameException, match="Player not in game"):
        engine.run_action(LEAVE)


def test_leave_action_only_player():
    """Test the only player in the game leaving"""
    game = GamePlay()
    characters = {}
    for char_type in [KNIGHT, ARCHER, MAGE]:
        characters[char_type] = CharacterCard(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", characters=characters)

    engine = GameEngine("test_game", "player1", game)
    engine.run_action(LEAVE)

    assert len(game.players) == 0
