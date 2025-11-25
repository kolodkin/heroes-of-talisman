"""
Opponent Selection Stage Actions

This module implements actions for the opponent selection stage:
- OpponentPressAction: Highlights selected opponent by setting stage_meta
- OpponentSelectAction: Confirms opponent selection and transitions to battle stage
"""

import copy
from .action import Action
from ..models import (
    GamePlay,
    GameException,
    ReportedException,
    Opponent2,
    BATTLE_DICE_ROLL,
    OPPONENT_SELECTION,
    APPLY_TO_BATTLE_OPPONENT,
)


class OpponentPressAction(Action):
    """
    Action invoked when an opponent's character is clicked during opponent selection.

    Sets stage_meta to an Opponent object with the chosen opponent player and character,
    triggering a game_update that highlights the selected opponent in the UI.
    """

    def run(self, opponent: str, character: str) -> GamePlay:
        # Validate stage
        if self.game.stage != OPPONENT_SELECTION:
            raise GameException(
                f"Cannot select opponent in stage: {self.game.stage}"
            )

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
            raise ReportedException(f"Opponent character {character} is dead and can't be selected")

        # Set selected opponent in stage metadata
        self.game.stage_meta = Opponent2(player=opponent, character=character)

        return self.game


class OpponentSelectAction(Action):
    """
    Action invoked when the Select button is pressed to confirm opponent choice.

    Reads the selected opponent from stage_meta, populates the opponent field
    in game metadata, and transitions the game stage to 'battle'.
    """

    def run(self) -> GamePlay:
        # Validate stage
        if self.game.stage != OPPONENT_SELECTION:
            raise GameException(
                f"Cannot confirm selection in stage: {self.game.stage}"
            )

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
            raise ReportedException("No opponent selected")

        # Get opponent from stage_meta
        selected_opponent = self.game.stage_meta

        # Validate opponent character is still alive
        opponent_player = self.game.players[selected_opponent.player]
        opponent_character = opponent_player.characters[selected_opponent.character]
        if not opponent_character.is_alive:
            raise ReportedException(
                f"Opponent character {selected_opponent.character} is dead and can't be selected"
            )

        # Set opponent in game metadata
        self.game.opponent = selected_opponent

        # Apply "battle_opponent" effects to the opponent's character
        if self.game.ability:
            for effect in self.game.ability.effects:
                if effect.apply_to == APPLY_TO_BATTLE_OPPONENT:
                    # Deep copy the effect to avoid modifying the original ability definition
                    effect_copy = copy.deepcopy(effect)
                    opponent_character.effects.append(effect_copy)

        # Transition to battle dice roll stage
        self.game.stage = BATTLE_DICE_ROLL
        self.game.stage_meta = None  # Clear stage metadata

        return self.game
