"""
Tests for ConnectAction.

These tests verify player connection behavior including new connections,
reconnections, game capacity limits, and character initialization.
"""

import pytest

from .connection import ConnectAction, MAX_PLAYERS
from ..common import (
    ReportedException,
    CHARACTER_KNIGHT,
    CHARACTER_ARCHER,
    CHARACTER_MAGE,
    STATUS_CONNECTED,
    STATUS_DISCONNECTED,
)
from ..gameplay import (
    STAGE_CHARACTER_SELECT,
    GamePlay,
    Player,
    Character,
    ActivePlayer1,
    CHARACTER_DEFAULT_STATS,
    ARCHER_L1_ATTACK,
    MAGE_L1_ATTACK,
)


def test_connect_action_new_player():
    """Test connecting a new player to an empty game"""
    game = GamePlay()
    action = ConnectAction("player1", game)

    updated_game = action.run()

    assert "player1" in updated_game.players
    assert updated_game.players["player1"].name == "player1"
    assert updated_game.players["player1"].status == STATUS_CONNECTED
    assert len(updated_game.players["player1"].characters) == 3
    assert CHARACTER_KNIGHT in updated_game.players["player1"].characters
    assert CHARACTER_ARCHER in updated_game.players["player1"].characters
    assert CHARACTER_MAGE in updated_game.players["player1"].characters
    # Verify each character has empty cards list
    assert updated_game.players["player1"].characters[CHARACTER_KNIGHT].cards == []
    assert updated_game.players["player1"].characters[CHARACTER_ARCHER].cards == []
    assert updated_game.players["player1"].characters[CHARACTER_MAGE].cards == []
    assert updated_game.stage == STAGE_CHARACTER_SELECT
    assert updated_game.active.player == "player1"


def test_connect_action_existing_player_reconnect():
    """Test reconnecting an existing player who was disconnected"""
    game = GamePlay()
    knight_char = Character(level=2, **CHARACTER_DEFAULT_STATS[CHARACTER_KNIGHT])
    knight_char.cards = ["talisman"]  # Knight has a card
    game.players["player1"] = Player(
        name="player1",
        status=STATUS_DISCONNECTED,
        characters={
            CHARACTER_KNIGHT: knight_char,
            CHARACTER_ARCHER: Character(level=1, **CHARACTER_DEFAULT_STATS[CHARACTER_ARCHER]),
            CHARACTER_MAGE: Character(level=1, **CHARACTER_DEFAULT_STATS[CHARACTER_MAGE]),
        },
    )

    action = ConnectAction("player1", game)
    updated_game = action.run()

    # Player should be reconnected with their existing data
    assert updated_game.players["player1"].status == STATUS_CONNECTED
    assert updated_game.players["player1"].characters[CHARACTER_KNIGHT].cards == ["talisman"]
    assert updated_game.players["player1"].characters[CHARACTER_KNIGHT].level == 2


def test_connect_action_game_full():
    """Test connecting when game is at maximum capacity"""
    game = GamePlay()

    # Fill game to max capacity
    for i in range(MAX_PLAYERS):
        player_name = f"player{i+1}"
        characters = {}
        for char_type in [CHARACTER_KNIGHT, CHARACTER_ARCHER, CHARACTER_MAGE]:
            characters[char_type] = Character(level=1, **CHARACTER_DEFAULT_STATS[char_type])
        game.players[player_name] = Player(name=player_name, characters=characters)

    action = ConnectAction("player_overflow", game)

    with pytest.raises(ReportedException, match="Game is full"):
        action.run()


def test_connect_action_second_player():
    """Test connecting a second player to a game with one player"""
    game = GamePlay()
    game.stage = STAGE_CHARACTER_SELECT
    game.active = ActivePlayer1(player="player1")
    characters = {}
    for char_type in [CHARACTER_KNIGHT, CHARACTER_ARCHER, CHARACTER_MAGE]:
        characters[char_type] = Character(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", characters=characters)

    action = ConnectAction("player2", game)
    updated_game = action.run()

    assert "player2" in updated_game.players
    assert updated_game.players["player2"].status == STATUS_CONNECTED
    assert updated_game.stage == STAGE_CHARACTER_SELECT
    assert updated_game.active.player == "player1"  # Active player should not change


def test_connect_action_stage_none():
    """Test connecting a player when game stage is None"""
    game = GamePlay()
    game.stage = None  # Explicitly set to None
    action = ConnectAction("player1", game)

    updated_game = action.run()

    assert updated_game.stage == STAGE_CHARACTER_SELECT
    assert updated_game.active.player == "player1"


def test_connect_action_character_stats():
    """Test that connected player gets correct default character stats"""
    game = GamePlay()
    action = ConnectAction("player1", game)

    updated_game = action.run()

    player = updated_game.players["player1"]

    # Check knight stats
    knight = player.characters[CHARACTER_KNIGHT]
    assert knight.level == 1
    assert knight.health == CHARACTER_DEFAULT_STATS[CHARACTER_KNIGHT]["health"]
    assert knight.max_health == CHARACTER_DEFAULT_STATS[CHARACTER_KNIGHT]["max_health"]
    assert knight.dice == CHARACTER_DEFAULT_STATS[CHARACTER_KNIGHT]["dice"]
    assert knight.attack == CHARACTER_DEFAULT_STATS[CHARACTER_KNIGHT]["attack"]

    # Check archer stats (no attack bonus)
    archer = player.characters[CHARACTER_ARCHER]
    assert archer.level == 1
    assert archer.health == CHARACTER_DEFAULT_STATS[CHARACTER_ARCHER]["health"]
    assert archer.max_health == CHARACTER_DEFAULT_STATS[CHARACTER_ARCHER]["max_health"]
    assert archer.dice == CHARACTER_DEFAULT_STATS[CHARACTER_ARCHER]["dice"]
    assert archer.attack == ARCHER_L1_ATTACK

    # Check mage stats (no attack bonus)
    mage = player.characters[CHARACTER_MAGE]
    assert mage.level == 1
    assert mage.health == CHARACTER_DEFAULT_STATS[CHARACTER_MAGE]["health"]
    assert mage.max_health == CHARACTER_DEFAULT_STATS[CHARACTER_MAGE]["max_health"]
    assert mage.dice == CHARACTER_DEFAULT_STATS[CHARACTER_MAGE]["dice"]
    assert mage.attack == MAGE_L1_ATTACK
