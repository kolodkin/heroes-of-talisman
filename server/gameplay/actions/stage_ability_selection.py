"""
Ability Selection Stage Actions

This module implements actions for the ability selection stage:
- AbilityPressAction: Highlights selected ability by setting stage_meta
- AbilitySelectAction: Confirms ability selection and transitions to ability_opponent_selection stage
"""

from .action import Action
from ..models import (
    GamePlay,
    GameException,
    ReportedException,
    ABILITY_SELECTION,
    ABILITY_OPPONENT_SELECTION,
    AbilityName,
)


class AbilitySelectMeta:
    """Metadata for ability selection stage"""

    selected: AbilityName  # Currently highlighted ability


class AbilityPressAction(Action):
    """
    Action invoked when an ability is clicked during ability selection.

    Sets stage_meta to the chosen ability name, triggering
    a game_update that highlights the selected ability in the UI.
    """

    def run(self, ability: AbilityName) -> GamePlay:
        # Validate stage
        if self.game.stage != ABILITY_SELECTION:
            raise GameException(f"Cannot select ability in stage: {self.game.stage}")

        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Get the active character
        if not hasattr(self.game.active, "character"):
            raise GameException("No character selected")

        player = self.game.players[self.user]
        character = player.characters[self.game.active.character]

        # Validate ability is available for this character
        available_abilities = [a.name for a in character.abilities]
        if ability not in available_abilities:
            raise ReportedException(f"Ability {ability} not available for this character")

        # Set selected ability in stage metadata
        from ..models import StrictModel
        from pydantic import Field

        class AbilitySelectMeta(StrictModel):
            selected: str

        self.game.stage_meta = AbilitySelectMeta(selected=ability)

        return self.game


class AbilitySelectAction(Action):
    """
    Action invoked when the Select button is pressed to confirm ability choice.

    Stores the selected ability and transitions the game stage to 'ability_opponent_selection'.
    """

    def run(self, ability: AbilityName) -> GamePlay:
        # Validate stage
        if self.game.stage != ABILITY_SELECTION:
            raise GameException(f"Cannot confirm ability selection in stage: {self.game.stage}")

        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Get the active character
        if not hasattr(self.game.active, "character"):
            raise GameException("No character selected")

        player = self.game.players[self.user]
        character = player.characters[self.game.active.character]

        # Validate ability is available for this character
        available_abilities = [a.name for a in character.abilities]
        if ability not in available_abilities:
            raise ReportedException(f"Ability {ability} not available for this character")

        # Store selected ability in active player (we'll need to extend ActivePlayer model)
        # For now, store in stage_meta as we transition
        from ..models import StrictModel

        class AbilitySelectMeta(StrictModel):
            ability: str

        self.game.stage_meta = AbilitySelectMeta(ability=ability)

        # Transition to ability_opponent_selection stage
        self.game.stage = ABILITY_OPPONENT_SELECTION

        return self.game
