"""
Tests for ConnectAction.

These tests verify player connection behavior including new connections,
reconnections, game capacity limits, and character initialization.
"""

import pytest

from .connection import ConnectAction, MAX_PLAYERS
from ..models import (
    ReportedException,
    CHARACTER_SELECT,
    KNIGHT,
    ARCHER,
    MAGE,
    CONNECTED,
    DISCONNECTED,
)
from ..gameplay import (
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
    assert updated_game.players["player1"].status == CONNECTED
    assert updated_game.players["player1"].cards == []
    assert len(updated_game.players["player1"].characters) == 3
    assert KNIGHT in updated_game.players["player1"].characters
    assert ARCHER in updated_game.players["player1"].characters
    assert MAGE in updated_game.players["player1"].characters
    assert updated_game.stage == CHARACTER_SELECT
    assert updated_game.active.player == "player1"


def test_connect_action_existing_player_reconnect():
    """Test reconnecting an existing player who was disconnected"""
    game = GamePlay()
    game.players["player1"] = Player(
        name="player1",
        status=DISCONNECTED,
        cards=["talisman"],
        characters={
            KNIGHT: Character(level=2, **CHARACTER_DEFAULT_STATS[KNIGHT]),
            ARCHER: Character(level=1, **CHARACTER_DEFAULT_STATS[ARCHER]),
            MAGE: Character(level=1, **CHARACTER_DEFAULT_STATS[MAGE]),
        },
    )

    action = ConnectAction("player1", game)
    updated_game = action.run()

    # Player should be reconnected with their existing data
    assert updated_game.players["player1"].status == CONNECTED
    assert updated_game.players["player1"].cards == ["talisman"]
    assert updated_game.players["player1"].characters[KNIGHT].level == 2


def test_connect_action_game_full():
    """Test connecting when game is at maximum capacity"""
    game = GamePlay()

    # Fill game to max capacity
    for i in range(MAX_PLAYERS):
        player_name = f"player{i+1}"
        characters = {}
        for char_type in [KNIGHT, ARCHER, MAGE]:
            characters[char_type] = Character(level=1, **CHARACTER_DEFAULT_STATS[char_type])
        game.players[player_name] = Player(name=player_name, characters=characters)

    action = ConnectAction("player_overflow", game)

    with pytest.raises(ReportedException, match="Game is full"):
        action.run()


def test_connect_action_second_player():
    """Test connecting a second player to a game with one player"""
    game = GamePlay()
    game.stage = CHARACTER_SELECT
    game.active = ActivePlayer1(player="player1")
    characters = {}
    for char_type in [KNIGHT, ARCHER, MAGE]:
        characters[char_type] = Character(level=1, **CHARACTER_DEFAULT_STATS[char_type])
    game.players["player1"] = Player(name="player1", characters=characters)

    action = ConnectAction("player2", game)
    updated_game = action.run()

    assert "player2" in updated_game.players
    assert updated_game.players["player2"].status == CONNECTED
    assert updated_game.stage == CHARACTER_SELECT
    assert updated_game.active.player == "player1"  # Active player should not change


def test_connect_action_stage_none():
    """Test connecting a player when game stage is None"""
    game = GamePlay()
    game.stage = None  # Explicitly set to None
    action = ConnectAction("player1", game)

    updated_game = action.run()

    assert updated_game.stage == CHARACTER_SELECT
    assert updated_game.active.player == "player1"


def test_connect_action_character_stats():
    """Test that connected player gets correct default character stats"""
    game = GamePlay()
    action = ConnectAction("player1", game)

    updated_game = action.run()

    player = updated_game.players["player1"]

    # Check knight stats
    knight = player.characters[KNIGHT]
    assert knight.level == 1
    assert knight.health == CHARACTER_DEFAULT_STATS[KNIGHT]["health"]
    assert knight.max_health == CHARACTER_DEFAULT_STATS[KNIGHT]["max_health"]
    assert knight.dice == CHARACTER_DEFAULT_STATS[KNIGHT]["dice"]
    assert knight.attack == CHARACTER_DEFAULT_STATS[KNIGHT]["attack"]

    # Check archer stats (no attack bonus)
    archer = player.characters[ARCHER]
    assert archer.level == 1
    assert archer.health == CHARACTER_DEFAULT_STATS[ARCHER]["health"]
    assert archer.max_health == CHARACTER_DEFAULT_STATS[ARCHER]["max_health"]
    assert archer.dice == CHARACTER_DEFAULT_STATS[ARCHER]["dice"]
    assert archer.attack == ARCHER_L1_ATTACK

    # Check mage stats (no attack bonus)
    mage = player.characters[MAGE]
    assert mage.level == 1
    assert mage.health == CHARACTER_DEFAULT_STATS[MAGE]["health"]
    assert mage.max_health == CHARACTER_DEFAULT_STATS[MAGE]["max_health"]
    assert mage.dice == CHARACTER_DEFAULT_STATS[MAGE]["dice"]
    assert mage.attack == MAGE_L1_ATTACK
