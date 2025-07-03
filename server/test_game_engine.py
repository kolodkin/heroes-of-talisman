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
        return ActionResult(
            success=True,
            message="Test action executed successfully",
            data={"test": True}
        )


class TestGameEngine:
    """Test suite for GameEngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.game = Game(
            id="test-game-123",
            name="Test Game",
            data={},
            last_updated=datetime.now(timezone.utc),
            created=datetime.now(timezone.utc)
        )
        self.user_id = "test-user-456"
        self.engine = GameEngine(self.game, self.user_id)
    
    def test_game_engine_instantiation(self):
        """Test GameEngine can be instantiated with Game model and user."""
        assert self.engine.game == self.game
        assert self.engine.user_id == self.user_id
        assert self.engine._action_history == []
    
    def test_connect_action_execution(self):
        """Test Connect action execution."""
        # Execute connect action
        result = self.engine.execute("connect")
        
        # Verify result
        assert result.success is True
        assert "connected to game" in result.message
        assert result.data["user_id"] == self.user_id
        assert result.data["game_id"] == self.game.id
        
        # Verify game state
        assert self.game.data["users"][self.user_id]["connected"] is True
        assert "connected_at" in self.game.data["users"][self.user_id]
        assert "last_activity" in self.game.data["users"][self.user_id]
        
        # Verify action history
        assert len(self.engine.get_action_history()) == 1
        action_log = self.engine.get_action_history()[0]
        assert action_log["action"] == "connect"
        assert action_log["user_id"] == self.user_id
        assert action_log["success"] is True
    
    def test_disconnect_action_execution(self):
        """Test Disconnect action execution."""
        # First connect the user
        self.engine.execute("connect")
        
        # Then disconnect
        result = self.engine.execute("disconnect")
        
        # Verify result
        assert result.success is True
        assert "disconnected from game" in result.message
        assert result.data["user_id"] == self.user_id
        assert result.data["game_id"] == self.game.id
        
        # Verify game state
        assert self.game.data["users"][self.user_id]["connected"] is False
        assert "disconnected_at" in self.game.data["users"][self.user_id]
        
        # Verify action history
        assert len(self.engine.get_action_history()) == 2
        disconnect_log = self.engine.get_action_history()[1]
        assert disconnect_log["action"] == "disconnect"
        assert disconnect_log["user_id"] == self.user_id
        assert disconnect_log["success"] is True
    
    def test_disconnect_without_connect(self):
        """Test disconnect action when user never connected."""
        result = self.engine.execute("disconnect")
        
        # Should still succeed
        assert result.success is True
        assert self.game.data["users"][self.user_id]["connected"] is False
        assert "disconnected_at" in self.game.data["users"][self.user_id]
    
    def test_connect_action_adds_user_to_game_users(self):
        """Test Connect action adds user to game.users as connected."""
        # Execute connect
        self.engine.execute("connect")
        
        # Verify user is in connected users list
        connected_users = self.engine.get_connected_users()
        assert self.user_id in connected_users
        assert len(connected_users) == 1
    
    def test_disconnect_action_marks_user_as_disconnected(self):
        """Test Disconnect action marks user as disconnected."""
        # Connect then disconnect
        self.engine.execute("connect")
        self.engine.execute("disconnect")
        
        # Verify user is not in connected users list
        connected_users = self.engine.get_connected_users()
        assert self.user_id not in connected_users
        assert len(connected_users) == 0
    
    def test_action_system_extensibility(self):
        """Test action system extensibility by registering new action."""
        # Register test action
        self.engine.register_action(CustomTestAction)
        
        # Verify action is available
        available_actions = self.engine.get_available_actions()
        assert "test_action" in available_actions
        
        # Execute test action
        result = self.engine.execute("test_action")
        assert result.success is True
        assert result.message == "Test action executed successfully"
        assert result.data["test"] is True
    
    def test_unknown_action_execution(self):
        """Test execution of unknown action."""
        result = self.engine.execute("unknown_action")
        
        assert result.success is False
        assert "Unknown action" in result.message
        assert "available_actions" in result.data
    
    def test_multiple_users_connect(self):
        """Test multiple users connecting to the same game."""
        # Create second engine for different user
        user2_id = "test-user-789"
        engine2 = GameEngine(self.game, user2_id)
        
        # Connect both users
        self.engine.execute("connect")
        engine2.execute("connect")
        
        # Verify both users are connected
        connected_users = self.engine.get_connected_users()
        assert len(connected_users) == 2
        assert self.user_id in connected_users
        assert user2_id in connected_users
    
    def test_get_game_state(self):
        """Test getting current game state."""
        # Initially empty
        state = self.engine.get_game_state()
        assert state == {}
        
        # After connect
        self.engine.execute("connect")
        state = self.engine.get_game_state()
        assert "users" in state
        assert self.user_id in state["users"]
        assert state["users"][self.user_id]["connected"] is True
    
    def test_game_initialization_with_empty_data(self):
        """Test game engine works with empty game data."""
        # Create game with None data
        empty_game = Game(
            id="empty-game",
            name="Empty Game",
            data=None,
            last_updated=datetime.now(timezone.utc),
            created=datetime.now(timezone.utc)
        )
        
        engine = GameEngine(empty_game, self.user_id)
        result = engine.execute("connect")
        
        assert result.success is True
        assert empty_game.data is not None
        assert "users" in empty_game.data
        assert self.user_id in empty_game.data["users"]
    
    def test_action_history_tracking(self):
        """Test action history is properly tracked."""
        # Execute multiple actions
        self.engine.execute("connect")
        self.engine.execute("disconnect")
        self.engine.execute("connect")
        
        history = self.engine.get_action_history()
        assert len(history) == 3
        
        # Check action sequence
        assert history[0]["action"] == "connect"
        assert history[1]["action"] == "disconnect"
        assert history[2]["action"] == "connect"
        
        # Check all have timestamps
        for action_log in history:
            assert "timestamp" in action_log
            assert action_log["user_id"] == self.user_id
    
    def test_game_last_updated_timestamp(self):
        """Test game last_updated is updated on actions."""
        initial_time = self.game.last_updated
        
        # Execute action
        self.engine.execute("connect")
        
        # Verify timestamp was updated
        assert self.game.last_updated > initial_time


class TestConnectAction:
    """Test suite for ConnectAction class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.game = Game(
            id="test-game-123",
            name="Test Game",
            data={},
            last_updated=datetime.now(timezone.utc),
            created=datetime.now(timezone.utc)
        )
        self.user_id = "test-user-456"
        self.engine = GameEngine(self.game, self.user_id)
    
    def test_connect_action_initialization(self):
        """Test ConnectAction initialization."""
        action = ConnectAction(self.engine)
        assert action.name == "connect"
        assert action.description == "Connect user to game"
        assert action.game_engine == self.engine


class TestDisconnectAction:
    """Test suite for DisconnectAction class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.game = Game(
            id="test-game-123",
            name="Test Game",
            data={},
            last_updated=datetime.now(timezone.utc),
            created=datetime.now(timezone.utc)
        )
        self.user_id = "test-user-456"
        self.engine = GameEngine(self.game, self.user_id)
    
    def test_disconnect_action_initialization(self):
        """Test DisconnectAction initialization."""
        action = DisconnectAction(self.engine)
        assert action.name == "disconnect"
        assert action.description == "Disconnect user from game"
        assert action.game_engine == self.engine


class TestActionResult:
    """Test suite for ActionResult class."""
    
    def test_action_result_creation(self):
        """Test ActionResult creation."""
        result = ActionResult(
            success=True,
            message="Test message",
            data={"test": "data"}
        )
        
        assert result.success is True
        assert result.message == "Test message"
        assert result.data == {"test": "data"}
    
    def test_action_result_without_data(self):
        """Test ActionResult creation without data."""
        result = ActionResult(
            success=False,
            message="Error message"
        )
        
        assert result.success is False
        assert result.message == "Error message"
        assert result.data is None 