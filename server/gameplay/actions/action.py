from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..models import GameException, ReportedException, StageName
from ..gameplay import (
    GamePlay,
    Player,
    Character,
    ActivePlayer1,
    ActivePlayer2,
    ActivePlayer3,
    ActivePlayer4,
    Opponent2,
    Opponent3,
    Opponent4,
)


class Action(ABC):
    def __init__(self, user: str, game: GamePlay):
        self.user: str = user
        self.game: GamePlay = game

    # convenience helpers similar to GameEngine properties

    @property
    def stage(self) -> Optional[str]:
        return self.game.stage

    @stage.setter
    def stage(self, value: Optional[str]):
        self.game.stage = value

    @property
    def active(self) -> Optional[ActivePlayer1 | ActivePlayer2 | ActivePlayer3 | ActivePlayer4]:
        return self.game.active

    @active.setter
    def active(self, value: Optional[ActivePlayer1 | ActivePlayer2 | ActivePlayer3 | ActivePlayer4]):
        self.game.active = value

    @property
    def active_character(self) -> Character:
        """
        Get the active player's character card.

        Provides validation that active player exists and has a character selected.

        Raises:
            GameException: If active player is not set or has no character selected
        """
        if not self.active or not isinstance(self.active, (ActivePlayer2, ActivePlayer3, ActivePlayer4)):
            raise GameException("Active player not set or has no character selected")
        return self.game.players[self.active.player].characters[self.active.character]

    @property
    def players(self):
        return self.game.players

    @players.setter
    def players(self, value: dict[str, Player]):
        self.game.players = value

    @property
    def player(self) -> Player:
        if self.user not in self.players:
            raise GameException("Player not in game")
        return self.players[self.user]

    @property
    def stage_meta(self) -> Optional[Dict[str, Any]]:
        return self.game.stage_meta

    @stage_meta.setter
    def stage_meta(self, value: Optional[Dict[str, Any]]):
        self.game.stage_meta = value

    @property
    def opponent(self) -> Optional[Opponent2 | Opponent3 | Opponent4]:
        return self.game.opponent

    @opponent.setter
    def opponent(self, value: Optional[Opponent2 | Opponent3 | Opponent4]):
        self.game.opponent = value

    @property
    def opponent_character(self) -> Character:
        """
        Get the opponent's character card.

        Provides validation that opponent exists and has a character selected.

        Raises:
            GameException: If opponent is not set or has no character selected
        """
        if not self.opponent or not isinstance(self.opponent, (Opponent2, Opponent3, Opponent4)):
            raise GameException("Opponent not set or has no character selected")
        return self.game.players[self.opponent.player].characters[self.opponent.character]

    @property
    @abstractmethod
    def action_stages(self) -> Optional[list[StageName]]:
        """
        Return list of valid stages for this action, or None if action works in any stage.

        Examples:
            return [CHARACTER_SELECT]  # Only works in character select stage
            return [BATTLE_DICE_ROLL, BATTLE_END]  # Works in multiple stages
            return None  # Works in any stage (e.g., connection actions)
        """

    def assert_stage(self):
        """Validate that the game is in the correct stage for this action."""
        if self.action_stages is None:
            # Action works in any stage
            return

        if self.stage not in self.action_stages:
            stages_str = ", ".join(self.action_stages)
            raise GameException(f"Cannot perform action in stage '{self.stage}'. Valid stages: {stages_str}")

    def run(self, *args, **kwargs) -> GamePlay:
        """Execute the action with automatic stage validation."""
        self.assert_stage()
        return self._run(*args, **kwargs)

    @abstractmethod
    def _run(self, *args, **kwargs) -> GamePlay:
        """Execute the action logic. Implemented by subclasses."""
