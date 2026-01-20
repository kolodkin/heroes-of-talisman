"""
Card Draw Stage Actions

This module implements actions for the card draw stage:
- CardDrawAction: Automatically draws a random card and stores it in stage_meta
- CardSelectAction: Applies the drawn card's effects and transitions to ability_selection
"""

import random
import copy
from .action import Action
from ..common import GameException, ReportedException
from ..effects import APPLY_TO_SELF, APPLY_TO_BATTLE_OPPONENT
from ..cards import CardName, CARDS_MAP, CARDS_NAMES
from ..gameplay import CARD_DRAW, ABILITY_SELECTION
from ..gameplay import GamePlay, CardDrawMeta, AbilitySelectMeta


class CardDrawAction(Action):
    """
    Action invoked when entering the card draw stage.

    Draws a random card from the available cards and stores it in stage_meta.
    This action should be called automatically when the stage starts.
    """

    @property
    def action_stages(self):
        return [CARD_DRAW]

    def _run(self) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Draw a random card
        drawn_card = random.choice(CARDS_NAMES)

        # Store the drawn card in stage metadata
        self.game.stage_meta = CardDrawMeta(drawn_card=drawn_card)

        return self.game


class CardSelectAction(Action):
    """
    Action invoked when the player confirms to use the drawn card.

    Applies the card's effects to the active player's character and transitions
    to the ability_selection stage.
    """

    @property
    def action_stages(self):
        return [CARD_DRAW]

    def _run(self) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Get the active character
        if not hasattr(self.game.active, "character"):
            raise GameException("No character selected")

        # Validate that a card was drawn
        if not self.game.stage_meta or not isinstance(self.game.stage_meta, CardDrawMeta):
            raise GameException("No card was drawn")

        player = self.game.players[self.user]
        character = player.characters[self.game.active.character]

        # Get the drawn card
        drawn_card_name = self.game.stage_meta.drawn_card
        card_obj = CARDS_MAP.get(drawn_card_name)

        if not card_obj:
            raise GameException(f"Card {drawn_card_name} not found")

        # Store the selected card in GamePlay.card
        self.game.card = drawn_card_name

        # Check if character is restricted from using this card
        character_type = self.game.active.character
        is_restricted = character_type in card_obj.restricted_characters

        # Apply effects and add card only if not restricted
        if not is_restricted:
            for effect in card_obj.effects:
                if effect.apply_to == APPLY_TO_SELF:
                    # Deep copy the effect to avoid modifying the original card definition
                    effect_copy = copy.deepcopy(effect)
                    character.effects.append(effect_copy)

            # Add the card to the character's card list
            character.cards.append(drawn_card_name)

        # Clear stage_meta after selection
        self.game.stage_meta = None

        # Transition to ability_selection stage
        self.game.stage = ABILITY_SELECTION

        # Auto-select if character has only one ability
        if len(character.abilities) == 1:
            self.game.stage_meta = AbilitySelectMeta(
                selected=character.abilities[0].name
            )

        return self.game
