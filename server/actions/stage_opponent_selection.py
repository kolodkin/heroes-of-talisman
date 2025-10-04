"""
Opponent Selection Stage Actions

This module implements actions for the opponent selection stage:
- OpponentSelectAction: Confirms opponent selection and transitions to battle stage
"""

from server.actions.base import Action
from server.gameplay.models import (
    GamePlay,
    GameException,
    ReportedException,
    Opponent,
    BATTLE,
    OPPONENT_SELECTION,
)


class OpponentSelectAction(Action):
    """
    Action invoked when an opponent and character are selected.

    Populates the opponent field in game metadata and transitions the game
    stage to 'battle'.
    """

    def run(self, opponent: str, character: str) -> GamePlay:
        # Validate stage
        if self.game.stage != OPPONENT_SELECTION:
            raise GameException(
                f"Cannot select opponent in stage: {self.game.stage}"
            )

        # Validate user is the active player
        if self.game.playing != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate opponent exists
        if opponent not in self.game.players:
            raise ReportedException(f"Opponent {opponent} not in game")

        # Validate opponent is not the current player
        if opponent == self.user:
            raise ReportedException("Cannot select yourself as opponent")

        # Validate character exists for opponent
        opponent_player = self.game.players[opponent]
        if character not in opponent_player.characters:
            raise ReportedException(
                f"Character {character} not available for opponent"
            )

        # Set opponent in game metadata
        self.game.opponent = Opponent(player=opponent, character=character)

        # Transition to battle stage
        self.game.stage = BATTLE
        self.game.stage_meta = None  # Clear stage metadata

        return self.game
