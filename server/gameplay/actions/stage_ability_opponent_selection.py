"""
Ability Opponent Selection Stage Actions

This module implements actions for the ability opponent selection stage:
- AbilityOpponentPressAction: Highlights selected opponent for ability targeting by setting stage_meta
- AbilityOpponentSelectAction: Confirms ability target, applies effects, and transitions to opponent_selection stage
"""

from .action import Action
from ..common import GameException, ReportedException
from ..abilities import get_ability_effects
from ..effects import EFFECT_MIND_READING, DrainEffect, NeutralizeItemEffect
from ..gameplay import (
    STAGE_ABILITY_OPPONENT_SELECTION,
    STAGE_ABILITY_ITEM_SELECTION,
    STAGE_OPPONENT_SELECTION,
    GamePlay,
    AbilityItemMeta,
    Opponent2,
)


class AbilityOpponentPressAction(Action):
    """
    Action invoked when an opponent's character is clicked during ability opponent selection.

    Sets stage_meta to an Opponent2 object with the chosen opponent player and character,
    triggering a game_update that highlights the selected opponent in the UI.
    """

    @property
    def action_stages(self):
        return [STAGE_ABILITY_OPPONENT_SELECTION]

    def _run(self, opponent: str, character: str) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate opponent exists
        if opponent not in self.game.players:
            raise ReportedException(f"Opponent {opponent} not in game")

        # Validate opponent is not the current player
        if opponent == self.user:
            raise ReportedException("Cannot select yourself as opponent")

        # Validate character exists for opponent
        opponent_player = self.game.players[opponent]
        if character not in opponent_player.characters:
            raise ReportedException(
                f"Character {character} not available for opponent"
            )

        # Validate character is alive
        if not opponent_player.characters[character].is_alive:
            raise ReportedException(f"Opponent character {character} is dead and can't be targeted")

        # Validate character is not protected by mind_reading against the active player
        mind_reading_protection = f"{EFFECT_MIND_READING}:{self.user}"
        if mind_reading_protection in opponent_player.characters[character].effects:
            raise ReportedException(f"Character {character} is protected by mind reading")

        # Set selected opponent in stage metadata
        self.game.stage_meta = Opponent2(player=opponent, character=character)

        return self.game


class AbilityOpponentSelectAction(Action):
    """
    Action invoked when the Select button is pressed to confirm ability target.

    Reads the selected opponent from stage_meta, applies the ability's effects to the target character,
    stores the target in ability_opponent field, and transitions the game stage to 'opponent_selection'.
    """

    @property
    def action_stages(self):
        return [STAGE_ABILITY_OPPONENT_SELECTION]

    def _run(self) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate stage_meta is set and is an Opponent2
        if not self.game.stage_meta or not isinstance(
            self.game.stage_meta, Opponent2
        ):
            raise ReportedException("No ability target selected")

        # Validate ability is selected
        if not self.game.ability:
            raise GameException("No ability selected")

        # Get opponent from stage_meta
        selected_opponent = self.game.stage_meta

        # Validate opponent character is still alive
        opponent_player = self.game.players[selected_opponent.player]
        target_character = opponent_player.characters[selected_opponent.character]
        if not target_character.is_alive:
            raise ReportedException(
                f"Opponent character {selected_opponent.character} is dead and can't be targeted"
            )

        # Validate character is not protected by mind_reading against the active player
        mind_reading_protection = f"{EFFECT_MIND_READING}:{self.user}"
        if mind_reading_protection in target_character.effects:
            raise ReportedException(f"Character {selected_opponent.character} is protected by mind reading")

        # Check if any effect requires item selection
        has_neutralize_item = any(
            isinstance(effect, NeutralizeItemEffect)
            for effect in get_ability_effects(self.game.ability)
        )
        has_drain = any(
            isinstance(effect, DrainEffect)
            for effect in get_ability_effects(self.game.ability)
        )

        if (has_neutralize_item or has_drain) and target_character.active_cards:
            # Route to item selection stage so active player can choose which item to neutralize/drain
            self.game.stage = STAGE_ABILITY_ITEM_SELECTION
            self.game.stage_meta = AbilityItemMeta(
                target_player=selected_opponent.player,
                target_character=selected_opponent.character,
            )
            # Store the ability opponent now (used by item selection stage)
            self.game.ability_opponent = selected_opponent
        else:
            # No items to select (or no item-targeting effect): apply remaining effects and proceed
            for effect in get_ability_effects(self.game.ability):
                if not isinstance(effect, (NeutralizeItemEffect, DrainEffect)):
                    target_character.effects.append(effect.name)

            # Store the ability opponent
            self.game.ability_opponent = selected_opponent

            # Transition to opponent selection stage
            self.game.stage = STAGE_OPPONENT_SELECTION
            self.game.stage_meta = None

        return self.game
