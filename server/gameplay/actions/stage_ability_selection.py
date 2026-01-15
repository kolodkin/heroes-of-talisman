"""
Ability Selection Stage Actions

This module implements actions for the ability selection stage:
- AbilityPressAction: Highlights selected ability by setting stage_meta
- AbilitySelectAction: Confirms ability selection and transitions to ability_opponent_selection
  (if ability requires opponent selection) or opponent_selection stage
"""

import copy
from .action import Action
from ..models import (
    GamePlay,
    GameException,
    ReportedException,
    AbilitySelectMeta,
    ABILITY_SELECTION,
    ABILITY_OPPONENT_SELECTION,
    OPPONENT_SELECTION,
    APPLY_TO_SELF,
    AbilityName,
)


class AbilityPressAction(Action):
    """
    Action invoked when an ability is clicked during ability selection.

    Sets stage_meta to the chosen ability name, triggering
    a game_update that highlights the selected ability in the UI.
    """

    @property
    def action_stages(self):
        return [ABILITY_SELECTION]

    def run(self, ability: AbilityName) -> GamePlay:

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
        self.game.stage_meta = AbilitySelectMeta(selected=ability)

        return self.game


class AbilitySelectAction(Action):
    """
    Action invoked when the Select button is pressed to confirm ability choice.

    Stores the selected ability and transitions the game stage to:
    - 'ability_opponent_selection' if the ability has effects requiring target selection (e.g., SkipTurnEffect)
    - 'opponent_selection' if the ability effects are applied to battle opponent automatically
    """

    @property
    def action_stages(self):
        return [ABILITY_SELECTION]

    def run(self, ability: AbilityName) -> GamePlay:

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

        # Store selected ability in GamePlay.ability
        ability_obj = next((a for a in character.abilities if a.name == ability), None)
        if not ability_obj:
            raise GameException(f"Ability {ability} not found in character abilities")

        self.game.ability = ability_obj

        # Apply "self" effects to the active player's character
        for effect in ability_obj.effects:
            if effect.apply_to == APPLY_TO_SELF:
                # Deep copy the effect to avoid modifying the original ability definition
                effect_copy = copy.deepcopy(effect)
                character.effects.append(effect_copy)

        # Clear stage_meta after selection
        self.game.stage_meta = None

        # Transition to ability_opponent_selection if ability requires it, otherwise skip to opponent_selection
        if ability_obj.requires_opponent_selection:
            self.game.stage = ABILITY_OPPONENT_SELECTION
        else:
            self.game.stage = OPPONENT_SELECTION

        return self.game
