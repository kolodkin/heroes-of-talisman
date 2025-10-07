"""
Character Select Stage Actions

This module implements actions for the character selection stage:
- CharacterPressAction: Highlights selected character by setting stage_meta
- CharacterSelectAction: Confirms selection and transitions to battle stage
"""

from .action import Action
from ..models import (
    GamePlay,
    GameException,
    ReportedException,
    CharacterSelectMeta,
    ActivePlayer2,
    OPPONENT_SELECTION,
    CHARACTER_SELECT,
)


class CharacterPressAction(Action):
    """
    Action invoked when a character is clicked during character selection.

    Sets stage_meta['selected'] to the chosen character name, triggering
    a game_update that highlights the selected character in the UI.
    """

    def run(self, character: str) -> GamePlay:
        # Validate stage
        if self.game.stage != CHARACTER_SELECT:
            raise GameException(f"Cannot select character in stage: {self.game.stage}")

        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate character exists for this player
        player = self.game.players[self.user]
        if character not in player.characters:
            raise ReportedException(f"Character {character} not available")

        # Set selected character in stage metadata
        self.game.stage_meta = CharacterSelectMeta(selected=character)

        return self.game


class CharacterSelectAction(Action):
    """
    Action invoked when the Select button is pressed to confirm character choice.

    Populates selected_character in game metadata and transitions the game
    stage to 'opponent_selection'.
    """

    def run(self, character: str) -> GamePlay:
        # Validate stage
        if self.game.stage != CHARACTER_SELECT:
            raise GameException(f"Cannot confirm selection in stage: {self.game.stage}")

        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate character exists for this player
        player = self.game.players[self.user]
        if character not in player.characters:
            raise ReportedException(f"Character {character} not available")

        # Update active player with selected character
        self.game.active = ActivePlayer2(player=self.user, character=character)

        # Transition to opponent_selection stage
        self.game.stage = OPPONENT_SELECTION
        self.game.stage_meta = None  # Clear stage metadata

        return self.game
