"""
Character Select Stage Actions

This module implements actions for the character selection stage:
- CharacterPressAction: Highlights selected character by setting stage_meta
- CharacterSelectAction: Confirms selection and transitions to battle stage
"""

from typing import Optional

from server.actions.base import Action
from server.gameplay.models import (
    GamePlay,
    GameException,
    ReportedException,
    BATTLE,
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
        if self.game.playing != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate character exists for this player
        player = self.game.players[self.user]
        if character not in player.characters:
            raise ReportedException(f"Character {character} not available")

        # Set selected character in stage metadata
        if self.game.stage_meta is None:
            self.game.stage_meta = {}
        self.game.stage_meta["selected"] = character

        return self.game


class CharacterSelectAction(Action):
    """
    Action invoked when the Select button is pressed to confirm character choice.

    Populates selected_character in game metadata and transitions the game
    stage to 'battle'.
    """

    def run(self, character: str) -> GamePlay:
        # Validate stage
        if self.game.stage != CHARACTER_SELECT:
            raise GameException(f"Cannot confirm selection in stage: {self.game.stage}")

        # Validate user is the active player
        if self.game.playing != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate character exists for this player
        player = self.game.players[self.user]
        if character not in player.characters:
            raise ReportedException(f"Character {character} not available")

        # Set selected character in game metadata
        self.game.selected_character = character

        # Transition to battle stage
        self.game.stage = BATTLE
        self.game.stage_meta = None  # Clear stage metadata

        return self.game
