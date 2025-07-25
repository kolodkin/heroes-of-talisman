import pytest
from unittest.mock import patch

from .connection import ConnectAction, LeaveAction, DisconnectAction
from ..models import GameModel, PlayerModel, CharacterModel, GameException, ReportedException


@pytest.fixture
def empty_game_model():
    """Create an empty test game model"""
    return GameModel(
        stage=None, stage_meta={}, deck=["talisman", "golden_apple"], playing=None, selected_character=None, players={}
    )


@pytest.fixture
def player_model():
    """Create a test player model"""
    characters = {"knight": CharacterModel(health=2, level=1, max_health=2, skills={}, dice=1, attack=1)}
    return PlayerModel(status="connected", cards=["talisman"], characters=characters)


@pytest.fixture
def game_model_with_player(player_model):
    """Create a test game model with existing player"""
    return GameModel(
        stage="character_select",
        stage_meta={},
        deck=["talisman", "golden_apple"],
        playing="test_user",
        selected_character=None,
        players={"test_user": player_model},
    )


def test_connect_action_new_player(empty_game_model):
    """Test ConnectAction with new player joining empty game"""
    action = ConnectAction("test_user", empty_game_model)
    result = action.run()

    assert isinstance(result, GameModel)
    assert "test_user" in action.players
    assert action.player.status == "connected"
    assert len(action.player.characters) == 3  # knight, archer, mage
    assert action.game.stage == "character_select"
    assert action.game.playing == "test_user"


def test_connect_action_existing_player_reconnect(game_model_with_player):
    """Test ConnectAction with existing player reconnecting"""
    # Set player as disconnected
    game_model_with_player.players["test_user"].status = "disconnected"

    action = ConnectAction("test_user", game_model_with_player)
    result = action.run()

    assert isinstance(result, GameModel)
    assert action.player.status == "connected"
    assert action.game.playing == "test_user"


def test_connect_action_game_full(empty_game_model):
    """Test ConnectAction when game is full"""
    # Fill the game with max players
    for i in range(4):  # __MAX_PLAYERS__ = 4
        empty_game_model.players[f"player_{i}"] = PlayerModel(status="connected")

    action = ConnectAction("new_player", empty_game_model)

    with pytest.raises(ReportedException, match="Game is full"):
        action.run()


def test_connect_action_character_creation():
    """Test ConnectAction creates characters with correct stats"""
    game_model = GameModel()
    action = ConnectAction("test_user", game_model)
    result = action.run()

    characters = action.player.characters

    # Test knight character
    knight = characters["knight"]
    assert knight.health == 2
    assert knight.max_health == 2
    assert knight.level == 1
    assert knight.dice == 1
    assert knight.attack == 1

    # Test archer character
    archer = characters["archer"]
    assert archer.health == 3
    assert archer.max_health == 3
    assert archer.level == 1
    assert archer.dice == 1
    assert archer.attack is None

    # Test mage character
    mage = characters["mage"]
    assert mage.health == 2
    assert mage.max_health == 2
    assert mage.level == 1
    assert mage.dice == 1
    assert mage.attack is None


def test_connect_action_game_already_started(empty_game_model):
    """Test ConnectAction when game already has a stage set"""
    empty_game_model.stage = "card_draw"
    action = ConnectAction("test_user", empty_game_model)
    result = action.run()

    assert action.game.stage == "card_draw"  # Should not change existing stage
    assert action.game.playing == "test_user"


def test_leave_action_success(game_model_with_player):
    """Test LeaveAction removes player from game"""
    action = LeaveAction("test_user", game_model_with_player)
    result = action.run()

    assert isinstance(result, GameModel)
    assert "test_user" not in action.players


def test_leave_action_player_not_in_game(empty_game_model):
    """Test LeaveAction when player not in game"""
    action = LeaveAction("nonexistent_user", empty_game_model)

    with pytest.raises(GameException, match="Player not in game"):
        action.run()


def test_disconnect_action_success(game_model_with_player):
    """Test DisconnectAction sets player status to disconnected"""
    action = DisconnectAction("test_user", game_model_with_player)
    result = action.run()

    assert isinstance(result, GameModel)
    assert action.player.status == "disconnected"
    assert "test_user" in action.players  # Player should still be in game


def test_disconnect_action_player_not_in_game(empty_game_model):
    """Test DisconnectAction when player not in game"""
    action = DisconnectAction("nonexistent_user", empty_game_model)

    with pytest.raises(GameException, match="Player not in game"):
        action.run()
