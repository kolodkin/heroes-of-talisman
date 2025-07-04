from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from .models import Game


class ActionResult(BaseModel):
    """Result of an action execution."""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class Action(ABC):
    """Base class for all game actions."""

    def __init__(self, game_engine: "GameEngine", name: str, description: str = ""):
        self.game_engine = game_engine
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> ActionResult:
        """Execute the action and return result."""
        pass

    def validate(self, **kwargs) -> bool:
        """Validate if action can be executed."""
        return True


class ConnectAction(Action):
    """Action to connect a user to a game."""

    def __init__(self, game_engine: "GameEngine"):
        super().__init__(game_engine, "connect", "Connect user to game")

    def execute(self, **kwargs) -> ActionResult:
        """Connect user to the game."""
        user_id = self.game_engine.user_id

        # Initialize game data structure if needed
        if not self.game_engine.game.data:
            self.game_engine.game.data = {
                "users": {},
                "game_state": "waiting",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

        # Ensure users dict exists
        if "users" not in self.game_engine.game.data:
            self.game_engine.game.data["users"] = {}

        # Add or update user connection
        self.game_engine.game.data["users"][user_id] = {
            "connected": True,
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
        }

        # Update game last_updated timestamp
        self.game_engine.game.last_updated = datetime.now(timezone.utc)

        return ActionResult(
            success=True,
            message=f"User {user_id} connected to game {self.game_engine.game.id}",
            data={"user_id": user_id, "game_id": self.game_engine.game.id},
        )


class DisconnectAction(Action):
    """Action to disconnect a user from a game."""

    def __init__(self, game_engine: "GameEngine"):
        super().__init__(game_engine, "disconnect", "Disconnect user from game")

    def execute(self, **kwargs) -> ActionResult:
        """Disconnect user from the game."""
        user_id = self.game_engine.user_id

        # Initialize game data if needed
        if not self.game_engine.game.data:
            self.game_engine.game.data = {"users": {}}

        # Ensure users dict exists
        if "users" not in self.game_engine.game.data:
            self.game_engine.game.data["users"] = {}

        # Update user connection status
        if user_id in self.game_engine.game.data["users"]:
            self.game_engine.game.data["users"][user_id]["connected"] = False
            self.game_engine.game.data["users"][user_id]["disconnected_at"] = datetime.now(timezone.utc).isoformat()
        else:
            # Create user record as disconnected
            self.game_engine.game.data["users"][user_id] = {
                "connected": False,
                "disconnected_at": datetime.now(timezone.utc).isoformat(),
            }

        # Update game last_updated timestamp
        self.game_engine.game.last_updated = datetime.now(timezone.utc)

        return ActionResult(
            success=True,
            message=f"User {user_id} disconnected from game {self.game_engine.game.id}",
            data={"user_id": user_id, "game_id": self.game_engine.game.id},
        )


class GameEngine:
    """Game engine for executing actions and managing game state."""

    def __init__(self, game: Game, user: str):
        """Initialize game engine with game instance and user ID.

        Args:
            game: The Game model instance
            user: The user ID string
        """
        self.game = game
        self.user_id = user
        self._action_history: List[Dict[str, Any]] = []

        # Initialize actions dictionary with instances
        self.actions: Dict[str, Action] = {"connect": ConnectAction(self), "disconnect": DisconnectAction(self)}

    def execute(self, action: str, **kwargs) -> ActionResult:
        """Execute an action with given parameters.

        Args:
            action: The action name to execute
            **kwargs: Additional parameters for the action

        Returns:
            ActionResult with success status and details
        """
        if action not in self.actions:
            return ActionResult(
                success=False,
                message=f"Unknown action: {action}",
                data={"available_actions": list(self.actions.keys())},
            )

        action_instance = self.actions[action]

        # Validate action can be executed
        if not action_instance.validate(**kwargs):
            return ActionResult(
                success=False,
                message=f"Action {action} validation failed",
                data={"action": action, "user_id": self.user_id},
            )

        # Execute the action
        try:
            result = action_instance.execute(**kwargs)

            # Log action in history
            self._action_history.append(
                {
                    "action": action,
                    "user_id": self.user_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "success": result.success,
                    "kwargs": kwargs,
                }
            )

            return result

        except Exception as e:
            error_result = ActionResult(
                success=False,
                message=f"Action {action} failed: {str(e)}",
                data={"action": action, "user_id": self.user_id, "error": str(e)},
            )

            # Log failed action
            self._action_history.append(
                {
                    "action": action,
                    "user_id": self.user_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "success": False,
                    "error": str(e),
                    "kwargs": kwargs,
                }
            )

            return error_result

    def get_connected_users(self) -> List[str]:
        """Get list of currently connected user IDs."""
        if not self.game.data or "users" not in self.game.data:
            return []

        connected_users = []
        for user_id, user_data in self.game.data["users"].items():
            if user_data.get("connected", False):
                connected_users.append(user_id)

        return connected_users

    def get_game_state(self) -> Dict[str, Any]:
        """Get current game state."""
        return self.game.data or {}

    def get_action_history(self) -> List[Dict[str, Any]]:
        """Get action history for debugging."""
        return self._action_history.copy()

    def register_action(self, action_class: type, *args, **kwargs):
        """Register a new action with the engine."""
        # Create action instance with self as game_engine
        action_instance = action_class(self, *args, **kwargs)
        self.actions[action_instance.name] = action_instance

    def get_available_actions(self) -> List[str]:
        """Get list of available action names."""
        return list(self.actions.keys())
