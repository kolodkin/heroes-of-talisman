"""
Battle End Action

Ends the battle, calculates winner, and reduces loser's health by 1.
"""

from .action import Action, rotate_to_next_player
from ..common import GameException, ReportedException, ACTION_BATTLE_END
from ..gameplay import (
    STAGE_BATTLE_END,
    GamePlay,
    ActivePlayer3,
    ActivePlayer4,
    Opponent3,
    Opponent4,
)


class BattleEndAction(Action):
    """
    Action invoked when the active player presses continue after battle.

    Calculates the winner based on dice + attack values, reduces loser's health by 1,
    clears battle state, and transitions to character_select stage.
    """

    @property
    def action_stages(self):
        return [STAGE_BATTLE_END]

    def _run(self) -> GamePlay:
        # Validate user is the active player
        if not self.game.active or self.game.active.player != self.user:
            raise ReportedException("It's not your turn")

        # Validate both players have rolled (must be ActivePlayer3/4 and Opponent3/4)
        if not isinstance(self.game.active, (ActivePlayer3, ActivePlayer4)) or not self.game.active.dice_roll:
            raise ReportedException("Active player hasn't rolled yet")

        if not self.game.opponent or not isinstance(self.game.opponent, (Opponent3, Opponent4)) or not self.game.opponent.dice_roll:
            raise ReportedException("Opponent hasn't rolled yet")

        # Get characters using properties
        active_character = self.active_character
        opponent_character = self.opponent_character

        # Calculate scores (including effects)
        active_total_attack = active_character.attack + active_character.effect.attack_bonus + active_character.effect.attack_neg_bonus
        opponent_total_attack = opponent_character.attack + opponent_character.effect.attack_bonus + opponent_character.effect.attack_neg_bonus

        active_score = sum(self.game.active.dice_roll) + active_total_attack
        opponent_score = sum(self.game.opponent.dice_roll) + opponent_total_attack

        # Determine loser and reduce health (defense reduces incoming damage)
        if active_score > opponent_score:
            # Active player wins, opponent loses health
            damage = max(0, 1 - opponent_character.effect.defense_bonus)
            opponent_character.health = max(0, opponent_character.health - damage)
        elif opponent_score > active_score:
            # Opponent wins, active player loses health
            damage = max(0, 1 - active_character.effect.defense_bonus)
            active_character.health = max(0, active_character.health - damage)
        # If tied, no one loses health

        # Dispose effects with 'battle_end' in their dispose_actions list
        def should_keep_effect(effect):
            """Returns True if effect should be kept after battle"""
            return ACTION_BATTLE_END not in effect.dispose_actions

        active_character.effects = [
            effect for effect in active_character.effects
            if should_keep_effect(effect)
        ]
        opponent_character.effects = [
            effect for effect in opponent_character.effects
            if should_keep_effect(effect)
        ]

        # Rotate to next player's turn
        rotate_to_next_player(self.game)

        return self.game
