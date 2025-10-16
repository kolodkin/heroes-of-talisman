"""
Battle Stage Actions

This module implements actions for the battle stage:
- ActivePlayerRollAction: Rolls dice for active player
- OpponentRollAction: Rolls dice for opponent
- RerollAction: Resets dice rolls in case of a draw
- BattleEndAction: Ends battle and reduces loser's health
"""

import random
from .action import Action
from ..models import (
    GamePlay,
    GameException,
    ReportedException,
    ActivePlayer2,
    ActivePlayer3,
    ActivePlayer4,
    Opponent2,
    Opponent3,
    Opponent4,
    BATTLE,
    CHARACTER_SELECT,
)


def calculate_winner(game: GamePlay) -> tuple[int, int]:
    """
    Calculate scores for active player and opponent.
    Returns (active_score, opponent_score).
    """
    if not game.active or not hasattr(game.active, "dice_roll"):
        raise GameException("Active player has no dice roll")
    if not game.opponent or not hasattr(game.opponent, "dice_roll"):
        raise GameException("Opponent has no dice roll")

    # Get players and characters
    active_player = game.players[game.active.player]
    opponent_player = game.players[game.opponent.player]
    active_character = active_player.characters[game.active.character]
    opponent_character = opponent_player.characters[game.opponent.character]

    # Calculate scores
    active_score = sum(game.active.dice_roll) + (active_character.attack or 0)
    opponent_score = sum(game.opponent.dice_roll) + (opponent_character.attack or 0)

    return active_score, opponent_score


def set_winner_if_both_rolled(game: GamePlay) -> None:
    """
    If both active and opponent have rolled, calculate winner and upgrade to ActivePlayer4/Opponent4.
    Modifies game in place.
    """
    # Check if both have rolled
    if not game.active or not hasattr(game.active, "dice_roll") or not game.active.dice_roll:
        return
    if not game.opponent or not hasattr(game.opponent, "dice_roll") or not game.opponent.dice_roll:
        return

    # Calculate winner
    active_score, opponent_score = calculate_winner(game)
    active_is_winner = active_score > opponent_score
    opponent_is_winner = opponent_score > active_score

    # Upgrade to ActivePlayer4 and Opponent4 with winner fields
    game.active = ActivePlayer4(
        player=game.active.player,
        character=game.active.character,
        dice_roll=game.active.dice_roll,
        winner=active_is_winner,
    )
    game.opponent = Opponent4(
        player=game.opponent.player,
        character=game.opponent.character,
        dice_roll=game.opponent.dice_roll,
        winner=opponent_is_winner,
    )


class ActivePlayerRollAction(Action):
    """
    Action invoked when the active player rolls their dice during battle.

    Rolls a dice (1-6) and sets active.dice to the rolled value.
    """

    def run(self) -> GamePlay:
        # Validate stage
        if self.game.stage != BATTLE:
            raise GameException(f"Cannot roll dice in stage: {self.game.stage}")

        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate active is ActivePlayer2 (has player and character but no dice yet)
        if not hasattr(self.game.active, "character"):
            raise GameException("Active player has no character selected")

        # Get character's dice value
        player = self.game.players[self.user]
        character = player.characters[self.game.active.character]
        num_dice = character.dice

        # Roll dice
        dice_roll = [random.randint(1, 6) for _ in range(num_dice)]

        # Upgrade active to ActivePlayer3 with dice_roll
        self.game.active = ActivePlayer3(
            player=self.game.active.player, character=self.game.active.character, dice_roll=dice_roll
        )

        # If opponent has also rolled, calculate winner and upgrade both
        set_winner_if_both_rolled(self.game)

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
            raise GameException(f"Cannot roll dice in stage: {self.game.stage}")

        # Validate opponent exists
        if not self.game.opponent:
            raise GameException("No opponent selected")

        # Validate user is the opponent player
        if self.game.opponent.player != self.user:
            raise ReportedException("You are not the opponent")

        # Validate opponent is Opponent2 (has player and character but no dice yet)
        if not hasattr(self.game.opponent, "character"):
            raise GameException("Opponent has no character selected")

        # Get character's dice value
        player = self.game.players[self.user]
        character = player.characters[self.game.opponent.character]
        num_dice = character.dice

        # Roll dice
        dice_roll = [random.randint(1, 6) for _ in range(num_dice)]

        # Upgrade opponent to Opponent3 with dice_roll
        self.game.opponent = Opponent3(
            player=self.game.opponent.player, character=self.game.opponent.character, dice_roll=dice_roll
        )

        # If active has also rolled, calculate winner and upgrade both
        set_winner_if_both_rolled(self.game)

        return self.game


class RerollAction(Action):
    """
    Action invoked when both players rolled and the result is a draw.

    Resets both active and opponent dice rolls, downgrading them back to
    ActivePlayer2 and Opponent2 (no dice_roll, no winner).
    """

    def run(self) -> GamePlay:
        # Validate stage
        if self.game.stage != BATTLE:
            raise GameException(f"Cannot reroll in stage: {self.game.stage}")

        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate both players have rolled
        if not hasattr(self.game.active, "dice_roll") or not self.game.active.dice_roll:
            raise GameException("Active player has not rolled yet")
        if not self.game.opponent or not hasattr(self.game.opponent, "dice_roll") or not self.game.opponent.dice_roll:
            raise GameException("Opponent has not rolled yet")

        # Validate it's actually a draw
        if not hasattr(self.game.active, "winner") or not hasattr(self.game.opponent, "winner"):
            raise GameException("Winner not determined yet")

        if self.game.active.winner or self.game.opponent.winner:
            raise GameException("Cannot reroll when there is a winner")

        # Reset to ActivePlayer2 and Opponent2 (remove dice_roll and winner)
        self.game.active = ActivePlayer2(
            player=self.game.active.player,
            character=self.game.active.character
        )
        self.game.opponent = Opponent2(
            player=self.game.opponent.player,
            character=self.game.opponent.character
        )

        return self.game
