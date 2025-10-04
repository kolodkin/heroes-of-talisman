"""
Opponent Selection Stage Actions

This module implements actions for the opponent selection stage:
- OpponentPressAction: Highlights selected opponent by setting stage_meta
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


class OpponentPressAction(Action):
    """
    Action invoked when an opponent's character is clicked during opponent selection.

    Sets stage_meta to an Opponent object with the chosen opponent player and character,
    triggering a game_update that highlights the selected opponent in the UI.
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

        # Set selected opponent in stage metadata
        self.game.stage_meta = Opponent(player=opponent, character=character)

        return self.game


class OpponentSelectAction(Action):
    """
    Action invoked when the Select button is pressed to confirm opponent choice.

    Reads the selected opponent from stage_meta, populates the opponent field
    in game metadata, and transitions the game stage to 'battle'.
    """

    def run(self) -> GamePlay:
        # Validate stage
        if self.game.stage != OPPONENT_SELECTION:
            raise GameException(
                f"Cannot confirm selection in stage: {self.game.stage}"
            )

        # Validate user is the active player
        if self.game.playing != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate stage_meta is set and is an Opponent
        if not self.game.stage_meta or not isinstance(
            self.game.stage_meta, Opponent
        ):
            raise ReportedException("No opponent selected")

        # Get opponent from stage_meta
        selected_opponent = self.game.stage_meta

        # Set opponent in game metadata
        self.game.opponent = selected_opponent

        # Transition to battle stage
        self.game.stage = BATTLE
        self.game.stage_meta = None  # Clear stage metadata

        return self.game
