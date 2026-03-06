"""
Ability Selection Stage Actions

This module implements actions for the ability selection stage:
- AbilityPressAction: Highlights selected ability by setting stage_meta
- AbilitySelectAction: Confirms ability selection and transitions to ability_opponent_selection
  (if ability requires opponent selection) or opponent_selection stage
"""

from .action import Action
from ..common import GameException, ReportedException
from ..effects import APPLY_TO_SELF, APPLY_TO_SELECTED_OPPONENT
from ..abilities import AbilityName, get_ability_effects
from ..gameplay import STAGE_ABILITY_SELECTION, STAGE_ABILITY_OPPONENT_SELECTION, STAGE_OPPONENT_SELECTION
from ..gameplay import GamePlay, AbilitySelectMeta


class AbilityPressAction(Action):
    """
    Action invoked when an ability is clicked during ability selection.

    Sets stage_meta to the chosen ability name, triggering
    a game_update that highlights the selected ability in the UI.
    """

    @property
    def action_stages(self):
        return [STAGE_ABILITY_SELECTION]

    def _run(self, ability: AbilityName) -> GamePlay:
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
        return [STAGE_ABILITY_SELECTION]

    def _run(self, ability: AbilityName) -> GamePlay:
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

        # Store selected ability name in GamePlay.ability
        self.game.ability = ability

        # Apply self-target effects by adding ability name to active_abilities
        effects = get_ability_effects(ability)
        has_self_effects = any(e.apply_to == APPLY_TO_SELF for e in effects)
        if has_self_effects:
            character.active_abilities.append(ability)

        # Clear stage_meta after selection
        self.game.stage_meta = None

        # Transition to ability_opponent_selection if any effect targets a selected opponent
        has_opponent_selection = any(e.apply_to == APPLY_TO_SELECTED_OPPONENT for e in effects)
        if has_opponent_selection:
            self.game.stage = STAGE_ABILITY_OPPONENT_SELECTION
        else:
            self.game.stage = STAGE_OPPONENT_SELECTION

        return self.game
