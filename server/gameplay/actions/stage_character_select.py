"""
Character Select Stage Actions

This module implements actions for the character selection stage:
- CharacterPressAction: Highlights selected character by setting stage_meta
- CharacterSelectAction: Confirms selection, disposes effects, and transitions to ability_selection
"""

from .action import Action
from ..models import (
    GamePlay,
    GameException,
    ReportedException,
    CharacterSelectMeta,
    ActivePlayer2,
    ABILITY_SELECTION,
    CHARACTER_SELECT,
    CHARACTER_SELECT_ACTION,
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

        # Validate character is alive
        if not player.characters[character].is_alive:
            raise ReportedException(f"Character {character} is dead and can't be selected")

        # Set selected character in stage metadata
        self.game.stage_meta = CharacterSelectMeta(selected=character)

        return self.game


class CharacterSelectAction(Action):
    """
    Action invoked when the Select button is pressed to confirm character choice.

    Populates selected_character in game metadata, disposes effects with
    'character_select' in dispose_actions, and transitions the game stage to 'ability_selection'.
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

        # Validate character is alive
        if not player.characters[character].is_alive:
            raise ReportedException(f"Character {character} is dead and can't be selected")

        # Dispose effects with 'character_select' in dispose_actions from active player's characters
        for char in player.characters.values():
            char.effects = [
                effect for effect in char.effects
                if CHARACTER_SELECT_ACTION not in effect.dispose_actions
            ]

        # Update active player with selected character
        self.game.active = ActivePlayer2(player=self.user, character=character)

        # Transition to ability_selection stage
        self.game.stage = ABILITY_SELECTION
        self.game.stage_meta = None  # Clear stage metadata

        return self.game
