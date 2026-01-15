"""
Ability Opponent Selection Stage Actions

This module implements actions for the ability opponent selection stage:
- AbilityOpponentPressAction: Highlights selected opponent for ability targeting by setting stage_meta
- AbilityOpponentSelectAction: Confirms ability target, applies effects, and transitions to opponent_selection stage
"""

from .action import Action
from ..models import (
    GamePlay,
    GameException,
    ReportedException,
    Opponent2,
    ABILITY_OPPONENT_SELECTION,
    OPPONENT_SELECTION,
)


class AbilityOpponentPressAction(Action):
    """
    Action invoked when an opponent's character is clicked during ability opponent selection.

    Sets stage_meta to an Opponent2 object with the chosen opponent player and character,
    triggering a game_update that highlights the selected opponent in the UI.
    """

    @property
    def action_stages(self):
        return [ABILITY_OPPONENT_SELECTION]

    def run(self, opponent: str, character: str) -> GamePlay:

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
        return [ABILITY_OPPONENT_SELECTION]

    def run(self) -> GamePlay:

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

        # Apply ability effects to target character
        for effect in self.game.ability.effects:
            target_character.effects.append(effect)

        # Store the ability opponent
        self.game.ability_opponent = selected_opponent

        # Transition to opponent selection stage
        self.game.stage = OPPONENT_SELECTION
        self.game.stage_meta = None  # Clear stage metadata

        return self.game
