"""
Battle End Action

Ends the battle, calculates winner, and reduces loser's health by 1.
"""

from .action import Action
from ..models import (
    GamePlay,
    GameException,
    ReportedException,
    ActivePlayer1,
    ActivePlayer3,
    ActivePlayer4,
    Opponent3,
    Opponent4,
    BATTLE_END,
    CHARACTER_SELECT,
)


class BattleEndAction(Action):
    """
    Action invoked when the active player presses continue after battle.

    Calculates the winner based on dice + attack values, reduces loser's health by 1,
    clears battle state, and transitions to character_select stage.
    """

    @property
    def action_stages(self):
        return [BATTLE_END]

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

        # Calculate scores
        active_score = sum(self.game.active.dice_roll) + active_character.attack
        opponent_score = sum(self.game.opponent.dice_roll) + opponent_character.attack

        # Determine loser and reduce health
        if active_score > opponent_score:
            # Active player wins, opponent loses health
            opponent_character.health = max(0, opponent_character.health - 1)
        elif opponent_score > active_score:
            # Opponent wins, active player loses health
            active_character.health = max(0, active_character.health - 1)
        # If tied, no one loses health

        # Dispose effects with 'battle_end' in their dispose_actions list
        from ..models import BATTLE_END_ACTION

        def should_keep_effect(effect):
            """Returns True if effect should be kept after battle"""
            return BATTLE_END_ACTION not in effect.dispose_actions

        active_character.effects = [
            effect for effect in active_character.effects
            if should_keep_effect(effect)
        ]
        opponent_character.effects = [
            effect for effect in opponent_character.effects
            if should_keep_effect(effect)
        ]

        # Get next player (circular rotation)
        player_names = list(self.game.players.keys())
        current_active_index = player_names.index(self.game.active.player)
        next_player_index = (current_active_index + 1) % len(player_names)
        next_player_name = player_names[next_player_index]

        # Clear battle state and transition to next turn
        self.game.active = ActivePlayer1(player=next_player_name)
        self.game.opponent = None
        self.game.stage = CHARACTER_SELECT
        self.game.stage_meta = None

        return self.game
