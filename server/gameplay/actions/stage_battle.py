"""
Battle Stage Actions

This module implements actions for the battle stage:
- ActivePlayerRollAction: Rolls dice for active player
- OpponentRollAction: Rolls dice for opponent
"""

import random
from .action import Action
from ..models import (
    GamePlay,
    GameException,
    ReportedException,
    ActivePlayer3,
    Opponent3,
    BATTLE,
)


class ActivePlayerRollAction(Action):
    """
    Action invoked when the active player rolls their dice during battle.

    Rolls a dice (1-6) and sets active.dice to the rolled value.
    """

    def run(self) -> GamePlay:
        # Validate stage
        if self.game.stage != BATTLE:
            raise GameException(
                f"Cannot roll dice in stage: {self.game.stage}"
            )

        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate active is ActivePlayer2 (has player and character but no dice yet)
        if not hasattr(self.game.active, 'character'):
            raise GameException("Active player has no character selected")

        # Roll dice
        dice_value = random.randint(1, 6)

        # Upgrade active to ActivePlayer3 with dice_roll
        self.game.active = ActivePlayer3(
            player=self.game.active.player,
            character=self.game.active.character,
            dice_roll=dice_value
        )

        return self.game


class OpponentRollAction(Action):
    """
    Action invoked when the opponent rolls their dice during battle.

    Rolls a dice (1-6) and sets opponent.dice to the rolled value.
    Note: Can be invoked by any player (not just active player).
    """

    def run(self) -> GamePlay:
        # Validate stage
        if self.game.stage != BATTLE:
            raise GameException(
                f"Cannot roll dice in stage: {self.game.stage}"
            )

        # Validate opponent exists
        if not self.game.opponent:
            raise GameException("No opponent selected")

        # Validate user is the opponent player
        if self.game.opponent.player != self.user:
            raise ReportedException("You are not the opponent")

        # Validate opponent is Opponent2 (has player and character but no dice yet)
        if not hasattr(self.game.opponent, 'character'):
            raise GameException("Opponent has no character selected")

        # Roll dice
        dice_value = random.randint(1, 6)

        # Upgrade opponent to Opponent3 with dice_roll
        self.game.opponent = Opponent3(
            player=self.game.opponent.player,
            character=self.game.opponent.character,
            dice_roll=dice_value
        )

        return self.game
