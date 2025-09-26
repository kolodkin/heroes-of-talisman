"""
Tests for ConnectAction.

These tests verify player connection behavior including new connections,
reconnections, game capacity limits, and character initialization.
"""

import pytest

from server.actions.connection import ConnectAction
from server.gameplay.models import (
    GameBoard,
    PlayerModel,
    CharacterModel,
    ReportedException,
    CHARACTER_DEFAULT_STATS,
)
from server.actions.connection import __MAX_PLAYERS__


def test_connect_action_new_player():
    """Test connecting a new player to an empty game"""
    game = GameBoard()
    action = ConnectAction("player1", game)

    updated_game = action.run()

    assert "player1" in updated_game.players
    assert updated_game.players["player1"].name == "player1"
    assert updated_game.players["player1"].status == "connected"
    assert updated_game.players["player1"].cards == []
    assert len(updated_game.players["player1"].characters) == 3
    assert "knight" in updated_game.players["player1"].characters
    assert "archer" in updated_game.players["player1"].characters
    assert "mage" in updated_game.players["player1"].characters
    assert updated_game.stage == "start"  # Default stage remains "start"
    assert updated_game.playing == "player1"


def test_connect_action_existing_player_reconnect():
    """Test reconnecting an existing player who was disconnected"""
    game = GameBoard()
    game.players["player1"] = PlayerModel(
        name="player1",
        status="disconnected",
        cards=["talisman"],
        characters={
            "knight": CharacterModel(level=2, **CHARACTER_DEFAULT_STATS["knight"]),
            "archer": CharacterModel(level=1, **CHARACTER_DEFAULT_STATS["archer"]),
            "mage": CharacterModel(level=1, **CHARACTER_DEFAULT_STATS["mage"]),
        },
    )

    action = ConnectAction("player1", game)
    updated_game = action.run()

    # Player should be reconnected with their existing data
    assert updated_game.players["player1"].status == "connected"
    assert updated_game.players["player1"].cards == ["talisman"]
    assert updated_game.players["player1"].characters["knight"].level == 2


def test_connect_action_game_full():
    """Test connecting when game is at maximum capacity"""
    game = GameBoard()

    # Fill game to max capacity
    for i in range(__MAX_PLAYERS__):
        player_name = f"player{i+1}"
        characters = {}
        for char_type in ["knight", "archer", "mage"]:
            characters[char_type] = CharacterModel(level=1, **CHARACTER_DEFAULT_STATS[char_type])
        game.players[player_name] = PlayerModel(name=player_name, characters=characters)

    action = ConnectAction("player_overflow", game)

    with pytest.raises(ReportedException, match="Game is full"):
        action.run()


def test_connect_action_second_player():
    """Test connecting a second player to a game with one player"""
    game = GameBoard()
    game.stage = "character_select"
    game.playing = "player1"
    characters = {}
    for char_type in ["knight", "archer", "mage"]:
        characters[char_type] = CharacterModel(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = PlayerModel(name="player1", characters=characters)

    action = ConnectAction("player2", game)
    updated_game = action.run()

    assert "player2" in updated_game.players
    assert updated_game.players["player2"].status == "connected"
    assert updated_game.stage == "character_select"
    assert updated_game.playing == "player1"  # Playing player should not change


def test_connect_action_stage_none():
    """Test connecting a player when game stage is None"""
    game = GameBoard()
    game.stage = None  # Explicitly set to None
    action = ConnectAction("player1", game)

    updated_game = action.run()

    assert updated_game.stage == "character_select"
    assert updated_game.playing == "player1"


def test_connect_action_character_stats():
    """Test that connected player gets correct default character stats"""
    game = GameBoard()
    action = ConnectAction("player1", game)

    updated_game = action.run()

    player = updated_game.players["player1"]

    # Check knight stats
    knight = player.characters["knight"]
    assert knight.level == 1
    assert knight.health == CHARACTER_DEFAULT_STATS["knight"]["health"]
    assert knight.max_health == CHARACTER_DEFAULT_STATS["knight"]["max_health"]
    assert knight.dice == CHARACTER_DEFAULT_STATS["knight"]["dice"]
    assert knight.attack == CHARACTER_DEFAULT_STATS["knight"]["attack"]

    # Check archer stats (no attack)
    archer = player.characters["archer"]
    assert archer.level == 1
    assert archer.health == CHARACTER_DEFAULT_STATS["archer"]["health"]
    assert archer.max_health == CHARACTER_DEFAULT_STATS["archer"]["max_health"]
    assert archer.dice == CHARACTER_DEFAULT_STATS["archer"]["dice"]
    assert archer.attack is None

    # Check mage stats (no attack)
    mage = player.characters["mage"]
    assert mage.level == 1
    assert mage.health == CHARACTER_DEFAULT_STATS["mage"]["health"]
    assert mage.max_health == CHARACTER_DEFAULT_STATS["mage"]["max_health"]
    assert mage.dice == CHARACTER_DEFAULT_STATS["mage"]["dice"]
    assert mage.attack is None
