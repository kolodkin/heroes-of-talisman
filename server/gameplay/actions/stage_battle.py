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
    BATTLE_DICE_ROLL,
    BATTLE_END,
    CHARACTER_SELECT,
)


def calculate_winner(game: GamePlay) -> tuple[int, int]:
    """
    Calculate scores for active player and opponent.
    Returns (active_score, opponent_score).
    """
    if not game.active or not isinstance(game.active, (ActivePlayer3, ActivePlayer4)):
        raise GameException("Active player has no dice roll")
    if not game.opponent or not isinstance(game.opponent, (Opponent3, Opponent4)):
        raise GameException("Opponent has no dice roll")

    # Get characters
    active_player = game.players[game.active.player]
    opponent_player = game.players[game.opponent.player]
    active_character = active_player.characters[game.active.character]
    opponent_character = opponent_player.characters[game.opponent.character]

    # Calculate scores
    active_score = sum(game.active.dice_roll) + active_character.attack
    opponent_score = sum(game.opponent.dice_roll) + opponent_character.attack

    return active_score, opponent_score


def set_winner_if_both_rolled(game: GamePlay) -> None:
    """
    If both active and opponent have rolled, calculate winner and upgrade to ActivePlayer4/Opponent4.
    If there's a winner (not a draw), transition to BATTLE_END stage.
    Modifies game in place.
    """
    # Check if both have rolled
    if not game.active or not isinstance(game.active, (ActivePlayer3, ActivePlayer4)) or not game.active.dice_roll:
        return
    if not game.opponent or not isinstance(game.opponent, (Opponent3, Opponent4)) or not game.opponent.dice_roll:
        return

    # Calculate winner
    active_score, opponent_score = calculate_winner(game)
    active_is_winner = active_score > opponent_score
    opponent_is_winner = opponent_score > active_score

    # Import BattleResult at top of function to avoid circular imports
    from ..models import BattleResult

    # Upgrade to ActivePlayer4 and Opponent4 with result fields
    game.active = ActivePlayer4(
        player=game.active.player,
        character=game.active.character,
        dice_roll=game.active.dice_roll,
        result=BattleResult(winner=active_is_winner, score=active_score),
    )
    game.opponent = Opponent4(
        player=game.opponent.player,
        character=game.opponent.character,
        dice_roll=game.opponent.dice_roll,
        result=BattleResult(winner=opponent_is_winner, score=opponent_score),
    )

    # If there's a winner (not a draw), transition to BATTLE_END
    if active_is_winner or opponent_is_winner:
        game.stage = BATTLE_END


class ActivePlayerRollAction(Action):
    """
    Action invoked when the active player rolls their dice during battle.

    Rolls a dice (1-6) and sets active.dice to the rolled value.
    """

    def run(self) -> GamePlay:
        # Validate stage
        if self.game.stage != BATTLE_DICE_ROLL:
            raise GameException(f"Cannot roll dice in stage: {self.game.stage}")

        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate user exists
        if self.user not in self.game.players:
            raise GameException("Player not in game")

        # Validate active is ActivePlayer2 or higher (has player and character but no dice yet)
        if not isinstance(self.game.active, (ActivePlayer2, ActivePlayer3, ActivePlayer4)):
            raise GameException("Active player has no character selected")

        # Get character's dice value using the property
        character = self.active_character
        num_dice = character.dice

        # Roll dice
        dice_roll = [random.randint(1, 6) for _ in range(num_dice)]

        # Validate dice count matches character's dice
        if len(dice_roll) != num_dice:
            raise GameException(f"Dice roll count {len(dice_roll)} does not match character dice {num_dice}")

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
        if self.game.stage != BATTLE_DICE_ROLL:
            raise GameException(f"Cannot roll dice in stage: {self.game.stage}")

        # Validate opponent exists
        if not self.game.opponent:
            raise GameException("No opponent selected")

        # Validate user is the opponent player
        if self.game.opponent.player != self.user:
            raise ReportedException("You are not the opponent")

        # Validate opponent is Opponent2 or higher (has player and character but no dice yet)
        if not isinstance(self.game.opponent, (Opponent2, Opponent3, Opponent4)):
            raise GameException("Opponent has no character selected")

        # Get character's dice value using the property
        character = self.opponent_character
        num_dice = character.dice

        # Roll dice
        dice_roll = [random.randint(1, 6) for _ in range(num_dice)]

        # Validate dice count matches character's dice
        if len(dice_roll) != num_dice:
            raise GameException(f"Dice roll count {len(dice_roll)} does not match character dice {num_dice}")

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
        if self.game.stage != BATTLE_DICE_ROLL:
            raise GameException(f"Cannot reroll in stage: {self.game.stage}")

        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate both players have rolled (must be ActivePlayer3/4 and Opponent3/4)
        if not isinstance(self.game.active, (ActivePlayer3, ActivePlayer4)) or not self.game.active.dice_roll:
            raise GameException("Active player has not rolled yet")
        if not self.game.opponent or not isinstance(self.game.opponent, (Opponent3, Opponent4)) or not self.game.opponent.dice_roll:
            raise GameException("Opponent has not rolled yet")

        # Validate winner has been determined (must be ActivePlayer4/Opponent4)
        if not isinstance(self.game.active, ActivePlayer4) or not isinstance(self.game.opponent, Opponent4):
            raise GameException("Winner not determined yet")

        if self.game.active.result.winner or self.game.opponent.result.winner:
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


class DebugSetBattleDiceRollsAction(Action):
    """
    DEBUG ONLY: Set dice rolls for battle participants to deterministic values.

    This action is only used for debugging and testing purposes. It is NOT part
    of the formal game flow and should never be used in production gameplay.

    Allows setting specific dice roll values for both active player and opponent
    to create deterministic test scenarios (e.g., ensuring player 1 always wins).

    Args:
        active_dice_roll: list of dice values for the active player
        opponent_dice_roll: list of dice values for the opponent
        Example: active_dice_roll=[6], opponent_dice_roll=[1]
    """

    def run(self, active_dice_roll: list[int], opponent_dice_roll: list[int]) -> GamePlay:
        # Validate stage - allow both BATTLE_DICE_ROLL and BATTLE_END
        if self.game.stage not in [BATTLE_DICE_ROLL, BATTLE_END]:
            raise GameException(f"Cannot set dice rolls in stage: {self.game.stage}")

        # Validate both players have rolled (must be ActivePlayer3/4 and Opponent3/4)
        if not isinstance(self.game.active, (ActivePlayer3, ActivePlayer4)) or not self.game.active.dice_roll:
            raise GameException("Active player has not rolled yet")
        if not self.game.opponent or not isinstance(self.game.opponent, (Opponent3, Opponent4)) or not self.game.opponent.dice_roll:
            raise GameException("Opponent has not rolled yet")

        # Get character dice counts using properties
        active_character = self.active_character
        opponent_character = self.opponent_character

        # Validate dice roll counts match character dice
        if len(active_dice_roll) != active_character.dice:
            raise GameException(
                f"Active dice roll count {len(active_dice_roll)} does not match character dice {active_character.dice}"
            )
        if len(opponent_dice_roll) != opponent_character.dice:
            raise GameException(
                f"Opponent dice roll count {len(opponent_dice_roll)} does not match character dice {opponent_character.dice}"
            )

        # Update active player's dice roll
        self.game.active = ActivePlayer3(
            player=self.game.active.player,
            character=self.game.active.character,
            dice_roll=active_dice_roll
        )

        # Update opponent's dice roll
        self.game.opponent = Opponent3(
            player=self.game.opponent.player,
            character=self.game.opponent.character,
            dice_roll=opponent_dice_roll
        )

        # Recalculate winner based on new dice rolls
        set_winner_if_both_rolled(self.game)

        return self.game
