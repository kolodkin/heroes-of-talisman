"""
Character Select Stage Actions

This module implements actions for the character selection stage:
- CharacterPressAction: Highlights selected character by setting stage_meta
- CharacterSelectAction: Confirms selection, disposes effects, and transitions to card_draw
- SkipTurnAction: Skips turn when no character is available (all dead or have skip_turn effect)
"""

from .action import Action, rotate_to_next_player
from ..common import (
    GameException,
    ReportedException,
    ACTION_CHARACTER_SELECT,
)
from ..gameplay import (
    STAGE_CARD_DRAW,
    STAGE_ABILITY_SELECTION,
    STAGE_CHARACTER_SELECT,
    GamePlay,
    CharacterSelectMeta,
    CardDrawMeta,
    AbilitySelectMeta,
    ActivePlayer2,
)


class CharacterPressAction(Action):
    """
    Action invoked when a character is clicked during character selection.

    Sets stage_meta['selected'] to the chosen character name, triggering
    a game_update that highlights the selected character in the UI.
    """

    @property
    def action_stages(self):
        return [STAGE_CHARACTER_SELECT]

    def _run(self, character: str) -> GamePlay:
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
    'character_select' in dispose_actions, and transitions the game stage to 'card_draw'.
    """

    @property
    def action_stages(self):
        return [STAGE_CHARACTER_SELECT]

    def _run(self, character: str) -> GamePlay:
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
                if ACTION_CHARACTER_SELECT not in effect.dispose_actions
            ]

        # Update active player with selected character
        self.game.active = ActivePlayer2(player=self.user, character=character)

        # Transition to card_draw stage
        self.game.stage = STAGE_CARD_DRAW

        # Clear stage_meta - will be populated by CardDrawAction
        self.game.stage_meta = None

        return self.game


class SkipTurnAction(Action):
    """
    Action invoked when no character is available for selection.

    This happens when all characters are either dead (health=0) or have
    a skip_turn effect. The turn is skipped and passes to the next player.

    Disposes effects with 'character_select' in dispose_actions and
    transitions to the next player's character_select stage.
    """

    @property
    def action_stages(self):
        return [STAGE_CHARACTER_SELECT]

    def _run(self) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        player = self.game.players[self.user]

        # Validate that no character is available
        # A character is unavailable if dead or has skip_turn effect
        available_characters = [
            char_name for char_name, char in player.characters.items()
            if char.is_alive and not char.effect.skip_next_turn
        ]

        if available_characters:
            raise ReportedException(
                "Cannot skip turn: available characters exist"
            )

        # Dispose effects with 'character_select' in dispose_actions from active player's characters
        for char in player.characters.values():
            char.effects = [
                effect for effect in char.effects
                if ACTION_CHARACTER_SELECT not in effect.dispose_actions
            ]

        # Rotate to next player's turn
        rotate_to_next_player(self.game)

        return self.game
