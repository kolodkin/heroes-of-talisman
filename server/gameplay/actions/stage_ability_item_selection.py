"""
Ability Item Selection Stage Actions

This module implements actions for the ability item selection stage:
- AbilityItemPressAction: Highlights a selected item card from the target's active_cards
- AbilityItemSelectAction: Removes the selected item from the target's active_cards and
  transitions to opponent_selection stage
"""

from .action import Action
from ..common import GameException, ReportedException
from ..gameplay import STAGE_ABILITY_ITEM_SELECTION, STAGE_OPPONENT_SELECTION, GamePlay, AbilityItemMeta


class AbilityItemPressAction(Action):
    """
    Action invoked when a card is clicked during ability item selection.

    Sets stage_meta.selected_item to the clicked card name,
    triggering a game_update that highlights the selected item in the UI.
    """

    @property
    def action_stages(self):
        return [STAGE_ABILITY_ITEM_SELECTION]

    def _run(self, item: str) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate stage_meta is set and is an AbilityItemMeta
        if not self.game.stage_meta or not isinstance(self.game.stage_meta, AbilityItemMeta):
            raise GameException("Invalid stage metadata for item selection")

        # Validate the item exists in the target's active_cards
        target_character = self.ability_item_target_character
        if item not in target_character.active_cards:
            raise ReportedException(f"Item {item} is not in target's active cards")

        # Highlight the selected item
        self.game.stage_meta.selected_item = item

        return self.game


class AbilityItemSelectAction(Action):
    """
    Action invoked when the Select button is pressed to confirm item selection.

    Removes the selected item from the target's active_cards and
    transitions the game stage to 'opponent_selection'.
    """

    @property
    def action_stages(self):
        return [STAGE_ABILITY_ITEM_SELECTION]

    def _run(self) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate stage_meta is set and is an AbilityItemMeta
        if not self.game.stage_meta or not isinstance(self.game.stage_meta, AbilityItemMeta):
            raise GameException("Invalid stage metadata for item selection")

        # Validate an item has been selected
        if not self.game.stage_meta.selected_item:
            raise ReportedException("No item selected")

        selected_item = self.game.stage_meta.selected_item
        target_character = self.ability_item_target_character

        # Validate the item is still in the target's active_cards
        if selected_item not in target_character.active_cards:
            raise ReportedException(f"Item {selected_item} is no longer in target's active cards")

        # Remove the selected item
        target_character.active_cards.remove(selected_item)

        # Transition to opponent selection stage
        self.game.stage = STAGE_OPPONENT_SELECTION
        self.game.stage_meta = None

        return self.game
