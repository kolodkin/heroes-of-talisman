import pytest
from datetime import datetime, timezone
from unittest.mock import Mock

from .game_engine import GameEngine, ConnectAction, DisconnectAction, Action, ActionResult
from .models import Game


class CustomTestAction(Action):
    """Test action for extensibility testing."""

    def __init__(self, game_engine: GameEngine):
        super().__init__(game_engine, "test_action", "Test action for unit tests")

    def execute(self, **kwargs) -> ActionResult:
        return ActionResult(success=True, message="Test action executed successfully", data={"test": True})


@pytest.fixture
def game_fixture():
    """Fixture for creating a test game."""
    return Game(
        id="test-game-123",
        name="Test Game",
        data={},
        last_updated=datetime.now(timezone.utc),
        created=datetime.now(timezone.utc),
    )


@pytest.fixture
def user_id_fixture():
    """Fixture for test user ID."""
    return "test-user-456"


@pytest.fixture
def game_engine_fixture(game_fixture, user_id_fixture):
    """Fixture for creating a game engine with test game and user."""
    return GameEngine(game_fixture, user_id_fixture)


def test_game_engine_instantiation(game_engine_fixture, game_fixture, user_id_fixture):
    """Test GameEngine can be instantiated with Game model and user."""
    assert game_engine_fixture.game == game_fixture
    assert game_engine_fixture.user_id == user_id_fixture
    assert game_engine_fixture._action_history == []


def test_connect_action_execution(game_engine_fixture, game_fixture, user_id_fixture):
    """Test Connect action execution."""
    # Execute connect action
    result = game_engine_fixture.execute("connect")

    # Verify result
    assert result.success is True
    assert "connected to game" in result.message
    assert result.data["user_id"] == user_id_fixture
    assert result.data["game_id"] == game_fixture.id

    # Verify game state
    assert game_fixture.data["users"][user_id_fixture]["connected"] is True
    assert "connected_at" in game_fixture.data["users"][user_id_fixture]
    assert "last_activity" in game_fixture.data["users"][user_id_fixture]

    # Verify action history
    assert len(game_engine_fixture.get_action_history()) == 1
    action_log = game_engine_fixture.get_action_history()[0]
    assert action_log["action"] == "connect"
    assert action_log["user_id"] == user_id_fixture
    assert action_log["success"] is True


def test_disconnect_action_execution(game_engine_fixture, game_fixture, user_id_fixture):
    """Test Disconnect action execution."""
    # First connect the user
    game_engine_fixture.execute("connect")

    # Then disconnect
    result = game_engine_fixture.execute("disconnect")

    # Verify result
    assert result.success is True
    assert "disconnected from game" in result.message
    assert result.data["user_id"] == user_id_fixture
    assert result.data["game_id"] == game_fixture.id

    # Verify game state
    assert game_fixture.data["users"][user_id_fixture]["connected"] is False
    assert "disconnected_at" in game_fixture.data["users"][user_id_fixture]

    # Verify action history
    assert len(game_engine_fixture.get_action_history()) == 2
    disconnect_log = game_engine_fixture.get_action_history()[1]
    assert disconnect_log["action"] == "disconnect"
    assert disconnect_log["user_id"] == user_id_fixture
    assert disconnect_log["success"] is True


def test_disconnect_without_connect(game_engine_fixture, game_fixture, user_id_fixture):
    """Test disconnect action when user never connected."""
    result = game_engine_fixture.execute("disconnect")

    # Should still succeed
    assert result.success is True
    assert game_fixture.data["users"][user_id_fixture]["connected"] is False
    assert "disconnected_at" in game_fixture.data["users"][user_id_fixture]


def test_connect_action_adds_user_to_game_users(game_engine_fixture, user_id_fixture):
    """Test Connect action adds user to game.users as connected."""
    # Execute connect
    game_engine_fixture.execute("connect")

    # Verify user is in connected users list
    connected_users = game_engine_fixture.get_connected_users()
    assert user_id_fixture in connected_users
    assert len(connected_users) == 1


def test_disconnect_action_marks_user_as_disconnected(game_engine_fixture, user_id_fixture):
    """Test Disconnect action marks user as disconnected."""
    # Connect then disconnect
    game_engine_fixture.execute("connect")
    game_engine_fixture.execute("disconnect")

    # Verify user is not in connected users list
    connected_users = game_engine_fixture.get_connected_users()
    assert user_id_fixture not in connected_users
    assert len(connected_users) == 0


def test_action_system_extensibility(game_engine_fixture):
    """Test action system extensibility by registering new action."""
    # Register test action
    game_engine_fixture.register_action(CustomTestAction)

    # Verify action is available
    available_actions = game_engine_fixture.get_available_actions()
    assert "test_action" in available_actions

    # Execute test action
    result = game_engine_fixture.execute("test_action")
    assert result.success is True
    assert result.message == "Test action executed successfully"
    assert result.data["test"] is True


def test_unknown_action_execution(game_engine_fixture):
    """Test execution of unknown action."""
    result = game_engine_fixture.execute("unknown_action")

    assert result.success is False
    assert "Unknown action" in result.message
    assert "available_actions" in result.data


def test_multiple_users_connect(game_fixture, user_id_fixture):
    """Test multiple users connecting to the same game."""
    # Create second engine for different user
    user2_id = "test-user-789"
    engine1 = GameEngine(game_fixture, user_id_fixture)
    engine2 = GameEngine(game_fixture, user2_id)

    # Connect both users
    engine1.execute("connect")
    engine2.execute("connect")

    # Verify both users are connected
    connected_users = engine1.get_connected_users()
    assert len(connected_users) == 2
    assert user_id_fixture in connected_users
    assert user2_id in connected_users


def test_get_game_state(game_engine_fixture, user_id_fixture):
    """Test getting current game state."""
    # Initially empty
    state = game_engine_fixture.get_game_state()
    assert state == {}

    # After connect
    game_engine_fixture.execute("connect")
    state = game_engine_fixture.get_game_state()
    assert "users" in state
    assert user_id_fixture in state["users"]
    assert state["users"][user_id_fixture]["connected"] is True


def test_game_initialization_with_empty_data(user_id_fixture):
    """Test game engine works with empty game data."""
    # Create game with None data
    empty_game = Game(
        id="empty-game",
        name="Empty Game",
        data=None,
        last_updated=datetime.now(timezone.utc),
        created=datetime.now(timezone.utc),
    )

    engine = GameEngine(empty_game, user_id_fixture)
    result = engine.execute("connect")

    assert result.success is True
    assert empty_game.data is not None
    assert "users" in empty_game.data
    assert user_id_fixture in empty_game.data["users"]


def test_action_history_tracking(game_engine_fixture, user_id_fixture):
    """Test action history is properly tracked."""
    # Execute multiple actions
    game_engine_fixture.execute("connect")
    game_engine_fixture.execute("disconnect")
    game_engine_fixture.execute("connect")

    history = game_engine_fixture.get_action_history()
    assert len(history) == 3

    # Check action sequence
    assert history[0]["action"] == "connect"
    assert history[1]["action"] == "disconnect"
    assert history[2]["action"] == "connect"

    # Check all have timestamps
    for action_log in history:
        assert "timestamp" in action_log
        assert action_log["user_id"] == user_id_fixture


def test_game_last_updated_timestamp(game_fixture, game_engine_fixture):
    """Test game last_updated is updated on actions."""
    initial_time = game_fixture.last_updated

    # Execute action
    game_engine_fixture.execute("connect")

    # Verify timestamp was updated
    assert game_fixture.last_updated > initial_time


def test_connect_action_initialization(game_engine_fixture):
    """Test ConnectAction initialization."""
    action = ConnectAction(game_engine_fixture)
    assert action.name == "connect"
    assert action.description == "Connect user to game"
    assert action.game_engine == game_engine_fixture


def test_disconnect_action_initialization(game_engine_fixture):
    """Test DisconnectAction initialization."""
    action = DisconnectAction(game_engine_fixture)
    assert action.name == "disconnect"
    assert action.description == "Disconnect user from game"
    assert action.game_engine == game_engine_fixture


def test_action_result_creation():
    """Test ActionResult creation."""
    result = ActionResult(success=True, message="Test message", data={"test": "data"})

    assert result.success is True
    assert result.message == "Test message"
    assert result.data == {"test": "data"}


def test_action_result_without_data():
    """Test ActionResult creation without data."""
    result = ActionResult(success=False, message="Error message")

    assert result.success is False
    assert result.message == "Error message"
    assert result.data is None
