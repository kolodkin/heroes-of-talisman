"""
Card Draw Stage Actions

This module implements actions for the card draw stage:
- CardDrawAction: Automatically draws a card from the deck and stores it in stage_meta
- CardSelectAction: Applies the drawn card's effects and transitions to ability_selection
"""

from .action import Action
from ..common import GameException, ReportedException
from ..effects import HealEffect, LevelDownEffect, LevelUpEffect
from ..cards import CardName, CARDS_MAP
from ..gameplay import STAGE_CARD_DRAW, STAGE_ABILITY_SELECTION, CHARACTER_STATS_BY_LEVEL, MAX_LEVEL
from ..gameplay import GamePlay, CardDrawMeta, AbilitySelectMeta


class CardDrawAction(Action):
    """
    Action invoked when entering the card draw stage.

    Draws a random card from the available cards and stores it in stage_meta.
    This action should be called automatically when the stage starts.
    """

    @property
    def action_stages(self):
        return [STAGE_CARD_DRAW]

    def _run(self) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Draw a card from the deck (auto-resets when empty)
        drawn_card = self.game.deck.draw()

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
        return [STAGE_CARD_DRAW]

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
                # Handle instant effects (like HealEffect, LevelUpEffect) immediately
                if isinstance(effect, HealEffect):
                    character.health = min(
                        character.max_health,
                        character.health + effect.heal_amount
                    )
                elif isinstance(effect, LevelDownEffect):
                    # No effect if already at level 1
                    if character.level > 1:
                        new_level = max(1, character.level - effect.level_decrease)
                        level_stats = CHARACTER_STATS_BY_LEVEL[new_level]
                        char_stats = level_stats[character_type]
                        # Update character stats
                        character.level = new_level
                        character.max_health = char_stats["max_health"]
                        character.dice = char_stats["dice"]
                        character.attack = char_stats["attack"]
                        # Cap health at new max_health
                        character.health = min(character.health, character.max_health)
                elif isinstance(effect, LevelUpEffect):
                    # No effect if already at max level
                    if character.level < MAX_LEVEL:
                        # Increase character level
                        new_level = min(MAX_LEVEL, character.level + effect.level_increase)
                        level_stats = CHARACTER_STATS_BY_LEVEL[new_level]
                        char_stats = level_stats[character_type]
                        # Update character stats
                        character.level = new_level
                        character.max_health = char_stats["max_health"]
                        character.dice = char_stats["dice"]
                        character.attack = char_stats["attack"]
                        # Restore health to new max_health
                        character.health = character.max_health
                else:
                    # Persistent card effect - add card name to active_cards
                    character.active_cards.append(drawn_card_name)
                    break  # Only add card name once

            # Add the card to the character's card list
            character.cards.append(drawn_card_name)

        # Clear stage_meta after selection
        self.game.stage_meta = None

        # Transition to ability_selection stage
        self.game.stage = STAGE_ABILITY_SELECTION

        # Auto-select if character has only one ability
        if len(character.abilities) == 1:
            self.game.stage_meta = AbilitySelectMeta(
                selected=character.abilities[0].name
            )

        return self.game


class DebugSetDrawnCardAction(Action):
    """
    DEBUG ONLY: Set the drawn card to a specific card for testing.

    This action is only used for debugging and testing purposes. It is NOT part
    of the formal game flow and should never be used in production gameplay.

    Allows setting a specific card in stage_meta to create deterministic test
    scenarios (e.g., ensuring a specific card is always drawn).

    Args:
        card_name: The card name to set (e.g., "metal_armor", "sacred_sord")
    """

    @property
    def action_stages(self):
        return [STAGE_CARD_DRAW]

    def _run(self, card_name: str) -> GamePlay:
        # Validate card exists
        if card_name not in CARDS_MAP:
            raise GameException(f"Invalid card name: {card_name}")

        # Set the drawn card in stage_meta
        self.game.stage_meta = CardDrawMeta(drawn_card=card_name)

        return self.game
